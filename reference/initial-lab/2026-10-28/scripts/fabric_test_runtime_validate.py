#!/usr/bin/env python3
"""Execute and validate the Fabric TEST Data Pipeline.

The command runs the already deployed TEST Data Pipeline under the current
Azure CLI workload identity and creates non-secret release evidence.

Correlation chain:
Azure DevOps run
    -> checked-out dev commit
    -> Fabric job instance ID
    -> Fabric Data Factory pipelineRunId
    -> Notebook validation_run_id

The Notebook is expected to:
- receive environment_name from the TEST Variable Library;
- receive @pipeline().RunId as release_candidate_label;
- perform deterministic runtime assertions;
- append one cicd_run_audit row;
- return a JSON validation payload through notebookutils.notebook.exit().
"""

from __future__ import annotations

import argparse
import json
import os
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

from fabric_nonprod_release import (
    FABRIC_API_BASE,
    FABRIC_SCOPE,
    JOB_TIMEOUT_MINUTES,
    ReleaseFailure,
    now_utc,
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


TEST_PIPELINE_NAME = "pl_01_run_cicd_lab_transform"
NOTEBOOK_ACTIVITY_NAME = "act_run_seed_and_transform_notebook"

EXPECTED_RESULT = {
    "raw_row_count": 30,
    "curated_row_count": 30,
    "aggregate_row_count": 30,
    "total_quantity": 330,
    "total_sales_amount": 45905.0,
    "min_order_date": "2026-01-01",
    "max_order_date": "2026-01-10",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReleaseFailure(message)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Execute the TEST Data Pipeline and validate the "
            "Notebook exit evidence."
        )
    )
    parser.add_argument("--tenant-id", required=True)
    parser.add_argument("--expected-branch", default="dev")
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to participant-specific tutorial resource configuration.",
    )
    parser.add_argument(
        "--output",
        default="artifacts/fabric-test-runtime-validation.json",
    )
    return parser.parse_args()


def uuid_text(value: Any, description: str) -> str:
    try:
        return str(uuid.UUID(str(value)))
    except (ValueError, TypeError) as exc:
        raise ReleaseFailure(
            f"{description} is not a valid UUID: {value!r}."
        ) from exc


def extract_job_instance_id(location: str) -> str:
    require(bool(location.strip()), "Pipeline job response has no Location header.")

    parsed = urlparse(location)
    require(
        parsed.scheme == "https"
        and parsed.hostname == "api.fabric.microsoft.com",
        f"Unexpected pipeline job Location: {location}",
    )

    segments = [
        segment
        for segment in parsed.path.split("/")
        if segment
    ]

    try:
        instances_index = segments.index("instances")
    except ValueError as exc:
        raise ReleaseFailure(
            f"Pipeline job Location has no instances segment: {location}"
        ) from exc

    require(
        instances_index + 1 < len(segments),
        f"Pipeline job Location has no job instance ID: {location}",
    )

    return uuid_text(
        segments[instances_index + 1],
        "Fabric pipeline job instance ID",
    )


def azure_devops_context() -> dict[str, Any]:
    return {
        "buildId": os.getenv("BUILD_BUILDID") or None,
        "buildNumber": os.getenv("BUILD_BUILDNUMBER") or None,
        "sourceBranch": os.getenv("BUILD_SOURCEBRANCH") or None,
        "sourceVersion": os.getenv("BUILD_SOURCEVERSION") or None,
        "repository": os.getenv("BUILD_REPOSITORY_NAME") or None,
    }


def run_pipeline(
    session: requests.Session,
    headers: dict[str, str],
    workspace_id: str,
    pipeline_id: str,
) -> dict[str, Any]:
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

    returned_location = response.headers.get("Location") or ""
    job_instance_id = extract_job_instance_id(returned_location)

    canonical_job_url = (
        f"{FABRIC_API_BASE}/workspaces/{workspace_id}/"
        f"items/{pipeline_id}/jobs/instances/{job_instance_id}"
    )

    wait_seconds = retry_after(
        response.headers.get("Retry-After"),
        30,
    )
    deadline = now_utc() + timedelta(minutes=JOB_TIMEOUT_MINUTES)

    final_job: dict[str, Any] | None = None

    print(f"Fabric job instance ID: {job_instance_id}")
    print(f"Polling: {canonical_job_url}")

    while True:
        require(
            now_utc() <= deadline,
            "TEST pipeline job timed out.",
        )

        time.sleep(wait_seconds)

        job_response = request_json(
            session,
            "GET",
            canonical_job_url,
            headers,
            allowed_statuses=(200,),
        )

        job = response_json(
            job_response,
            "TEST pipeline job instance",
        )

        status = job.get("status")
        print(f"TEST pipeline status: {status}")

        if status == "Completed":
            final_job = job
            break

        if status in {
            "Failed",
            "Cancelled",
            "Deduped",
        }:
            raise ReleaseFailure(
                "TEST pipeline did not complete successfully: "
                + json.dumps(job, ensure_ascii=False)
            )

        wait_seconds = retry_after(
            job_response.headers.get("Retry-After"),
            wait_seconds,
        )

    require(
        final_job is not None,
        "TEST pipeline completed without final job evidence.",
    )

    return {
        "submission": {
            "httpStatusCode": response.status_code,
            "returnedLocationHeader": returned_location,
            "jobInstanceId": job_instance_id,
            "canonicalPollingUrl": canonical_job_url,
        },
        "jobInstance": final_job,
    }


def query_activity_runs(
    session: requests.Session,
    headers: dict[str, str],
    workspace_id: str,
    job_instance_id: str,
) -> list[dict[str, Any]]:
    query_url = (
        f"{FABRIC_API_BASE}/workspaces/{workspace_id}/"
        f"datapipelines/pipelineruns/{job_instance_id}/queryactivityruns"
    )

    # The endpoint is scoped to the pipeline job ID. The time bounds are
    # intentionally generous because activity details can become visible
    # shortly after the top-level job reaches Completed.
    request_body = {
        "filters": [],
        "orderBy": [
            {
                "orderBy": "ActivityRunStart",
                "order": "DESC",
            }
        ],
        "lastUpdatedAfter": (
            datetime.now(timezone.utc)
            - timedelta(hours=2)
        ).isoformat(),
        "lastUpdatedBefore": (
            datetime.now(timezone.utc)
            + timedelta(minutes=15)
        ).isoformat(),
    }

    last_payload: Any = None

    for attempt in range(1, 7):
        response = request_json(
            session,
            "POST",
            query_url,
            headers,
            body=request_body,
            allowed_statuses=(200,),
        )

        try:
            payload = response.json()
        except requests.JSONDecodeError as exc:
            raise ReleaseFailure(
                "Query activity runs returned invalid JSON."
            ) from exc

        last_payload = payload

        if isinstance(payload, dict):
            activity_values = payload.get("value")
        elif isinstance(payload, list):
            activity_values = payload
        else:
            activity_values = None

        if isinstance(activity_values, list) and activity_values:
            return [
                value
                for value in activity_values
                if isinstance(value, dict)
            ]

        if attempt < 6:
            print(
                "Activity-run evidence is not available yet; "
                "retrying in 5 seconds..."
            )
            time.sleep(5)

    raise ReleaseFailure(
        "No activity runs were returned for the completed TEST job. "
        f"Last payload: {last_payload!r}"
    )


def find_exit_values(value: Any) -> list[str]:
    found: list[str] = []

    if isinstance(value, dict):
        for key, child in value.items():
            if (
                isinstance(key, str)
                and key.lower() == "exitvalue"
                and isinstance(child, str)
            ):
                found.append(child)

            found.extend(
                find_exit_values(child)
            )

    elif isinstance(value, list):
        for child in value:
            found.extend(
                find_exit_values(child)
            )

    return found


def notebook_validation_from_activity(
    activity: dict[str, Any],
) -> dict[str, Any]:
    output = activity.get("output")

    exit_values = find_exit_values(output)

    require(
        len(exit_values) == 1,
        (
            "Expected exactly one Notebook exitValue in the "
            f"activity output; found {len(exit_values)}. "
            f"Output: {json.dumps(output, ensure_ascii=False)}"
        ),
    )

    try:
        validation = json.loads(exit_values[0])
    except json.JSONDecodeError as exc:
        raise ReleaseFailure(
            "Notebook exitValue is not valid JSON."
        ) from exc

    require(
        isinstance(validation, dict),
        "Notebook exitValue JSON root is not an object.",
    )

    return validation


def validate_runtime_result(
    activity: dict[str, Any],
    validation: dict[str, Any],
) -> dict[str, Any]:
    pipeline_run_id = uuid_text(
        activity.get("pipelineRunId"),
        "Fabric Data Factory pipelineRunId",
    )

    validation_run_id = uuid_text(
        validation.get("validation_run_id"),
        "Notebook validation_run_id",
    )

    release_candidate_label = uuid_text(
        validation.get("release_candidate_label"),
        "Notebook release_candidate_label",
    )

    require(
        release_candidate_label == pipeline_run_id,
        (
            "Notebook release_candidate_label does not match "
            "the Fabric Data Factory pipelineRunId."
        ),
    )

    require(
        validation.get("environment_name") == "TEST",
        (
            "Notebook runtime environment is "
            f"'{validation.get('environment_name')}', expected 'TEST'."
        ),
    )

    require(
        validation.get("validation_status") == "SUCCEEDED",
        (
            "Notebook validation status is not SUCCEEDED: "
            f"{validation.get('validation_status')!r}."
        ),
    )

    for key, expected in EXPECTED_RESULT.items():
        actual = validation.get(key)
        require(
            actual == expected,
            (
                f"Notebook runtime metric '{key}' is {actual!r}, "
                f"expected {expected!r}."
            ),
        )

    return {
        "pipelineRunId": pipeline_run_id,
        "validationRunId": validation_run_id,
        "releaseCandidateLabel": release_candidate_label,
        "environmentName": "TEST",
        "validationStatus": "SUCCEEDED",
        **EXPECTED_RESULT,
        "validatedAtUtc": validation.get("validated_at_utc"),
    }


def main() -> int:
    arguments = parse_arguments()

    try:
        resources = load_tutorial_resources(
            arguments.config
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
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

        with requests.Session() as session:
            workspace_response = request_json(
                session,
                "GET",
                f"{FABRIC_API_BASE}/workspaces",
                headers,
            )
            workspace_payload = response_json(
                workspace_response,
                "Fabric workspace list",
            )

            workspace = single(
                workspace_payload.get("value"),
                lambda value: (
                    value.get("displayName")
                    == resources.test_workspace_name
                ),
                (
                    "visible TEST workspace named "
                    f"'{resources.test_workspace_name}'"
                ),
            )

            workspace_id = uuid_text(
                workspace.get("id"),
                "TEST workspace ID",
            )

            items_response = request_json(
                session,
                "GET",
                (
                    f"{FABRIC_API_BASE}/workspaces/"
                    f"{workspace_id}/items"
                ),
                headers,
            )
            items_payload = response_json(
                items_response,
                "TEST item list",
            )

            pipeline = single(
                items_payload.get("value"),
                lambda value: (
                    value.get("type") == "DataPipeline"
                    and value.get("displayName")
                    == TEST_PIPELINE_NAME
                ),
                (
                    "TEST DataPipeline named "
                    f"'{TEST_PIPELINE_NAME}'"
                ),
            )

            pipeline_id = uuid_text(
                pipeline.get("id"),
                "TEST Data Pipeline item ID",
            )

            job = run_pipeline(
                session,
                headers,
                workspace_id,
                pipeline_id,
            )

            job_instance_id = (
                job["submission"]["jobInstanceId"]
            )

            activities = query_activity_runs(
                session,
                headers,
                workspace_id,
                job_instance_id,
            )

            notebook_activity = single(
                activities,
                lambda value: (
                    value.get("activityName")
                    == NOTEBOOK_ACTIVITY_NAME
                    and value.get("activityType")
                    == "TridentNotebook"
                ),
                (
                    "Notebook activity named "
                    f"'{NOTEBOOK_ACTIVITY_NAME}'"
                ),
            )

            require(
                notebook_activity.get("status")
                == "Succeeded",
                (
                    "Notebook activity did not succeed: "
                    f"{notebook_activity.get('status')!r}."
                ),
            )

            notebook_validation = (
                notebook_validation_from_activity(
                    notebook_activity
                )
            )

            validated = validate_runtime_result(
                notebook_activity,
                notebook_validation,
            )

            evidence = {
                "evidenceSchemaVersion": 1,
                "evidenceType": "FabricTestRuntimeValidation",
                "generatedAtUtc": now_utc().isoformat(),
                "azureDevOpsRun": (
                    azure_devops_context()
                ),
                "codeState": code_state,
                "resourceConfiguration": (
                    resources.evidence()
                ),
                "target": {
                    "workspaceName": (
                        resources.test_workspace_name
                    ),
                    "workspaceId": workspace_id,
                    "pipelineName": TEST_PIPELINE_NAME,
                    "pipelineItemId": pipeline_id,
                },
                "fabricJob": job,
                "notebookActivity": notebook_activity,
                "runtimeValidation": validated,
                "auditExpectation": {
                    "table": "cicd_run_audit",
                    "validationRunId": (
                        validated["validationRunId"]
                    ),
                    "releaseCandidateLabel": (
                        validated["releaseCandidateLabel"]
                    ),
                    "environmentName": "TEST",
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
            print("TEST RUNTIME VALIDATION SUCCEEDED")
            print(
                "Source commit:          "
                f"{code_state['headCommit']}"
            )
            print(
                "Fabric job instance ID: "
                f"{job_instance_id}"
            )
            print(
                "Fabric pipelineRunId:    "
                f"{validated['pipelineRunId']}"
            )
            print(
                "Notebook validation ID:  "
                f"{validated['validationRunId']}"
            )
            print(
                "Environment:             "
                f"{validated['environmentName']}"
            )
            print(
                "Evidence written to:     "
                f"{output_path}"
            )

        return 0

    except (
        CredentialUnavailableError,
        ClientAuthenticationError,
    ) as exc:
        print(
            "TEST RUNTIME VALIDATION FAILED: "
            f"authentication failed: {exc}",
            file=sys.stderr,
        )
        return 1

    except (
        requests.RequestException,
        ReleaseFailure,
        TutorialConfigError,
    ) as exc:
        print(
            f"TEST RUNTIME VALIDATION FAILED: {exc}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
