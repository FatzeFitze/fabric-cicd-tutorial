#!/usr/bin/env python3
"""Deploy the protected DEV repository state directly to Fabric TEST.

This script is the repository-owned wrapper around Microsoft's fabric-cicd
deployment library. It deliberately owns only the release controls that belong
to this solution:

- validate trusted Git provenance;
- restrict the deployable solution to four known Fabric items;
- resolve and guard the exact TEST workspace;
- invoke fabric-cicd for Fabric-specific deployment semantics;
- verify that the expected TEST item inventory still exists after deployment;
- write non-secret JSON evidence.

It deliberately does NOT:
- implement Fabric logical-ID rebinding;
- call low-level updateDefinition APIs directly;
- delete orphaned Fabric items;
- execute TEST runtime workloads.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

import requests
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import AzureCliCredential, CredentialUnavailableError
from fabric_cicd import FabricWorkspace, publish_all_items

from fabric_nonprod_release import (
    FABRIC_API_BASE,
    FABRIC_SCOPE,
    ReleaseFailure,
    now_utc,
    request_json,
    response_json,
    single,
    validate_git_state,
)
from tutorial_config import (
    DEFAULT_CONFIG_PATH,
    TutorialConfigError,
    load_tutorial_resources,
)


# The value must match the TEST Variable Library value-set name exactly.
TEST_VALUE_SET_NAME = "test_environment_name"
EXECUTION_CONFIRMATION = "DEPLOY_DEV_TO_TEST_WITH_FABRIC_CICD"

MANAGED_ITEMS = (
    {
        "type": "Lakehouse",
        "displayName": "lh_cicd_lab",
        "path": Path("01_data_engineering/lh_cicd_lab.Lakehouse"),
    },
    {
        "type": "Notebook",
        "displayName": "nb_01_seed_and_transform_cicd_lab",
        "path": Path(
            "01_data_engineering/"
            "nb_01_seed_and_transform_cicd_lab.Notebook"
        ),
    },
    {
        "type": "DataPipeline",
        "displayName": "pl_01_run_cicd_lab_transform",
        "path": Path(
            "02_orchestration/"
            "pl_01_run_cicd_lab_transform.DataPipeline"
        ),
    },
    {
        "type": "VariableLibrary",
        "displayName": "vl_cicd_lab_config",
        "path": Path(
            "99_admin/"
            "vl_cicd_lab_config.VariableLibrary"
        ),
    },
)

ITEM_TYPES_IN_SCOPE = [
    "Lakehouse",
    "Notebook",
    "DataPipeline",
    "VariableLibrary",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReleaseFailure(message)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate or deploy the protected dev repository "
            "state directly to Fabric TEST with fabric-cicd."
        )
    )
    parser.add_argument("--tenant-id", required=True)
    parser.add_argument("--expected-branch", default="dev")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirmation")
    parser.add_argument(
        "--output",
        default="artifacts/fabric-test-deployment.json",
    )
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to participant-specific tutorial resource configuration.",
    )
    return parser.parse_args()


def read_platform(item: dict[str, Any]) -> dict[str, Any]:
    platform_path = Path(item["path"]) / ".platform"
    require(
        platform_path.is_file(),
        f"Missing repository .platform: {platform_path}",
    )

    try:
        payload = json.loads(
            platform_path.read_text(encoding="utf-8-sig")
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReleaseFailure(
            f"Invalid repository .platform: {platform_path}"
        ) from exc

    require(
        isinstance(payload, dict),
        f"Unexpected .platform root: {platform_path}",
    )

    metadata = payload.get("metadata")
    config = payload.get("config")

    require(
        isinstance(metadata, dict),
        f"Missing metadata in {platform_path}",
    )
    require(
        isinstance(config, dict),
        f"Missing config in {platform_path}",
    )
    require(
        metadata.get("type") == item["type"],
        (
            f"{platform_path} type is "
            f"'{metadata.get('type')}', expected "
            f"'{item['type']}'."
        ),
    )
    require(
        metadata.get("displayName")
        == item["displayName"],
        (
            f"{platform_path} displayName is "
            f"'{metadata.get('displayName')}', expected "
            f"'{item['displayName']}'."
        ),
    )

    logical_id = config.get("logicalId")
    require(
        isinstance(logical_id, str)
        and bool(logical_id.strip())
        and logical_id
        != "00000000-0000-0000-0000-000000000000",
        (
            f"{platform_path} must contain a real "
            "repository logicalId."
        ),
    )

    return payload


def validate_repository_inventory() -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []

    for item in MANAGED_ITEMS:
        item_path = Path(item["path"])
        require(
            item_path.is_dir(),
            f"Missing managed item directory: {item_path}",
        )

        platform = read_platform(item)
        logical_id = platform["config"]["logicalId"]

        evidence.append(
            {
                "type": item["type"],
                "displayName": item["displayName"],
                "repositoryPath": item_path.as_posix(),
                "logicalId": logical_id,
            }
        )

    return evidence


def get_test_workspace(
    session: requests.Session,
    headers: dict[str, str],
    workspace_name: str,
) -> dict[str, Any]:
    response = request_json(
        session,
        "GET",
        f"{FABRIC_API_BASE}/workspaces",
        headers,
    )
    payload = response_json(
        response,
        "Fabric workspace list",
    )

    return single(
        payload.get("value"),
        lambda value: (
            value.get("displayName")
            == workspace_name
        ),
        (
            "visible TEST workspace named "
            f"'{workspace_name}'"
        ),
    )


def get_workspace_items(
    session: requests.Session,
    headers: dict[str, str],
    workspace_id: str,
) -> list[dict[str, Any]]:
    response = request_json(
        session,
        "GET",
        (
            f"{FABRIC_API_BASE}/workspaces/"
            f"{workspace_id}/items"
        ),
        headers,
    )
    payload = response_json(
        response,
        "Fabric TEST item list",
    )
    values = payload.get("value")
    require(
        isinstance(values, list),
        "Fabric TEST item list is not a list.",
    )

    return [
        value
        for value in values
        if isinstance(value, dict)
    ]


def expected_item_inventory(
    live_items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []

    for expected in MANAGED_ITEMS:
        item = single(
            live_items,
            lambda value, expected=expected: (
                value.get("type") == expected["type"]
                and value.get("displayName")
                == expected["displayName"]
            ),
            (
                f"TEST {expected['type']} named "
                f"'{expected['displayName']}'"
            ),
        )

        item_id = item.get("id")
        require(
            isinstance(item_id, str)
            and bool(item_id),
            (
                f"TEST item '{expected['displayName']}' "
                "has no item ID."
            ),
        )

        evidence.append(
            {
                "type": expected["type"],
                "displayName": expected["displayName"],
                "itemId": item_id,
            }
        )

    return evidence


def inventory_by_key(
    inventory: list[dict[str, Any]],
) -> dict[tuple[str, str], str]:
    return {
        (item["type"], item["displayName"]): item["itemId"]
        for item in inventory
    }


def stage_deployment_source(
    root: Path,
) -> Path:
    deployment_root = root / "fabric-source"
    deployment_root.mkdir(parents=True, exist_ok=True)

    for item in MANAGED_ITEMS:
        source = Path(item["path"])
        target = deployment_root / source

        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        shutil.copytree(
            source,
            target,
            dirs_exist_ok=False,
        )

    return deployment_root


def installed_fabric_cicd_version() -> str:
    try:
        return version("fabric-cicd")
    except PackageNotFoundError as exc:
        raise ReleaseFailure(
            "fabric-cicd is not installed."
        ) from exc


def main() -> int:
    arguments = parse_arguments()

    try:
        resources = load_tutorial_resources(
            arguments.config
        )

        if arguments.execute:
            require(
                arguments.confirmation
                == EXECUTION_CONFIRMATION,
                (
                    "Execution cancelled: confirmation "
                    f"must be '{EXECUTION_CONFIRMATION}'."
                ),
            )

        code_state = validate_git_state(
            arguments.expected_branch,
            resources.repository_name,
        )
        repository_inventory = (
            validate_repository_inventory()
        )
        package_version = (
            installed_fabric_cicd_version()
        )

        credential = AzureCliCredential(
            tenant_id=arguments.tenant_id
        )
        token = credential.get_token(
            FABRIC_SCOPE
        ).token

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

        with requests.Session() as session:
            workspace = get_test_workspace(
                session,
                headers,
                resources.test_workspace_name,
            )
            workspace_id = workspace.get("id")

            require(
                isinstance(workspace_id, str)
                and bool(workspace_id),
                "TEST workspace ID is missing.",
            )

            before_items = get_workspace_items(
                session,
                headers,
                workspace_id,
            )
            before_inventory = (
                expected_item_inventory(
                    before_items
                )
            )

            print("Fabric TEST deployment")
            print("======================")
            print(
                "Source branch: "
                f"{code_state['branch']}"
            )
            print(
                "Source commit: "
                f"{code_state['headCommit']}"
            )
            print(
                "Checkout mode: "
                f"{code_state['checkoutMode']}"
            )
            print(
                "Deployment engine: "
                f"fabric-cicd {package_version}"
            )
            print(
                "Target workspace: "
                f"{resources.test_workspace_name}"
            )
            print(
                "Managed items: "
                f"{len(MANAGED_ITEMS)}"
            )
            print(
                "Execution mode: "
                f"{'EXECUTE' if arguments.execute else 'PLAN ONLY'}"
            )
            print()

            publish_result = None

            if arguments.execute:
                with tempfile.TemporaryDirectory(
                    prefix="fabric-cicd-s3-u2-"
                ) as temporary_directory:
                    deployment_root = (
                        stage_deployment_source(
                            Path(temporary_directory)
                        )
                    )

                    target_workspace = (
                        FabricWorkspace(
                            workspace_id=workspace_id,
                            repository_directory=str(
                                deployment_root
                            ),
                            environment=TEST_VALUE_SET_NAME,
                            item_type_in_scope=(
                                ITEM_TYPES_IN_SCOPE
                            ),
                            token_credential=credential,
                        )
                    )

                    publish_result = publish_all_items(
                        target_workspace
                    )

            after_items = get_workspace_items(
                session,
                headers,
                workspace_id,
            )
            after_inventory = (
                expected_item_inventory(
                    after_items
                )
            )

            before_by_key = inventory_by_key(
                before_inventory
            )
            after_by_key = inventory_by_key(
                after_inventory
            )

            item_ids_stable = all(
                before_by_key[key]
                == after_by_key[key]
                for key in before_by_key
            )

            if arguments.execute:
                require(
                    item_ids_stable,
                    (
                        "At least one existing TEST item "
                        "was replaced with a different "
                        "physical item ID."
                    ),
                )

            evidence = {
                "evidenceSchemaVersion": 1,
                "evidenceType": "FabricTestDeployment",
                "generatedAtUtc": (
                    now_utc().isoformat()
                ),
                "codeState": code_state,
                "resourceConfiguration": (
                    resources.evidence()
                ),
                "deploymentEngine": {
                    "name": "fabric-cicd",
                    "version": package_version,
                    "bulkPublishEnabled": False,
                    "orphanDeletionEnabled": False,
                },
                "execution": {
                    "executeRequested": (
                        arguments.execute
                    ),
                    "confirmationRequired": (
                        arguments.execute
                    ),
                },
                "repository": {
                    "managedItems": (
                        repository_inventory
                    ),
                },
                "target": {
                    "workspaceName": (
                        resources.test_workspace_name
                    ),
                    "workspaceId": workspace_id,
                    "fabricCicdEnvironment": (
                        TEST_VALUE_SET_NAME
                    ),
                },
                "deploymentState": {
                    "itemsBefore": (
                        before_inventory
                    ),
                    "itemsAfter": (
                        after_inventory
                    ),
                    "existingItemIdsStable": (
                        item_ids_stable
                    ),
                },
                "publishResultReturned": (
                    publish_result is not None
                ),
            }

            output_path = Path(
                arguments.output
            )
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

            print(
                "Existing TEST item IDs stable: "
                f"{item_ids_stable}"
            )
            print(
                "Writes performed: "
                f"{'yes' if arguments.execute else 'no'}"
            )
            print()

            if arguments.execute:
                print(
                    "FABRIC-CICD TEST DEPLOYMENT SUCCEEDED"
                )
            else:
                print(
                    "FABRIC-CICD TEST DEPLOYMENT PLAN SUCCEEDED"
                )

            print(
                "Evidence written to: "
                f"{output_path}"
            )

        return 0

    except (
        CredentialUnavailableError,
        ClientAuthenticationError,
    ) as exc:
        print(
            "TEST DEPLOYMENT FAILED: "
            f"authentication failed: {exc}",
            file=sys.stderr,
        )
        return 1

    except (
        requests.RequestException,
        ReleaseFailure,
        TutorialConfigError,
        ValueError,
    ) as exc:
        print(
            f"TEST DEPLOYMENT FAILED: {exc}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
