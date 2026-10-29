# Native-promotion rehearsal: replace only Cell 1 in build_sales with this source.
# Configure all six workspace names in Code Dev, then commit that common source.
# Keep the fixture, transformation and persistence cells from Unit 1 unchanged.
from decimal import Decimal
import json

from pyspark.sql import functions as F

TARGET_WORKSPACES = {
    "REPLACE_WITH_CODE_DEV_WORKSPACE_NAME": {
        "environment": "dev",
        "data_workspace": "REPLACE_WITH_DATA_DEV_WORKSPACE_NAME",
    },
    "REPLACE_WITH_CODE_TEST_WORKSPACE_NAME": {
        "environment": "test",
        "data_workspace": "REPLACE_WITH_DATA_TEST_WORKSPACE_NAME",
    },
    "REPLACE_WITH_CODE_PROD_WORKSPACE_NAME": {
        "environment": "prod",
        "data_workspace": "REPLACE_WITH_DATA_PROD_WORKSPACE_NAME",
    },
}
EXPECTED_LAKEHOUSE = "sales"
TABLE_NAME = "sales"


def validate_target(context):
    if len(TARGET_WORKSPACES) != 3:
        raise RuntimeError("Configure three distinct Code workspace names.")
    if {target["environment"] for target in TARGET_WORKSPACES.values()} != {
        "dev", "test", "prod"
    }:
        raise RuntimeError("Configure one Code/Data pair for each of dev, test and prod.")
    names = list(TARGET_WORKSPACES) + [
        target["data_workspace"] for target in TARGET_WORKSPACES.values()
    ]
    if any(
        not isinstance(name, str) or not name.strip() or "REPLACE_WITH_" in name
        for name in names
    ):
        raise RuntimeError("Replace all six workspace-name placeholders before running.")
    if len(set(names)) != 6:
        raise RuntimeError("Use six distinct workspaces for the three Code/Data pairs.")

    code_workspace = context.get("currentWorkspaceName")
    if code_workspace not in TARGET_WORKSPACES:
        raise RuntimeError(f"Unrecognized Code workspace: {code_workspace!r}")
    target = TARGET_WORKSPACES[code_workspace]
    expected = {
        "currentWorkspaceName": code_workspace,
        "defaultLakehouseWorkspaceName": target["data_workspace"],
        "defaultLakehouseName": EXPECTED_LAKEHOUSE,
    }
    actual = {key: context.get(key) for key in expected}
    if actual != expected:
        raise RuntimeError(
            f"Target check failed for {target['environment']}. "
            f"Expected: {expected}. Actual: {actual}. "
            "Check the target-stage default lakehouse rule and restart any old session."
        )
    return {
        "environment": target["environment"],
        **actual,
        "codeWorkspaceId": context.get("currentWorkspaceId"),
        "dataWorkspaceId": context.get("defaultLakehouseWorkspaceId"),
        "lakehouseId": context.get("defaultLakehouseId"),
    }


def check_target():
    result = validate_target(notebookutils.runtime.context)
    print(json.dumps(result, indent=2))


check_target()
