"""Check planned workspace identities and read the target inventory from Fabric."""

import argparse
import json
from pathlib import Path
import subprocess
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener
from uuid import UUID

import yaml

from toolkit.release_plan import PlanError, build_preview, fields, load_mask, mapping, text


FABRIC_ORIGIN = "https://api.fabric.microsoft.com"


class NoRedirect(HTTPRedirectHandler):
    """Keep authenticated requests on the fixed Fabric API origin."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fabric_token():
    """Use the Azure CLI session established by the authorized pipeline task."""
    result = subprocess.run(
        ["az", "account", "get-access-token", "--resource", FABRIC_ORIGIN,
         "--query", "accessToken", "--output", "tsv", "--only-show-errors"],
        capture_output=True, text=True, timeout=60, check=False,
    )
    token = result.stdout.strip()
    if result.returncode != 0 or not token or any(char.isspace() for char in token):
        raise PlanError("Azure CLI could not acquire a Fabric token. Check the task's service connection.")
    return token


def fabric_reader(token):
    opener = build_opener(NoRedirect())

    def get(path):
        request = Request(FABRIC_ORIGIN + "/v1" + path, method="GET")
        request.add_unredirected_header("Authorization", f"Bearer {token}")
        request.add_header("Accept", "application/json")
        try:
            with opener.open(request, timeout=30) as response:
                data = json.load(response)
        except HTTPError as exc:
            # Record status without dumping response content or authorization headers.
            raise PlanError(f"Fabric GET {path.split('?')[0]} returned HTTP {exc.code}") from exc
        if not isinstance(data, dict):
            raise PlanError(f"Fabric GET {path.split('?')[0]} returned an unexpected response")
        return data

    return get


def guid(value, label):
    try:
        return str(UUID(value))
    except (ValueError, TypeError, AttributeError) as exc:
        raise PlanError(f"{label}: Fabric did not return a valid GUID") from exc


def list_workspace_items(get, workspace_id):
    path = f"/workspaces/{workspace_id}/items"
    query = ""
    seen = set()
    while True:
        page = get(path + query)
        items = page.get("value")
        if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
            raise PlanError(f"{path}: expected an item list")
        yield from items
        continuation = page.get("continuationToken")
        if continuation is None:
            return
        if not isinstance(continuation, str) or not continuation or continuation in seen:
            raise PlanError(f"{path}: invalid or repeated continuation token")
        seen.add(continuation)
        # Rebuild the URL from the documented token. Keep the same API host and path.
        query = "?" + urlencode({"continuationToken": continuation})


def read_environment_config(path, roles):
    """Read the same environment settings Azure Pipelines uses for this run."""
    document = fields(load_mask(path), str(path), ("variables",))
    workspace_keys = {role: f"{role}WorkspaceName" for role in roles}
    required = ("releaseUamiName", "releaseServiceConnection", *workspace_keys.values())
    variables = mapping(document["variables"], f"{path}.variables")
    values = {key: text(variables.get(key), f"{path}.variables.{key}") for key in required}
    names = {role: values[key] for role, key in workspace_keys.items()}
    # These labels record release intent. The service connection supplies the login.
    identity = {
        "uamiName": values["releaseUamiName"],
        "serviceConnectionName": values["releaseServiceConnection"],
    }
    return names, identity


def verify_workspaces(workspaces, names, get):
    """Check all target IDs against independently recorded display names."""
    fields(names, "expected workspace names", workspaces)
    verified = {}
    for role, workspace_id in workspaces.items():
        expected = text(names[role], f"expected workspace names.{role}")
        info = get(f"/workspaces/{workspace_id}")
        if guid(info.get("id"), f"{role} workspace") != workspace_id:
            raise PlanError(f"{role} workspace: Fabric returned a different ID from {workspace_id}")
        if info.get("type") != "Workspace":
            raise PlanError(f"{role} workspace {workspace_id}: expected a regular Fabric workspace")
        actual = info.get("displayName")
        if actual != expected:
            raise PlanError(f"{role} workspace {workspace_id}: expected {expected!r}, found {actual!r}")
        verified[role] = {"id": workspace_id, "displayName": actual}
    return verified


def item_record(item, role, workspace_id):
    name = text(item.get("displayName"), f"{role} item display name")
    if guid(item.get("workspaceId"), name) != workspace_id:
        raise PlanError(f"{name}: Fabric reported a different workspace ID")
    return {
        "role": role,
        "name": name,
        "type": text(item.get("type"), f"{name} item type"),
        "workspaceId": workspace_id,
        "itemId": guid(item.get("id"), name),
        "logicalId": item.get("logicalId"),
    }


def verify_expected_items(items, workspaces, live_items):
    inventory = {}
    for key, desired in items.items():
        role = desired["role"]
        matches = [item for item in live_items[role]
                   if item.get("type") == desired["type"] and item.get("displayName") == desired["name"]]
        if len(matches) != 1:
            raise PlanError(f"{role} workspace: expected one {desired['type']} named {desired['name']!r}, found {len(matches)}")
        inventory[key] = item_record(matches[0], role, workspaces[role])
    return inventory


def inspect_target(plan, target, names, get, inventory_only):
    workspaces = plan["targets"][target]["workspaces"]
    verified = verify_workspaces(workspaces, names, get)
    live_items = {role: list(list_workspace_items(get, workspace_id))
                  for role, workspace_id in workspaces.items()}
    evidence = {"environment": target, "declared_sources": plan["sources"],
                "verified_workspaces": verified}
    if inventory_only:
        evidence["workspace_items"] = {
            role: [item_record(item, role, workspace_id) for item in live_items[role]]
            for role, workspace_id in workspaces.items()
        }
    else:
        evidence["observed_items"] = verify_expected_items(plan["items"], workspaces, live_items)
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mask", type=Path, required=True)
    parser.add_argument("--environment-config", type=Path, required=True)
    parser.add_argument("--checkout-revision", required=True)
    parser.add_argument("--target", default="dev", help="Select an environment from the release mask")
    parser.add_argument("--inventory-only", action="store_true",
                        help="List visible items without requiring the complete source inventory")
    args = parser.parse_args()
    try:
        plan = build_preview(load_mask(args.mask), Path.cwd(), args.checkout_revision, target=args.target)
        workspaces = plan["targets"][args.target]["workspaces"]
        names, identity = read_environment_config(args.environment_config, workspaces)
        evidence = inspect_target(plan, args.target, names, fabric_reader(fabric_token()), args.inventory_only)
        evidence["configured_release_identity"] = identity
    except (PlanError, OSError, URLError, subprocess.TimeoutExpired, UnicodeError,
            yaml.YAMLError, json.JSONDecodeError) as exc:
        print(f"PREFLIGHT FAILED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(evidence, indent=2))
    if args.inventory_only:
        result = "workspace names verified and visible items recorded."
    else:
        result = "workspace names and expected item inventory verified."
    print(f"PREFLIGHT PASSED: {args.target.capitalize()} {result}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
