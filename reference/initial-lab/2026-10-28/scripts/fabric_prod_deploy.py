#!/usr/bin/env python3
"""Deploy an approved, TEST-validated repository state to Fabric PROD.

The script deliberately performs definition deployment only. It does not execute
the Production Data Pipeline or Notebook; Production runtime validation is the
next tutorial boundary.
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

PROD_VALUE_SET_NAME = "prod_environment_name"
EXECUTION_CONFIRMATION = "DEPLOY_MAIN_TO_PROD_WITH_FABRIC_CICD"

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
            "Deploy protected main directly to Fabric PROD with fabric-cicd "
            "after validating the approved TEST candidate contract."
        )
    )
    parser.add_argument("--tenant-id", required=True)
    parser.add_argument("--candidate-evidence", required=True)
    parser.add_argument("--release-plan", required=True)
    parser.add_argument("--expected-branch", default="main")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirmation")
    parser.add_argument(
        "--output",
        default="artifacts/fabric-prod-deployment.json",
    )
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to participant-specific tutorial resource configuration.",
    )
    return parser.parse_args()


def load_json(path: Path, description: str) -> dict[str, Any]:
    require(path.is_file(), f"{description} does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReleaseFailure(f"{description} is invalid JSON: {path}") from exc
    require(isinstance(payload, dict), f"{description} root must be an object.")
    return payload


def read_platform(item: dict[str, Any]) -> dict[str, Any]:
    platform_path = Path(item["path"]) / ".platform"
    require(platform_path.is_file(), f"Missing repository .platform: {platform_path}")
    try:
        payload = json.loads(platform_path.read_text(encoding="utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReleaseFailure(f"Invalid repository .platform: {platform_path}") from exc

    require(isinstance(payload, dict), f"Unexpected .platform root: {platform_path}")
    metadata = payload.get("metadata")
    config = payload.get("config")
    require(isinstance(metadata, dict), f"Missing metadata in {platform_path}")
    require(isinstance(config, dict), f"Missing config in {platform_path}")
    require(
        metadata.get("type") == item["type"],
        f"{platform_path} type is {metadata.get('type')!r}, expected {item['type']!r}.",
    )
    require(
        metadata.get("displayName") == item["displayName"],
        (
            f"{platform_path} displayName is {metadata.get('displayName')!r}, "
            f"expected {item['displayName']!r}."
        ),
    )
    logical_id = config.get("logicalId")
    require(
        isinstance(logical_id, str)
        and bool(logical_id.strip())
        and logical_id != "00000000-0000-0000-0000-000000000000",
        f"{platform_path} must contain a real repository logicalId.",
    )
    return payload


def validate_repository_inventory() -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for item in MANAGED_ITEMS:
        item_path = Path(item["path"])
        require(item_path.is_dir(), f"Missing managed item directory: {item_path}")
        platform = read_platform(item)
        evidence.append(
            {
                "type": item["type"],
                "displayName": item["displayName"],
                "repositoryPath": item_path.as_posix(),
                "logicalId": platform["config"]["logicalId"],
            }
        )
    return evidence


def get_prod_workspace(
    session: requests.Session,
    headers: dict[str, str],
    workspace_name: str,
) -> dict[str, Any]:
    response = request_json(session, "GET", f"{FABRIC_API_BASE}/workspaces", headers)
    payload = response_json(response, "Fabric workspace list")
    return single(
        payload.get("value"),
        lambda value: value.get("displayName") == workspace_name,
        f"visible PROD workspace named '{workspace_name}'",
    )


def get_workspace_items(
    session: requests.Session,
    headers: dict[str, str],
    workspace_id: str,
) -> list[dict[str, Any]]:
    response = request_json(
        session,
        "GET",
        f"{FABRIC_API_BASE}/workspaces/{workspace_id}/items",
        headers,
    )
    payload = response_json(response, "Fabric PROD item list")
    values = payload.get("value")
    require(isinstance(values, list), "Fabric PROD item list is not a list.")
    return [value for value in values if isinstance(value, dict)]


def expected_item_inventory(live_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for expected in MANAGED_ITEMS:
        item = single(
            live_items,
            lambda value, expected=expected: (
                value.get("type") == expected["type"]
                and value.get("displayName") == expected["displayName"]
            ),
            f"PROD {expected['type']} named '{expected['displayName']}'",
        )
        item_id = item.get("id")
        require(
            isinstance(item_id, str) and bool(item_id),
            f"PROD item '{expected['displayName']}' has no item ID.",
        )
        evidence.append(
            {
                "type": expected["type"],
                "displayName": expected["displayName"],
                "itemId": item_id,
            }
        )
    return evidence


def inventory_by_key(inventory: list[dict[str, Any]]) -> dict[tuple[str, str], str]:
    return {
        (item["type"], item["displayName"]): item["itemId"]
        for item in inventory
    }


def stage_deployment_source(root: Path) -> Path:
    deployment_root = root / "fabric-source"
    deployment_root.mkdir(parents=True, exist_ok=True)
    for item in MANAGED_ITEMS:
        source = Path(item["path"])
        target = deployment_root / source
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target, dirs_exist_ok=False)
    return deployment_root


def installed_fabric_cicd_version() -> str:
    try:
        return version("fabric-cicd")
    except PackageNotFoundError as exc:
        raise ReleaseFailure("fabric-cicd is not installed.") from exc


def validate_release_contract(
    candidate: dict[str, Any],
    release_plan: dict[str, Any],
    code_state: dict[str, Any],
    expected_configuration: dict[str, Any],
    prod_workspace_name: str,
) -> str:
    require(
        candidate.get("evidenceType") == "FabricReleaseCandidate",
        "Unexpected release-candidate evidence type.",
    )
    require(
        candidate.get("status") == "TEST_VALIDATED_PENDING_CODE_APPROVAL",
        "Release candidate is not TEST-validated and pending code approval.",
    )
    require(
        release_plan.get("evidenceType") == "FabricProdReleasePlan",
        "Unexpected Production release-plan evidence type.",
    )
    require(
        release_plan.get("status") == "PROD_APPROVAL_PENDING",
        "Production release plan is not in approval-pending state.",
    )
    require(
        candidate.get("resourceConfiguration") == expected_configuration,
        "Candidate resource configuration differs from current configuration.",
    )
    require(
        release_plan.get("resourceConfiguration") == expected_configuration,
        "Production release plan uses different resource configuration.",
    )

    candidate_id = candidate.get("releaseCandidateId")
    require(isinstance(candidate_id, str) and bool(candidate_id), "Candidate ID is missing.")

    planned_candidate = release_plan.get("releaseCandidate")
    require(isinstance(planned_candidate, dict), "Release plan has no releaseCandidate section.")
    require(
        planned_candidate.get("releaseCandidateId") == candidate_id,
        "Release plan refers to a different release candidate.",
    )

    tested_code = candidate.get("testedCodeState")
    require(isinstance(tested_code, dict), "Candidate has no testedCodeState section.")
    tested_tree = tested_code.get("repositoryTreeHash")
    require(
        isinstance(tested_tree, str)
        and tested_tree == code_state.get("repositoryTreeHash"),
        "Current main repository tree differs from the TEST-validated candidate.",
    )

    authority = release_plan.get("productionCodeAuthority")
    require(isinstance(authority, dict), "Release plan has no productionCodeAuthority section.")
    require(authority.get("branch") == "main", "Release plan is not bound to main.")
    require(
        authority.get("repositoryTreeHash") == code_state.get("repositoryTreeHash"),
        "Release plan repository tree differs from current main.",
    )
    require(
        authority.get("matchesTestedRepositoryTree") is True,
        "Release plan did not prove TEST/main tree equality.",
    )

    target = release_plan.get("target")
    require(isinstance(target, dict), "Release plan has no target section.")
    require(
        target.get("workspaceName") == prod_workspace_name,
        "Release plan targets a different Production workspace.",
    )
    require(
        target.get("deployment") == "NotPerformed",
        "Release plan already claims a Production deployment.",
    )

    test_runtime = candidate.get("testRuntime")
    require(isinstance(test_runtime, dict), "Candidate has no testRuntime section.")
    require(test_runtime.get("validationStatus") == "SUCCEEDED", "TEST validation failed.")
    require(test_runtime.get("environmentName") == "TEST", "Candidate runtime is not TEST.")

    return candidate_id


def main() -> int:
    arguments = parse_arguments()

    try:
        resources = load_tutorial_resources(arguments.config)
        if arguments.execute:
            require(
                arguments.confirmation == EXECUTION_CONFIRMATION,
                (
                    "Execution cancelled: confirmation must be "
                    f"'{EXECUTION_CONFIRMATION}'."
                ),
            )

        code_state = validate_git_state(
            arguments.expected_branch,
            resources.repository_name,
        )
        repository_inventory = validate_repository_inventory()
        package_version = installed_fabric_cicd_version()
        candidate = load_json(Path(arguments.candidate_evidence), "release-candidate evidence")
        release_plan = load_json(Path(arguments.release_plan), "Production release plan")
        expected_configuration = resources.evidence()
        candidate_id = validate_release_contract(
            candidate,
            release_plan,
            code_state,
            expected_configuration,
            resources.prod_workspace_name,
        )

        credential = AzureCliCredential(tenant_id=arguments.tenant_id)
        token = credential.get_token(FABRIC_SCOPE).token
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

        with requests.Session() as session:
            workspace = get_prod_workspace(
                session,
                headers,
                resources.prod_workspace_name,
            )
            workspace_id = workspace.get("id")
            require(
                isinstance(workspace_id, str) and bool(workspace_id),
                "PROD workspace ID is missing.",
            )

            before_items = get_workspace_items(session, headers, workspace_id)
            before_inventory = expected_item_inventory(before_items)

            print("Fabric PROD deployment")
            print("======================")
            print(f"Source branch:       {code_state['branch']}")
            print(f"Source commit:       {code_state['headCommit']}")
            print(f"Repository tree:     {code_state['repositoryTreeHash']}")
            print(f"Release candidate:   {candidate_id}")
            print(f"Deployment engine:   fabric-cicd {package_version}")
            print(f"Target workspace:    {resources.prod_workspace_name}")
            print(f"Managed items:       {len(MANAGED_ITEMS)}")
            print(f"Execution mode:      {'EXECUTE' if arguments.execute else 'PLAN ONLY'}")
            print()

            publish_result = None
            if arguments.execute:
                with tempfile.TemporaryDirectory(
                    prefix="fabric-cicd-s3-u5-prod-"
                ) as temporary_directory:
                    deployment_root = stage_deployment_source(Path(temporary_directory))
                    target_workspace = FabricWorkspace(
                        workspace_id=workspace_id,
                        repository_directory=str(deployment_root),
                        environment=PROD_VALUE_SET_NAME,
                        item_type_in_scope=ITEM_TYPES_IN_SCOPE,
                        token_credential=credential,
                    )
                    publish_result = publish_all_items(target_workspace)

            after_items = get_workspace_items(session, headers, workspace_id)
            after_inventory = expected_item_inventory(after_items)

            before_by_key = inventory_by_key(before_inventory)
            after_by_key = inventory_by_key(after_inventory)
            item_ids_stable = all(
                before_by_key[key] == after_by_key[key]
                for key in before_by_key
            )

            if arguments.execute:
                require(
                    item_ids_stable,
                    (
                        "At least one existing PROD item was replaced with a "
                        "different physical item ID."
                    ),
                )

            evidence = {
                "evidenceSchemaVersion": 1,
                "evidenceType": "FabricProdDeployment",
                "generatedAtUtc": now_utc().isoformat(),
                "status": (
                    "PROD_DEPLOYED_RUNTIME_PENDING"
                    if arguments.execute
                    else "PROD_DEPLOYMENT_PLAN_VALID"
                ),
                "codeState": code_state,
                "resourceConfiguration": expected_configuration,
                "releaseCandidate": {
                    "releaseCandidateId": candidate_id,
                    "testedCommit": candidate["testedCodeState"].get("headCommit"),
                    "testedRepositoryTreeHash": candidate["testedCodeState"].get(
                        "repositoryTreeHash"
                    ),
                    "selectedCandidateRun": release_plan.get("selectedCandidateRun"),
                },
                "deploymentEngine": {
                    "name": "fabric-cicd",
                    "version": package_version,
                    "bulkPublishEnabled": False,
                    "orphanDeletionEnabled": False,
                },
                "execution": {
                    "executeRequested": arguments.execute,
                    "confirmationRequired": arguments.execute,
                },
                "repository": {
                    "managedItems": repository_inventory,
                },
                "target": {
                    "workspaceName": resources.prod_workspace_name,
                    "workspaceId": workspace_id,
                    "fabricCicdEnvironment": PROD_VALUE_SET_NAME,
                },
                "deploymentState": {
                    "itemsBefore": before_inventory,
                    "itemsAfter": after_inventory,
                    "existingItemIdsStable": item_ids_stable,
                },
                "runtimeState": {
                    "executed": False,
                    "validation": "DeferredToSection3Unit6",
                },
                "publishResultReturned": publish_result is not None,
            }

            output_path = Path(arguments.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                json.dumps(evidence, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

            print(f"Existing PROD item IDs stable: {item_ids_stable}")
            print(f"Writes performed:              {'yes' if arguments.execute else 'no'}")
            print("Runtime executed:              no")
            print()
            if arguments.execute:
                print("FABRIC-CICD PROD DEPLOYMENT SUCCEEDED")
            else:
                print("FABRIC-CICD PROD DEPLOYMENT PLAN SUCCEEDED")
            print(f"Evidence written to: {output_path}")

        return 0

    except (CredentialUnavailableError, ClientAuthenticationError) as exc:
        print(
            f"PROD DEPLOYMENT FAILED: authentication failed: {exc}",
            file=sys.stderr,
        )
        return 1
    except (
        requests.RequestException,
        ReleaseFailure,
        TutorialConfigError,
        ValueError,
    ) as exc:
        print(f"PROD DEPLOYMENT FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
