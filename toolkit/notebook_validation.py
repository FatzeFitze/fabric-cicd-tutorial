"""Read and validate the source of a versioned Fabric Python notebook."""

import ast
import json
from pathlib import Path
from uuid import UUID


class ValidationError(ValueError):
    """A source validation failure suitable for a CI log."""


def read_python_notebook(item_dir: Path) -> ast.Module:
    """Return the syntax tree after checking the item metadata and source."""
    platform_path = item_dir / ".platform"
    try:
        platform = json.loads(platform_path.read_text(encoding="utf-8-sig"))
        item_type = platform["metadata"]["type"]
        UUID(platform["config"]["logicalId"])
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, AttributeError) as exc:
        raise ValidationError(f"{platform_path}: invalid item metadata or logical ID ({exc})") from exc

    if item_type != "Notebook":
        raise ValidationError(f"{platform_path}: expected Notebook, found {item_type!r}")

    source_path = item_dir / "notebook-content.py"
    try:
        tree = ast.parse(source_path.read_text(encoding="utf-8-sig"), filename=str(source_path))
        compile(tree, str(source_path), "exec")
    except SyntaxError as exc:
        raise ValidationError(f"{source_path}:{exc.lineno}: {exc.msg}") from exc
    except (OSError, UnicodeError) as exc:
        raise ValidationError(f"{source_path}: cannot read notebook source ({exc})") from exc
    return tree
