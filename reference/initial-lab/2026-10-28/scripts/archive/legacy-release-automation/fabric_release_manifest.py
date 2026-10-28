#!/usr/bin/env python3
"""Create a release-candidate manifest from a successful non-production release.

The manifest bridges the tested dev commit to a later main-branch production
release. It does not deploy anything and performs no network calls.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

FABRIC_DEFINITION_ROOTS = (
    "01_data_engineering",
    "02_orchestration",
    "99_admin",
)


class ManifestFailure(RuntimeError):
    """Raised when release-candidate evidence is incomplete or inconsistent."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ManifestFailure(message)


def git(*args: str, binary: bool = False) -> str | bytes:
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=not binary,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr if isinstance(result.stderr, str) else result.stderr.decode("utf-8", errors="replace")
        raise ManifestFailure(
            f"Git command failed: git {' '.join(args)}\n{stderr.strip()}"
        )
    return result.stdout


def load_json(path: Path, description: str) -> dict[str, Any]:
    require(path.is_file(), f"{description} does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ManifestFailure(f"{description} is invalid JSON: {path}") from exc
    require(isinstance(payload, dict), f"{description} root must be an object.")
    return payload


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def validate_git_state(expected_branch: str) -> dict[str, Any]:
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


def validate_nonprod_evidence(
    evidence: dict[str, Any],
    *,
    release_label: str,
    expected_commit: str,
) -> dict[str, Any]:
    require(evidence.get("releaseLabel") == release_label, "Non-production evidence has a different release label.")

    code_state = evidence.get("codeState")
    require(isinstance(code_state, dict), "Non-production evidence has no codeState object.")
    require(code_state.get("branch") == "dev", "Non-production evidence was not created from branch dev.")
    require(code_state.get("headCommit") == expected_commit, "Non-production evidence commit differs from current dev HEAD.")
    require(code_state.get("remoteCommit") == expected_commit, "Non-production evidence remote commit differs from current dev HEAD.")
    require(code_state.get("workingTreeClean") is True, "Non-production evidence does not confirm a clean working tree.")

    transitions = evidence.get("stateTransitions")
    require(isinstance(transitions, dict), "Non-production evidence has no stateTransitions object.")
    require(transitions.get("codeToDevDeployment") == "Verified", "DEV Git synchronization was not verified.")
    require(transitions.get("devToTestDeployment") == "Verified", "DEV-to-TEST deployment was not verified.")
    require(transitions.get("testRuntimeExecution") == "Completed", "TEST runtime execution was not completed.")
    require(transitions.get("productionDeployment") == "NotPerformed", "Production was already deployed during the non-production release.")

    runtime = evidence.get("runtime")
    require(isinstance(runtime, dict), "Non-production evidence has no runtime object.")
    require(runtime.get("status") == "Completed", "TEST runtime job did not complete successfully.")
    runtime_job_id = runtime.get("jobInstanceId")
    try:
        runtime_job_id = str(uuid.UUID(str(runtime_job_id)))
    except ValueError as exc:
        raise ManifestFailure("TEST runtime job instance ID is invalid.") from exc

    deployment = evidence.get("deployment")
    require(isinstance(deployment, dict), "Non-production evidence has no deployment object.")
    deployment_id = deployment.get("deploymentId")
    try:
        deployment_id = str(uuid.UUID(str(deployment_id)))
    except ValueError as exc:
        raise ManifestFailure("DEV-to-TEST deployment ID is invalid.") from exc

    git_sync = evidence.get("gitSync")
    require(isinstance(git_sync, dict), "Non-production evidence has no gitSync object.")
    sync_evidence = git_sync.get("evidence")
    require(isinstance(sync_evidence, dict), "Non-production evidence has no embedded Git-sync evidence.")
    status_after = sync_evidence.get("statusAfter")
    require(isinstance(status_after, dict), "Git-sync evidence has no statusAfter object.")
    require(status_after.get("workspaceHead") == expected_commit, "DEV workspaceHead differs from the tested commit.")
    require(status_after.get("remoteCommitHash") == expected_commit, "Fabric remoteCommitHash differs from the tested commit.")
    require(status_after.get("changes") == [], "DEV workspace was not clean after Git synchronization.")
    require(sync_evidence.get("synchronized") is True, "DEV synchronization was not confirmed.")

    return {
        "testRuntimeJobInstanceId": runtime_job_id,
        "devToTestDeploymentId": deployment_id,
        "devToTestLongRunningOperationId": deployment.get("longRunningOperationId"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a release-candidate manifest from successful TEST evidence."
    )
    parser.add_argument("--release-label", required=True)
    parser.add_argument("--nonprod-evidence", required=True)
    parser.add_argument("--test-validation-run-id", required=True)
    parser.add_argument("--test-validation-note", required=True)
    parser.add_argument("--expected-branch", default="dev")
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        test_validation_run_id = str(uuid.UUID(args.test_validation_run_id))
        code_state = validate_git_state(args.expected_branch)
        evidence_path = Path(args.nonprod_evidence)
        nonprod = load_json(evidence_path, "Non-production release evidence")
        evidence_summary = validate_nonprod_evidence(
            nonprod,
            release_label=args.release_label,
            expected_commit=code_state["headCommit"],
        )

        manifest = {
            "schemaVersion": 1,
            "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "tutorialUnit": "Enterprise Deployment Automation / Unit 6",
            "releaseLabel": args.release_label,
            "testedCodeState": code_state,
            "testEvidence": {
                "nonProductionReleasePath": str(evidence_path),
                "nonProductionReleaseSha256": sha256_file(evidence_path),
                **evidence_summary,
                "testValidationRunId": test_validation_run_id,
                "testValidationEnvironment": "TEST",
                "testValidationStatus": "SUCCEEDED",
                "testValidationNote": args.test_validation_note,
            },
            "releaseIntent": {
                "sourceStage": "Test",
                "targetStage": "Production",
                "itemType": "Notebook",
                "itemName": "nb_01_seed_and_transform_cicd_lab",
                "productionRuntimePipeline": "pl_01_run_cicd_lab_transform",
            },
            "approvalBoundary": {
                "codeApproval": "Azure DevOps pull request from dev to main with branch policies",
                "productionExecutionApproval": "Explicit local confirmation in fabric_prod_release.py",
                "independentSeparationOfDutiesVerified": False,
            },
        }

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        print("RELEASE-CANDIDATE MANIFEST CREATED")
        print(f"Release label:       {args.release_label}")
        print(f"Tested dev commit:   {code_state['headCommit']}")
        print(f"Repository tree:     {code_state['repositoryTreeHash']}")
        print(f"Fabric definitions:  {code_state['fabricDefinitionsSha256']}")
        print(f"TEST validation run: {test_validation_run_id}")
        print(f"Output:              {output_path}")
        return 0

    except ManifestFailure as exc:
        print(f"MANIFEST FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
