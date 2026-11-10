"""Tiny Sales source contract for the returned-order feature from Unit 5."""

import argparse
import ast
from pathlib import Path
import sys

from toolkit.notebook_validation import ValidationError, read_python_notebook


def assignment_value(tree: ast.Module, name: str) -> ast.expr:
    matches = [
        stmt.value
        for stmt in tree.body
        if isinstance(stmt, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == name for target in stmt.targets)
    ]
    if len(matches) != 1:
        raise ValidationError(f"Expected one top-level assignment to {name}; found {len(matches)}")
    return matches[0]


def require_expression(actual: ast.expr, expected: str, label: str) -> None:
    expected_tree = ast.parse(expected, mode="eval").body
    if ast.dump(actual) != ast.dump(expected_tree):
        raise ValidationError(
            f"line {actual.lineno}: {label} expects {expected}; found {ast.unparse(actual)}"
        )


def check_tiny_sales(tree: ast.Module) -> None:
    sales = assignment_value(tree, "sales")
    revenue_columns = [
        call
        for call in ast.walk(sales)
        if isinstance(call, ast.Call)
        and isinstance(call.func, ast.Attribute)
        and call.func.attr == "withColumn"
        and call.args
        and isinstance(call.args[0], ast.Constant)
        and call.args[0].value == "revenue"
    ]
    if len(revenue_columns) != 1 or len(revenue_columns[0].args) != 2 or revenue_columns[0].keywords:
        raise ValidationError('Expected one withColumn("revenue", expression) in the sales transformation')

    require_expression(
        revenue_columns[0].args[1],
        'F.when(F.col("is_returned"), F.lit(0).cast("decimal(12,2)"))'
        '.otherwise(F.col("gross_revenue"))',
        "Returned orders must contribute zero revenue",
    )

    metrics = assignment_value(tree, "EXPECTED_METRICS")
    if not isinstance(metrics, ast.Dict):
        raise ValidationError("EXPECTED_METRICS must be a dictionary literal")

    for key, amount in {"gross_revenue": "357.20", "revenue": "204.70"}.items():
        values = [
            value
            for field, value in zip(metrics.keys, metrics.values)
            if isinstance(field, ast.Constant) and field.value == key
        ]
        if len(values) != 1:
            raise ValidationError(f"EXPECTED_METRICS must declare {key!r} exactly once")
        require_expression(values[0], f'Decimal("{amount}")', f"EXPECTED_METRICS[{key!r}]")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the Tiny Sales notebook source")
    parser.add_argument("--item-dir", type=Path, required=True, help="Path to the Fabric Notebook item folder")
    args = parser.parse_args()

    try:
        tree = read_python_notebook(args.item_dir)
        check_tiny_sales(tree)
    except ValidationError as exc:
        print(f"VALIDATION FAILED: {exc}", file=sys.stderr)
        return 1

    print("VALIDATION PASSED: Notebook metadata, Python syntax and Tiny Sales source contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
