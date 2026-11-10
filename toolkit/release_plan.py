"""Validate a release mask and preview declared targets without Fabric access."""

import argparse
from graphlib import CycleError, TopologicalSorter
import json
from pathlib import Path, PurePosixPath
import re
import sys
from uuid import UUID

import yaml


class PlanError(ValueError):
    """An invalid release input."""


class MaskLoader(yaml.SafeLoader):
    """Load explicit mappings and reject duplicate keys."""

    def construct_mapping(self, node, deep=False):
        # A repeated YAML key could silently replace an earlier workspace mapping.
        keys = set()
        for key, _ in node.value:
            if not isinstance(key, yaml.ScalarNode) or key.tag != "tag:yaml.org,2002:str":
                raise PlanError(f"line {key.start_mark.line + 1}: expected a string key")
            if key.value in keys:
                raise PlanError(f"line {key.start_mark.line + 1}: duplicate key {key.value!r}")
            keys.add(key.value)
        return super().construct_mapping(node, deep=deep)


def mapping(value, where):
    if not isinstance(value, dict):
        raise PlanError(f"{where}: expected a mapping")
    return value


def fields(value, where, required, optional=()):
    value = mapping(value, where)
    missing = set(required) - value.keys()
    unknown = value.keys() - set(required) - set(optional)
    if missing or unknown:
        raise PlanError(f"{where}: missing {sorted(missing)}, unexpected {sorted(unknown)}")
    return value


def text(value, where):
    if not isinstance(value, str) or not value.strip() or value.startswith("REPLACE_"):
        raise PlanError(f"{where}: enter a non-empty value in place of the starter placeholder")
    return value.strip()


def relative_folder(value, where):
    value = text(value, where)
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or any(char in value for char in "\\:"):
        raise PlanError(f"{where}: expected a repo-relative folder with forward slashes")
    return str(path)


def commit_id(value, where):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", value):
        raise PlanError(f"{where}: enter the full 40-character Git commit ID")
    return value.lower()


def source_revisions(entries, checkout_revision):
    """Record the build checkout revision and the pins for the other repositories."""
    entries = mapping(entries, "sources")
    result = {}
    checkout_roles = []
    for role, entry in entries.items():
        where = f"sources.{role}"
        fields(entry, where, ("folder", "revision"), ("repository",))
        folder = relative_folder(entry["folder"], f"{where}.folder")
        if entry["revision"] == "checkout":
            checkout_roles.append(role)
            fields(entry, where, ("folder", "revision"))
            result[role] = {"source": "checkout", "folder": folder, "revision": checkout_revision}
        else:
            result[role] = {
                "repository": text(entry.get("repository"), f"{where}.repository"),
                "folder": folder,
                "revision": commit_id(entry["revision"], f"{where}.revision"),
            }
    if len(checkout_roles) != 1:
        raise PlanError("sources: exactly one role must use revision: checkout")
    return result, checkout_roles[0]


def ordered_items(entries, sources):
    """Build a definition order from binding references and explicit prerequisites."""
    entries = mapping(entries, "items")
    if not entries:
        raise PlanError("items: declare at least one Fabric item")
    graph = {}
    normalized = {}
    identities = set()
    for key, item in entries.items():
        where = f"items.{key}"
        fields(item, where, ("role", "type", "name"), ("bindings", "after"))
        role, kind, name = (text(item[field], f"{where}.{field}") for field in ("role", "type", "name"))
        if role not in sources:
            raise PlanError(f"{where}.role: unknown source role {role!r}")
        identity = role, kind.casefold(), name.casefold()
        if identity in identities:
            raise PlanError(f"{where}: duplicate role, type and item name")
        identities.add(identity)
        bindings = {
            label: text(ref, f"{where}.bindings.{label}")
            for label, ref in mapping(item.get("bindings", {}), f"{where}.bindings").items()
        }
        after = item.get("after", [])
        if not isinstance(after, list):
            raise PlanError(f"{where}.after: expected a list of item keys")
        after = [text(ref, f"{where}.after") for ref in after]
        dependencies = [*bindings.values(), *after]
        for ref in dependencies:
            if ref not in entries:
                raise PlanError(f"{where}: unknown dependency {ref!r}")
        graph[key] = dependencies
        normalized[key] = {"role": role, "type": kind, "name": name, "bindings": bindings, "after": after}
    try:
        order = list(TopologicalSorter(graph).static_order())
    except CycleError as exc:
        raise PlanError(f"items: dependency cycle {' -> '.join(exc.args[1])}") from exc
    return normalized, order


def target_workspaces(environments, sources):
    environments = mapping(environments, "environments")
    if not environments:
        raise PlanError("environments: declare at least one target")
    # Track assignments across the whole mask to catch a Dev ID reused in Test.
    seen = {}
    result = {}
    for env, value in environments.items():
        where = f"environments.{env}"
        fields(value, where, ("workspaces", "value_set"))
        workspaces = fields(value["workspaces"], f"{where}.workspaces", sources)
        normalized = {}
        for role, workspace in workspaces.items():
            field = f"{where}.workspaces.{role}"
            try:
                workspace_id = UUID(text(workspace, field))
            except (ValueError, AttributeError) as exc:
                raise PlanError(f"{field}: enter the Fabric workspace ID as a GUID") from exc
            if not workspace_id.int:
                raise PlanError(f"{field}: enter a nonzero workspace ID")
            if workspace_id in seen:
                raise PlanError(f"{field}: reuses the workspace ID assigned to {seen[workspace_id]}")
            seen[workspace_id] = field
            normalized[role] = str(workspace_id)
        result[env] = (normalized, text(value["value_set"], f"{where}.value_set"))
    return result


def read_json(path, root):
    if not path.resolve().is_relative_to(root):
        raise PlanError(f"{path}: expected a file inside the checkout")
    return mapping(json.loads(path.read_text(encoding="utf-8-sig")), str(path))


def variable_value(data, path, collection, name, fallback=None):
    entries = data.get(collection)
    if not isinstance(entries, list) or any(not isinstance(entry, dict) for entry in entries):
        raise PlanError(f"{path}: expected a list of {collection}")
    matches = [entry for entry in entries if entry.get("name") == name]
    # A value set inherits the default for a variable it does not override.
    if not matches and fallback is not None:
        return fallback
    if len(matches) != 1:
        raise PlanError(f"{path}: expected one entry named {name!r}")
    return text(matches[0].get("value"), f"{path} ({name})")


def build_preview(mask, root, checkout_revision, target=None):
    """Validate every declared environment, then return the requested preview."""
    fields(mask, "release mask", ("version", "sources", "items", "variable_library", "project_checks", "environments"))
    if type(mask["version"]) is not int or mask["version"] != 1:
        raise PlanError("version: expected 1")
    sources, checkout_role = source_revisions(mask["sources"], commit_id(checkout_revision, "checkout revision"))
    items, order = ordered_items(mask["items"], sources)
    targets = target_workspaces(mask["environments"], sources)
    if target is not None and target not in targets:
        raise PlanError(f"target: unknown environment {target!r}")
    checks = {}
    for key, module in mapping(mask["project_checks"], "project_checks").items():
        module = text(module, f"project_checks.{key}")
        if not re.fullmatch(r"[A-Za-z_]\w*(\.[A-Za-z_]\w*)*", module):
            raise PlanError(f"project_checks.{key}: expected a Python module name")
        checks[key] = module

    library = fields(mask["variable_library"], "variable_library", ("item", "folder", "environment_variable"))
    library_key = text(library["item"], "variable_library.item")
    library_item = items.get(library_key)
    if not library_item or library_item["type"] != "VariableLibrary" or library_item["role"] != checkout_role:
        raise PlanError("variable_library.item: expected a VariableLibrary item in the checkout role")
    root = root.resolve()
    folder = (root / sources[checkout_role]["folder"] / relative_folder(library["folder"], "variable_library.folder")).resolve()
    if not folder.is_relative_to(root):
        raise PlanError("variable_library.folder: expected a directory inside the checkout")
    metadata_path = folder / ".platform"
    metadata = read_json(metadata_path, root).get("metadata")
    metadata = mapping(metadata, f"{metadata_path}.metadata")
    if (metadata.get("type"), metadata.get("displayName")) != ("VariableLibrary", library_item["name"]):
        raise PlanError(f"{metadata_path}: expected VariableLibrary {library_item['name']!r}")
    variable = text(library["environment_variable"], "variable_library.environment_variable")
    variables_path = folder / "variables.json"
    default = variable_value(read_json(variables_path, root), variables_path, "variables", variable)

    plans = {}
    for env, (workspaces, value_set) in targets.items():
        # Read the values in Git. Workspace activation happens during release.
        value = default
        if value_set != "Default":
            if not re.fullmatch(r"[A-Za-z0-9_-]+", value_set):
                raise PlanError(f"environments.{env}.value_set: use letters, digits, hyphens or underscores")
            path = folder / "valueSets" / f"{value_set}.json"
            data = read_json(path, root)
            if data.get("name") != value_set:
                raise PlanError(f"{path}: name must match the selected value set {value_set!r}")
            value = variable_value(data, path, "variableOverrides", variable, fallback=default)
        if value != env:
            raise PlanError(f"environments.{env}.value_set: {value_set!r} supplies {variable}={value!r}, expected {env!r}")
        if target is None or target == env:
            plans[env] = {
                "workspaces": workspaces,
                "item_workspaces": {key: workspaces[items[key]["role"]] for key in order},
                "variable_library": {"item": library_key, "desired_value_set": value_set, "variable": variable, "value": value},
            }
    return {"sources": sources, "items": items, "definition_order": order, "project_checks": checks, "targets": plans}


def load_mask(path):
    """Read the same strict mask format for offline and live checks."""
    return yaml.load(path.read_text(encoding="utf-8-sig"), Loader=MaskLoader)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mask", type=Path, required=True)
    parser.add_argument("--checkout-revision", required=True)
    parser.add_argument("--target", help="Show one target while validating the whole mask")
    args = parser.parse_args()
    try:
        mask = load_mask(args.mask)
        plan = build_preview(mask, Path.cwd(), args.checkout_revision, args.target)
    except (PlanError, OSError, UnicodeError, yaml.YAMLError, json.JSONDecodeError) as exc:
        print(f"PLAN INVALID: {exc}", file=sys.stderr)
        return 1
    # Keep stdout as JSON so another tool can consume the plan.
    print(json.dumps(plan, indent=2))
    print("PLAN VALID: declared targets checked offline. Live Fabric resolution is pending.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
