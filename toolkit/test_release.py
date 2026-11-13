"""Check the pinned Tiny Sales snapshot and optionally publish it to Test."""

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

from toolkit.fabric_preflight import fabric_reader, fabric_token, read_environment_config
from toolkit.release_plan import PlanError, build_preview, load_mask
from toolkit.tiny_sales_release import checkout_pins, fabric_publisher, run_release, stage_items, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--reports", type=Path, required=True)
    parser.add_argument("--checkout-revision", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--mode", choices=("preflight", "deploy"), default="preflight")
    parser.add_argument("--stop-before-reporting", action="store_true",
                        help="Rehearse a partial Test deployment after publishing Code")
    args = parser.parse_args()
    deploy = args.mode == "deploy"
    evidence = {"environment": "test", "run_id": os.getenv("BUILD_BUILDID"), "status": "failed",
                "mode": args.mode,
                "phase": "preflight", "started_utc": datetime.now(timezone.utc).isoformat()}
    try:
        if args.stop_before_reporting and not deploy:
            raise PlanError("The recovery rehearsal requires a Test publish run")
        mask = load_mask(args.code / "config/tiny-sales-release.yml")
        plan = build_preview(mask, args.code, args.checkout_revision)
        if "validation" in plan["items"]:
            raise PlanError("The Test publisher supplies the validation notebook for this exercise")
        plan["items"]["validation"] = {"role": "code", "type": "Notebook", "name": "validate_release"}
        evidence["declared_sources"] = plan["sources"]
        dev = plan["targets"]["dev"]["workspaces"]
        repos = {"code": args.code, "data": args.data, "reports": args.reports}
        checkout_pins(plan["sources"], repos)
        evidence["verified_source_revisions"] = {role: source["revision"] for role, source in plan["sources"].items()}
        names, identity = read_environment_config(args.code / "config/environments/test.yml", plan["targets"]["test"]["workspaces"])
        evidence["configured_release_identity"] = identity
        publish = fabric_publisher()

        with TemporaryDirectory(prefix="tiny-sales-test-") as directory:
            paths = stage_items(plan, repos, Path(directory))
            run_release(plan, dev, paths, names, fabric_reader(fabric_token()), publish, evidence,
                        deploy=deploy, target="test", stop_before_reporting=args.stop_before_reporting)
        evidence.update(status="published" if deploy else "preflight_passed", phase="complete")
        if deploy:
            print("TEST RELEASE PUBLISHED. Review the Test release evidence artifact.")
    except Exception as exc:
        evidence["error_type"] = type(exc).__name__
        print(f"TEST RELEASE FAILED during {evidence['phase']}: {exc}", file=sys.stderr)
        return 1
    finally:
        evidence["finished_utc"] = datetime.now(timezone.utc).isoformat()
        args.evidence.parent.mkdir(parents=True, exist_ok=True)
        write_json(args.evidence, evidence)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
