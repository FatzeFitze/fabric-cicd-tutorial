#!/usr/bin/env python3
"""Create an immutable TEST release-candidate manifest.

The manifest is created only after:
- protected dev was deployed to TEST;
- the TEST Data Pipeline completed;
- the Notebook returned deterministic validation evidence.

No Fabric API calls are performed here. The command validates the evidence
produced earlier in the same Azure DevOps run and binds it to the current
protected dev commit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fabric_nonprod_release import (
    ReleaseFailure,
    validate_git_state,
)
from tutorial_config import (
    DEFAULT_CONFIG_PATH,
    TutorialConfigError,
    load_tutorial_resources,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReleaseFailure(message)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create a TEST release-candidate manifest from "
            "deployment and runtime evidence."
        )
    )
    parser.add_argument("--deployment-evidence", required=True)
    parser.add_argument("--runtime-evidence", required=True)
    parser.add_argument("--expected-branch", default="dev")
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to participant-specific tutorial resource configuration.",
    )
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def load_json(
    path: Path,
    description: str,
) -> dict[str, Any]:
    require(
        path.is_file(),
        f"{description} does not exist: {path}",
    )

    try:
        value = json.loads(
            path.read_text(encoding="utf-8-sig")
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
        f"{description} root is not an object.",
    )

    return value


def sha256_file(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def ado_context() -> dict[str, Any]:
    return {
        "buildId": os.getenv("BUILD_BUILDID") or None,
        "buildNumber": os.getenv("BUILD_BUILDNUMBER") or None,
        "sourceBranch": os.getenv("BUILD_SOURCEBRANCH") or None,
        "sourceVersion": os.getenv("BUILD_SOURCEVERSION") or None,
        "repository": os.getenv("BUILD_REPOSITORY_NAME") or None,
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

        deployment_path = Path(
            arguments.deployment_evidence
        )
        runtime_path = Path(
            arguments.runtime_evidence
        )

        deployment = load_json(
            deployment_path,
            "TEST deployment evidence",
        )
        runtime = load_json(
            runtime_path,
            "TEST runtime evidence",
        )

        require(
            deployment.get("evidenceType")
            == "FabricTestDeployment",
            "Unexpected TEST deployment evidence type.",
        )
        require(
            runtime.get("evidenceType")
            == "FabricTestRuntimeValidation",
            "Unexpected TEST runtime evidence type.",
        )

        deployment_code = deployment.get("codeState")
        runtime_code = runtime.get("codeState")

        require(
            isinstance(deployment_code, dict),
            "TEST deployment evidence has no codeState.",
        )
        require(
            isinstance(runtime_code, dict),
            "TEST runtime evidence has no codeState.",
        )

        expected_commit = code_state["headCommit"]

        require(
            deployment_code.get("headCommit")
            == expected_commit,
            (
                "TEST deployment evidence was produced "
                "from a different commit."
            ),
        )
        require(
            runtime_code.get("headCommit")
            == expected_commit,
            (
                "TEST runtime evidence was produced "
                "from a different commit."
            ),
        )

        execution = deployment.get("execution")
        require(
            isinstance(execution, dict)
            and execution.get("executeRequested")
            is True,
            "TEST deployment evidence is not an execution run.",
        )

        target = deployment.get("target")
        require(
            isinstance(target, dict)
            and target.get("workspaceName")
            == resources.test_workspace_name,
            "Deployment evidence does not target TEST.",
        )

        runtime_target = runtime.get("target")
        require(
            isinstance(runtime_target, dict)
            and runtime_target.get("workspaceName")
            == resources.test_workspace_name,
            "Runtime evidence does not target the configured TEST workspace.",
        )

        expected_configuration = resources.evidence()
        require(
            deployment.get("resourceConfiguration")
            == expected_configuration,
            (
                "TEST deployment evidence was created with a different "
                "tutorial resource configuration."
            ),
        )
        require(
            runtime.get("resourceConfiguration")
            == expected_configuration,
            (
                "TEST runtime evidence was created with a different "
                "tutorial resource configuration."
            ),
        )

        deployment_state = deployment.get(
            "deploymentState"
        )
        require(
            isinstance(deployment_state, dict),
            "Deployment evidence has no deploymentState.",
        )
        require(
            deployment_state.get(
                "existingItemIdsStable"
            )
            is True,
            (
                "TEST deployment did not preserve "
                "the established item IDs."
            ),
        )

        validation = runtime.get(
            "runtimeValidation"
        )
        require(
            isinstance(validation, dict),
            "Runtime evidence has no runtimeValidation.",
        )
        require(
            validation.get("validationStatus")
            == "SUCCEEDED",
            "TEST runtime validation did not succeed.",
        )
        require(
            validation.get("environmentName")
            == "TEST",
            "TEST runtime evidence has wrong environment.",
        )

        validation_run_id = validation.get(
            "validationRunId"
        )
        pipeline_run_id = validation.get(
            "pipelineRunId"
        )

        require(
            isinstance(validation_run_id, str)
            and bool(validation_run_id),
            "Runtime validation ID is missing.",
        )
        require(
            isinstance(pipeline_run_id, str)
            and bool(pipeline_run_id),
            "Fabric pipelineRunId is missing.",
        )

        candidate_id = (
            "fabric-cicd-lab-"
            f"{expected_commit[:12]}-"
            f"{validation_run_id[:8]}"
        )

        manifest = {
            "schemaVersion": 1,
            "evidenceType": "FabricReleaseCandidate",
            "generatedAtUtc": (
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),
            "releaseCandidateId": candidate_id,
            "status": (
                "TEST_VALIDATED_PENDING_CODE_APPROVAL"
            ),
            "azureDevOpsRun": ado_context(),
            "testedCodeState": code_state,
            "resourceConfiguration": (
                expected_configuration
            ),
            "testDeployment": {
                "workspaceName": (
                    target.get("workspaceName")
                ),
                "workspaceId": (
                    target.get("workspaceId")
                ),
                "evidenceFile": str(
                    deployment_path
                ),
                "evidenceSha256": (
                    sha256_file(
                        deployment_path
                    )
                ),
                "deploymentEngine": (
                    deployment.get(
                        "deploymentEngine"
                    )
                ),
            },
            "testRuntime": {
                "evidenceFile": str(
                    runtime_path
                ),
                "evidenceSha256": (
                    sha256_file(
                        runtime_path
                    )
                ),
                "fabricJobInstanceId": (
                    runtime.get(
                        "fabricJob",
                        {},
                    )
                    .get(
                        "submission",
                        {},
                    )
                    .get("jobInstanceId")
                ),
                "fabricPipelineRunId": (
                    pipeline_run_id
                ),
                "validationRunId": (
                    validation_run_id
                ),
                "environmentName": "TEST",
                "validationStatus": (
                    "SUCCEEDED"
                ),
            },
            "releaseIntent": {
                "approvedCodeBranch": "main",
                "productionWorkspace": (
                    resources.prod_workspace_name
                ),
                "productionDeployment": (
                    "NotPerformed"
                ),
                "productionRuntime": (
                    "NotExecuted"
                ),
            },
        }

        output_path = Path(arguments.output)
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        output_path.write_text(
            json.dumps(
                manifest,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        print("RELEASE CANDIDATE CREATED")
        print(
            f"Candidate:        {candidate_id}"
        )
        print(
            f"Tested commit:    {expected_commit}"
        )
        print(
            f"Fabric run:       {pipeline_run_id}"
        )
        print(
            f"Validation run:   {validation_run_id}"
        )
        print(
            f"Status:           "
            "TEST_VALIDATED_PENDING_CODE_APPROVAL"
        )
        print(
            f"Output:           {output_path}"
        )

        return 0

    except (ReleaseFailure, TutorialConfigError) as exc:
        print(
            f"RELEASE CANDIDATE FAILED: {exc}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
