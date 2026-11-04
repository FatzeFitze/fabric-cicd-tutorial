# Add these as two separate cells in the existing build_sales notebook.
# Keep the Unit 3 target guard, fixtures, transformation and write cells intact.

# %% Parameter cell - place BEFORE the existing target-guard cell
# Use the Fabric cell menu to Toggle parameter cell for this cell only.
runtime_environment = "dev"
run_label = "interactive"

# %% Runtime validation cell - place AFTER the target-guard cell, BEFORE fixtures
def validate_runtime_parameters(context, target_workspaces, environment, label):
    code_workspace = context.get("currentWorkspaceName")
    if code_workspace not in target_workspaces:
        raise RuntimeError(f"No declared target for Code workspace {code_workspace!r}")
    expected_environment = target_workspaces[code_workspace]["environment"]
    if environment != expected_environment:
        raise RuntimeError(
            f"Runtime environment mismatch: expected {expected_environment!r}, "
            f"received {environment!r}. Check the library value and pipeline parameter."
        )
    if not isinstance(label, str) or not label.strip():
        raise ValueError("run_label must be a non-empty string.")
    return {"runtime_environment": environment, "run_label": label}


received_parameters = validate_runtime_parameters(
    notebookutils.runtime.context,
    TARGET_WORKSPACES,
    runtime_environment,
    run_label,
)
print("UNIT_04_PARAMETERS_PASS:", json.dumps(received_parameters, sort_keys=True))
