"""Check the source declarations required by the Tiny Sales returns report."""

import re


REQUIRED_MEASURE = "Returned Orders"


def check_returns_report(repositories, plan):
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
