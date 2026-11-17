"""Run the Tiny Sales notebook contract and check the measure used by the returns report."""

import re

from checks.validate_tiny_sales import check_tiny_sales
from toolkit.notebook_validation import read_python_notebook


REQUIRED_MEASURE = "Returned Orders"


def run(repositories, plan):
    notebook = plan["items"]["notebook"]
    code = repositories["code"] / plan["sources"]["code"]["folder"]
    check_tiny_sales(read_python_notebook(code / f"{notebook['name']}.Notebook"))

    if "returns_report" not in plan["items"]:
        raise ValueError("Declare returns_report in the release mask")
    model = plan["items"]["model"]
    role = model["role"]
    tables = (repositories[role] / plan["sources"][role]["folder"]
              / f"{model['name']}.SemanticModel" / "definition" / "tables")
    name = re.escape(REQUIRED_MEASURE)
    measure = re.compile(rf"^\s*measure\s+(?:'{name}'|{name})\s*=", re.MULTILINE)
    if not any(measure.search(file.read_text(encoding="utf-8-sig")) for file in tables.glob("*.tmdl")):
        raise ValueError(f"{model['name']}: missing measure {REQUIRED_MEASURE!r} required by returns_overview")
