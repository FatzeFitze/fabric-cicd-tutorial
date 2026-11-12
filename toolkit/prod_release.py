"""Publish the exact Tiny Sales snapshot evidenced by a selected Test run."""

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

from toolkit.fabric_preflight import fabric_reader, fabric_token, read_environment_config
from toolkit.release_plan import PlanError, build_preview, commit_id, load_mask
from toolkit.test_release import checkout_pins, git, read_json, run_release, stage_items, write_json


def reviewed_revisions(test, run_id, code_revision):
    expected = {"environment": "test", "mode": "deploy", "status": "published",
                "phase": "complete", "active_value_set": "Test", "run_id": run_id}
    if any(test.get(key) != value for key, value in expected.items()):
        raise PlanError("Expected the selected completed Test publish artifact with the Test value set")
    revisions = test["verified_source_revisions"]
    if set(revisions) != {"code", "data", "reports"}:
        raise PlanError("Expected verified Code, Data and Reporting revisions in the Test artifact")
    revisions = {role: commit_id(revision, f"Test {role} revision") for role, revision in revisions.items()}
    if revisions["code"] != code_revision:
        raise PlanError("Test artifact Code revision differs from the selected Azure Pipelines run")
    return revisions


def release(args, evidence):
    from azure.identity import AzureCliCredential
    from fabric_cicd import FabricWorkspace, publish_all_items

    config = args.release / "config/environments/prod.yml"
    variables = load_mask(config)["variables"]
    if variables["approvedTestRunId"] != args.test_run_id:
        raise PlanError("The selected Test run differs from the reviewed Prod settings")
    test = read_json(args.test_manifest)
    revisions = reviewed_revisions(test, args.test_run_id, args.test_code_revision)
    evidence["selected_test_source_revisions"] = revisions
    evidence["release_definition_revision"] = git(args.release, "rev-parse", "HEAD")
    git(args.release, "merge-base", "--is-ancestor", revisions["code"], "HEAD")

    with TemporaryDirectory(prefix="tiny-sales-prod-") as directory:
        root = Path(directory)
        code = root / "code"
        git(args.release, "worktree", "add", "--detach", str(code), revisions["code"])
        try:
            plan = build_preview(load_mask(code / "config/tiny-sales-release.yml"), code, revisions["code"])
            if {role: source["revision"] for role, source in plan["sources"].items()} != revisions:
                raise PlanError("Pinned source from the reviewed mask differs from the Test artifact")
            if plan["sources"] != test["declared_sources"]:
                raise PlanError("Repository or folder declarations differ from the Test artifact")
            plan["items"]["validation"] = {"role": "code", "type": "Notebook", "name": "validate_release"}
            repos = {"code": code, "data": args.data, "reports": args.reports}
            checkout_pins(plan["sources"], repos)
            evidence["verified_source_revisions"] = revisions
            paths = stage_items(plan, repos, root / "staged")
            evidence["validation_logical_id"] = read_json(paths["validation"] / ".platform")["config"]["logicalId"]

            names, identity = read_environment_config(config, plan["targets"]["prod"]["workspaces"])
            evidence["configured_release_identity"] = identity
            credential = AzureCliCredential()

            def publish(workspace, folder, types, value_set):
                publish_all_items(FabricWorkspace(workspace_id=workspace, repository_directory=str(folder),
                                                  item_type_in_scope=types, environment=value_set,
                                                  token_credential=credential))

            run_release(plan, plan["targets"]["dev"]["workspaces"], paths, names, fabric_reader(fabric_token()),
                        publish, evidence, deploy=True, target="prod", first_creation=args.mode == "first")
        finally:
            git(args.release, "worktree", "remove", str(code))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("release", "data", "reports", "test-manifest", "evidence"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--test-run-id", required=True)
    parser.add_argument("--test-code-revision", required=True)
    parser.add_argument("--mode", choices=("first", "repeat"), default="first")
    args = parser.parse_args()
    evidence = {"environment": "prod", "run_id": os.getenv("BUILD_BUILDID"),
                "test_run_id": args.test_run_id, "mode": args.mode, "status": "failed",
                "phase": "preflight", "started_utc": datetime.now(timezone.utc).isoformat()}
    try:
        release(args, evidence)
        evidence.update(status="published", phase="complete")
        print("PROD RELEASE PUBLISHED. Review the Prod release evidence artifact.")
    except Exception as exc:
        evidence["error_type"] = type(exc).__name__
        print(f"PROD RELEASE FAILED during {evidence['phase']}: {exc}", file=sys.stderr)
        return 1
    finally:
        evidence["finished_utc"] = datetime.now(timezone.utc).isoformat()
        args.evidence.parent.mkdir(parents=True, exist_ok=True)
        write_json(args.evidence, evidence)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
