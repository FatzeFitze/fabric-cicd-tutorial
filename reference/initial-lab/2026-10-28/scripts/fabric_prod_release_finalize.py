#!/usr/bin/env python3
"""Create final Section 3 Production release evidence.

This command performs no Fabric writes. It closes the evidence chain only after
Production deployment and runtime validation have both succeeded for the same
approved repository tree and release candidate.
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

from tutorial_config import (
    DEFAULT_CONFIG_PATH,
    TutorialConfigError,
    load_tutorial_resources,
)


class FinalizationFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FinalizationFailure(message)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create final Production release evidence after PROD runtime validation."
    )
    parser.add_argument("--candidate-evidence", required=True)
    parser.add_argument("--release-plan", required=True)
    parser.add_argument("--deployment-evidence", required=True)
    parser.add_argument("--runtime-evidence", required=True)
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to participant-specific tutorial resource configuration.",
    )
    parser.add_argument(
        "--output",
        default="artifacts/fabric-prod-release.json",
    )
    return parser.parse_args()


def load_json(path: Path, description: str) -> dict[str, Any]:
    require(path.is_file(), f"Missing {description}: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FinalizationFailure(f"Invalid {description}: {path}") from exc
    require(isinstance(payload, dict), f"{description} root is not an object.")
    return payload


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def azure_devops_context() -> dict[str, Any]:
    return {
        "buildId": os.getenv("BUILD_BUILDID") or None,
        "buildNumber": os.getenv("BUILD_BUILDNUMBER") or None,
        "definitionId": os.getenv("SYSTEM_DEFINITIONID") or None,
        "sourceBranch": os.getenv("BUILD_SOURCEBRANCH") or None,
        "sourceVersion": os.getenv("BUILD_SOURCEVERSION") or None,
        "repository": os.getenv("BUILD_REPOSITORY_NAME") or None,
    }


def main() -> int:
    arguments = parse_arguments()

    try:
        resources = load_tutorial_resources(arguments.config)
        expected_configuration = resources.evidence()

        candidate_path = Path(arguments.candidate_evidence)
        release_plan_path = Path(arguments.release_plan)
        deployment_path = Path(arguments.deployment_evidence)
        runtime_path = Path(arguments.runtime_evidence)

        candidate = load_json(candidate_path, "release-candidate evidence")
        release_plan = load_json(release_plan_path, "Production release plan")
        deployment = load_json(deployment_path, "Production deployment evidence")
        runtime = load_json(runtime_path, "Production runtime evidence")

        require(
            candidate.get("evidenceType") == "FabricReleaseCandidate",
            "Candidate evidence is not FabricReleaseCandidate.",
        )
        require(
            candidate.get("status") == "TEST_VALIDATED_PENDING_CODE_APPROVAL",
            "Candidate is not TEST_VALIDATED_PENDING_CODE_APPROVAL.",
        )
        require(
            release_plan.get("evidenceType") == "FabricProdReleasePlan",
            "Release plan is not FabricProdReleasePlan.",
        )
        require(
            deployment.get("evidenceType") == "FabricProdDeployment",
            "Deployment evidence is not FabricProdDeployment.",
        )
        require(
            deployment.get("status") == "PROD_DEPLOYED_RUNTIME_PENDING",
            "Production deployment does not await runtime validation.",
        )
        require(
            runtime.get("evidenceType") == "FabricProdRuntimeValidation",
            "Runtime evidence is not FabricProdRuntimeValidation.",
        )

        for description, payload in (
            ("candidate", candidate),
            ("release plan", release_plan),
            ("deployment", deployment),
            ("runtime", runtime),
        ):
            require(
                payload.get("resourceConfiguration") == expected_configuration,
                f"{description} resource configuration differs from current configuration.",
            )

        candidate_id = candidate.get("releaseCandidateId")
        require(
            isinstance(candidate_id, str) and bool(candidate_id),
            "Release candidate ID is missing.",
        )

        planned_candidate = release_plan.get("releaseCandidate")
        require(isinstance(planned_candidate, dict), "Release plan has no releaseCandidate.")
        require(
            planned_candidate.get("releaseCandidateId") == candidate_id,
            "Release plan refers to a different release candidate.",
        )

        deployment_candidate = deployment.get("releaseCandidate")
        require(
            isinstance(deployment_candidate, dict),
            "Deployment evidence has no releaseCandidate.",
        )
        require(
            deployment_candidate.get("releaseCandidateId") == candidate_id,
            "Deployment used a different release candidate.",
        )

        runtime_correlation = runtime.get("releaseCorrelation")
        require(
            isinstance(runtime_correlation, dict),
            "Runtime evidence has no releaseCorrelation.",
        )
        require(
            runtime_correlation.get("releaseCandidateId") == candidate_id,
            "Runtime validation belongs to a different release candidate.",
        )

        tested_code = candidate.get("testedCodeState")
        authority = release_plan.get("productionCodeAuthority")
        deployment_code = deployment.get("codeState")
        runtime_code = runtime.get("codeState")
        require(isinstance(tested_code, dict), "Candidate has no testedCodeState.")
        require(isinstance(authority, dict), "Release plan has no productionCodeAuthority.")
        require(isinstance(deployment_code, dict), "Deployment has no codeState.")
        require(isinstance(runtime_code, dict), "Runtime evidence has no codeState.")

        expected_tree = tested_code.get("repositoryTreeHash")
        require(isinstance(expected_tree, str) and bool(expected_tree), "Tested tree hash is missing.")
        require(authority.get("repositoryTreeHash") == expected_tree, "Approved main tree differs from TEST tree.")
        require(deployment_code.get("repositoryTreeHash") == expected_tree, "Deployed PROD tree differs from TEST tree.")
        require(runtime_code.get("repositoryTreeHash") == expected_tree, "Validated PROD tree differs from TEST tree.")

        deployment_target = deployment.get("target")
        runtime_target = runtime.get("target")
        require(isinstance(deployment_target, dict), "Deployment has no target.")
        require(isinstance(runtime_target, dict), "Runtime evidence has no target.")
        require(
            deployment_target.get("workspaceName") == resources.prod_workspace_name,
            "Deployment target is not configured PROD.",
        )
        require(
            runtime_target.get("workspaceName") == resources.prod_workspace_name,
            "Runtime target is not configured PROD.",
        )

        validation = runtime.get("runtimeValidation")
        require(isinstance(validation, dict), "Runtime evidence has no runtimeValidation.")
        require(validation.get("validationStatus") == "SUCCEEDED", "PROD runtime validation did not succeed.")
        require(validation.get("environmentName") == "PROD", "Runtime validation environment is not PROD.")

        deployment_state = deployment.get("deploymentState")
        require(isinstance(deployment_state, dict), "Deployment has no deploymentState.")
        require(
            deployment_state.get("existingItemIdsStable") is True,
            "Production deployment did not preserve established item IDs.",
        )

        manifest = {
            "evidenceSchemaVersion": 1,
            "evidenceType": "FabricProdReleaseEvidence",
            "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "status": "PROD_RUNTIME_VALIDATED",
            "azureDevOpsRun": azure_devops_context(),
            "releaseCandidateId": candidate_id,
            "resourceConfiguration": expected_configuration,
            "codeCorrelation": {
                "testedDevCommit": tested_code.get("headCommit"),
                "approvedMainCommit": authority.get("headCommit"),
                "repositoryTreeHash": expected_tree,
                "treeEqualityProven": True,
            },
            "testEvidence": {
                "candidateRun": release_plan.get("selectedCandidateRun"),
                "testRuntime": candidate.get("testRuntime"),
            },
            "productionDeployment": {
                "workspaceName": deployment_target.get("workspaceName"),
                "workspaceId": deployment_target.get("workspaceId"),
                "existingItemIdsStable": True,
                "fabricCicdEnvironment": deployment_target.get("fabricCicdEnvironment"),
                "evidenceSha256": sha256_file(deployment_path),
            },
            "productionRuntime": {
                "fabricJobInstanceId": runtime.get("fabricJob", {}).get("submission", {}).get("jobInstanceId"),
                "fabricPipelineRunId": validation.get("pipelineRunId"),
                "validationRunId": validation.get("validationRunId"),
                "environmentName": validation.get("environmentName"),
                "validationStatus": validation.get("validationStatus"),
                "evidenceSha256": sha256_file(runtime_path),
            },
            "evidenceFiles": {
                "releaseCandidate": str(candidate_path),
                "releasePlan": str(release_plan_path),
                "productionDeployment": str(deployment_path),
                "productionRuntime": str(runtime_path),
            },
        }

        output_path = Path(arguments.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        print("PRODUCTION RELEASE EVIDENCE FINALIZED")
        print(f"Candidate:       {candidate_id}")
        print(f"Repository tree: {expected_tree}")
        print(f"PROD run:        {validation.get('pipelineRunId')}")
        print("Status:          PROD_RUNTIME_VALIDATED")
        print(f"Output:          {output_path}")
        return 0

    except (FinalizationFailure, TutorialConfigError) as exc:
        print(f"PRODUCTION RELEASE FINALIZATION FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
