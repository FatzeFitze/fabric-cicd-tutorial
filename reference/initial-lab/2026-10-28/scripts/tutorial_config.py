#!/usr/bin/env python3
"""Load and validate participant-specific tutorial resource names.

The configuration contains non-secret names only. Physical Fabric IDs are
resolved from the Fabric APIs at execution time and credentials remain owned by
Azure DevOps service connections or the active Azure CLI session.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_CONFIG_PATH = Path("config/tutorial-resources.json")
PLACEHOLDER_MARKERS = (
    "<replace-",
    "replace-with-",
    "<your-",
)


class TutorialConfigError(RuntimeError):
    """Raised when tutorial resource configuration is missing or invalid."""


@dataclass(frozen=True)
class TutorialResources:
    config_path: Path
    config_sha256: str
    repository_name: str
    deployment_pipeline_name: str
    dev_workspace_name: str
    test_workspace_name: str
    prod_workspace_name: str
    nonprod_managed_identity_name: str
    prod_managed_identity_name: str

    def evidence(self) -> dict[str, Any]:
        """Return the non-secret configuration provenance used by a run."""
        return {
            "path": self.config_path.as_posix(),
            "sha256": self.config_sha256,
            "schemaVersion": 2,
            "azureDevOpsRepositoryName": self.repository_name,
            "fabricDeploymentPipelineName": self.deployment_pipeline_name,
            "fabricWorkspaces": {
                "dev": self.dev_workspace_name,
                "test": self.test_workspace_name,
                "prod": self.prod_workspace_name,
            },
            "nonProductionManagedIdentityName": (
                self.nonprod_managed_identity_name
            ),
            "productionManagedIdentityName": (
                self.prod_managed_identity_name
            ),
        }


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise TutorialConfigError(message)


def _strict_object(
    value: Any,
    description: str,
    expected_keys: set[str],
) -> dict[str, Any]:
    _require(isinstance(value, dict), f"{description} must be a JSON object.")
    actual_keys = set(value)
    missing = sorted(expected_keys - actual_keys)
    unexpected = sorted(actual_keys - expected_keys)
    _require(not missing, f"{description} is missing keys: {missing}.")
    _require(
        not unexpected,
        f"{description} contains unexpected keys: {unexpected}.",
    )
    return value


def _name(value: Any, description: str) -> str:
    _require(isinstance(value, str), f"{description} must be a string.")
    normalized = value.strip()
    _require(bool(normalized), f"{description} must not be empty.")
    lowered = normalized.lower()
    _require(
        not any(marker in lowered for marker in PLACEHOLDER_MARKERS),
        f"{description} still contains a tutorial placeholder: {normalized!r}.",
    )
    return normalized


def load_tutorial_resources(
    path: str | Path = DEFAULT_CONFIG_PATH,
) -> TutorialResources:
    config_path = Path(path)
    _require(
        config_path.is_file(),
        f"Tutorial resource configuration does not exist: {config_path}",
    )

    raw_bytes = config_path.read_bytes()
    try:
        payload = json.loads(raw_bytes.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TutorialConfigError(
            f"Tutorial resource configuration is invalid JSON: {config_path}"
        ) from exc

    root = _strict_object(
        payload,
        "Configuration root",
        {
            "schemaVersion",
            "azureDevOps",
            "fabric",
            "deploymentIdentities",
        },
    )
    _require(
        root["schemaVersion"] == 2,
        "schemaVersion must be the integer 2.",
    )

    azure_devops = _strict_object(
        root["azureDevOps"],
        "azureDevOps",
        {"repositoryName"},
    )
    fabric = _strict_object(
        root["fabric"],
        "fabric",
        {"deploymentPipelineName", "workspaces"},
    )
    workspaces = _strict_object(
        fabric["workspaces"],
        "fabric.workspaces",
        {"dev", "test", "prod"},
    )
    identities = _strict_object(
        root["deploymentIdentities"],
        "deploymentIdentities",
        {"nonProductionManagedIdentityName", "productionManagedIdentityName"},
    )
    nonprod_managed_identity_name = _name(
        identities["nonProductionManagedIdentityName"],
        "deploymentIdentities.nonProductionManagedIdentityName",
    )

    prod_managed_identity_name = _name(
        identities["productionManagedIdentityName"],
        "deploymentIdentities.productionManagedIdentityName",
    )

    _require(
        nonprod_managed_identity_name.casefold()
        != prod_managed_identity_name.casefold(),
        (
            "Production and non-Production managed identity names "
            "must be distinct."
        ),
    )

    dev_workspace_name = _name(
        workspaces["dev"], "fabric.workspaces.dev"
    )
    test_workspace_name = _name(
        workspaces["test"], "fabric.workspaces.test"
    )
    prod_workspace_name = _name(
        workspaces["prod"], "fabric.workspaces.prod"
    )
    workspace_names = {
        dev_workspace_name,
        test_workspace_name,
        prod_workspace_name,
    }
    _require(
        len(workspace_names) == 3,
        "DEV, TEST, and PROD workspace names must be distinct.",
    )

    return TutorialResources(
        config_path=config_path,
        config_sha256=hashlib.sha256(raw_bytes).hexdigest(),
        repository_name=_name(
            azure_devops["repositoryName"],
            "azureDevOps.repositoryName",
        ),
        deployment_pipeline_name=_name(
            fabric["deploymentPipelineName"],
            "fabric.deploymentPipelineName",
        ),
        dev_workspace_name=dev_workspace_name,
        test_workspace_name=test_workspace_name,
        prod_workspace_name=prod_workspace_name,
        nonprod_managed_identity_name=nonprod_managed_identity_name,
        prod_managed_identity_name=prod_managed_identity_name,
    )


def _resolve_key(payload: dict[str, Any], dotted_key: str) -> Any:
    current: Any = payload
    for segment in dotted_key.split("."):
        if not isinstance(current, dict) or segment not in current:
            raise TutorialConfigError(
                f"Unknown tutorial configuration key: {dotted_key}"
            )
        current = current[segment]
    return current


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate or read tutorial resource configuration."
    )
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to tutorial-resources.json.",
    )
    parser.add_argument(
        "--get",
        dest="dotted_key",
        help="Print one validated configuration value by dotted key.",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        resources = load_tutorial_resources(arguments.config)
        if arguments.dotted_key:
            value = _resolve_key(
                {
                    "azureDevOps": {
                        "repositoryName": resources.repository_name,
                    },
                    "fabric": {
                        "deploymentPipelineName": (
                            resources.deployment_pipeline_name
                        ),
                        "workspaces": {
                            "dev": resources.dev_workspace_name,
                            "test": resources.test_workspace_name,
                            "prod": resources.prod_workspace_name,
                        },
                    },
                    "deploymentIdentities": {
                        "nonProductionManagedIdentityName": (
                            resources.nonprod_managed_identity_name
                        ),
                        "productionManagedIdentityName": (
                            resources.prod_managed_identity_name
                        ),
                    },
                },
                arguments.dotted_key,
            )
            if isinstance(value, (dict, list)):
                print(json.dumps(value, ensure_ascii=False))
            else:
                print(value)
            return 0

        print(json.dumps(resources.evidence(), indent=2, ensure_ascii=False))
        print("TUTORIAL RESOURCE CONFIGURATION VALID")
        return 0
    except TutorialConfigError as exc:
        print(f"TUTORIAL RESOURCE CONFIGURATION INVALID: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
