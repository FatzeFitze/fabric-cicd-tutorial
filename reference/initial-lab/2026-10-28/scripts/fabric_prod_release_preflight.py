#!/usr/bin/env python3
"""Validate that a TEST-validated candidate is eligible for PROD deployment.

This command performs no Fabric write and requires no Production credential.
It proves that:
- the current checkout is protected main;
- the selected Azure DevOps non-production run completed successfully;
- the selected run produced the supplied Fabric release-candidate manifest;
- the manifest represents a successful TEST deployment and runtime validation;
- the tested repository tree is byte-for-byte the same Git tree as current main;
- the participant-specific resource configuration still matches.

Commit SHA equality is deliberately not required because Azure Repos can create a
new merge/squash commit while preserving an identical repository tree.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fabric_nonprod_release import ReleaseFailure, validate_git_state
from tutorial_config import (
    DEFAULT_CONFIG_PATH,
    TutorialConfigError,
    load_tutorial_resources,
)

EXPECTED_CANDIDATE_PIPELINE = "fabric-cicd-lab-nonprod-release"
EXPECTED_CANDIDATE_BRANCH = "refs/heads/dev"
EXPECTED_CANDIDATE_STATUS = "TEST_VALIDATED_PENDING_CODE_APPROVAL"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReleaseFailure(message)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a TEST release candidate against protected main before "
            "Production credential use is permitted."
        )
    )
    parser.add_argument("--candidate-evidence", required=True)
    parser.add_argument("--candidate-run-metadata", required=True)
    parser.add_argument("--candidate-run-id", required=True)
    parser.add_argument("--expected-branch", default="main")
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to participant-specific tutorial resource configuration.",
    )
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def load_json(path: Path, description: str) -> dict[str, Any]:
    require(path.is_file(), f"{description} does not exist: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReleaseFailure(f"{description} is invalid JSON: {path}") from exc
    require(isinstance(value, dict), f"{description} root must be an object.")
    return value


def normalized_run_id(value: Any) -> str:
    text = str(value).strip() if value is not None else ""
    require(text.isdigit(), f"Candidate run ID must be numeric, got {value!r}.")
    return text


def require_string(value: Any, description: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{description} is missing.")
    return value.strip()


def main() -> int:
    arguments = parse_arguments()

    try:
        resources = load_tutorial_resources(arguments.config)
        code_state = validate_git_state(
            arguments.expected_branch,
            resources.repository_name,
        )

        candidate_path = Path(arguments.candidate_evidence)
        run_metadata_path = Path(arguments.candidate_run_metadata)

        candidate = load_json(candidate_path, "release-candidate evidence")
        run_metadata = load_json(run_metadata_path, "candidate run metadata")

        expected_run_id = normalized_run_id(arguments.candidate_run_id)
        actual_run_id = normalized_run_id(run_metadata.get("id"))
        require(
            actual_run_id == expected_run_id,
            (
                "Downloaded Azure DevOps run metadata does not match the "
                f"requested run ID: metadata={actual_run_id}, "
                f"requested={expected_run_id}."
            ),
        )

        definition = run_metadata.get("definition")
        require(isinstance(definition, dict), "Candidate run metadata has no definition.")
        require(
            definition.get("name") == EXPECTED_CANDIDATE_PIPELINE,
            (
                "Candidate run came from an unexpected pipeline: "
                f"{definition.get('name')!r}."
            ),
        )
        require(
            run_metadata.get("status") == "completed",
            "Candidate Azure DevOps run is not completed.",
        )
        require(
            run_metadata.get("result") == "succeeded",
            "Candidate Azure DevOps run did not succeed.",
        )
        require(
            run_metadata.get("sourceBranch") == EXPECTED_CANDIDATE_BRANCH,
            (
                "Candidate Azure DevOps run did not originate from protected dev. "
                f"Actual branch: {run_metadata.get('sourceBranch')!r}."
            ),
        )

        candidate_source_commit = require_string(
            run_metadata.get("sourceVersion"),
            "Candidate Azure DevOps sourceVersion",
        )

        require(
            candidate.get("evidenceType") == "FabricReleaseCandidate",
            "Unexpected release-candidate evidence type.",
        )
        require(
            candidate.get("status") == EXPECTED_CANDIDATE_STATUS,
            (
                "Release candidate is not in the expected TEST-validated state. "
                f"Actual status: {candidate.get('status')!r}."
            ),
        )

        candidate_id = require_string(
            candidate.get("releaseCandidateId"),
            "releaseCandidateId",
        )

        candidate_run = candidate.get("azureDevOpsRun")
        require(isinstance(candidate_run, dict), "Candidate has no azureDevOpsRun section.")
        require(
            normalized_run_id(candidate_run.get("buildId")) == expected_run_id,
            "Candidate manifest was not created by the selected Azure DevOps run.",
        )
        require(
            candidate_run.get("sourceBranch") == EXPECTED_CANDIDATE_BRANCH,
            "Candidate manifest source branch is not protected dev.",
        )
        require(
            candidate_run.get("sourceVersion") == candidate_source_commit,
            "Candidate manifest source commit differs from Azure DevOps run metadata.",
        )
        require(
            candidate_run.get("repository") == resources.repository_name,
            "Candidate manifest refers to a different Azure DevOps repository.",
        )

        tested_code = candidate.get("testedCodeState")
        require(isinstance(tested_code, dict), "Candidate has no testedCodeState section.")
        require(
            tested_code.get("branch") == "dev",
            "Candidate testedCodeState is not based on dev.",
        )
        require(
            tested_code.get("headCommit") == candidate_source_commit,
            "Candidate tested commit differs from the selected non-production run.",
        )

        tested_tree = require_string(
            tested_code.get("repositoryTreeHash"),
            "Candidate tested repositoryTreeHash",
        )
        main_tree = require_string(
            code_state.get("repositoryTreeHash"),
            "Current main repositoryTreeHash",
        )
        require(
            tested_tree == main_tree,
            (
                "Protected main does not contain the exact repository tree that "
                "passed TEST validation. "
                f"testedTree={tested_tree}, mainTree={main_tree}."
            ),
        )

        expected_configuration = resources.evidence()
        require(
            candidate.get("resourceConfiguration") == expected_configuration,
            (
                "Release candidate was created with different tutorial resource "
                "configuration."
            ),
        )

        test_runtime = candidate.get("testRuntime")
        require(isinstance(test_runtime, dict), "Candidate has no testRuntime section.")
        require(
            test_runtime.get("validationStatus") == "SUCCEEDED",
            "Candidate TEST runtime validation did not succeed.",
        )
        require(
            test_runtime.get("environmentName") == "TEST",
            "Candidate runtime evidence does not represent TEST.",
        )

        release_intent = candidate.get("releaseIntent")
        require(isinstance(release_intent, dict), "Candidate has no releaseIntent section.")
        require(
            release_intent.get("approvedCodeBranch") == "main",
            "Candidate release intent does not require main approval.",
        )
        require(
            release_intent.get("productionWorkspace") == resources.prod_workspace_name,
            "Candidate release intent targets a different Production workspace.",
        )
        require(
            release_intent.get("productionDeployment") == "NotPerformed",
            "Candidate already claims that Production deployment occurred.",
        )
        require(
            release_intent.get("productionRuntime") == "NotExecuted",
            "Candidate already claims that Production runtime occurred.",
        )

        evidence = {
            "evidenceSchemaVersion": 1,
            "evidenceType": "FabricProdReleasePlan",
            "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "status": "PROD_APPROVAL_PENDING",
            "codeState": code_state,
            "resourceConfiguration": expected_configuration,
            "selectedCandidateRun": {
                "runId": expected_run_id,
                "pipelineName": definition.get("name"),
                "buildNumber": run_metadata.get("buildNumber"),
                "sourceBranch": run_metadata.get("sourceBranch"),
                "sourceCommit": candidate_source_commit,
                "result": run_metadata.get("result"),
            },
            "releaseCandidate": {
                "releaseCandidateId": candidate_id,
                "testedCommit": tested_code.get("headCommit"),
                "testedRepositoryTreeHash": tested_tree,
                "testValidationRunId": test_runtime.get("validationRunId"),
                "testFabricPipelineRunId": test_runtime.get("fabricPipelineRunId"),
            },
            "productionCodeAuthority": {
                "branch": "main",
                "headCommit": code_state.get("headCommit"),
                "repositoryTreeHash": main_tree,
                "matchesTestedRepositoryTree": True,
            },
            "target": {
                "workspaceName": resources.prod_workspace_name,
                "deployment": "NotPerformed",
                "runtime": "NotExecuted",
            },
        }

        output_path = Path(arguments.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(evidence, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        print("PRODUCTION RELEASE PREFLIGHT SUCCEEDED")
        print(f"Candidate:        {candidate_id}")
        print(f"Candidate run:    {expected_run_id}")
        print(f"Tested dev:       {candidate_source_commit}")
        print(f"Main commit:      {code_state['headCommit']}")
        print(f"Repository tree:  {main_tree}")
        print(f"Target workspace: {resources.prod_workspace_name}")
        print("Production write: no")
        print(f"Evidence:         {output_path}")
        return 0

    except (ReleaseFailure, TutorialConfigError) as exc:
        print(f"PRODUCTION RELEASE PREFLIGHT FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
