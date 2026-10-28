#!/usr/bin/env python3
"""
Read-only topology preflight for dp_fabric_cicd_lab.

The script:

- authenticates through the current Azure CLI session;
- discovers one Fabric Deployment Pipeline by exact name;
- validates its stage-to-workspace assignments;
- validates the expected item inventory in all stages;
- validates adjacent-stage item pairing;
- writes non-secret JSON evidence.

The script performs HTTP GET operations only.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import AzureCliCredential, CredentialUnavailableError


FABRIC_API_BASE = "https://api.fabric.microsoft.com/v1"
FABRIC_SCOPE = "https://api.fabric.microsoft.com/.default"
ALLOWED_API_HOST = "api.fabric.microsoft.com"

EXPECTED_STAGE_WORKSPACES = {
    "Development": "ws_reference_lab_dev",
    "Test": "ws_reference_lab_test",
    "Production": "ws_reference_lab_prod",
}

EXPECTED_ITEMS = {
    ("Lakehouse", "lh_cicd_lab"),
    ("Notebook", "nb_01_seed_and_transform_cicd_lab"),
    ("DataPipeline", "pl_01_run_cicd_lab_transform"),
    ("VariableLibrary", "vl_cicd_lab_config"),
}


class PreflightFailure(RuntimeError):
    """Raised when the Fabric topology violates an expected invariant."""


class TokenProvider:
    """Cache a Fabric token acquired through AzureCliCredential."""

    def __init__(self, credential: AzureCliCredential) -> None:
        self._credential = credential
        self._access_token: AccessToken | None = None

    def get_token(self) -> str:
        now = int(time.time())

        if (
            self._access_token is None
            or self._access_token.expires_on - now < 300
        ):
            self._access_token = self._credential.get_token(
                FABRIC_SCOPE
            )

        return self._access_token.token


class FabricClient:
    """Small read-only client for Fabric REST API collections."""

    def __init__(self, token_provider: TokenProvider) -> None:
        self._token_provider = token_provider
        self._session = requests.Session()

    def get_collection(self, url: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        next_url: str | None = url

        while next_url:
            self._validate_fabric_url(next_url)
            payload = self._get_json(next_url)

            values = payload.get("value")

            if not isinstance(values, list):
                raise PreflightFailure(
                    f"GET {next_url} returned no valid 'value' array."
                )

            for value in values:
                if not isinstance(value, dict):
                    raise PreflightFailure(
                        f"GET {next_url} returned a non-object item."
                    )

                results.append(value)

            continuation_uri = payload.get("continuationUri")

            next_url = (
                continuation_uri
                if isinstance(continuation_uri, str)
                and continuation_uri.strip()
                else None
            )

        return results

    def _get_json(self, url: str) -> dict[str, Any]:
        max_attempts = 5

        for attempt in range(1, max_attempts + 1):
            response = self._session.get(
                url,
                headers={
                    "Authorization": (
                        f"Bearer {self._token_provider.get_token()}"
                    ),
                    "Accept": "application/json",
                },
                timeout=60,
            )

            should_retry = (
                response.status_code == 429
                or 500 <= response.status_code < 600
            )

            if should_retry:
                if attempt == max_attempts:
                    self._raise_http_failure(response)

                retry_after = response.headers.get("Retry-After")

                delay = (
                    int(retry_after)
                    if retry_after and retry_after.isdigit()
                    else min(2**attempt, 30)
                )

                print(
                    f"Fabric returned HTTP {response.status_code}; "
                    f"retrying in {delay} second(s)...",
                    file=sys.stderr,
                )

                time.sleep(delay)
                continue

            if not response.ok:
                self._raise_http_failure(response)

            try:
                payload = response.json()
            except requests.JSONDecodeError as error:
                raise PreflightFailure(
                    f"GET {url} returned invalid JSON."
                ) from error

            if not isinstance(payload, dict):
                raise PreflightFailure(
                    f"GET {url} returned an unexpected JSON payload."
                )

            return payload

        raise AssertionError("HTTP retry loop exited unexpectedly.")

    @staticmethod
    def _validate_fabric_url(url: str) -> None:
        parsed = urlparse(url)

        if (
            parsed.scheme != "https"
            or parsed.hostname != ALLOWED_API_HOST
        ):
            raise PreflightFailure(
                "Refusing to send a Fabric bearer token to an "
                f"unexpected URL: {url}"
            )

    @staticmethod
    def _raise_http_failure(
        response: requests.Response,
    ) -> None:
        request_id = (
            response.headers.get("x-ms-request-id")
            or response.headers.get("requestId")
            or response.headers.get("ActivityId")
        )

        try:
            response_body: Any = response.json()
            body_text = json.dumps(
                response_body,
                ensure_ascii=False,
            )
        except requests.JSONDecodeError:
            body_text = response.text.strip()

        request_suffix = (
            f" Request ID: {request_id}."
            if request_id
            else ""
        )

        raise PreflightFailure(
            f"GET {response.url} failed with HTTP "
            f"{response.status_code}: {body_text}."
            f"{request_suffix}"
        )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the read-only topology and item pairing "
            "of a Fabric Deployment Pipeline."
        )
    )

    parser.add_argument(
        "--pipeline-name",
        default="dp_fabric_cicd_lab",
        help="Exact Fabric Deployment Pipeline display name.",
    )

    parser.add_argument(
        "--tenant-id",
        help=(
            "Optional Microsoft Entra tenant ID used when "
            "requesting the Fabric token."
        ),
    )

    parser.add_argument(
        "--output",
        default="artifacts/fabric-deployment-preflight.json",
        help="Path for the generated JSON evidence.",
    )

    return parser.parse_args()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PreflightFailure(message)


def get_item_key(
    item: dict[str, Any],
) -> tuple[str, str]:
    item_type = item.get("itemType")
    display_name = item.get("itemDisplayName")

    require(
        isinstance(item_type, str) and bool(item_type.strip()),
        "A stage item has no valid itemType.",
    )

    require(
        isinstance(display_name, str)
        and bool(display_name.strip()),
        "A stage item has no valid itemDisplayName.",
    )

    return item_type, display_name


def find_pipeline(
    pipelines: list[dict[str, Any]],
    pipeline_name: str,
) -> dict[str, Any]:
    matches = [
        pipeline
        for pipeline in pipelines
        if pipeline.get("displayName") == pipeline_name
    ]

    visible_names = sorted(
        str(pipeline.get("displayName"))
        for pipeline in pipelines
        if pipeline.get("displayName")
    )

    require(
        len(matches) == 1,
        (
            f"Expected exactly one visible Deployment Pipeline "
            f"named '{pipeline_name}', found {len(matches)}. "
            f"Visible pipelines: {visible_names}"
        ),
    )

    return matches[0]


def validate_stages(
    stages: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    stages_by_name = {
        str(stage.get("displayName")): stage
        for stage in stages
        if stage.get("displayName")
    }

    for stage_name, expected_workspace in (
        EXPECTED_STAGE_WORKSPACES.items()
    ):
        require(
            stage_name in stages_by_name,
            f"Expected stage '{stage_name}' was not returned.",
        )

        stage = stages_by_name[stage_name]
        actual_workspace = stage.get("workspaceName")

        require(
            actual_workspace == expected_workspace,
            (
                f"Stage '{stage_name}' is assigned to "
                f"'{actual_workspace}', expected "
                f"'{expected_workspace}'."
            ),
        )

        require(
            isinstance(stage.get("id"), str)
            and bool(stage["id"].strip()),
            f"Stage '{stage_name}' has no valid stage ID.",
        )

        require(
            isinstance(stage.get("workspaceId"), str)
            and bool(stage["workspaceId"].strip()),
            (
                f"Stage '{stage_name}' has no visible "
                "workspace ID."
            ),
        )

    return stages_by_name


def validate_stage_inventory(
    stage_name: str,
    items: list[dict[str, Any]],
) -> dict[tuple[str, str], dict[str, Any]]:
    items_by_key: dict[
        tuple[str, str],
        dict[str, Any],
    ] = {}

    for item in items:
        key = get_item_key(item)

        require(
            key not in items_by_key,
            (
                f"Stage '{stage_name}' contains more than "
                f"one item with type/name {key}."
            ),
        )

        items_by_key[key] = item

    missing_items = sorted(
        EXPECTED_ITEMS - set(items_by_key)
    )

    require(
        not missing_items,
        (
            f"Stage '{stage_name}' is missing expected "
            f"items: {missing_items}"
        ),
    )

    extra_items = sorted(
        set(items_by_key) - EXPECTED_ITEMS
    )

    if extra_items:
        print(
            f"  Note: stage '{stage_name}' also contains "
            f"supported items: {extra_items}"
        )

    return items_by_key


def validate_adjacent_pairing(
    items_by_stage: dict[
        str,
        dict[tuple[str, str], dict[str, Any]],
    ],
) -> None:
    development = items_by_stage["Development"]
    test = items_by_stage["Test"]
    production = items_by_stage["Production"]

    for key in sorted(EXPECTED_ITEMS):
        dev_item = development[key]
        test_item = test[key]
        prod_item = production[key]

        dev_id = dev_item.get("itemId")
        test_id = test_item.get("itemId")
        prod_id = prod_item.get("itemId")

        require(
            isinstance(dev_id, str),
            f"Development item {key} has no itemId.",
        )

        require(
            isinstance(test_id, str),
            f"Test item {key} has no itemId.",
        )

        require(
            isinstance(prod_id, str),
            f"Production item {key} has no itemId.",
        )

        require(
            dev_item.get("targetItemId") == test_id,
            (
                f"Development item {key} does not target "
                "the corresponding Test item."
            ),
        )

        require(
            test_item.get("sourceItemId") == dev_id,
            (
                f"Test item {key} does not identify the "
                "corresponding Development item as its source."
            ),
        )

        require(
            test_item.get("targetItemId") == prod_id,
            (
                f"Test item {key} does not target the "
                "corresponding Production item."
            ),
        )

        require(
            prod_item.get("sourceItemId") == test_id,
            (
                f"Production item {key} does not identify "
                "the corresponding Test item as its source."
            ),
        )


def build_evidence(
    pipeline: dict[str, Any],
    stages: list[dict[str, Any]],
    items_by_stage: dict[str, list[dict[str, Any]]],
    tenant_id: str | None,
) -> dict[str, Any]:
    return {
        "generatedAtUtc": datetime.now(
            timezone.utc
        ).isoformat(),
        "authentication": {
            "credentialType": "AzureCliCredential",
            "requestedTenantId": tenant_id,
        },
        "validation": {
            "readOnly": True,
            "expectedStageWorkspaces": (
                EXPECTED_STAGE_WORKSPACES
            ),
            "expectedItems": [
                {
                    "itemType": item_type,
                    "itemDisplayName": display_name,
                }
                for item_type, display_name
                in sorted(EXPECTED_ITEMS)
            ],
            "adjacentStagePairingValidated": True,
        },
        "deploymentPipeline": pipeline,
        "stages": [
            {
                **stage,
                "items": items_by_stage[
                    str(stage["displayName"])
                ],
            }
            for stage in sorted(
                stages,
                key=lambda value: value.get("order", 0),
            )
        ],
    }


def main() -> int:
    arguments = parse_arguments()

    try:
        credential = (
            AzureCliCredential(
                tenant_id=arguments.tenant_id
            )
            if arguments.tenant_id
            else AzureCliCredential()
        )

        client = FabricClient(
            TokenProvider(credential)
        )

        print("Fabric Deployment Pipeline preflight")
        print("====================================")
        print(f"Pipeline: {arguments.pipeline_name}")
        print(
            "Authentication: Azure CLI authenticated identity"
        )
        print("Mode: read-only")
        print()

        pipelines = client.get_collection(
            f"{FABRIC_API_BASE}/deploymentPipelines"
        )

        pipeline = find_pipeline(
            pipelines,
            arguments.pipeline_name,
        )

        pipeline_id = pipeline.get("id")

        require(
            isinstance(pipeline_id, str)
            and bool(pipeline_id.strip()),
            "The selected Deployment Pipeline has no valid ID.",
        )

        print(
            f"Deployment Pipeline ID: {pipeline_id}"
        )

        stages = client.get_collection(
            f"{FABRIC_API_BASE}/deploymentPipelines/"
            f"{pipeline_id}/stages"
        )

        stages_by_name = validate_stages(stages)

        raw_items_by_stage: dict[
            str,
            list[dict[str, Any]],
        ] = {}

        indexed_items_by_stage: dict[
            str,
            dict[tuple[str, str], dict[str, Any]],
        ] = {}

        for stage_name in EXPECTED_STAGE_WORKSPACES:
            stage = stages_by_name[stage_name]
            stage_id = stage["id"]

            items = client.get_collection(
                f"{FABRIC_API_BASE}/deploymentPipelines/"
                f"{pipeline_id}/stages/{stage_id}/items"
            )

            raw_items_by_stage[stage_name] = items

            indexed_items_by_stage[stage_name] = (
                validate_stage_inventory(
                    stage_name,
                    items,
                )
            )

            print()
            print(
                f"{stage_name} -> "
                f"{stage['workspaceName']} "
                f"[stageId={stage_id}, "
                f"workspaceId={stage['workspaceId']}]"
            )

            for item in sorted(
                items,
                key=get_item_key,
            ):
                print(
                    f"  {item['itemType']}: "
                    f"{item['itemDisplayName']} "
                    f"[itemId={item.get('itemId')}]"
                )

        validate_adjacent_pairing(
            indexed_items_by_stage
        )

        evidence = build_evidence(
            pipeline,
            stages,
            raw_items_by_stage,
            arguments.tenant_id,
        )

        output_path = Path(arguments.output)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path.write_text(
            json.dumps(
                evidence,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        print()
        print("Validated adjacent-stage item pairing:")
        print("  Development -> Test")
        print("  Test -> Production")
        print()
        print("PREFLIGHT SUCCEEDED")
        print(
            f"Evidence written to: {output_path}"
        )

        return 0

    except (
        CredentialUnavailableError,
        ClientAuthenticationError,
    ) as error:
        print(
            "PREFLIGHT FAILED: Azure CLI authentication "
            "failed. Ensure Azure CLI is authenticated "
            "as the intended Fabric principal. "
            f"Details: {error}",
            file=sys.stderr,
        )

        return 1

    except requests.RequestException as error:
        print(
            "PREFLIGHT FAILED: Fabric HTTP request "
            f"failed: {error}",
            file=sys.stderr,
        )

        return 1

    except PreflightFailure as error:
        print(
            f"PREFLIGHT FAILED: {error}",
            file=sys.stderr,
        )

        return 1


if __name__ == "__main__":
    raise SystemExit(main())
