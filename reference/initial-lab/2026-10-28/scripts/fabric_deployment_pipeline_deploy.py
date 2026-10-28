#!/usr/bin/env python3
"""Guarded, repository-owned Fabric DEV -> TEST item deployment."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import AzureCliCredential, CredentialUnavailableError

FABRIC_API_BASE = "https://api.fabric.microsoft.com/v1"
FABRIC_SCOPE = "https://api.fabric.microsoft.com/.default"
FABRIC_HOST = "api.fabric.microsoft.com"
PIPELINE_NAME = "dp_fabric_cicd_lab"
CONFIRMATION = "DEPLOY_DEV_TO_TEST"
MAX_PREFLIGHT_AGE_MINUTES = 15
MAX_GIT_SYNC_EVIDENCE_AGE_MINUTES = 30
POLL_TIMEOUT_MINUTES = 30

EXPECTED_WORKSPACES = {
    "Development": "ws_reference_lab_dev",
    "Test": "ws_reference_lab_test",
    "Production": "ws_reference_lab_prod",
}


class DeploymentFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise DeploymentFailure(message)


def uuid_text(value: Any, name: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{name} is missing.")
    try:
        return str(uuid.UUID(value))
    except ValueError as exc:
        raise DeploymentFailure(f"{name} is not a valid UUID: {value!r}.") from exc


def utc_timestamp(value: Any, name: str) -> datetime:
    require(isinstance(value, str) and bool(value.strip()), f"{name} is missing.")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise DeploymentFailure(f"{name} is not valid ISO-8601: {value!r}.") from exc
    require(parsed.tzinfo is not None, f"{name} must include a timezone.")
    return parsed.astimezone(timezone.utc)


def single(values: Any, predicate, description: str) -> dict[str, Any]:
    require(isinstance(values, list), f"{description} collection is not a list.")
    matches = [value for value in values if isinstance(value, dict) and predicate(value)]
    require(len(matches) == 1, f"Expected exactly one {description}; found {len(matches)}.")
    return matches[0]


def validate_url(url: str) -> None:
    parsed = urlparse(url)
    require(
        parsed.scheme == "https" and parsed.hostname == FABRIC_HOST,
        f"Refusing to send a Fabric bearer token to unexpected URL: {url}",
    )


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise DeploymentFailure(
            f"Git command failed: git {' '.join(args)}\n{result.stderr.strip()}"
        )
    return result.stdout.strip()


def validate_git_state(expected_branch: str) -> dict[str, Any]:
    branch = git("branch", "--show-current")
    head = git("rev-parse", "HEAD")
    remote_ref = f"origin/{expected_branch}"
    remote_head = git("rev-parse", remote_ref)
    dirty = git("status", "--porcelain")

    require(branch == expected_branch, f"Current branch is '{branch}', expected '{expected_branch}'.")
    require(not dirty, "Git working tree is not clean.")
    require(head == remote_head, f"Local HEAD does not match {remote_ref}. Fetch or pull first.")

    return {
        "branch": branch,
        "headCommit": head,
        "remoteRef": remote_ref,
        "remoteCommit": remote_head,
        "workingTreeClean": True,
        "devWorkspaceCommitVerified": False,
    }


def load_and_validate_preflight(
    path: Path,
    item_type: str,
    item_name: str,
) -> tuple[dict[str, Any], dict[str, Any], str]:
    require(path.is_file(), f"Preflight evidence does not exist: {path}")
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()

    try:
        preflight = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DeploymentFailure(f"Preflight evidence is invalid JSON: {path}") from exc

    require(isinstance(preflight, dict), "Preflight root must be a JSON object.")
    validation = preflight.get("validation")
    require(isinstance(validation, dict), "Preflight has no validation object.")
    require(validation.get("readOnly") is True, "Preflight is not marked read-only.")
    require(
        validation.get("adjacentStagePairingValidated") is True,
        "Preflight did not validate adjacent-stage pairing.",
    )

    generated = utc_timestamp(preflight.get("generatedAtUtc"), "generatedAtUtc")
    now = datetime.now(timezone.utc)
    age = now - generated
    require(generated <= now + timedelta(minutes=5), "Preflight timestamp is unexpectedly in the future.")
    require(
        age <= timedelta(minutes=MAX_PREFLIGHT_AGE_MINUTES),
        f"Preflight evidence is {age.total_seconds() / 60:.1f} minutes old; maximum is 15.",
    )

    pipeline = preflight.get("deploymentPipeline")
    require(isinstance(pipeline, dict), "Preflight has no deploymentPipeline object.")
    require(pipeline.get("displayName") == PIPELINE_NAME, "Unexpected Deployment Pipeline.")
    pipeline_id = uuid_text(pipeline.get("id"), "deploymentPipeline.id")

    stages = preflight.get("stages")
    stage_by_name: dict[str, dict[str, Any]] = {}

    for stage_name, expected_workspace in EXPECTED_WORKSPACES.items():
        stage = single(
            stages,
            lambda value, name=stage_name: value.get("displayName") == name,
            f"stage named '{stage_name}'",
        )
        require(
            stage.get("workspaceName") == expected_workspace,
            f"Stage '{stage_name}' is assigned to an unexpected workspace.",
        )
        uuid_text(stage.get("id"), f"{stage_name}.id")
        uuid_text(stage.get("workspaceId"), f"{stage_name}.workspaceId")
        stage_by_name[stage_name] = stage

    source_stage = stage_by_name["Development"]
    target_stage = stage_by_name["Test"]
    production_stage = stage_by_name["Production"]

    source_stage_id = uuid_text(source_stage.get("id"), "Development.id")
    target_stage_id = uuid_text(target_stage.get("id"), "Test.id")
    production_stage_id = uuid_text(production_stage.get("id"), "Production.id")

    require(target_stage_id != production_stage_id, "PRODUCTION DEPLOYMENT IS BLOCKED.")
    require(source_stage_id != target_stage_id, "Source and target stages are identical.")

    source_item = single(
        source_stage.get("items"),
        lambda value: value.get("itemType") == item_type
        and value.get("itemDisplayName") == item_name,
        f"Development {item_type} named '{item_name}'",
    )
    target_item = single(
        target_stage.get("items"),
        lambda value: value.get("itemType") == item_type
        and value.get("itemDisplayName") == item_name,
        f"Test {item_type} named '{item_name}'",
    )

    source_item_id = uuid_text(source_item.get("itemId"), "sourceItem.itemId")
    target_item_id = uuid_text(target_item.get("itemId"), "targetItem.itemId")
    require(
        uuid_text(source_item.get("targetItemId"), "sourceItem.targetItemId") == target_item_id,
        "Source item does not target the selected Test item.",
    )
    require(
        uuid_text(target_item.get("sourceItemId"), "targetItem.sourceItemId") == source_item_id,
        "Test item does not identify the selected source item.",
    )

    topology = {
        "pipeline": pipeline,
        "pipelineId": pipeline_id,
        "sourceStage": source_stage,
        "sourceStageId": source_stage_id,
        "targetStage": target_stage,
        "targetStageId": target_stage_id,
        "sourceItem": source_item,
        "sourceItemId": source_item_id,
        "targetItem": target_item,
        "targetItemId": target_item_id,
        "generatedAtUtc": generated.isoformat(),
        "ageMinutes": age.total_seconds() / 60,
    }
    return preflight, topology, digest



def load_and_validate_git_sync_evidence(
    path: Path,
    expected_commit: str,
    expected_workspace_id: str,
) -> tuple[dict[str, Any], str]:
    require(path.is_file(), f"Git-sync evidence does not exist: {path}")
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()

    try:
        evidence = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DeploymentFailure(f"Git-sync evidence is invalid JSON: {path}") from exc

    require(isinstance(evidence, dict), "Git-sync evidence root must be a JSON object.")
    generated = utc_timestamp(evidence.get("generatedAtUtc"), "gitSync.generatedAtUtc")
    now = datetime.now(timezone.utc)
    age = now - generated
    require(generated <= now + timedelta(minutes=5), "Git-sync evidence timestamp is in the future.")
    require(
        age <= timedelta(minutes=MAX_GIT_SYNC_EVIDENCE_AGE_MINUTES),
        (
            f"Git-sync evidence is {age.total_seconds() / 60:.1f} minutes old; "
            f"maximum is {MAX_GIT_SYNC_EVIDENCE_AGE_MINUTES}."
        ),
    )

    workspace = evidence.get("workspace")
    require(isinstance(workspace, dict), "Git-sync evidence has no workspace object.")
    require(workspace.get("name") == EXPECTED_WORKSPACES["Development"], "Unexpected DEV workspace name.")
    require(
        uuid_text(workspace.get("id"), "gitSync.workspace.id") == expected_workspace_id,
        "Git-sync evidence belongs to a different DEV workspace.",
    )

    code_state = evidence.get("codeState")
    require(isinstance(code_state, dict), "Git-sync evidence has no codeState object.")
    require(code_state.get("branch") == "dev", "Git-sync evidence does not identify branch 'dev'.")
    require(code_state.get("headCommit") == expected_commit, "Git-sync commit does not match local dev HEAD.")
    require(code_state.get("remoteCommit") == expected_commit, "Git-sync remote commit does not match local dev HEAD.")
    require(code_state.get("workingTreeClean") is True, "Git-sync evidence does not confirm a clean working tree.")

    status_after = evidence.get("statusAfter")
    require(isinstance(status_after, dict), "Git-sync evidence has no statusAfter object.")
    require(status_after.get("workspaceHead") == expected_commit, "DEV workspaceHead does not match the release commit.")
    require(status_after.get("remoteCommitHash") == expected_commit, "Fabric remoteCommitHash does not match the release commit.")
    require(status_after.get("changes") == [], "DEV workspace still has Git changes after synchronization.")
    require(evidence.get("synchronized") is True, "Git-sync evidence does not confirm synchronization.")

    return evidence, digest

def retry_after(value: str | None, default: int = 10) -> int:
    try:
        parsed = int(value) if value else 0
    except ValueError:
        parsed = 0
    return min(parsed, 300) if parsed > 0 else default


def raise_http(response: requests.Response) -> None:
    try:
        body = json.dumps(response.json(), ensure_ascii=False)
    except requests.JSONDecodeError:
        body = response.text.strip()
    request_id = response.headers.get("x-ms-request-id") or response.headers.get("ActivityId")
    suffix = f" Request ID: {request_id}." if request_id else ""
    raise DeploymentFailure(
        f"{response.request.method} {response.url} failed with HTTP "
        f"{response.status_code}: {body}.{suffix}"
    )


def get_json(
    session: requests.Session,
    url: str,
    headers: dict[str, str],
    attempts: int = 6,
) -> tuple[requests.Response, dict[str, Any]]:
    validate_url(url)

    for attempt in range(1, attempts + 1):
        response = session.get(url, headers=headers, timeout=60)
        retryable = response.status_code == 429 or response.status_code >= 500
        if retryable and attempt < attempts:
            delay = retry_after(response.headers.get("Retry-After"), min(2**attempt, 30))
            print(f"GET returned HTTP {response.status_code}; retrying in {delay}s...", file=sys.stderr)
            time.sleep(delay)
            continue
        if not response.ok:
            raise_http(response)
        try:
            payload = response.json()
        except requests.JSONDecodeError as exc:
            raise DeploymentFailure(f"GET {url} returned invalid JSON.") from exc
        require(isinstance(payload, dict), f"GET {url} returned unexpected JSON.")
        return response, payload

    raise AssertionError("GET retry loop exited unexpectedly.")


def poll_operation(
    session: requests.Session,
    operation_id: str,
    headers: dict[str, str],
    wait_seconds: int,
) -> tuple[str, dict[str, Any]]:
    operation_id = uuid_text(operation_id, "x-ms-operation-id")
    operation_url = f"{FABRIC_API_BASE}/operations/{operation_id}"
    deadline = datetime.now(timezone.utc) + timedelta(minutes=POLL_TIMEOUT_MINUTES)

    while True:
        require(datetime.now(timezone.utc) <= deadline, "Fabric operation polling timed out.")
        time.sleep(wait_seconds)
        response, state = get_json(session, operation_url, headers)
        status = state.get("status")
        percent = state.get("percentComplete", "?")
        print(f"Operation status: {status} ({percent}%)")

        if status == "Succeeded":
            return operation_url, state
        if status == "Failed":
            raise DeploymentFailure(
                "Fabric deployment failed: " + json.dumps(state.get("error"), ensure_ascii=False)
            )
        wait_seconds = retry_after(response.headers.get("Retry-After"), wait_seconds)


def validate_deployment_operation(
    operation: dict[str, Any],
    source_stage_id: str,
    target_stage_id: str,
    selected_source_item_id: str,
) -> None:
    require(operation.get("status") == "Succeeded", "Detailed deployment operation did not succeed.")
    require(operation.get("sourceStageId") == source_stage_id, "Unexpected source stage in deployment result.")
    require(operation.get("targetStageId") == target_stage_id, "Unexpected target stage in deployment result.")

    plan = operation.get("executionPlan")
    require(isinstance(plan, dict), "Deployment result has no execution plan.")
    steps = plan.get("steps")
    require(isinstance(steps, list), "Deployment execution plan has no steps.")

    deployed_source_ids = {
        source_target.get("sourceItemId")
        for step in steps
        if isinstance(step, dict)
        for source_target in [step.get("sourceAndTarget")]
        if isinstance(source_target, dict)
        and isinstance(source_target.get("sourceItemId"), str)
    }
    require(selected_source_item_id in deployed_source_ids, "Selected item is absent from the execution plan.")
    require(
        deployed_source_ids == {selected_source_item_id},
        f"Execution plan contains unexpected source items: {sorted(deployed_source_ids)}",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Guarded Fabric DEV -> TEST item deployment.")
    parser.add_argument("--preflight", default="artifacts/fabric-deployment-preflight.json")
    parser.add_argument("--git-sync-evidence", required=True)
    parser.add_argument("--tenant-id")
    parser.add_argument("--item-type", default="Notebook")
    parser.add_argument("--item-name", default="nb_01_seed_and_transform_cicd_lab")
    parser.add_argument("--expected-branch", default="dev")
    parser.add_argument("--note-prefix", default="tutorial unit 5 nonprod release")
    parser.add_argument("--output", default="artifacts/fabric-deployment-dev-to-test.json")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirmation")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        preflight_path = Path(args.preflight)
        _, topology, preflight_sha256 = load_and_validate_preflight(
            preflight_path, args.item_type, args.item_name
        )
        git_state = validate_git_state(args.expected_branch)
        git_sync_path = Path(args.git_sync_evidence)
        git_sync_evidence, git_sync_sha256 = load_and_validate_git_sync_evidence(
            git_sync_path,
            git_state["headCommit"],
            topology["sourceStage"]["workspaceId"],
        )
        git_state["devWorkspaceCommitVerified"] = True

        note = (
            f"{args.note_prefix} | DEV->TEST | "
            f"item={args.item_type}/{args.item_name} | "
            f"commit={git_state['headCommit']}"
        )
        require(len(note) <= 1024, "Deployment note exceeds 1,024 characters.")

        deployment_request = {
            "sourceStageId": topology["sourceStageId"],
            "targetStageId": topology["targetStageId"],
            "items": [
                {
                    "sourceItemId": topology["sourceItemId"],
                    "itemType": args.item_type,
                }
            ],
            "note": note,
        }

        print("Deployment plan")
        print("===============")
        print(f"Pipeline: {topology['pipeline']['displayName']}")
        print(f"Source:   Development / {topology['sourceStage']['workspaceName']}")
        print(f"Target:   Test / {topology['targetStage']['workspaceName']}")
        print(f"Item:     {args.item_type} / {args.item_name}")
        print(f"Git:      {git_state['branch']} / {git_state['headCommit']}")
        print(f"Preflight age: {topology['ageMinutes']:.1f} minute(s)")
        print(json.dumps(deployment_request, indent=2))

        if not args.execute:
            print("\nDRY RUN SUCCEEDED\nNo Fabric write request was submitted.")
            return 0

        confirmation = args.confirmation or input(f"Type {CONFIRMATION} to submit: ")
        require(confirmation == CONFIRMATION, "Deployment cancelled: confirmation did not match.")

        credential = AzureCliCredential(tenant_id=args.tenant_id) if args.tenant_id else AzureCliCredential()
        token = credential.get_token(FABRIC_SCOPE).token
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        session = requests.Session()

        deployment_url = (
            f"{FABRIC_API_BASE}/deploymentPipelines/"
            f"{topology['pipelineId']}/deploy"
        )
        validate_url(deployment_url)
        response = session.post(
            deployment_url,
            headers={**headers, "Content-Type": "application/json"},
            json=deployment_request,
            timeout=60,
        )
        if response.status_code not in (200, 202):
            raise_http(response)

        status_code = response.status_code
        lro_id = response.headers.get("x-ms-operation-id")
        deployment_id = response.headers.get("deployment-id")
        returned_location = response.headers.get("Location")
        polling_url: str | None = None
        lro_state: dict[str, Any] | None = None
        deployment_operation: dict[str, Any] | None = None

        if status_code == 200:
            require(bool(response.content), "HTTP 200 response body is empty.")
            try:
                deployment_operation = response.json()
            except requests.JSONDecodeError as exc:
                raise DeploymentFailure("HTTP 200 response is invalid JSON.") from exc
            require(isinstance(deployment_operation, dict), "HTTP 200 response has unexpected JSON.")
            deployment_id = deployment_id or deployment_operation.get("id")
        else:
            require(isinstance(lro_id, str) and bool(lro_id), "HTTP 202 response has no x-ms-operation-id.")
            require(isinstance(deployment_id, str) and bool(deployment_id), "HTTP 202 response has no deployment-id.")
            print(f"Service Location header recorded but not followed: {returned_location}")
            polling_url, lro_state = poll_operation(
                session,
                lro_id,
                headers,
                retry_after(response.headers.get("Retry-After"), 10),
            )

        deployment_id = uuid_text(deployment_id, "deployment-id")

        if deployment_operation is None:
            operation_url = (
                f"{FABRIC_API_BASE}/deploymentPipelines/"
                f"{topology['pipelineId']}/operations/{deployment_id}"
            )
            _, deployment_operation = get_json(session, operation_url, headers)

        validate_deployment_operation(
            deployment_operation,
            topology["sourceStageId"],
            topology["targetStageId"],
            topology["sourceItemId"],
        )

        evidence = {
            "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "tutorialUnit": "Enterprise Deployment Automation / Unit 5",
            "codeState": git_state,
            "gitSync": {
                "path": str(git_sync_path),
                "sha256": git_sync_sha256,
                "generatedAtUtc": git_sync_evidence["generatedAtUtc"],
                "devWorkspaceCommitVerified": True,
            },
            "traceabilityLimitations": {
                "devWorkspaceCommitVerified": True,
                "runtimeTablesQueriedByClient": False,
                "explanation": (
                    "The deployment command proves the DEV workspace commit. "
                    "Runtime table content is validated by notebook assertions and a separate smoke run."
                ),
            },
            "preflight": {
                "path": str(preflight_path),
                "sha256": preflight_sha256,
                "generatedAtUtc": topology["generatedAtUtc"],
                "ageMinutesAtSubmission": topology["ageMinutes"],
            },
            "deploymentRequest": deployment_request,
            "response": {
                "httpStatusCode": status_code,
                "longRunningOperationId": lro_id,
                "deploymentId": deployment_id,
                "returnedLocationHeader": returned_location,
                "canonicalPollingUrl": polling_url,
            },
            "longRunningOperation": lro_state,
            "deploymentOperation": deployment_operation,
        }

        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")

        print("\nDEV -> TEST ITEM DEPLOYMENT SUCCEEDED")
        print(f"Deployment ID: {deployment_id}")
        print(f"LRO ID:        {lro_id}")
        print(f"Evidence:      {output}")
        return 0

    except (CredentialUnavailableError, ClientAuthenticationError) as exc:
        print(f"DEPLOYMENT FAILED: Azure CLI authentication failed: {exc}", file=sys.stderr)
        return 1
    except requests.RequestException as exc:
        print(f"DEPLOYMENT FAILED: Fabric HTTP request failed: {exc}", file=sys.stderr)
        return 1
    except DeploymentFailure as exc:
        print(f"DEPLOYMENT FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
