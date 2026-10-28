#!/usr/bin/env python3
"""Guarded TEST -> PROD release for the Fabric CI/CD tutorial.

The command verifies that the current main-branch content is byte-for-byte the
same repository tree and Fabric-definition content that previously passed the
non-production release. It then deploys one paired Notebook from TEST to PROD,
runs the PROD Data Pipeline, and writes non-secret release evidence.

The command intentionally does not synchronize a Production workspace from Git.
Production is promoted from the tested TEST deployment state through the Fabric
Deployment Pipeline.
"""

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
from typing import Any, Iterable
from urllib.parse import urlparse

import requests
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import AzureCliCredential, CredentialUnavailableError

FABRIC_API_BASE = "https://api.fabric.microsoft.com/v1"
FABRIC_SCOPE = "https://api.fabric.microsoft.com/.default"
FABRIC_HOST = "api.fabric.microsoft.com"
DEPLOYMENT_PIPELINE_NAME = "dp_fabric_cicd_lab"
TEST_WORKSPACE_NAME = "ws_reference_lab_test"
PROD_WORKSPACE_NAME = "ws_reference_lab_prod"
NOTEBOOK_NAME = "nb_01_seed_and_transform_cicd_lab"
PROD_PIPELINE_NAME = "pl_01_run_cicd_lab_transform"
CONFIRMATION = "RELEASE_TEST_TO_PROD"
LRO_TIMEOUT_MINUTES = 30
JOB_TIMEOUT_MINUTES = 60
FABRIC_DEFINITION_ROOTS = (
    "01_data_engineering",
    "02_orchestration",
    "99_admin",
)


class ProductionReleaseFailure(RuntimeError):
    """Raised when a production-release invariant is violated."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProductionReleaseFailure(message)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def uuid_text(value: Any, name: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{name} is missing.")
    try:
        return str(uuid.UUID(value))
    except ValueError as exc:
        raise ProductionReleaseFailure(f"{name} is not a valid UUID: {value!r}.") from exc


def git(*args: str, binary: bool = False) -> str | bytes:
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=not binary,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr if isinstance(result.stderr, str) else result.stderr.decode("utf-8", errors="replace")
        raise ProductionReleaseFailure(
            f"Git command failed: git {' '.join(args)}\n{stderr.strip()}"
        )
    return result.stdout


def tracked_files(roots: Iterable[str]) -> list[str]:
    output = git("ls-files", "-z", "--", *roots, binary=True)
    assert isinstance(output, bytes)
    paths = [entry.decode("utf-8") for entry in output.split(b"\0") if entry]
    require(paths, f"No tracked files found under: {', '.join(roots)}")
    return sorted(paths)


def digest_paths(paths: Iterable[str]) -> str:
    digest = hashlib.sha256()
    for relative_path in paths:
        path = Path(relative_path)
        require(path.is_file(), f"Tracked file is missing from the working tree: {path}")
        path_bytes = relative_path.replace("\\", "/").encode("utf-8")
        content = path.read_bytes()
        digest.update(len(path_bytes).to_bytes(8, "big"))
        digest.update(path_bytes)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def validate_main_state(expected_branch: str) -> dict[str, Any]:
    git("fetch", "--quiet", "origin", expected_branch)
    branch = str(git("branch", "--show-current")).strip()
    head = str(git("rev-parse", "HEAD")).strip()
    remote_ref = f"origin/{expected_branch}"
    remote_commit = str(git("rev-parse", remote_ref)).strip()
    tree_hash = str(git("rev-parse", "HEAD^{tree}")).strip()
    dirty = str(git("status", "--porcelain")).strip()

    require(branch == expected_branch, f"Current branch is '{branch}', expected '{expected_branch}'.")
    require(not dirty, "Git working tree is not clean.")
    require(head == remote_commit, f"Local HEAD does not match {remote_ref}.")

    fabric_files = tracked_files(FABRIC_DEFINITION_ROOTS)
    return {
        "branch": branch,
        "headCommit": head,
        "remoteRef": remote_ref,
        "remoteCommit": remote_commit,
        "repositoryTreeHash": tree_hash,
        "fabricDefinitionRoots": list(FABRIC_DEFINITION_ROOTS),
        "fabricDefinitionFileCount": len(fabric_files),
        "fabricDefinitionsSha256": digest_paths(fabric_files),
        "workingTreeClean": True,
    }


def load_json(path: Path, description: str) -> dict[str, Any]:
    require(path.is_file(), f"{description} does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProductionReleaseFailure(f"{description} is invalid JSON: {path}") from exc
    require(isinstance(payload, dict), f"{description} root must be an object.")
    return payload


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_manifest(
    manifest: dict[str, Any],
    main_state: dict[str, Any],
    release_label: str,
) -> dict[str, Any]:
    require(manifest.get("schemaVersion") == 1, "Unsupported release-manifest schema version.")
    require(manifest.get("releaseLabel") == release_label, "Release manifest has a different release label.")

    tested = manifest.get("testedCodeState")
    require(isinstance(tested, dict), "Release manifest has no testedCodeState object.")
    require(tested.get("branch") == "dev", "Release candidate was not tested from branch dev.")
    tested_commit = tested.get("headCommit")
    require(isinstance(tested_commit, str) and len(tested_commit) == 40, "Tested dev commit is invalid.")
    require(tested.get("workingTreeClean") is True, "Tested code state was not clean.")

    require(
        main_state["repositoryTreeHash"] == tested.get("repositoryTreeHash"),
        (
            "Current main tree differs from the exact repository tree tested in TEST. "
            "Do not promote an untested merge result."
        ),
    )
    require(
        main_state["fabricDefinitionsSha256"] == tested.get("fabricDefinitionsSha256"),
        "Current main Fabric definitions differ from the definitions tested in TEST.",
    )

    test_evidence = manifest.get("testEvidence")
    require(isinstance(test_evidence, dict), "Release manifest has no testEvidence object.")
    require(test_evidence.get("testValidationEnvironment") == "TEST", "Release manifest does not confirm TEST validation.")
    require(test_evidence.get("testValidationStatus") == "SUCCEEDED", "Release manifest does not confirm successful TEST validation.")
    uuid_text(test_evidence.get("testValidationRunId"), "testValidationRunId")
    uuid_text(test_evidence.get("testRuntimeJobInstanceId"), "testRuntimeJobInstanceId")
    uuid_text(test_evidence.get("devToTestDeploymentId"), "devToTestDeploymentId")

    intent = manifest.get("releaseIntent")
    require(isinstance(intent, dict), "Release manifest has no releaseIntent object.")
    require(intent.get("sourceStage") == "Test", "Release source stage is not Test.")
    require(intent.get("targetStage") == "Production", "Release target stage is not Production.")
    require(intent.get("itemType") == "Notebook", "Release item type is not Notebook.")
    require(intent.get("itemName") == NOTEBOOK_NAME, "Release Notebook is unexpected.")
    require(intent.get("productionRuntimePipeline") == PROD_PIPELINE_NAME, "Production runtime pipeline is unexpected.")

    return {
        "testedDevCommit": tested_commit,
        "testedRepositoryTreeHash": tested["repositoryTreeHash"],
        "testedFabricDefinitionsSha256": tested["fabricDefinitionsSha256"],
        "testValidationRunId": test_evidence["testValidationRunId"],
        "testRuntimeJobInstanceId": test_evidence["testRuntimeJobInstanceId"],
        "devToTestDeploymentId": test_evidence["devToTestDeploymentId"],
    }


def validate_url(url: str) -> None:
    parsed = urlparse(url)
    require(
        parsed.scheme == "https" and parsed.hostname == FABRIC_HOST,
        f"Refusing to send a Fabric bearer token to unexpected URL: {url}",
    )


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
    request_id = (
        response.headers.get("x-ms-request-id")
        or response.headers.get("requestId")
        or response.headers.get("ActivityId")
    )
    suffix = f" Request ID: {request_id}." if request_id else ""
    raise ProductionReleaseFailure(
        f"{response.request.method} {response.url} failed with HTTP "
        f"{response.status_code}: {body}.{suffix}"
    )


def request(
    session: requests.Session,
    method: str,
    url: str,
    headers: dict[str, str],
    *,
    body: dict[str, Any] | None = None,
    allowed_statuses: tuple[int, ...] = (200,),
    attempts: int = 6,
) -> requests.Response:
    validate_url(url)
    for attempt in range(1, attempts + 1):
        response = session.request(
            method,
            url,
            headers=(
                {**headers, "Content-Type": "application/json"}
                if body is not None
                else headers
            ),
            json=body,
            timeout=60,
        )
        retryable = response.status_code == 429 or response.status_code >= 500
        if retryable and attempt < attempts:
            delay = retry_after(response.headers.get("Retry-After"), min(2**attempt, 30))
            print(f"{method} returned HTTP {response.status_code}; retrying in {delay}s...", file=sys.stderr)
            time.sleep(delay)
            continue
        if response.status_code not in allowed_statuses:
            raise_http(response)
        return response
    raise AssertionError("HTTP retry loop exited unexpectedly.")


def response_json(response: requests.Response, description: str) -> dict[str, Any]:
    require(bool(response.content), f"{description} returned an empty body.")
    try:
        payload = response.json()
    except requests.JSONDecodeError as exc:
        raise ProductionReleaseFailure(f"{description} returned invalid JSON.") from exc
    require(isinstance(payload, dict), f"{description} returned unexpected JSON.")
    return payload


def get_collection(
    session: requests.Session,
    url: str,
    headers: dict[str, str],
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    next_url: str | None = url
    while next_url:
        response = request(session, "GET", next_url, headers)
        payload = response_json(response, f"GET {next_url}")
        values = payload.get("value")
        require(isinstance(values, list), f"GET {next_url} returned no value collection.")
        require(all(isinstance(value, dict) for value in values), f"GET {next_url} returned an invalid collection item.")
        items.extend(values)
        continuation = payload.get("continuationUri")
        next_url = continuation if isinstance(continuation, str) and continuation.strip() else None
    return items


def single(values: Any, predicate, description: str) -> dict[str, Any]:
    require(isinstance(values, list), f"{description} collection is not a list.")
    matches = [value for value in values if isinstance(value, dict) and predicate(value)]
    require(len(matches) == 1, f"Expected exactly one {description}; found {len(matches)}.")
    return matches[0]


def run_preflight(tenant_id: str, output_path: Path) -> dict[str, Any]:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/fabric_deployment_pipeline_preflight.py",
            "--pipeline-name",
            DEPLOYMENT_PIPELINE_NAME,
            "--tenant-id",
            tenant_id,
            "--output",
            str(output_path),
        ],
        check=False,
    )
    require(result.returncode == 0, "Fabric deployment topology preflight failed.")
    return load_json(output_path, "Fabric deployment topology preflight")


def stage(preflight: dict[str, Any], name: str, workspace: str) -> dict[str, Any]:
    found = single(
        preflight.get("stages"),
        lambda value: value.get("displayName") == name,
        f"stage named '{name}'",
    )
    require(found.get("workspaceName") == workspace, f"Stage '{name}' is assigned to an unexpected workspace.")
    uuid_text(found.get("id"), f"{name}.id")
    uuid_text(found.get("workspaceId"), f"{name}.workspaceId")
    return found


def topology_for_prod(preflight: dict[str, Any]) -> dict[str, Any]:
    pipeline = preflight.get("deploymentPipeline")
    require(isinstance(pipeline, dict), "Preflight has no deploymentPipeline object.")
    require(pipeline.get("displayName") == DEPLOYMENT_PIPELINE_NAME, "Unexpected Deployment Pipeline.")
    pipeline_id = uuid_text(pipeline.get("id"), "deploymentPipeline.id")

    test_stage = stage(preflight, "Test", TEST_WORKSPACE_NAME)
    prod_stage = stage(preflight, "Production", PROD_WORKSPACE_NAME)
    test_stage_id = uuid_text(test_stage.get("id"), "Test.id")
    prod_stage_id = uuid_text(prod_stage.get("id"), "Production.id")
    require(test_stage_id != prod_stage_id, "TEST and Production stage IDs are identical.")

    source_item = single(
        test_stage.get("items"),
        lambda value: value.get("itemType") == "Notebook" and value.get("itemDisplayName") == NOTEBOOK_NAME,
        f"TEST Notebook named '{NOTEBOOK_NAME}'",
    )
    target_item = single(
        prod_stage.get("items"),
        lambda value: value.get("itemType") == "Notebook" and value.get("itemDisplayName") == NOTEBOOK_NAME,
        f"PROD Notebook named '{NOTEBOOK_NAME}'",
    )
    source_item_id = uuid_text(source_item.get("itemId"), "Test.Notebook.itemId")
    target_item_id = uuid_text(target_item.get("itemId"), "Production.Notebook.itemId")
    require(uuid_text(source_item.get("targetItemId"), "Test.Notebook.targetItemId") == target_item_id, "TEST Notebook does not target the paired PROD Notebook.")
    require(uuid_text(target_item.get("sourceItemId"), "Production.Notebook.sourceItemId") == source_item_id, "PROD Notebook does not identify the paired TEST Notebook.")

    prod_pipeline = single(
        prod_stage.get("items"),
        lambda value: value.get("itemType") == "DataPipeline" and value.get("itemDisplayName") == PROD_PIPELINE_NAME,
        f"PROD DataPipeline named '{PROD_PIPELINE_NAME}'",
    )

    return {
        "pipeline": pipeline,
        "pipelineId": pipeline_id,
        "sourceStage": test_stage,
        "sourceStageId": test_stage_id,
        "targetStage": prod_stage,
        "targetStageId": prod_stage_id,
        "sourceItem": source_item,
        "sourceItemId": source_item_id,
        "targetItem": target_item,
        "targetItemId": target_item_id,
        "prodPipelineItem": prod_pipeline,
        "prodPipelineItemId": uuid_text(prod_pipeline.get("itemId"), "Production.DataPipeline.itemId"),
        "prodWorkspaceId": uuid_text(prod_stage.get("workspaceId"), "Production.workspaceId"),
    }


def poll_lro(
    session: requests.Session,
    headers: dict[str, str],
    operation_id: str,
    initial_wait: int,
) -> tuple[str, dict[str, Any]]:
    operation_id = uuid_text(operation_id, "x-ms-operation-id")
    operation_url = f"{FABRIC_API_BASE}/operations/{operation_id}"
    deadline = now_utc() + timedelta(minutes=LRO_TIMEOUT_MINUTES)
    wait_seconds = initial_wait

    while True:
        require(now_utc() <= deadline, "Fabric deployment operation timed out.")
        time.sleep(wait_seconds)
        response = request(session, "GET", operation_url, headers)
        state = response_json(response, "Fabric deployment LRO")
        status = state.get("status")
        print(f"Deployment LRO status: {status} ({state.get('percentComplete', '?')}%)")
        if status == "Succeeded":
            return operation_url, state
        if status == "Failed":
            raise ProductionReleaseFailure(
                "Fabric deployment LRO failed: " + json.dumps(state.get("error"), ensure_ascii=False)
            )
        wait_seconds = retry_after(response.headers.get("Retry-After"), wait_seconds)


def validate_execution_plan(operation: dict[str, Any], source_item_id: str) -> None:
    plan = operation.get("executionPlan")
    require(isinstance(plan, dict), "Deployment operation has no executionPlan.")
    steps = plan.get("steps")
    require(isinstance(steps, list), "Deployment execution plan has no steps collection.")

    deployed_source_ids: set[str] = set()
    for step in steps:
        if not isinstance(step, dict):
            continue
        source_and_target = step.get("sourceAndTarget")
        if not isinstance(source_and_target, dict):
            continue
        source_id = source_and_target.get("sourceItemId")
        if isinstance(source_id, str) and source_id.strip():
            deployed_source_ids.add(uuid_text(source_id, "executionPlan.sourceItemId"))

    require(
        deployed_source_ids == {source_item_id},
        f"Deployment execution plan contains unexpected source items: {sorted(deployed_source_ids)}",
    )


def deploy_notebook(
    session: requests.Session,
    headers: dict[str, str],
    topology: dict[str, Any],
    note: str,
) -> dict[str, Any]:
    require(len(note) <= 1024, "Deployment note exceeds 1024 characters.")
    body = {
        "sourceStageId": topology["sourceStageId"],
        "targetStageId": topology["targetStageId"],
        "items": [
            {
                "sourceItemId": topology["sourceItemId"],
                "itemType": "Notebook",
            }
        ],
        "note": note,
    }
    deploy_url = f"{FABRIC_API_BASE}/deploymentPipelines/{topology['pipelineId']}/deploy"
    response = request(
        session,
        "POST",
        deploy_url,
        headers,
        body=body,
        allowed_statuses=(200, 202),
    )

    operation_id = response.headers.get("x-ms-operation-id")
    deployment_id = response.headers.get("deployment-id")
    returned_location = response.headers.get("Location")
    lro_state: dict[str, Any] | None = None
    canonical_polling_url: str | None = None
    deployment_operation: dict[str, Any] | None = None

    if response.status_code == 200 and response.content:
        deployment_operation = response_json(response, "Synchronous deployment operation")
        deployment_id = deployment_operation.get("id") or deployment_id
    else:
        require(operation_id, "Deployment returned HTTP 202 without x-ms-operation-id.")
        require(deployment_id, "Deployment returned HTTP 202 without deployment-id.")
        canonical_polling_url, lro_state = poll_lro(
            session,
            headers,
            operation_id,
            retry_after(response.headers.get("Retry-After"), 10),
        )

    deployment_id = uuid_text(deployment_id, "deployment-id")
    if deployment_operation is None:
        operation_url = (
            f"{FABRIC_API_BASE}/deploymentPipelines/{topology['pipelineId']}"
            f"/operations/{deployment_id}"
        )
        operation_response = request(session, "GET", operation_url, headers)
        deployment_operation = response_json(operation_response, "Deployment Pipeline operation")

    require(deployment_operation.get("status") == "Succeeded", "Detailed Deployment Pipeline operation did not succeed.")
    require(deployment_operation.get("sourceStageId") == topology["sourceStageId"], "Deployment operation reports an unexpected source stage.")
    require(deployment_operation.get("targetStageId") == topology["targetStageId"], "Deployment operation reports an unexpected target stage.")
    validate_execution_plan(deployment_operation, topology["sourceItemId"])

    return {
        "request": body,
        "response": {
            "httpStatusCode": response.status_code,
            "longRunningOperationId": operation_id,
            "deploymentId": deployment_id,
            "returnedLocationHeader": returned_location,
            "canonicalPollingUrl": canonical_polling_url,
        },
        "longRunningOperation": lro_state,
        "deploymentOperation": deployment_operation,
    }


def extract_job_instance_id(location: str) -> str:
    require(isinstance(location, str) and bool(location.strip()), "Pipeline job response has no Location header.")
    parsed = urlparse(location)
    require(parsed.scheme == "https", f"Pipeline job Location is not HTTPS: {location}")
    segments = [segment for segment in parsed.path.split("/") if segment]
    try:
        index = segments.index("instances")
    except ValueError as exc:
        raise ProductionReleaseFailure(f"Pipeline job Location has no instances segment: {location}") from exc
    require(index + 1 < len(segments), f"Pipeline job Location has no instance ID: {location}")
    return uuid_text(segments[index + 1], "Production pipeline job instance ID")


def run_prod_pipeline(
    session: requests.Session,
    headers: dict[str, str],
    topology: dict[str, Any],
) -> dict[str, Any]:
    workspace_id = topology["prodWorkspaceId"]
    pipeline_id = topology["prodPipelineItemId"]
    run_url = (
        f"{FABRIC_API_BASE}/workspaces/{workspace_id}/"
        f"dataPipelines/{pipeline_id}/jobs/execute/instances"
    )
    response = request(
        session,
        "POST",
        run_url,
        headers,
        allowed_statuses=(202,),
    )
    returned_location = response.headers.get("Location")
    job_id = extract_job_instance_id(returned_location or "")
    canonical_url = (
        f"{FABRIC_API_BASE}/workspaces/{workspace_id}/items/{pipeline_id}/"
        f"jobs/instances/{job_id}"
    )
    wait_seconds = retry_after(response.headers.get("Retry-After"), 30)
    deadline = now_utc() + timedelta(minutes=JOB_TIMEOUT_MINUTES)

    print(f"Production pipeline job instance: {job_id}")
    print(f"Service Location header recorded but not followed: {returned_location}")
    print(f"Polling canonical Fabric URL: {canonical_url}")

    while True:
        require(now_utc() <= deadline, "Production pipeline job timed out.")
        time.sleep(wait_seconds)
        job_response = request(session, "GET", canonical_url, headers)
        job = response_json(job_response, "Production pipeline job instance")
        status = job.get("status")
        print(f"Production pipeline status: {status}")
        if status == "Completed":
            return {
                "workspace": {"id": workspace_id, "name": PROD_WORKSPACE_NAME},
                "pipeline": {"id": pipeline_id, "name": PROD_PIPELINE_NAME, "jobType": "Execute"},
                "submission": {
                    "httpStatusCode": response.status_code,
                    "returnedLocationHeader": returned_location,
                    "jobInstanceId": job_id,
                    "canonicalPollingUrl": canonical_url,
                },
                "jobInstance": job,
                "runtimeAuditInspectionRequired": True,
            }
        if status in {"Failed", "Cancelled", "Deduped"}:
            raise ProductionReleaseFailure(
                "Production pipeline did not complete successfully: "
                + json.dumps(job, ensure_ascii=False)
            )
        wait_seconds = retry_after(job_response.headers.get("Retry-After"), wait_seconds)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Promote one tested Notebook from TEST to PROD and execute PROD."
    )
    parser.add_argument("--tenant-id", required=True)
    parser.add_argument("--release-label", required=True)
    parser.add_argument("--release-manifest", required=True)
    parser.add_argument("--approved-by", required=True)
    parser.add_argument("--approval-reference", required=True)
    parser.add_argument("--expected-branch", default="main")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirmation")
    parser.add_argument("--artifacts-dir", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        main_state = validate_main_state(args.expected_branch)
        manifest_path = Path(args.release_manifest)
        manifest = load_json(manifest_path, "Release-candidate manifest")
        manifest_summary = validate_manifest(manifest, main_state, args.release_label)

        artifacts_dir = Path(args.artifacts_dir)
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        preflight_path = artifacts_dir / "fabric-prod-preflight.json"
        post_preflight_path = artifacts_dir / "fabric-prod-preflight-after-deployment.json"
        evidence_path = artifacts_dir / "fabric-prod-release.json"

        preflight = run_preflight(args.tenant_id, preflight_path)
        topology = topology_for_prod(preflight)
        manifest_digest = sha256_file(manifest_path)

        print("\nProduction release plan")
        print("=======================")
        print(f"Release label:       {args.release_label}")
        print(f"Tested dev commit:   {manifest_summary['testedDevCommit']}")
        print(f"Current main commit: {main_state['headCommit']}")
        print(f"Repository tree:     {main_state['repositoryTreeHash']}")
        print(f"Source:              Test / {TEST_WORKSPACE_NAME}")
        print(f"Target:              Production / {PROD_WORKSPACE_NAME}")
        print(f"Item:                Notebook / {NOTEBOOK_NAME}")
        print(f"Runtime:             PROD pipeline / {PROD_PIPELINE_NAME}")
        print(f"Approved by:         {args.approved_by}")
        print(f"Approval reference:  {args.approval_reference}")
        print("Independent SoD:     NOT VERIFIED by this local command")

        if not args.execute:
            print("\nDRY RUN SUCCEEDED")
            print("No Fabric write request was submitted.")
            return 0

        confirmation = args.confirmation or input(
            f"Type {CONFIRMATION} to deploy TEST to PROD and run PROD: "
        )
        require(confirmation == CONFIRMATION, "Production release cancelled: confirmation did not match.")

        credential = AzureCliCredential(tenant_id=args.tenant_id)
        token = credential.get_token(FABRIC_SCOPE).token
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        session = requests.Session()

        note = (
            f"tutorial unit 6 | {args.release_label} | TEST->PROD | "
            f"dev={manifest_summary['testedDevCommit'][:12]} | "
            f"main={main_state['headCommit'][:12]} | manifest={manifest_digest[:12]}"
        )
        deployment = deploy_notebook(session, headers, topology, note)

        post_preflight = run_preflight(args.tenant_id, post_preflight_path)
        topology_after = topology_for_prod(post_preflight)
        require(
            topology_after["sourceItemId"] == topology["sourceItemId"],
            "TEST Notebook item changed unexpectedly during production release.",
        )
        require(
            topology_after["targetItemId"] == topology["targetItemId"],
            "PROD Notebook item changed unexpectedly during production release.",
        )

        runtime = run_prod_pipeline(session, headers, topology_after)

        evidence = {
            "schemaVersion": 1,
            "generatedAtUtc": now_utc().isoformat(),
            "tutorialUnit": "Enterprise Deployment Automation / Unit 6",
            "releaseLabel": args.release_label,
            "approval": {
                "approvedBy": args.approved_by,
                "approvalReference": args.approval_reference,
                "productionConfirmation": CONFIRMATION,
                "independentSeparationOfDutiesVerified": False,
            },
            "codeState": {
                "testedDevCommit": manifest_summary["testedDevCommit"],
                "currentMain": main_state,
                "testedAndMainRepositoryTreeMatch": True,
                "testedAndMainFabricDefinitionsMatch": True,
            },
            "releaseManifest": {
                "path": str(manifest_path),
                "sha256": manifest_digest,
                "testValidationRunId": manifest_summary["testValidationRunId"],
                "testRuntimeJobInstanceId": manifest_summary["testRuntimeJobInstanceId"],
                "devToTestDeploymentId": manifest_summary["devToTestDeploymentId"],
            },
            "stateTransitions": {
                "testToProductionDeployment": "Verified",
                "productionRuntimeExecution": "Completed",
                "backwardDeployment": "NotUsed",
            },
            "deployment": deployment,
            "runtime": runtime,
            "supportingEvidence": {
                "preflightPath": str(preflight_path),
                "preflightSha256": sha256_file(preflight_path),
                "postDeploymentPreflightPath": str(post_preflight_path),
                "postDeploymentPreflightSha256": sha256_file(post_preflight_path),
            },
            "manualCompletionChecks": [
                f"Verify the latest PROD cicd_run_audit row has release label {args.release_label}.",
                "Verify the latest PROD cicd_run_audit row has environment_name PROD.",
                "Verify PROD Variable Library active value remains PROD.",
                "Verify DEV and TEST runtime tables were not updated by the PROD job.",
            ],
        }
        evidence_path.write_text(
            json.dumps(evidence, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        print("\nPRODUCTION RELEASE SUCCEEDED")
        print(f"Release label: {args.release_label}")
        print(f"Deployment ID: {deployment['response']['deploymentId']}")
        print(f"PROD job ID:   {runtime['submission']['jobInstanceId']}")
        print(f"Evidence:      {evidence_path}")
        print("Manual PROD audit-table and cross-environment isolation checks remain required.")
        return 0

    except (CredentialUnavailableError, ClientAuthenticationError) as exc:
        print(f"PRODUCTION RELEASE FAILED: Azure CLI authentication failed: {exc}", file=sys.stderr)
        return 1
    except requests.RequestException as exc:
        print(f"PRODUCTION RELEASE FAILED: Fabric HTTP request failed: {exc}", file=sys.stderr)
        return 1
    except ProductionReleaseFailure as exc:
        print(f"PRODUCTION RELEASE FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
