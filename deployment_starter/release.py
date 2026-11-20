"""Validate or publish the versioned Fabric release starter."""

import argparse
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import importlib.util
import os
from pathlib import Path, PurePosixPath
import re
import sys
from tempfile import TemporaryDirectory

from toolkit.fabric_preflight import fabric_reader, fabric_token, read_environment_config
from toolkit.release_plan import PlanError, build_preview, commit_id, load_mask
from toolkit.tiny_sales_release import (
    ITEM_TYPES, checkout_pins, fabric_publisher, git, read_bindings, read_json,
    run_release, stage_items, write_json,
)


# Each phase corresponds to the publisher's supported Fabric binding order.
PHASES = {"Lakehouse": 0, "VariableLibrary": 1, "Notebook": 1,
          "DataPipeline": 2, "SemanticModel": 3, "Report": 4}
# Required edges for the starter's baseline item keys. Additional reports
# reuse the existing model and take the default edge in validate_contract.
BINDINGS = {
    "lakehouse": {}, "library": {},
    "notebook": {"default_lakehouse": "lakehouse"},
    "validation": {"default_lakehouse": "lakehouse"},
    "pipeline": {"notebook": "notebook", "variables": "library"},
    "model": {"sql_analytics_endpoint_of": "lakehouse"},
}


def source_file(repo, relative):
    # Keep masks, environment settings and project checks inside reviewed Git source.
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or "\\" in relative or ":" in relative:
        raise PlanError(f"{relative}: expected a file relative to the Code checkout")
    file = repo / path
    if not file.is_file() or file.is_symlink() or not file.resolve().is_relative_to(repo.resolve()):
        raise PlanError(f"{relative}: expected a regular file inside the Code checkout")
    git(repo, "ls-files", "--error-unmatch", "--", path.as_posix())
    return file


def validate_contract(plan):
    if set(plan["sources"]) != {"code", "data", "reports"} or plan["sources"]["code"].get("source") != "checkout":
        raise PlanError("Expected Code checkout and pinned Data and Reporting repositories")
    if set(plan["targets"]) != {"dev", "test", "prod"}:
        raise PlanError("Expected Dev, Test and Prod in the release mask")
    if set(plan["project_checks"]) != {"static"}:
        raise PlanError("Declare one project_checks.static module")
    for key, pair in ITEM_TYPES.items():
        item = plan["items"].get(key)
        if not item or (item["role"], item["type"]) != pair:
            raise PlanError(f"{key}: expected {pair[1]} in the {pair[0]} role")
    for key, item in plan["items"].items():
        if key not in ITEM_TYPES and (item["role"], item["type"]) != ("reports", "Report"):
            raise PlanError(f"{key}: the starter supports extending the graph with Reporting reports")
        bindings = BINDINGS.get(key, {"semantic_model": "model"})
        if item["bindings"] != bindings:
            raise PlanError(f"{key}: expected bindings {bindings}, found {item['bindings']}")
        for dependency in item["after"]:
            if PHASES[plan["items"][dependency]["type"]] >= PHASES[item["type"]]:
                raise PlanError(f"{key}: after may only name an item from an earlier publish phase")


def starter_version(repo):
    # Git object IDs bind the release to the reviewed implementation. The
    # starter tree covers YAML, Python and documentation in this directory.
    paths = ("deployment_starter", "toolkit/release_plan.py", "toolkit/fabric_preflight.py",
             "toolkit/tiny_sales_release.py", "toolkit/requirements-planning.txt",
             "toolkit/requirements-release.txt")
    return {path: git(repo, "rev-parse", f"HEAD:{path}") for path in paths}


def prepare(args, code, revision, staged_root):
    # Both commands resolve the mask, verify the pins and inspect copies of
    # the tracked exports before they can validate or publish.
    mask = load_mask(source_file(code, args.mask))
    plan = build_preview(mask, code, revision)
    validate_contract(plan)
    repos = {"code": code, "data": args.data, "reports": args.reports}
    checkout_pins(plan["sources"], repos)
    staged = stage_items(plan, repos, staged_root, allow_additional_reports=True)
    read_bindings(staged, plan, plan["targets"]["dev"]["workspaces"], args.target)
    snapshot = {
        "mask": args.mask,
        "starter_version": starter_version(code),
        "declared_sources": plan["sources"],
        "verified_source_revisions": {role: source["revision"] for role, source in plan["sources"].items()},
    }
    return repos, plan, staged, snapshot


def run_project_check(repos, plan):
    module = plan["project_checks"]["static"]
    if not re.fullmatch(r"checks\.[A-Za-z_]\w*", module):
        raise PlanError("project_checks.static must name a module directly under checks/")
    path = source_file(repos["code"], module.replace(".", "/") + ".py")
    spec = importlib.util.spec_from_file_location(module, path)
    if spec is None or spec.loader is None:
        raise PlanError(f"Could not load {module}")
    check = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(check)
    run = getattr(check, "run", None)
    if not callable(run):
        raise PlanError(f"{module} must define run(repositories, plan)")
    # Let the project inspect the source paths and a copy of the resolved plan.
    run(dict(repos), deepcopy(plan))


def validate(args, evidence, root):
    repos, plan, _, snapshot = prepare(args, args.code, args.checkout_revision, root)
    evidence.update(snapshot)
    evidence.update(plan=plan, phase="project static check", static_check=plan["project_checks"]["static"])
    run_project_check(repos, plan)
    checkout_pins(plan["sources"], repos)
    # The check passed and the candidate still matches the tracked source.
    evidence.update(status="validated", phase="complete")
    print(f"STATIC CHECK PASSED: {evidence['static_check']}")


@contextmanager
def source_candidate(args, root):
    if args.target == "test":
        yield args.code, args.checkout_revision, read_json(args.validation)
        return
    tested = read_json(args.test_manifest)
    selected_revision = commit_id(args.test_code_revision, "selected Test Code revision")
    expected = {"environment": "test", "mode": "deploy", "status": "published",
                "phase": "complete", "run_id": args.test_run_id}
    if (any(tested.get(key) != value for key, value in expected.items())
            or tested.get("verified_source_revisions", {}).get("code") != selected_revision):
        raise PlanError("Expected the selected completed Test deployment and its Code revision")
    variables = load_mask(source_file(args.code, args.environment_file))["variables"]
    if variables["approvedTestRunId"] != args.test_run_id:
        raise PlanError("Selected Test run differs from the reviewed Prod settings")
    git(args.code, "merge-base", "--is-ancestor", selected_revision, args.checkout_revision)
    # Keep Prod settings on the running checkout. Read the workload mask and
    # exports from the exact Test commit in a separate temporary worktree.
    code = root / "candidate"
    git(args.code, "worktree", "add", "--detach", str(code), selected_revision)
    try:
        yield code, selected_revision, tested
    finally:
        git(args.code, "worktree", "remove", "--force", str(code))


def publish(args, evidence, root):
    if (git(args.code, "rev-parse", "HEAD") != args.checkout_revision
            or git(args.code, "status", "--porcelain", "--untracked-files=no")):
        raise PlanError("Expected the running release revision and a clean Code checkout")
    with source_candidate(args, root) as (code, revision, prior):
        _, plan, staged, snapshot = prepare(args, code, revision, root / "staged")
        expected = {"environment": "test", "phase": "complete",
                    "static_check": plan["project_checks"]["static"], **snapshot}
        if args.target == "test":
            expected.update(status="validated", run_id=evidence["run_id"])
            validation_run = prior.get("run_id")
        else:
            expected.update(status="published", validation_run_id=args.test_run_id,
                            active_value_set=plan["targets"]["test"]["variable_library"]["desired_value_set"])
            validation_run = args.test_run_id
            evidence["test_run_id"] = args.test_run_id
        # Compare the prepared sources and validation result with the evidence
        # from Test, then verify the running publisher's version.
        if any(prior.get(key) != value for key, value in expected.items()):
            raise PlanError("Candidate source, starter version or validation evidence does not match")
        if starter_version(args.code) != snapshot["starter_version"]:
            raise PlanError("Release starter differs from the version validated in Test")
        names, identity = read_environment_config(
            source_file(args.code, args.environment_file), plan["targets"][args.target]["workspaces"])
        evidence.update(snapshot)
        evidence.update(validation_run_id=validation_run,
                        static_check=prior["static_check"], configured_release_identity=identity,
                        release_definition_revision=args.checkout_revision)
        # The Fabric calls use the signed-in CLI session. Preflight mode still
        # reads the workspace names and item IDs before returning.
        evidence["phase"] = "live preflight"
        run_release(plan, plan["targets"]["dev"]["workspaces"], staged, names,
                    fabric_reader(fabric_token()), fabric_publisher(), evidence,
                    deploy=args.mode == "deploy", target=args.target)
    evidence.update(status="published" if args.mode == "deploy" else "preflight_passed", phase="complete")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("validate", "publish"))
    for name in ("code", "data", "reports", "evidence"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--checkout-revision", required=True)
    parser.add_argument("--mask", required=True)
    parser.add_argument("--target", choices=("test", "prod"), default="test")
    parser.add_argument("--mode", choices=("preflight", "deploy"), default="preflight")
    parser.add_argument("--environment-file")
    parser.add_argument("--validation", type=Path)
    parser.add_argument("--test-manifest", type=Path)
    parser.add_argument("--test-run-id")
    parser.add_argument("--test-code-revision")
    args = parser.parse_args()
    if args.action == "validate" and args.target != "test":
        parser.error("Validate the Test candidate before Prod")
    if args.action == "publish":
        if not args.environment_file:
            parser.error("Publishing requires --environment-file")
        if args.target == "test" and not args.validation:
            parser.error("Test requires --validation from this run")
        if args.target == "prod" and not (args.test_manifest and args.test_run_id and args.test_code_revision):
            parser.error("Prod requires the selected Test manifest, run ID and Code revision")
    evidence = {"environment": args.target, "mode": args.mode, "status": "failed",
                "phase": "prepare candidate", "run_id": os.getenv("BUILD_BUILDID"),
                "started_utc": datetime.now(timezone.utc).isoformat()}
    try:
        with TemporaryDirectory(prefix="fabric-release-") as directory:
            (validate if args.action == "validate" else publish)(args, evidence, Path(directory))
        print(f"{args.target.upper()} {evidence['status'].upper()}")
    except Exception as exc:
        evidence["error_type"] = type(exc).__name__
        if evidence["phase"] == "project static check":
            evidence["diagnostic"] = str(exc)
        print(f"FAILED during {evidence['phase']}: {exc}", file=sys.stderr)
        return 1
    finally:
        # Preserve the phase and diagnostic even when a started command fails.
        evidence["finished_utc"] = datetime.now(timezone.utc).isoformat()
        args.evidence.parent.mkdir(parents=True, exist_ok=True)
        write_json(args.evidence, evidence)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
