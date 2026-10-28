#!/usr/bin/env python3
"""
Offline validation for the fabric-cicd-lab Git repository.

This script validates Fabric item definitions only. It does not connect to
Microsoft Fabric and cannot validate deployment state or runtime behavior.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

LAKEHOUSE_DIRECTORY = (
    REPOSITORY_ROOT
    / "01_data_engineering"
    / "lh_cicd_lab.Lakehouse"
)

NOTEBOOK_DIRECTORY = (
    REPOSITORY_ROOT
    / "01_data_engineering"
    / "nb_01_seed_and_transform_cicd_lab.Notebook"
)

PIPELINE_DIRECTORY = (
    REPOSITORY_ROOT
    / "02_orchestration"
    / "pl_01_run_cicd_lab_transform.DataPipeline"
)


@dataclass(frozen=True)
class ExpectedItem:
    directory: Path
    item_type: str
    display_name: str


EXPECTED_ITEMS = (
    ExpectedItem(
        directory=LAKEHOUSE_DIRECTORY,
        item_type="Lakehouse",
        display_name="lh_cicd_lab",
    ),
    ExpectedItem(
        directory=NOTEBOOK_DIRECTORY,
        item_type="Notebook",
        display_name="nb_01_seed_and_transform_cicd_lab",
    ),
    ExpectedItem(
        directory=PIPELINE_DIRECTORY,
        item_type="DataPipeline",
        display_name="pl_01_run_cicd_lab_transform",
    ),
)

EXPECTED_LAKEHOUSE_FILES = (
    ".platform",
    "alm.settings.json",
    "lakehouse.metadata.json",
    "shortcuts.metadata.json",
)

EXPECTED_NOTEBOOK_FILES = (
    ".platform",
    "notebook-content.py",
)

EXPECTED_PIPELINE_FILES = (
    ".platform",
    "pipeline-content.json",
)

EXPECTED_TABLE_NAMES = (
    "raw_sales_orders",
    "curated_sales_orders",
    "agg_sales_by_date",
    "cicd_run_audit",
)

EXPECTED_AGGREGATE_COLUMNS = (
    "order_count",
    "total_quantity",
    "total_sales_amount",
    "average_order_value",
)

EXPECTED_AGGREGATE_COLUMNS = (
    "order_count",
    "total_quantity",
    "total_sales_amount",
    "average_order_value",
)

EXPECTED_ACTIVITY_NAME = "act_run_seed_and_transform_notebook"
ZERO_WORKSPACE_ID = "00000000-0000-0000-0000-000000000000"


class ValidationFailure(Exception):
    """Raised when the repository does not satisfy an expected invariant."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationFailure(message)


def read_json(path: Path) -> Any:
    require(path.is_file(), f"Required JSON file is missing: {relative(path)}")

    try:
        with path.open("r", encoding="utf-8-sig") as file:
            return json.load(file)
    except json.JSONDecodeError as error:
        raise ValidationFailure(
            f"Invalid JSON in {relative(path)}: "
            f"line {error.lineno}, column {error.colno}: {error.msg}"
        ) from error


def read_text(path: Path) -> str:
    require(path.is_file(), f"Required text file is missing: {relative(path)}")
    return path.read_text(encoding="utf-8-sig")


def relative(path: Path) -> str:
    return path.relative_to(REPOSITORY_ROOT).as_posix()


def require_files(directory: Path, filenames: tuple[str, ...]) -> None:
    require(directory.is_dir(), f"Required directory is missing: {relative(directory)}")

    for filename in filenames:
        path = directory / filename
        require(path.is_file(), f"Required file is missing: {relative(path)}")


def platform_properties(item: ExpectedItem) -> tuple[str, dict[str, Any]]:
    platform_path = item.directory / ".platform"
    platform = read_json(platform_path)

    metadata = platform.get("metadata")
    config = platform.get("config")

    require(
        isinstance(metadata, dict),
        f"{relative(platform_path)} has no valid metadata object.",
    )
    require(
        isinstance(config, dict),
        f"{relative(platform_path)} has no valid config object.",
    )

    require(
        metadata.get("type") == item.item_type,
        f"{relative(platform_path)}: expected metadata.type "
        f"'{item.item_type}', found '{metadata.get('type')}'.",
    )
    require(
        metadata.get("displayName") == item.display_name,
        f"{relative(platform_path)}: expected metadata.displayName "
        f"'{item.display_name}', found '{metadata.get('displayName')}'.",
    )

    logical_id = config.get("logicalId")
    require(
        isinstance(logical_id, str) and logical_id.strip(),
        f"{relative(platform_path)} has no valid config.logicalId.",
    )

    return logical_id, platform


def validate_required_structure() -> None:
    print("Validating required repository structure...")

    require_files(LAKEHOUSE_DIRECTORY, EXPECTED_LAKEHOUSE_FILES)
    require_files(NOTEBOOK_DIRECTORY, EXPECTED_NOTEBOOK_FILES)
    require_files(PIPELINE_DIRECTORY, EXPECTED_PIPELINE_FILES)


def validate_platform_files() -> dict[str, str]:
    print("Validating Fabric .platform files...")

    logical_ids: dict[str, str] = {}

    for item in EXPECTED_ITEMS:
        logical_id, _ = platform_properties(item)
        logical_ids[item.item_type] = logical_id

        print(
            f"  {item.item_type}: {item.display_name} "
            f"[logicalId={logical_id}]"
        )

    require(
        len(set(logical_ids.values())) == len(logical_ids),
        "Fabric logical IDs must be unique across the expected items.",
    )

    return logical_ids


def validate_json_definitions() -> None:
    print("Validating JSON definition files...")

    for path in (
        LAKEHOUSE_DIRECTORY / "alm.settings.json",
        LAKEHOUSE_DIRECTORY / "lakehouse.metadata.json",
        LAKEHOUSE_DIRECTORY / "shortcuts.metadata.json",
        PIPELINE_DIRECTORY / "pipeline-content.json",
    ):
        read_json(path)
        print(f"  Valid JSON: {relative(path)}")


def validate_notebook_source() -> None:
    print("Validating Notebook source...")

    notebook_path = NOTEBOOK_DIRECTORY / "notebook-content.py"
    notebook_source = read_text(notebook_path)

    for table_name in EXPECTED_TABLE_NAMES:
        require(
            table_name in notebook_source,
            f"Notebook source does not contain expected table name "
            f"'{table_name}'.",
        )
    
    for column_name in EXPECTED_AGGREGATE_COLUMNS:
        require(
            column_name in notebook_source,
            f"Notebook source does not contain expected aggregate column "
            f"'{column_name}'.",
        )

    require(
        "saveAsTable" in notebook_source,
        "Notebook source does not contain saveAsTable calls.",
    )

    print("  Expected table names and saveAsTable logic are present.")


def validate_pipeline_notebook_reference(
    notebook_logical_id: str,
) -> None:
    print("Validating Pipeline-to-Notebook dependency...")

    pipeline_path = PIPELINE_DIRECTORY / "pipeline-content.json"
    pipeline = read_json(pipeline_path)

    properties = pipeline.get("properties")
    require(
        isinstance(properties, dict),
        "Pipeline definition has no valid properties object.",
    )

    activities = properties.get("activities")
    require(
        isinstance(activities, list),
        "Pipeline definition has no valid activities array.",
    )
    require(
        len(activities) == 1,
        f"Expected exactly one pipeline activity, found {len(activities)}.",
    )

    activity = activities[0]
    require(
        isinstance(activity, dict),
        "Pipeline activity is not a JSON object.",
    )
    require(
        activity.get("name") == EXPECTED_ACTIVITY_NAME,
        f"Expected activity name '{EXPECTED_ACTIVITY_NAME}', "
        f"found '{activity.get('name')}'.",
    )
    require(
        activity.get("type") == "TridentNotebook",
        f"Expected activity type 'TridentNotebook', "
        f"found '{activity.get('type')}'.",
    )

    type_properties = activity.get("typeProperties")
    require(
        isinstance(type_properties, dict),
        "Notebook activity has no valid typeProperties object.",
    )

    notebook_id = type_properties.get("notebookId")
    workspace_id = type_properties.get("workspaceId")

    require(
        notebook_id == notebook_logical_id,
        "Pipeline notebookId does not match the Notebook logicalId. "
        f"Pipeline notebookId='{notebook_id}', "
        f"Notebook logicalId='{notebook_logical_id}'.",
    )

    require(
        workspace_id == ZERO_WORKSPACE_ID,
        "Pipeline workspaceId is not workspace-relative. "
        f"Expected '{ZERO_WORKSPACE_ID}', found '{workspace_id}'. "
        "A hard-coded workspace ID may cause cross-environment binding.",
    )

    print("  Pipeline notebookId matches the Notebook logicalId.")
    print("  Pipeline workspaceId is workspace-relative.")


def main() -> int:
    print("Fabric repository validation")
    print("============================")
    print(f"Repository root: {REPOSITORY_ROOT}")

    try:
        validate_required_structure()
        logical_ids = validate_platform_files()
        validate_json_definitions()
        validate_notebook_source()
        validate_pipeline_notebook_reference(
            notebook_logical_id=logical_ids["Notebook"]
        )
    except ValidationFailure as error:
        print()
        print(f"VALIDATION FAILED: {error}", file=sys.stderr)
        return 1

    print()
    print("VALIDATION SUCCEEDED")
    print("The Fabric repository definitions are structurally coherent.")
    print(
        "Deployment bindings and runtime behavior still require "
        "environment-level validation."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())