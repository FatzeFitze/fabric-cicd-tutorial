#!/usr/bin/env python3
"""Materialize repository-owned Fabric definitions into the existing DEV workspace.

The command bypasses Fabric updateFromGit. Azure DevOps Git is the release
code authority and Fabric Item Definition APIs materialize that code into DEV.

The command deliberately:
- updates existing items only;
- validates repository .platform logical IDs against existing DEV items;
- does not send .platform during updateDefinition;
- compares repository and Fabric definitions using normalized hashes;
- defaults to plan-only execution;
- can rewrite unchanged items only for an explicit compatibility probe.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import AzureCliCredential, CredentialUnavailableError

from fabric_nonprod_release import (
    FABRIC_API_BASE,
    FABRIC_SCOPE,
    ReleaseFailure,
    now_utc,
    poll_lro,
    request_json,
    response_json,
    retry_after,
    single,
    validate_git_state,
)
from tutorial_config import (
    DEFAULT_CONFIG_PATH,
    TutorialConfigError,
    load_tutorial_resources,
)


EXECUTION_CONFIRMATION = "MATERIALIZE_DEV_DEFINITIONS"


@dataclass(frozen=True)
class ManagedItem:
    item_type: str
    display_name: str
    directory: Path


MANAGED_ITEMS = (
    ManagedItem(
        "Lakehouse",
        "lh_cicd_lab",
        Path("01_data_engineering/lh_cicd_lab.Lakehouse"),
    ),
    ManagedItem(
        "VariableLibrary",
        "vl_cicd_lab_config",
        Path("99_admin/vl_cicd_lab_config.VariableLibrary"),
    ),
    ManagedItem(
        "Notebook",
        "nb_01_seed_and_transform_cicd_lab",
        Path(
            "01_data_engineering/"
            "nb_01_seed_and_transform_cicd_lab.Notebook"
        ),
    ),
    ManagedItem(
        "DataPipeline",
        "pl_01_run_cicd_lab_transform",
        Path(
            "02_orchestration/"
            "pl_01_run_cicd_lab_transform.DataPipeline"
        ),
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Materialize repository Fabric definitions into DEV."
    )

    parser.add_argument(
        "--tenant-id",
        required=True,
    )

    parser.add_argument(
        "--expected-branch",
        default="dev",
    )

    parser.add_argument(
        "--execute",
        action="store_true",
    )

    parser.add_argument(
        "--rewrite-all",
        action="store_true",
        help=(
            "Rewrite already-matching definitions. "
            "Use only for the controlled Unit 2 compatibility probe."
        ),
    )

    parser.add_argument(
        "--confirmation",
    )

    parser.add_argument(
        "--output",
        default="artifacts/fabric-dev-materialization.json",
    )

    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help=(
            "Path to participant-specific tutorial "
            "resource configuration."
        ),
    )

    return parser.parse_args()


def require(
    condition: bool,
    message: str,
) -> None:
    if not condition:
        raise ReleaseFailure(message)


def read_json(
    path: Path,
    description: str,
) -> dict[str, Any]:
    require(
        path.is_file(),
        f"{description} does not exist: {path}",
    )

    try:
        value = json.loads(
            path.read_text(
                encoding="utf-8-sig"
            )
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as exc:
        raise ReleaseFailure(
            f"{description} is invalid JSON: {path}"
        ) from exc

    require(
        isinstance(value, dict),
        f"{description} root must be an object.",
    )

    return value


def repository_platform(
    item: ManagedItem,
) -> dict[str, Any]:
    platform = read_json(
        item.directory / ".platform",
        f"{item.display_name} .platform",
    )

    metadata = platform.get("metadata")
    config = platform.get("config")

    require(
        isinstance(metadata, dict),
        f"{item.display_name} metadata is invalid.",
    )

    require(
        isinstance(config, dict),
        f"{item.display_name} config is invalid.",
    )

    require(
        metadata.get("type") == item.item_type,
        (
            f"{item.display_name} repository type "
            "does not match."
        ),
    )

    require(
        metadata.get("displayName")
        == item.display_name,
        (
            f"{item.display_name} repository "
            "display name does not match."
        ),
    )

    logical_id = config.get("logicalId")

    require(
        isinstance(logical_id, str)
        and bool(logical_id),
        (
            f"{item.display_name} repository "
            "logical ID is missing."
        ),
    )

    return platform


def repository_parts(
    item: ManagedItem,
) -> dict[str, bytes]:
    require(
        item.directory.is_dir(),
        (
            "Item directory does not exist: "
            f"{item.directory}"
        ),
    )

    parts: dict[str, bytes] = {}

    for path in sorted(
        item.directory.rglob("*")
    ):
        if not path.is_file():
            continue

        relative_path = (
            path.relative_to(
                item.directory
            ).as_posix()
        )

        if relative_path == ".platform":
            continue

        parts[relative_path] = (
            path.read_bytes()
        )

    require(
        bool(parts),
        (
            f"{item.display_name} has no "
            "repository definition parts."
        ),
    )

    return parts


def normalize_part(
    path: str,
    payload: bytes,
) -> bytes:
    if path.lower().endswith(".json"):
        try:
            value = json.loads(
                payload.decode("utf-8-sig")
            )
        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
        ) as exc:
            raise ReleaseFailure(
                (
                    f"Definition part '{path}' "
                    "is invalid JSON."
                )
            ) from exc

        canonical = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

        return canonical.encode("utf-8")

    try:
        text = payload.decode(
            "utf-8-sig"
        )
    except UnicodeDecodeError:
        return payload

    return (
        text
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .encode("utf-8")
    )


def part_hashes(
    parts: dict[str, bytes],
) -> dict[str, str]:
    return {
        path: hashlib.sha256(
            normalize_part(
                path,
                payload,
            )
        ).hexdigest()
        for path, payload
        in sorted(parts.items())
    }


def definition_hash(
    parts: dict[str, bytes],
) -> str:
    serialized = json.dumps(
        part_hashes(parts),
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(
        serialized
    ).hexdigest()


def decode_definition(
    payload: dict[str, Any],
    description: str,
) -> tuple[
    dict[str, bytes],
    dict[str, Any],
]:
    definition = payload.get(
        "definition"
    )

    require(
        isinstance(definition, dict),
        (
            f"{description} has no "
            "definition object."
        ),
    )

    raw_parts = definition.get(
        "parts"
    )

    require(
        isinstance(raw_parts, list),
        (
            f"{description} has no "
            "definition parts."
        ),
    )

    parts: dict[str, bytes] = {}
    platform: dict[str, Any] | None = None

    for part in raw_parts:
        require(
            isinstance(part, dict),
            (
                f"{description} contains "
                "an invalid part."
            ),
        )

        path = part.get("path")
        encoded = part.get("payload")
        payload_type = part.get(
            "payloadType"
        )

        require(
            isinstance(path, str)
            and bool(path),
            (
                f"{description} contains "
                "a part without path."
            ),
        )

        require(
            payload_type
            == "InlineBase64",
            (
                "Unsupported payload type "
                f"for '{path}'."
            ),
        )

        require(
            isinstance(encoded, str),
            (
                f"{description} part "
                f"'{path}' has no payload."
            ),
        )

        try:
            decoded = base64.b64decode(
                encoded,
                validate=True,
            )
        except ValueError as exc:
            raise ReleaseFailure(
                (
                    f"{description} part "
                    f"'{path}' has invalid Base64."
                )
            ) from exc

        if path == ".platform":
            try:
                candidate = json.loads(
                    decoded.decode(
                        "utf-8-sig"
                    )
                )
            except (
                UnicodeDecodeError,
                json.JSONDecodeError,
            ) as exc:
                raise ReleaseFailure(
                    (
                        f"{description} .platform "
                        "is invalid JSON."
                    )
                ) from exc

            require(
                isinstance(candidate, dict),
                (
                    f"{description} .platform "
                    "root is invalid."
                ),
            )

            platform = candidate

        else:
            parts[path] = decoded

    require(
        platform is not None,
        (
            f"{description} did not "
            "return .platform metadata."
        ),
    )

    return parts, platform


def validate_platform_identity(
    item: ManagedItem,
    repo_platform: dict[str, Any],
    live_platform: dict[str, Any],
) -> tuple[str, str, str]:
    repo_metadata = repo_platform.get(
        "metadata"
    )
    repo_config = repo_platform.get(
        "config"
    )

    live_metadata = live_platform.get(
        "metadata"
    )
    live_config = live_platform.get(
        "config"
    )

    require(
        isinstance(repo_metadata, dict)
        and isinstance(repo_config, dict),
        "Invalid repository .platform.",
    )

    require(
        isinstance(live_metadata, dict)
        and isinstance(live_config, dict),
        (
            f"{item.display_name} live "
            ".platform is invalid."
        ),
    )

    repo_logical_id = (
        repo_config.get("logicalId")
    )

    live_logical_id = (
        live_config.get("logicalId")
    )

    empty_logical_id = (
        "00000000-0000-0000-0000-000000000000"
    )

    #
    # The repository .platform file is the authoritative
    # source-control representation of the logical identity.
    #
    require(
        isinstance(repo_logical_id, str)
        and bool(repo_logical_id)
        and repo_logical_id
        != empty_logical_id,
        (
            f"{item.display_name} repository "
            "logical ID is missing or empty."
        ),
    )

    #
    # GetDefinition does not necessarily expose a usable
    # Git logical ID for every Fabric item type.
    #
    # If Fabric returns a real logical ID, it must agree
    # with the repository. A zero GUID is treated as
    # unavailable metadata rather than as a mismatch.
    #
    require(
        isinstance(live_logical_id, str)
        and bool(live_logical_id),
        (
            f"{item.display_name} live "
            ".platform logical ID is missing."
        ),
    )

    if live_logical_id == empty_logical_id:
        print(
            "NOTICE: "
            f"{item.display_name} GetDefinition "
            "returned an empty logical ID; "
            "repository logical identity cannot "
            "be independently verified through "
            "this API response."
        )

    else:
        require(
            live_logical_id
            == repo_logical_id,
            (
                f"{item.display_name} logical "
                "ID mismatch: repository "
                f"'{repo_logical_id}', Fabric "
                f"'{live_logical_id}'."
            ),
        )

    require(
        live_metadata.get("type")
        == item.item_type,
        (
            f"{item.display_name} live "
            ".platform has unexpected type."
        ),
    )

    require(
        live_metadata.get(
            "displayName"
        )
        == item.display_name,
        (
            f"{item.display_name} live "
            ".platform has unexpected "
            "display name."
        ),
    )

    logical_id_verification = (
        "UnavailableFromGetDefinition"
        if live_logical_id == empty_logical_id
        else "Matched"
    )

    return (
        str(repo_logical_id),
        str(live_logical_id),
        logical_id_verification,
    )


def definition_request(
    session: requests.Session,
    method: str,
    url: str,
    headers: dict[str, str],
    *,
    body: dict[str, Any] | None = None,
    expect_result: bool,
) -> tuple[
    dict[str, Any] | None,
    dict[str, Any] | None,
]:
    response = request_json(
        session,
        method,
        url,
        headers,
        body=body,
        allowed_statuses=(200, 202),
    )

    if response.status_code == 200:
        if expect_result:
            return (
                response_json(
                    response,
                    f"{method} {url}",
                ),
                None,
            )

        return None, None

    operation_id = response.headers.get(
        "x-ms-operation-id"
    )

    require(
        bool(operation_id),
        (
            "Fabric returned HTTP 202 "
            "without x-ms-operation-id."
        ),
    )

    _, state, result = poll_lro(
        session,
        str(operation_id),
        headers,
        retry_after(
            response.headers.get(
                "Retry-After"
            ),
            10,
        ),
        get_result=expect_result,
    )

    if expect_result:
        require(
            result is not None,
            (
                "Fabric definition LRO "
                "completed without a result."
            ),
        )

    return result, state


def get_definition(
    session: requests.Session,
    workspace_id: str,
    item_id: str,
    headers: dict[str, str],
    display_name: str,
) -> tuple[
    dict[str, bytes],
    dict[str, Any],
    dict[str, Any] | None,
]:
    url = (
        f"{FABRIC_API_BASE}/workspaces/"
        f"{workspace_id}/items/"
        f"{item_id}/getDefinition"
    )

    result, lro = definition_request(
        session,
        "POST",
        url,
        headers,
        expect_result=True,
    )

    require(
        result is not None,
        (
            f"{display_name} definition "
            "result is missing."
        ),
    )

    parts, platform = decode_definition(
        result,
        f"{display_name} definition",
    )

    return parts, platform, lro


def update_definition(
    session: requests.Session,
    workspace_id: str,
    item_id: str,
    headers: dict[str, str],
    parts: dict[str, bytes],
) -> dict[str, Any] | None:
    url = (
        f"{FABRIC_API_BASE}/workspaces/"
        f"{workspace_id}/items/"
        f"{item_id}/updateDefinition"
    )

    request_parts = [
        {
            "path": path,
            "payload": (
                base64.b64encode(
                    payload
                ).decode("ascii")
            ),
            "payloadType": (
                "InlineBase64"
            ),
        }
        for path, payload
        in sorted(parts.items())
    ]

    _, lro = definition_request(
        session,
        "POST",
        url,
        headers,
        body={
            "definition": {
                "parts": request_parts
            }
        },
        expect_result=False,
    )

    return lro


def main() -> int:
    arguments = parse_args()

    try:
        resources = load_tutorial_resources(
            arguments.config
        )

        if arguments.execute:
            require(
                arguments.confirmation
                == EXECUTION_CONFIRMATION,
                (
                    "Execution cancelled: "
                    "confirmation must be "
                    f"'{EXECUTION_CONFIRMATION}'."
                ),
            )

        code_state = validate_git_state(
            arguments.expected_branch,
            resources.repository_name,
        )

        credential = AzureCliCredential(
            tenant_id=arguments.tenant_id
        )

        token = credential.get_token(
            FABRIC_SCOPE
        ).token

        headers = {
            "Authorization": (
                f"Bearer {token}"
            ),
            "Accept": "application/json",
        }

        with requests.Session() as session:
            workspaces_response = (
                request_json(
                    session,
                    "GET",
                    (
                        f"{FABRIC_API_BASE}"
                        "/workspaces"
                    ),
                    headers,
                )
            )

            workspaces = response_json(
                workspaces_response,
                "Workspace list",
            )

            workspace = single(
                workspaces.get("value"),
                lambda value: (
                    value.get("displayName")
                    == resources.dev_workspace_name
                ),
                (
                    "visible DEV workspace "
                    "named "
                    f"'{resources.dev_workspace_name}'"
                ),
            )

            workspace_id = workspace.get(
                "id"
            )

            require(
                isinstance(
                    workspace_id,
                    str,
                )
                and bool(workspace_id),
                "DEV workspace ID is missing.",
            )

            items_response = request_json(
                session,
                "GET",
                (
                    f"{FABRIC_API_BASE}"
                    f"/workspaces/{workspace_id}"
                    "/items"
                ),
                headers,
            )

            item_payload = response_json(
                items_response,
                "DEV item list",
            )

            live_items = item_payload.get(
                "value"
            )

            require(
                isinstance(live_items, list),
                "DEV item list is invalid.",
            )

            evidence_items: list[
                dict[str, Any]
            ] = []

            for managed in MANAGED_ITEMS:
                fabric_item = single(
                    live_items,
                    (
                        lambda value,
                        expected=managed: (
                            value.get("type")
                            == expected.item_type
                            and value.get(
                                "displayName"
                            )
                            == expected.display_name
                        )
                    ),
                    (
                        f"DEV {managed.item_type} "
                        f"named "
                        f"'{managed.display_name}'"
                    ),
                )

                item_id = fabric_item.get(
                    "id"
                )

                require(
                    isinstance(item_id, str)
                    and bool(item_id),
                    (
                        f"{managed.display_name} "
                        "item ID is missing."
                    ),
                )

                repo_platform = (
                    repository_platform(
                        managed
                    )
                )

                repo_parts = (
                    repository_parts(
                        managed
                    )
                )

                (
                    live_before,
                    live_platform,
                    get_before_lro,
                ) = get_definition(
                    session,
                    str(workspace_id),
                    item_id,
                    headers,
                    managed.display_name,
                )

                (
                    logical_id,
                    live_logical_id_before,
                    logical_id_verification_before,
                ) = validate_platform_identity(
                    managed,
                    repo_platform,
                    live_platform,
                )

                repo_hash = (
                    definition_hash(
                        repo_parts
                    )
                )

                before_hash = (
                    definition_hash(
                        live_before
                    )
                )

                matching_before = (
                    repo_hash == before_hash
                    and set(repo_parts)
                    == set(live_before)
                )

                update_requested = bool(
                    arguments.execute
                    and (
                        arguments.rewrite_all
                        or not matching_before
                    )
                )

                update_lro = None

                if update_requested:
                    print(
                        "Updating "
                        f"{managed.item_type}: "
                        f"{managed.display_name}"
                    )

                    update_lro = (
                        update_definition(
                            session,
                            str(workspace_id),
                            item_id,
                            headers,
                            repo_parts,
                        )
                    )

                else:
                    action = (
                        "already matches"
                        if matching_before
                        else "plan only"
                    )

                    print(
                        "Skipping "
                        f"{managed.item_type}: "
                        f"{managed.display_name} "
                        f"({action})"
                    )

                (
                    live_after,
                    live_after_platform,
                    get_after_lro,
                ) = get_definition(
                    session,
                    str(workspace_id),
                    item_id,
                    headers,
                    managed.display_name,
                )

                (
                    _,
                    live_logical_id_after,
                    logical_id_verification_after,
                ) = validate_platform_identity(
                    managed,
                    repo_platform,
                    live_after_platform,
                )

                after_hash = (
                    definition_hash(
                        live_after
                    )
                )

                matching_after = (
                    repo_hash == after_hash
                    and set(repo_parts)
                    == set(live_after)
                )

                if arguments.execute:
                    require(
                        matching_after,
                        (
                            f"{managed.display_name} "
                            "does not match the "
                            "repository definition "
                            "after materialization."
                        ),
                    )

                evidence_items.append(
                    {
                        "itemType": (
                            managed.item_type
                        ),
                        "displayName": (
                            managed.display_name
                        ),
                        "itemId": item_id,
                        "repositoryLogicalId": (
                            logical_id
                        ),
                        "fabricDefinitionLogicalIdBefore": (
                            live_logical_id_before
                        ),
                        "fabricDefinitionLogicalIdAfter": (
                            live_logical_id_after
                        ),
                        "logicalIdVerificationBefore": (
                            logical_id_verification_before
                        ),
                        "logicalIdVerificationAfter": (
                            logical_id_verification_after
                        ),
                        "repositoryParts": (
                            sorted(repo_parts)
                        ),
                        "fabricPartsBefore": (
                            sorted(live_before)
                        ),
                        "fabricPartsAfter": (
                            sorted(live_after)
                        ),
                        "repositoryDefinitionSha256": (
                            repo_hash
                        ),
                        "fabricDefinitionBeforeSha256": (
                            before_hash
                        ),
                        "fabricDefinitionAfterSha256": (
                            after_hash
                        ),
                        "matchedRepositoryBefore": (
                            matching_before
                        ),
                        "updateRequested": (
                            update_requested
                        ),
                        "matchedRepositoryAfter": (
                            matching_after
                        ),
                        "getBeforeLro": (
                            get_before_lro
                        ),
                        "updateLro": (
                            update_lro
                        ),
                        "getAfterLro": (
                            get_after_lro
                        ),
                    }
                )

            all_match = all(
                value[
                    "matchedRepositoryAfter"
                ]
                for value
                in evidence_items
            )

            already_matching_count = sum(
                1
                for value in evidence_items
                if value["matchedRepositoryBefore"]
            )

            require_update_count = (
                len(evidence_items)
                - already_matching_count
            )

            writes_performed_count = sum(
                1
                for value in evidence_items
                if value["updateRequested"]
            )

            plan_summary = {
                "totalManaged": len(evidence_items),
                "alreadyMatchingBefore": (
                    already_matching_count
                ),
                "requireUpdateBefore": (
                    require_update_count
                ),
                "writesPerformed": (
                    writes_performed_count
                ),
                "allDefinitionsCurrentlyMatchRepository": (
                    all_match
                ),
            }

            evidence = {
                "generatedAtUtc": (
                    now_utc().isoformat()
                ),
                "tutorialUnit": (
                    "Section 3 / Unit 2"
                ),
                "execution": {
                    "executeRequested": (
                        arguments.execute
                    ),
                    "rewriteAllRequested": (
                        arguments.rewrite_all
                    ),
                    "platformMetadataUpdated": (
                        False
                    ),
                    "releaseInvariant": (
                        "repository definitions "
                        "== DEV definitions"
                    ),
                },
                "codeState": code_state,
                "resourceConfiguration": (
                    resources.evidence()
                ),
                "workspace": {
                    "id": workspace_id,
                    "name": (
                        resources.dev_workspace_name
                    ),
                },
                "items": evidence_items,
                "planSummary": plan_summary,
                "validation": {
                    "allManagedDefinitionsMatchRepository": (
                        all_match
                    ),
                    "managedItemCount": (
                        len(evidence_items)
                    ),
                },
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

            print()
            print(
                "Fabric DEV definition "
                "materialization"
            )
            print(
                "=============================="
                "======="
            )
            print(
                "Repository commit: "
                f"{code_state['headCommit']}"
            )
            print(
                "Execute requested: "
                f"{arguments.execute}"
            )
            print(
                "Rewrite all: "
                f"{arguments.rewrite_all}"
            )
            print(
                "Execution mode: "
                + (
                    "EXECUTE"
                    if arguments.execute
                    else "PLAN ONLY"
                )
            )
            print(
                "Already matching: "
                f"{already_matching_count}"
            )
            print(
                "Require update:   "
                f"{require_update_count}"
            )
            print(
                "Writes performed: "
                f"{writes_performed_count}"
            )
            print(
                "Total managed:    "
                f"{len(evidence_items)}"
            )
            print(
                "All definitions currently "
                f"match repository: {all_match}"
            )
            print(
                "Platform metadata updated: no"
            )
            print()

            if arguments.execute:
                print(
                    "DEV DEFINITION "
                    "MATERIALIZATION SUCCEEDED"
                )
            else:
                print(
                    "DEV DEFINITION "
                    "MATERIALIZATION PLAN "
                    "SUCCEEDED"
                )

            print(
                "Evidence written to: "
                f"{output_path}"
            )

        return 0

    except (
        CredentialUnavailableError,
        ClientAuthenticationError,
    ) as error:
        print(
            (
                "DEV DEFINITION "
                "MATERIALIZATION FAILED: "
                "authentication failed. "
                f"{error}"
            ),
            file=sys.stderr,
        )

        return 1

    except (
        requests.RequestException,
        ReleaseFailure,
        TutorialConfigError,
    ) as error:
        print(
            (
                "DEV DEFINITION "
                "MATERIALIZATION FAILED: "
                f"{error}"
            ),
            file=sys.stderr,
        )

        return 1


if __name__ == "__main__":
    raise SystemExit(main())
