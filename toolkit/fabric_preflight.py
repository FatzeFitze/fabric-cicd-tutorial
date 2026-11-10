"""Check the planned Dev workspace identities and inventory against Fabric."""

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

from toolkit.release_plan import PlanError, build_preview, fields, load_mask, text


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


def verify_dev(plan, names, get):
    """Verify identities against independently recorded names, then inspect items."""
    dev = plan["targets"]["dev"]
    workspaces = dev["workspaces"]
    fields(names, "expected Dev workspace names", workspaces)
    verified = {}
    for role, workspace_id in workspaces.items():
        expected = text(names[role], f"expected Dev workspace names.{role}")
        info = get(f"/workspaces/{workspace_id}")
        if guid(info.get("id"), f"{role} workspace") != workspace_id:
            raise PlanError(f"{role} workspace: Fabric returned a different ID from {workspace_id}")
        if info.get("type") != "Workspace":
            raise PlanError(f"{role} workspace {workspace_id}: expected a regular Fabric workspace")
        actual = info.get("displayName")
        if actual != expected:
            raise PlanError(f"{role} workspace {workspace_id}: expected {expected!r}, found {actual!r}")
        verified[role] = {"id": workspace_id, "displayName": actual}

    live_items = {role: list(list_workspace_items(get, record["id"])) for role, record in verified.items()}
    inventory = {}
    for key, desired in plan["items"].items():
        role = desired["role"]
        workspace_id = workspaces[role]
        matches = [item for item in live_items[role]
                   if item.get("type") == desired["type"] and item.get("displayName") == desired["name"]]
        if len(matches) != 1:
            raise PlanError(f"{role} workspace: expected one {desired['type']} named {desired['name']!r}, found {len(matches)}")
        item = matches[0]
        if guid(item.get("workspaceId"), key) != workspace_id:
            raise PlanError(f"{key}: Fabric reported a different workspace ID")
        inventory[key] = {
            "role": role,
            "name": desired["name"],
            "type": desired["type"],
            "workspaceId": workspace_id,
            "itemId": guid(item.get("id"), key),
            "logicalId": item.get("logicalId"),
        }
    return {"environment": "dev", "declared_sources": plan["sources"],
            "verified_workspaces": verified, "observed_items": inventory}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mask", type=Path, required=True)
    parser.add_argument("--workspace-names", type=Path, required=True)
    parser.add_argument("--checkout-revision", required=True)
    args = parser.parse_args()
    try:
        plan = build_preview(load_mask(args.mask), Path.cwd(), args.checkout_revision, target="dev")
        names = load_mask(args.workspace_names)
        fields(names, "expected Dev workspace names", plan["targets"]["dev"]["workspaces"])
        for role, name in names.items():
            text(name, f"expected Dev workspace names.{role}")
        evidence = verify_dev(plan, names, fabric_reader(fabric_token()))
    except (PlanError, OSError, URLError, subprocess.TimeoutExpired, UnicodeError,
            yaml.YAMLError, json.JSONDecodeError) as exc:
        print(f"PREFLIGHT FAILED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(evidence, indent=2))
    print("PREFLIGHT PASSED: Dev workspace names and expected item inventory verified.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
