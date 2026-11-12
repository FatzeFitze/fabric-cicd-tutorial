"""Publish the pinned Tiny Sales snapshot to the three verified Test workspaces."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
from shutil import copyfile
import subprocess
import sys
from tempfile import TemporaryDirectory
from urllib.parse import unquote, urlsplit

from toolkit.fabric_preflight import fabric_reader, fabric_token, guid, inspect_target, list_workspace_items
from toolkit.fabric_preflight import read_environment_config, verify_expected_items
from toolkit.release_plan import PlanError, build_preview, load_mask


ITEM_TYPES = {
    "lakehouse": ("data", "Lakehouse"),
    "library": ("code", "VariableLibrary"),
    "notebook": ("code", "Notebook"),
    "validation": ("code", "Notebook"),
    "pipeline": ("code", "DataPipeline"),
    "model": ("reports", "SemanticModel"),
    "report": ("reports", "Report"),
}
NOTEBOOK_META = re.compile(r"(?:^# META .*\n)+", re.MULTILINE)
SQL_SOURCE = re.compile(r'Sql\.Database\("([^"\r\n]+)",\s*"([0-9a-fA-F-]{36})"\)')


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True, timeout=60).strip()


def checkout_pins(sources, repos):
    for role, source in sources.items():
        repo = repos[role].resolve()
        if Path(git(repo, "rev-parse", "--show-toplevel")).resolve() != repo:
            raise PlanError(f"{role}: expected a separate checkout")
        revision = source["revision"]
        if "repository" in source:
            # Azure Pipelines fetches the authorized dev branch and its history.
            repository = unquote(urlsplit(git(repo, "remote", "get-url", "origin")).path)
            project, _, name = repository.rpartition("/_git/")
            qualified = f"{project.rsplit('/', 1)[-1]}/{name}"
            if source["repository"] not in (name, qualified) or not name:
                raise PlanError(f"{role}: checked-out repository does not match the release mask")
            git(repo, "merge-base", "--is-ancestor", revision, "HEAD")
            git(repo, "checkout", "--detach", revision)
        if git(repo, "rev-parse", "HEAD") != revision or git(repo, "status", "--porcelain", "--untracked-files=no"):
            raise PlanError(f"{role}: expected the pinned revision and a clean checkout")


def stage_items(plan, repos, root):
    expected = {key: (item["role"], item["type"]) for key, item in plan["items"].items()}
    if expected != ITEM_TYPES:
        raise PlanError("Expected the Tiny Sales item set, including the validation notebook")
    paths = {}
    logical_ids = set()
    for key, item in plan["items"].items():
        role, kind = ITEM_TYPES[key]
        repo = repos[role].resolve()
        basename = f"{item['name']}.{kind}"
        if Path(basename).name != basename or "\\" in basename:
            raise PlanError(f"{key}: expected an item name without path separators")
        source = repo / plan["sources"][role]["folder"] / basename
        if source.is_symlink() or not source.resolve().is_relative_to(repo):
            raise PlanError(f"{key}: item must be inside the checkout")
        destination = root / role / basename
        tracked = git(repo, "ls-files", "-z", "--", source.relative_to(repo).as_posix()).split("\0")[:-1]
        for name in tracked:
            path = repo / name
            if path.is_symlink() or not path.resolve().is_relative_to(source.resolve()):
                raise PlanError(f"{key}: tracked item files must stay inside the item folder")
            output = destination / path.relative_to(source)
            output.parent.mkdir(parents=True, exist_ok=True)
            copyfile(path, output)
        platform = read_json(destination / ".platform")
        metadata = platform["metadata"]
        if (metadata["displayName"], metadata["type"]) != (item["name"], kind):
            raise PlanError(f"{key}: .platform does not match the release mask")
        logical_id = guid(platform["config"]["logicalId"], f"{key} logical ID")
        if logical_id in logical_ids or logical_id == "00000000-0000-0000-0000-000000000000":
            raise PlanError(f"{key}: expected a unique, nonzero logical ID")
        logical_ids.add(logical_id)
        paths[key] = destination
    return paths


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def notebook_source(path):
    source = path.read_text(encoding="utf-8-sig")
    match = NOTEBOOK_META.search(source)
    if match is None:
        raise PlanError(f"{path.parent.name}: expected top notebook metadata")
    metadata = json.loads("\n".join(line[7:] for line in match.group().splitlines()))
    return source, match, metadata


def read_bindings(paths, plan, dev):
    notebook = notebook_source(paths["notebook"] / "notebook-content.py")
    lakehouse = notebook[2]["dependencies"]["lakehouse"]
    source_id = guid(lakehouse["default_lakehouse"], "source lakehouse")
    if (lakehouse["default_lakehouse_name"] != plan["items"]["lakehouse"]["name"]
            or lakehouse["default_lakehouse_workspace_id"].lower() != dev["data"]
            or [entry["id"].lower() for entry in lakehouse["known_lakehouses"]] != [source_id]):
        raise PlanError("Notebook lakehouse metadata differs from the Tiny Sales source shape")
    validation = notebook_source(paths["validation"] / "notebook-content.py")

    pipeline_path = paths["pipeline"] / "pipeline-content.json"
    pipeline = read_json(pipeline_path)
    properties = pipeline["properties"]
    activities = [entry for entry in properties["activities"] if entry["type"] == "TridentNotebook"]
    if len(activities) != 1 or activities[0].get("externalReferences"):
        raise PlanError("Expected one Notebook activity with the workshop's default connection")
    activity = activities[0]["typeProperties"]
    guid(activity["notebookId"], "source pipeline notebook")
    if activity["workspaceId"].lower() != dev["code"]:
        raise PlanError("Notebook activity must reference Code Dev in source")
    aliases = properties["libraryVariables"]
    for parameter, alias, variable in (("runtime_environment", "EnvironmentName", "environment_name"),
                                        ("run_label", "RunLabel", "run_label")):
        if (aliases[alias]["libraryName"] != plan["items"]["library"]["name"]
                or aliases[alias]["variableName"] != variable
                or activity["parameters"][parameter]["value"] != f"@pipeline().libraryVariables.{alias}"):
            raise PlanError(f"Unexpected pipeline Variable Library binding for {parameter}")

    expression = paths["model"] / "definition" / "expressions.tmdl"
    model = expression.read_text(encoding="utf-8-sig")
    matches = list(SQL_SOURCE.finditer(model))
    if (len(matches) != 1 or model.count("Sql.Database(") != 1
            or not matches[0][1].lower().endswith(".datawarehouse.fabric.microsoft.com")
            or guid(matches[0][2], "source SQL catalog") == source_id):
        raise PlanError("Expected the observed Direct Lake SQL host and endpoint catalog")
    report = read_json(paths["report"] / "definition.pbir")
    expected_path = {"byPath": {"path": f"../{paths['model'].name}"}}
    if report["datasetReference"] != expected_path:
        raise PlanError("Expected the report's relative path to the staged semantic model")
    value_set = plan["targets"]["test"]["variable_library"]["desired_value_set"]
    if value_set not in read_json(paths["library"] / "settings.json")["valueSetsOrder"]:
        raise PlanError("Add the Test value set to the Variable Library settings")
    return notebook, validation, pipeline, activity, expression, model, matches[0], value_set


def bind_notebook(path, definition, lakehouse):
    source, match, metadata = definition
    metadata.setdefault("dependencies", {}).setdefault("lakehouse", {}).update(lakehouse)
    block = "".join(f"# META {line}\n" for line in json.dumps(metadata, indent=2).splitlines())
    path.write_text(source[:match.start()] + block + source[match.end():], encoding="utf-8")


def read_items(plan, keys, workspaces, get):
    items = {key: plan["items"][key] for key in keys}
    roles = {item["role"] for item in items.values()}
    live = {role: list(list_workspace_items(get, workspaces[role])) for role in roles}
    return verify_expected_items(items, workspaces, live)


def publish_test(plan, dev, paths, names, get, publish, evidence):
    notebook, validation, pipeline, activity, expression, model, sql, value_set = read_bindings(paths, plan, dev)
    workspaces = plan["targets"]["test"]["workspaces"]
    preflight = inspect_target(plan, "test", names, get, inventory_only=True)
    evidence.update(preflight)
    before = {}
    for key, item in plan["items"].items():
        matches = [record for record in preflight["workspace_items"][item["role"]]
                   if record["name"].casefold() == item["name"].casefold() and record["type"] == item["type"]]
        if len(matches) > 1 or (matches and matches[0]["name"] != item["name"]):
            raise PlanError(f"{key}: ambiguous or case-mismatched target item")
        before[key] = matches[0]["itemId"] if matches else None
    evidence["before_item_ids"] = before
    if not before["lakehouse"] or not before["notebook"]:
        raise PlanError("Complete the native Test promotion from Unit 3 before running this release")
    print("TEST PREFLIGHT PASSED. Publishing the reviewed snapshot.", flush=True)

    def publish_phase(role, types):
        evidence["phase"] = f"publish {role}: {', '.join(types)}"
        key = next(key for key, item in plan["items"].items() if item["role"] == role)
        publish(workspaces[role], paths[key].parent, types, value_set)

    publish_phase("data", ["Lakehouse"])
    lakehouse = read_items(plan, ["lakehouse"], workspaces, get)["lakehouse"]
    if lakehouse["itemId"] != before["lakehouse"]:
        raise PlanError("Publishing did not preserve the existing Test lakehouse")
    endpoint = get(f"/workspaces/{workspaces['data']}/lakehouses/{lakehouse['itemId']}")["properties"]["sqlEndpointProperties"]
    host = endpoint["connectionString"]
    catalog = guid(endpoint["id"], "Test SQL endpoint")
    if endpoint["provisioningStatus"] != "Success" or not re.fullmatch(r"[\w-]+\.datawarehouse\.fabric\.microsoft\.com", host, re.I):
        raise PlanError("Test lakehouse SQL analytics endpoint is not ready")
    evidence["sql_endpoint_id"] = catalog
    target_lakehouse = {
        "default_lakehouse": lakehouse["itemId"], "default_lakehouse_name": lakehouse["name"],
        "default_lakehouse_workspace_id": workspaces["data"], "known_lakehouses": [{"id": lakehouse["itemId"]}],
    }
    bind_notebook(paths["notebook"] / "notebook-content.py", notebook, target_lakehouse)
    bind_notebook(paths["validation"] / "notebook-content.py", validation, target_lakehouse)

    publish_phase("code", ["VariableLibrary", "Notebook"])
    code = read_items(plan, ["library", "notebook", "validation"], workspaces, get)
    for key, record in code.items():
        if before[key] and before[key] != record["itemId"]:
            raise PlanError(f"Publishing did not preserve the existing Test {key}")
    library = get(f"/workspaces/{workspaces['code']}/variableLibraries/{code['library']['itemId']}")
    actual_set = library["properties"]["activeValueSetName"]
    evidence["active_value_set"] = actual_set
    if actual_set != value_set:
        raise PlanError(f"Expected active value set {value_set!r}, found {actual_set!r}")
    activity.update(notebookId=code["notebook"]["itemId"], workspaceId=workspaces["code"])
    write_json(paths["pipeline"] / "pipeline-content.json", pipeline)
    publish_phase("code", ["DataPipeline"])

    expression.write_text(model[:sql.start()] + f'Sql.Database("{host}", "{catalog}")' + model[sql.end():], encoding="utf-8")
    publish_phase("reports", ["SemanticModel", "Report"])
    evidence["phase"] = "verify published inventory"
    after = read_items(plan, plan["items"], workspaces, get)
    evidence["published_items"] = after
    evidence["created_items"] = [key for key in after if before[key] is None]
    for key, record in after.items():
        if before[key] and before[key] != record["itemId"]:
            raise PlanError(f"Publishing did not preserve the existing Test {key}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--reports", type=Path, required=True)
    parser.add_argument("--checkout-revision", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    evidence = {"environment": "test", "run_id": os.getenv("BUILD_BUILDID"), "status": "failed",
                "phase": "preflight", "started_utc": datetime.now(timezone.utc).isoformat()}
    try:
        from azure.identity import AzureCliCredential
        from fabric_cicd import FabricWorkspace, publish_all_items

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
        credential = AzureCliCredential()

        def publish(workspace, folder, types, environment):
            publish_all_items(FabricWorkspace(workspace_id=workspace, repository_directory=str(folder),
                                              item_type_in_scope=types, environment=environment,
                                              token_credential=credential))

        with TemporaryDirectory(prefix="tiny-sales-test-") as directory:
            paths = stage_items(plan, repos, Path(directory))
            publish_test(plan, dev, paths, names, fabric_reader(fabric_token()), publish, evidence)
        evidence.update(status="published", phase="complete")
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
