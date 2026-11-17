"""Run the Tiny Sales source checks for a release candidate."""

from checks.validate_returns import check_returns_report
from checks.validate_tiny_sales import check_tiny_sales
from toolkit.notebook_validation import read_python_notebook


def run(repositories, plan):
    """Apply the notebook and reporting checks to the selected source revisions."""
    notebook = plan["items"]["notebook"]
    code = repositories["code"] / plan["sources"]["code"]["folder"]
    check_tiny_sales(read_python_notebook(code / f"{notebook['name']}.Notebook"))
    check_returns_report(repositories, plan)
