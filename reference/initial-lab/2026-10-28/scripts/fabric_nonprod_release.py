#!/usr/bin/env python3
"""End-to-end non-production release support for the Fabric CI/CD tutorial.

Sequence:
1. Validate the trusted dev code state against origin/dev.
2. Discover the Fabric deployment topology.
3. Verify and, when required, update the DEV workspace from Git.
4. Re-run deployment topology preflight.
5. Deploy the selected DEV item to TEST using the repository-owned deploy command.
6. Re-run preflight and execute the TEST data pipeline.
7. Write consolidated, non-secret release evidence.

The command supports both:
- interactive local execution;
- Azure DevOps execution against a checked-out immutable commit.

The command intentionally supports Development -> Test only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

import requests
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import AzureCliCredential, CredentialUnavailableError

from tutorial_config import (
    DEFAULT_CONFIG_PATH,
    TutorialConfigError,
    load_tutorial_resources,
)

FABRIC_API_BASE = "https://api.fabric.microsoft.com/v1"
FABRIC_SCOPE = "https://api.fabric.microsoft.com/.default"
FABRIC_HOST = "api.fabric.microsoft.com"
TEST_PIPELINE_NAME = "pl_01_run_cicd_lab_transform"
RELEASE_CONFIRMATION = "RELEASE_DEV_TO_TEST"
LRO_TIMEOUT_MINUTES = 30
JOB_TIMEOUT_MINUTES = 60
REMOTE_PROPAGATION_ATTEMPTS = 12
REMOTE_PROPAGATION_DELAY_SECONDS = 10


class ReleaseFailure(RuntimeError):
    """Raised when a release invariant is violated."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReleaseFailure(message)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def uuid_text(value: Any, name: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{name} is missing.")
    try:
        return str(uuid.UUID(value))
    except ValueError as exc:
        raise ReleaseFailure(f"{name} is not a valid UUID: {value!r}.") from exc


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


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise ReleaseFailure(
            f"Git command failed: git {' '.join(args)}\n{result.stderr.strip()}"
        )
    return result.stdout.strip()


def validate_git_state(
    expected_branch: str,
    expected_repository_name: str | None = None,
) -> dict[str, Any]:
    expected_source_ref = (
        f"refs/heads/{expected_branch}"
    )

    remote_ref = (
        f"origin/{expected_branch}"
    )

    # Azure Pipelines can check out a commit in detached-HEAD mode.
    # Therefore we explicitly materialize the remote-tracking branch
    # rather than assuming a local branch named "dev" exists.
    git(
        "fetch",
        "--quiet",
        "origin",
        (
            f"refs/heads/{expected_branch}:"
            f"refs/remotes/origin/{expected_branch}"
        ),
    )

    checkout_branch = git(
        "branch",
        "--show-current",
    )

    head = git(
        "rev-parse",
        "HEAD",
    )

    remote_head = git(
        "rev-parse",
        remote_ref,
    )

    tree_hash = git(
        "rev-parse",
        "HEAD^{tree}",
    )

    dirty = git(
        "status",
        "--porcelain",
    )

    # Local execution normally has an attached branch.
    # Azure Pipelines may legitimately use detached HEAD.
    if checkout_branch:
        require(
            checkout_branch
            == expected_branch,
            (
                "Current attached branch is "
                f"'{checkout_branch}', expected "
                f"'{expected_branch}'."
            ),
        )

        checkout_mode = "attached"

    else:
        checkout_mode = "detached"

    # Azure DevOps exposes the actual source ref and commit through
    # environment variables. They are absent during ordinary local use.
    pipeline_source_branch = (
        os.getenv(
            "BUILD_SOURCEBRANCH",
            "",
        ).strip()
    )

    pipeline_source_version = (
        os.getenv(
            "BUILD_SOURCEVERSION",
            "",
        ).strip()
    )

    pipeline_repository_name = (
        os.getenv(
            "BUILD_REPOSITORY_NAME",
            "",
        ).strip()
    )

    origin_url = git(
        "remote",
        "get-url",
        "origin",
    )
    origin_repository_name = unquote(
        origin_url.rstrip("/").rsplit("/", 1)[-1]
    )
    if origin_repository_name.endswith(".git"):
        origin_repository_name = origin_repository_name[:-4]

    if pipeline_source_branch:
        require(
            pipeline_source_branch
            == expected_source_ref,
            (
                "Azure DevOps source branch is "
                f"'{pipeline_source_branch}', expected "
                f"'{expected_source_ref}'."
            ),
        )

    if pipeline_source_version:
        require(
            pipeline_source_version
            == head,
            (
                "Azure DevOps Build.SourceVersion "
                "does not match checked-out HEAD: "
                f"pipeline='{pipeline_source_version}', "
                f"HEAD='{head}'."
            ),
        )

    if expected_repository_name:
        require(
            origin_repository_name == expected_repository_name,
            (
                "Git origin repository is "
                f"'{origin_repository_name}', expected "
                f"'{expected_repository_name}'."
            ),
        )

        if pipeline_repository_name:
            require(
                pipeline_repository_name == expected_repository_name,
                (
                    "Azure DevOps Build.Repository.Name is "
                    f"'{pipeline_repository_name}', expected "
                    f"'{expected_repository_name}'."
                ),
            )

    require(
        not dirty,
        "Git working tree is not clean.",
    )

    require(
        head == remote_head,
        (
            "Checked-out HEAD does not match "
            f"{remote_ref}: "
            f"HEAD='{head}', "
            f"{remote_ref}='{remote_head}'."
        ),
    )

    return {
        "branch": expected_branch,
        "checkoutMode": checkout_mode,
        "checkoutBranch": (
            checkout_branch or None
        ),
        "headCommit": head,
        "remoteRef": remote_ref,
        "remoteCommit": remote_head,
        "pipelineSourceBranch": (
            pipeline_source_branch
            or None
        ),
        "pipelineSourceVersion": (
            pipeline_source_version
            or None
        ),
        "expectedRepositoryName": expected_repository_name,
        "pipelineRepositoryName": pipeline_repository_name or None,
        "originRepositoryName": origin_repository_name,
        "repositoryTreeHash": tree_hash,
        "workingTreeClean": True,
    }


def run_repository_command(arguments: list[str], description: str) -> None:
    print(f"\n{description}")
    print("-" * len(description))
    result = subprocess.run(arguments, check=False)
    if result.returncode != 0:
        raise ReleaseFailure(
            f"{description} failed with exit code {result.returncode}."
        )


def load_json(path: Path, description: str) -> dict[str, Any]:
    require(path.is_file(), f"{description} does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReleaseFailure(f"{description} is invalid JSON: {path}") from exc
    require(isinstance(payload, dict), f"{description} root must be an object.")
    return payload


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def single(values: Any, predicate, description: str) -> dict[str, Any]:
    require(isinstance(values, list), f"{description} collection is not a list.")
    matches = [value for value in values if isinstance(value, dict) and predicate(value)]
    require(len(matches) == 1, f"Expected exactly one {description}; found {len(matches)}.")
    return matches[0]


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
    raise ReleaseFailure(
        f"{response.request.method} {response.url} failed with HTTP "
        f"{response.status_code}: {body}.{suffix}"
    )


def request_json(
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
            delay = retry_after(
                response.headers.get("Retry-After"), min(2**attempt, 30)
            )
            print(
                f"{method} returned HTTP {response.status_code}; retrying in {delay}s...",
                file=sys.stderr,
            )
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
        raise ReleaseFailure(f"{description} returned invalid JSON.") from exc
    require(isinstance(payload, dict), f"{description} returned unexpected JSON.")
    return payload


def poll_lro(
    session: requests.Session,
    operation_id: str,
    headers: dict[str, str],
    initial_wait: int,
    *,
    get_result: bool,
) -> tuple[str, dict[str, Any], dict[str, Any] | None]:
    operation_id = uuid_text(operation_id, "x-ms-operation-id")
    operation_url = f"{FABRIC_API_BASE}/operations/{operation_id}"
    deadline = now_utc() + timedelta(minutes=LRO_TIMEOUT_MINUTES)
    wait_seconds = initial_wait

    while True:
        require(now_utc() <= deadline, "Fabric long-running operation timed out.")
        time.sleep(wait_seconds)
        response = request_json(
            session,
            "GET",
            operation_url,
            headers,
            allowed_statuses=(200,),
        )
        state = response_json(response, "Fabric operation state")
        status = state.get("status")
        percent = state.get("percentComplete", "?")
        print(f"Operation status: {status} ({percent}%)")

        if status == "Succeeded":
            result: dict[str, Any] | None = None
            if get_result:
                result_url = f"{operation_url}/result"
                result_response = request_json(
                    session,
                    "GET",
                    result_url,
                    headers,
                    allowed_statuses=(200,),
                )
                result = response_json(result_response, "Fabric operation result")
            return operation_url, state, result

        if status == "Failed":
            raise ReleaseFailure(
                "Fabric operation failed: "
                + json.dumps(state.get("error"), ensure_ascii=False)
            )

        wait_seconds = retry_after(response.headers.get("Retry-After"), wait_seconds)


def get_json_or_lro(
    session: requests.Session,
    url: str,
    headers: dict[str, str],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    response = request_json(
        session,
        "GET",
        url,
        headers,
        allowed_statuses=(200, 202),
    )
    if response.status_code == 200:
        return response_json(response, f"GET {url}"), None

    operation_id = response.headers.get("x-ms-operation-id")
    require(operation_id, "Fabric returned HTTP 202 without x-ms-operation-id.")
    _, state, result = poll_lro(
        session,
        operation_id,
        headers,
        retry_after(response.headers.get("Retry-After"), 10),
        get_result=True,
    )
    require(result is not None, "Fabric LRO completed without a result.")
    return result, state


def run_preflight(
    tenant_id: str,
    deployment_pipeline_name: str,
    output_path: Path,
    description: str,
) -> dict[str, Any]:
    run_repository_command(
        [
            sys.executable,
            "scripts/fabric_deployment_pipeline_preflight.py",
            "--pipeline-name",
            deployment_pipeline_name,
            "--tenant-id",
            tenant_id,
            "--output",
            str(output_path),
        ],
        description,
    )
    return load_json(output_path, description)


def get_stage(preflight: dict[str, Any], name: str, workspace_name: str) -> dict[str, Any]:
    stage = single(
        preflight.get("stages"),
        lambda value: value.get("displayName") == name,
        f"stage named '{name}'",
    )
    require(
        stage.get("workspaceName") == workspace_name,
        f"Stage '{name}' is assigned to unexpected workspace '{stage.get('workspaceName')}'.",
    )
    uuid_text(stage.get("id"), f"{name}.id")
    uuid_text(stage.get("workspaceId"), f"{name}.workspaceId")
    return stage


def validate_git_connection(
    connection: dict[str, Any], expected_branch: str
) -> None:
    require(
        connection.get("gitConnectionState") == "ConnectedAndInitialized",
        "DEV workspace Git connection is not ConnectedAndInitialized.",
    )
    provider = connection.get("gitProviderDetails")
    require(isinstance(provider, dict), "DEV workspace has no Git provider details.")
    require(provider.get("gitProviderType") == "AzureDevOps", "DEV workspace is not connected to Azure DevOps Git.")
    require(provider.get("branchName") == expected_branch, f"DEV workspace is connected to '{provider.get('branchName')}', expected '{expected_branch}'.")


def validate_no_workspace_changes(status: dict[str, Any]) -> None:
    changes = status.get("changes")
    require(isinstance(changes, list), "Fabric Git status has no changes collection.")

    workspace_changes = [
        change
        for change in changes
        if isinstance(change, dict) and change.get("workspaceChange") is not None
    ]
    conflicts = [
        change
        for change in changes
        if isinstance(change, dict) and change.get("conflictType") == "Conflict"
    ]

    require(
        not workspace_changes,
        (
            "DEV contains workspace-side Git changes. Commit or discard them before release. "
            + json.dumps(workspace_changes, ensure_ascii=False)
        ),
    )
    require(
        not conflicts,
        "DEV contains Git conflicts. Resolve them before release.",
    )


def wait_for_fabric_remote_commit(
    session: requests.Session,
    status_url: str,
    headers: dict[str, str],
    expected_commit: str,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    last_status: dict[str, Any] | None = None
    last_lro: dict[str, Any] | None = None

    for attempt in range(1, REMOTE_PROPAGATION_ATTEMPTS + 1):
        status, lro = get_json_or_lro(session, status_url, headers)
        last_status = status
        last_lro = lro
        remote_commit = status.get("remoteCommitHash")
        if remote_commit == expected_commit:
            return status, lro

        if attempt < REMOTE_PROPAGATION_ATTEMPTS:
            print(
                "Fabric currently sees remote commit "
                f"{remote_commit}; waiting for {expected_commit}..."
            )
            time.sleep(REMOTE_PROPAGATION_DELAY_SECONDS)

    raise ReleaseFailure(
        "Fabric Git status did not observe the expected origin/dev commit. "
        f"Last status: {json.dumps(last_status, ensure_ascii=False)}"
    )


def synchronize_dev_workspace(
    session: requests.Session,
    headers: dict[str, str],
    workspace_id: str,
    expected_branch: str,
    code_state: dict[str, Any],
    dev_workspace_name: str,
    *,
    execute: bool,
) -> dict[str, Any]:
    connection_url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/git/connection"
    credentials_url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/git/myGitCredentials"
    status_url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/git/status"
    update_url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/git/updateFromGit"

    connection_response = request_json(session, "GET", connection_url, headers)
    connection = response_json(connection_response, "DEV Git connection")
    validate_git_connection(connection, expected_branch)

    credentials_response = request_json(session, "GET", credentials_url, headers)
    credentials = response_json(credentials_response, "DEV Git credentials")
    require(
        credentials.get("source") in {"Automatic", "ConfiguredConnection"},
        (
            "Git credentials are not configured for the current user. "
            "Configure Automatic or ConfiguredConnection credentials before continuing."
        ),
    )

    expected_commit = code_state["headCommit"]
    status_before, status_lro = wait_for_fabric_remote_commit(
        session, status_url, headers, expected_commit
    )
    validate_no_workspace_changes(status_before)

    workspace_head = status_before.get("workspaceHead")
    remote_commit = status_before.get("remoteCommitHash")
    require(remote_commit == expected_commit, "Fabric remote commit does not match origin/dev.")

    update_request: dict[str, Any] | None = None
    update_response_evidence: dict[str, Any] | None = None
    update_lro: dict[str, Any] | None = None
    status_after = status_before

    already_synchronized = workspace_head == expected_commit and status_before.get("changes") == []

    if not already_synchronized:
        update_request = {
            "workspaceHead": workspace_head,
            "remoteCommitHash": expected_commit,
            "options": {"allowOverrideItems": True},
        }

        print("\nDEV workspace requires Git update:")
        print(json.dumps(update_request, indent=2))

        if not execute:
            return {
                "generatedAtUtc": now_utc().isoformat(),
                "tutorialUnit": "Enterprise Deployment Automation / Unit 5",
                "codeState": code_state,
                "workspace": {"id": workspace_id, "name": dev_workspace_name},
                "gitConnection": connection,
                "gitCredentials": credentials,
                "statusBefore": status_before,
                "statusGetLro": status_lro,
                "updateRequired": True,
                "updateRequest": update_request,
                "updateResponse": None,
                "updateLro": None,
                "statusAfter": None,
                "synchronized": False,
                "dryRun": True,
            }

        update_response = request_json(
            session,
            "POST",
            update_url,
            headers,
            body=update_request,
            allowed_statuses=(200, 202),
        )
        update_response_evidence = {
            "httpStatusCode": update_response.status_code,
            "xMsOperationId": update_response.headers.get("x-ms-operation-id"),
            "returnedLocationHeader": update_response.headers.get("Location"),
            "canonicalPollingUrl": None,
        }

        if update_response.status_code == 202:
            operation_id = update_response.headers.get("x-ms-operation-id")
            require(operation_id, "Update From Git returned HTTP 202 without x-ms-operation-id.")
            polling_url, update_lro, _ = poll_lro(
                session,
                operation_id,
                headers,
                retry_after(update_response.headers.get("Retry-After"), 10),
                get_result=False,
            )
            update_response_evidence["canonicalPollingUrl"] = polling_url

        status_after, _ = get_json_or_lro(session, status_url, headers)

    require(status_after.get("workspaceHead") == expected_commit, "DEV workspaceHead does not match origin/dev after synchronization.")
    require(status_after.get("remoteCommitHash") == expected_commit, "Fabric remoteCommitHash does not match origin/dev after synchronization.")
    require(status_after.get("changes") == [], "DEV workspace still has Git changes after synchronization.")

    return {
        "generatedAtUtc": now_utc().isoformat(),
        "tutorialUnit": "Enterprise Deployment Automation / Unit 5",
        "codeState": code_state,
        "workspace": {"id": workspace_id, "name": dev_workspace_name},
        "gitConnection": connection,
        "gitCredentials": credentials,
        "statusBefore": status_before,
        "statusGetLro": status_lro,
        "updateRequired": not already_synchronized,
        "updateRequest": update_request,
        "updateResponse": update_response_evidence,
        "updateLro": update_lro,
        "statusAfter": status_after,
        "synchronized": True,
        "dryRun": not execute,
    }


def extract_job_instance_id(location: str) -> str:
    require(isinstance(location, str) and bool(location.strip()), "Pipeline job response has no Location header.")
    parsed = urlparse(location)
    require(parsed.scheme == "https", f"Pipeline job Location is not HTTPS: {location}")
    segments = [segment for segment in parsed.path.split("/") if segment]
    try:
        instances_index = segments.index("instances")
    except ValueError as exc:
        raise ReleaseFailure(f"Pipeline job Location has no instances segment: {location}") from exc
    require(instances_index + 1 < len(segments), f"Pipeline job Location has no job instance ID: {location}")
    return uuid_text(segments[instances_index + 1], "pipeline job instance ID")


def run_test_pipeline(
    session: requests.Session,
    headers: dict[str, str],
    post_deploy_preflight: dict[str, Any],
    test_workspace_name: str,
    prod_workspace_name: str,
) -> dict[str, Any]:
    test_stage = get_stage(post_deploy_preflight, "Test", test_workspace_name)
    production_stage = get_stage(
        post_deploy_preflight,
        "Production",
        prod_workspace_name,
    )
    require(test_stage.get("id") != production_stage.get("id"), "TEST stage unexpectedly equals Production stage.")

    pipeline_item = single(
        test_stage.get("items"),
        lambda value: value.get("itemType") == "DataPipeline"
        and value.get("itemDisplayName") == TEST_PIPELINE_NAME,
        f"TEST DataPipeline named '{TEST_PIPELINE_NAME}'",
    )
    workspace_id = uuid_text(test_stage.get("workspaceId"), "Test.workspaceId")
    pipeline_id = uuid_text(pipeline_item.get("itemId"), "Test.pipeline.itemId")

    run_url = (
        f"{FABRIC_API_BASE}/workspaces/{workspace_id}/"
        f"dataPipelines/{pipeline_id}/jobs/execute/instances"
    )
    response = request_json(
        session,
        "POST",
        run_url,
        headers,
        allowed_statuses=(202,),
    )
    returned_location = response.headers.get("Location")
    job_instance_id = extract_job_instance_id(returned_location or "")
    canonical_job_url = (
        f"{FABRIC_API_BASE}/workspaces/{workspace_id}/items/{pipeline_id}/"
        f"jobs/instances/{job_instance_id}"
    )
    wait_seconds = retry_after(response.headers.get("Retry-After"), 30)
    deadline = now_utc() + timedelta(minutes=JOB_TIMEOUT_MINUTES)
    final_job: dict[str, Any] | None = None

    print(f"Pipeline job instance: {job_instance_id}")
    print(f"Service Location header recorded but not followed: {returned_location}")
    print(f"Polling canonical Fabric URL: {canonical_job_url}")

    while True:
        require(now_utc() <= deadline, "TEST pipeline job timed out.")
        time.sleep(wait_seconds)
        job_response = request_json(
            session,
            "GET",
            canonical_job_url,
            headers,
            allowed_statuses=(200,),
        )
        job = response_json(job_response, "TEST pipeline job instance")
        status = job.get("status")
        print(f"TEST pipeline status: {status}")

        if status == "Completed":
            final_job = job
            break
        if status in {"Failed", "Cancelled", "Deduped"}:
            raise ReleaseFailure(
                "TEST pipeline did not complete successfully: "
                + json.dumps(job, ensure_ascii=False)
            )

        wait_seconds = retry_after(job_response.headers.get("Retry-After"), wait_seconds)

    return {
        "generatedAtUtc": now_utc().isoformat(),
        "workspace": {"id": workspace_id, "name": test_workspace_name},
        "pipeline": {
            "id": pipeline_id,
            "name": TEST_PIPELINE_NAME,
            "jobType": "Execute",
        },
        "submission": {
            "httpStatusCode": response.status_code,
            "returnedLocationHeader": returned_location,
            "jobInstanceId": job_instance_id,
            "canonicalPollingUrl": canonical_job_url,
        },
        "jobInstance": final_job,
        "embeddedNotebookValidationExpected": True,
        "runtimeTableInspectionRequired": True,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Synchronize DEV, deploy the Notebook to TEST, and run the TEST pipeline."
    )
    parser.add_argument("--tenant-id", required=True)
    parser.add_argument("--expected-branch", default="dev")
    parser.add_argument("--release-label", default="U05_NONPROD_RELEASE_V1")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirmation")
    parser.add_argument("--artifacts-dir", default="artifacts")
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to participant-specific tutorial resource configuration.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        resources = load_tutorial_resources(args.config)
        code_state = validate_git_state(
            args.expected_branch,
            resources.repository_name,
        )
        artifacts_dir = Path(args.artifacts_dir)
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        bootstrap_preflight_path = artifacts_dir / "fabric-deployment-preflight-bootstrap.json"
        git_sync_path = artifacts_dir / "fabric-git-sync-dev.json"
        preflight_path = artifacts_dir / "fabric-deployment-preflight.json"
        deployment_path = artifacts_dir / "fabric-deployment-dev-to-test.json"
        post_deploy_preflight_path = artifacts_dir / "fabric-deployment-preflight-after-unit-5.json"
        runtime_path = artifacts_dir / "fabric-test-runtime-smoke.json"
        release_path = artifacts_dir / "fabric-nonprod-release.json"

        credential = AzureCliCredential(tenant_id=args.tenant_id)
        token = credential.get_token(FABRIC_SCOPE).token
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        session = requests.Session()

        bootstrap = run_preflight(
            args.tenant_id,
            resources.deployment_pipeline_name,
            bootstrap_preflight_path,
            "Bootstrap Fabric deployment topology preflight",
        )
        dev_stage = get_stage(
            bootstrap,
            "Development",
            resources.dev_workspace_name,
        )
        get_stage(bootstrap, "Test", resources.test_workspace_name)
        get_stage(bootstrap, "Production", resources.prod_workspace_name)
        dev_workspace_id = uuid_text(dev_stage.get("workspaceId"), "Development.workspaceId")

        sync_evidence = synchronize_dev_workspace(
            session,
            headers,
            dev_workspace_id,
            args.expected_branch,
            code_state,
            resources.dev_workspace_name,
            execute=False,
        )

        print("\nNon-production release plan")
        print("===========================")
        print(f"Git branch:    {code_state['branch']}")
        print(f"Git commit:    {code_state['headCommit']}")
        print(f"Release label: {args.release_label}")
        print(f"DEV workspace: {resources.dev_workspace_name}")
        print(f"Deployment:    Development -> Test")
        print(f"Item:          Notebook / nb_01_seed_and_transform_cicd_lab")
        print(f"Runtime:       TEST pipeline / {TEST_PIPELINE_NAME}")
        print("Production:    BLOCKED")

        if not args.execute:
            print("\nDRY RUN SUCCEEDED")
            if sync_evidence.get("updateRequired"):
                print("DEV requires a Git update. No write request was submitted.")
            else:
                print("DEV is already synchronized. No write request was submitted.")
            return 0

        confirmation = args.confirmation or input(
            f"Type {RELEASE_CONFIRMATION} to synchronize, deploy, and run TEST: "
        )
        require(
            confirmation == RELEASE_CONFIRMATION,
            "Release cancelled: confirmation did not match.",
        )

        # Synchronize again after confirmation. The dry planning call above may have
        # returned before performing the update.
        sync_evidence = synchronize_dev_workspace(
            session,
            headers,
            dev_workspace_id,
            args.expected_branch,
            code_state,
            resources.dev_workspace_name,
            execute=True,
        )
        git_sync_path.write_text(
            json.dumps(sync_evidence, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"DEV Git-sync evidence: {git_sync_path}")

        run_preflight(
            args.tenant_id,
            resources.deployment_pipeline_name,
            preflight_path,
            "Post-sync Fabric deployment topology preflight",
        )

        run_repository_command(
            [
                sys.executable,
                "scripts/fabric_deployment_pipeline_deploy.py",
                "--tenant-id",
                args.tenant_id,
                "--preflight",
                str(preflight_path),
                "--git-sync-evidence",
                str(git_sync_path),
                "--item-type",
                "Notebook",
                "--item-name",
                "nb_01_seed_and_transform_cicd_lab",
                "--expected-branch",
                args.expected_branch,
                "--note-prefix",
                f"tutorial unit 5 | {args.release_label}",
                "--output",
                str(deployment_path),
                "--execute",
                "--confirmation",
                "DEPLOY_DEV_TO_TEST",
            ],
            "Guarded DEV-to-TEST Notebook deployment",
        )

        post_deploy_preflight = run_preflight(
            args.tenant_id,
            resources.deployment_pipeline_name,
            post_deploy_preflight_path,
            "Post-deployment Fabric topology preflight",
        )

        runtime_evidence = run_test_pipeline(
            session,
            headers,
            post_deploy_preflight,
            resources.test_workspace_name,
            resources.prod_workspace_name,
        )
        runtime_path.write_text(
            json.dumps(runtime_evidence, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        deployment_evidence = load_json(deployment_path, "Deployment evidence")

        consolidated = {
            "generatedAtUtc": now_utc().isoformat(),
            "tutorialUnit": "Enterprise Deployment Automation / Unit 5",
            "releaseLabel": args.release_label,
            "resourceConfiguration": resources.evidence(),
            "codeState": code_state,
            "stateTransitions": {
                "codeToDevDeployment": "Verified",
                "devToTestDeployment": "Verified",
                "testRuntimeExecution": "Completed",
                "productionDeployment": "NotPerformed",
                "productionRuntime": "NotExecuted",
            },
            "gitSync": {
                "path": str(git_sync_path),
                "sha256": sha256_file(git_sync_path),
                "evidence": sync_evidence,
            },
            "deployment": {
                "path": str(deployment_path),
                "sha256": sha256_file(deployment_path),
                "deploymentId": deployment_evidence.get("response", {}).get("deploymentId"),
                "longRunningOperationId": deployment_evidence.get("response", {}).get("longRunningOperationId"),
            },
            "runtime": {
                "path": str(runtime_path),
                "sha256": sha256_file(runtime_path),
                "jobInstanceId": runtime_evidence["submission"]["jobInstanceId"],
                "status": runtime_evidence["jobInstance"]["status"],
            },
            "postDeploymentPreflight": {
                "path": str(post_deploy_preflight_path),
                "sha256": sha256_file(post_deploy_preflight_path),
            },
            "manualCompletionChecks": [
                "Verify the latest TEST cicd_run_audit row has the expected release label and environment TEST.",
                "Verify DEV has no audit row for this release label unless DEV was intentionally executed.",
                "Verify PROD has no audit row for this release label.",
                "Verify TEST Variable Library active value remains TEST.",
            ],
        }
        release_path.write_text(
            json.dumps(consolidated, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        print("\nNON-PRODUCTION RELEASE SUCCEEDED")
        print(f"Git commit:    {code_state['headCommit']}")
        print(f"Release label: {args.release_label}")
        print(f"Runtime job:   {runtime_evidence['submission']['jobInstanceId']}")
        print(f"Evidence:      {release_path}")
        print("Manual audit-table isolation checks remain required.")
        return 0

    except (CredentialUnavailableError, ClientAuthenticationError) as exc:
        print(f"RELEASE FAILED: Azure CLI authentication failed: {exc}", file=sys.stderr)
        return 1
    except requests.RequestException as exc:
        print(f"RELEASE FAILED: Fabric HTTP request failed: {exc}", file=sys.stderr)
        return 1
    except (ReleaseFailure, TutorialConfigError) as exc:
        print(f"RELEASE FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
