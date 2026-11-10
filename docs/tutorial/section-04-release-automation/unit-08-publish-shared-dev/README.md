# Unit 8 — Prepare the shared Dev release

## Part A. Verify the targets with Fabric

Allow **25 minutes** with an authorized Azure DevOps service connection. You will run a separate Azure Pipeline that checks the shared Dev workspaces and records the physical IDs of the existing Tiny Sales items. This is the read-only checkpoint before the publishing handoff.

### Before you begin

Use your Code checkout with the Unit 7 release mask merged into `dev`. Bring the assigned **Dev workspace names and IDs** from your workspace inventory. For the supplied pipeline, the facilitator provides a named Azure Resource Manager service connection that uses workload identity federation and is authorized for this pipeline. Its identity needs at least Viewer on the three assigned Dev workspaces for these reads. The Fabric administrator must allow that identity to use Fabric APIs. [Unit 7](../unit-07-configure-and-preview-release/README.md) · [Workload identity service connections](https://learn.microsoft.com/en-us/azure/devops/pipelines/release/configure-workload-identity) · [Fabric API identity support](https://learn.microsoft.com/en-us/rest/api/fabric/articles/identity-support).

### Understand the two checks

Unit 7 catches repeated GUIDs from Git. This checkpoint asks Fabric which workspace each configured GUID identifies, then compares the returned name with your assigned inventory. A valid GUID for someone else's workspace can pass a static uniqueness check. Comparing with an independently recorded name catches many of those mistakes, and the item inventory adds context. A production release can use a protected inventory of approved workspace IDs and apply its own deployment permissions. [Get Workspace](https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces/get-workspace) · [List Items](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/list-items).

Azure DevOps uses the service connection to sign the Azure CLI task in as the release identity. The preflight uses that session to request a Fabric token. Later, the Fabric workload may use a different runtime or data-access identity. Success here establishes the identity's ability to read these targets and items. Write permission and runtime access have their own checks.

### 1. Add the Dev preflight to Git

1. Start from the reviewed Unit 7 merge.

   ```powershell
   git switch dev
   git pull --ff-only origin dev
   git switch -c feature/dev-release-preflight
   ```

2. Copy the supplied files into the matching paths in your Code checkout.

   | Starter | Destination |
   | --- | --- |
   | [Dev workspace name template](../../../../config/dev-workspace-names.yml) | `config/dev-workspace-names.yml` |
   | [Preflight command](../../../../toolkit/fabric_preflight.py) | `toolkit/fabric_preflight.py` |
   | [Release planner](../../../../toolkit/release_plan.py) | `toolkit/release_plan.py` |
   | [Dev preflight pipeline](../../../../.azuredevops/pipelines/dev-release-preflight.yml) | `.azuredevops/pipelines/dev-release-preflight.yml` |

3. Fill in the three exact display names in `config/dev-workspace-names.yml` from the assigned inventory. Compare that inventory with `environments.dev.workspaces` in your release mask. Keep the recorded expected names as your reference when you review the result.
4. In `dev-release-preflight.yml`, replace `REPLACE_WITH_APPROVED_DEV_SERVICE_CONNECTION` with the provided service connection name. The Azure CLI task uses this connection to sign in. The existing notebook CI continues to validate PRs using the offline checks. [Azure CLI pipeline task](https://learn.microsoft.com/en-us/azure/devops/pipelines/tasks/reference/azure-cli-v2?view=azure-pipelines).
5. Stage, commit and push the four files.

   ```powershell
   git add -- config/dev-workspace-names.yml toolkit/fabric_preflight.py toolkit/release_plan.py .azuredevops/pipelines/dev-release-preflight.yml
   git diff --cached --check
   git diff --cached --stat
   git commit -m "Add read-only Fabric preflight for shared Dev"
   git push -u origin feature/dev-release-preflight
   ```

6. Open a PR into `dev` titled **Add the shared Dev release preflight**. Use the following description. Record the PR build result, then complete the PR when the required checks pass.

   ```markdown
   ## Change
   Check the planned Dev workspace IDs against the assigned names and record the existing Tiny Sales item IDs.

   ## Validation
   Review the required CI run for this PR. After merge, run the separate preflight from dev and record its result.
   ```

**Expected result** The preflight files are reviewed and merged into `dev`. The PR build runs the existing offline checks.

### 2. Register and run the preflight pipeline

1. In **Pipelines → New pipeline → Azure Repos Git**, choose your Code repository, then **Existing Azure Pipelines YAML file**. Select `dev` and `/.azuredevops/pipelines/dev-release-preflight.yml`. Save the pipeline. On its details page, use **… → Rename/move** and set its name to **Tiny Sales - Dev Preflight**. [Register an existing YAML pipeline](https://learn.microsoft.com/en-us/azure/devops/pipelines/get-started/clone-import-pipeline?view=azure-devops#clone-or-copy-a-pipeline) · [Pipeline settings](https://learn.microsoft.com/en-us/azure/devops/pipelines/customize-pipeline?view=azure-devops#pipeline-settings).
2. Run the pipeline manually from `dev`. If Azure DevOps requests access to the service connection, have the connection owner authorize this pipeline. [Service connection permissions](https://learn.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops).
3. Open **Read Dev workspace and item identities** in the run log. Find `PREFLIGHT PASSED` and inspect the JSON. Compare the three verified names and IDs with your inventory. Find the physical item ID and workspace ID for `build_sales` and `sales`. Where Fabric also supplies `logicalId`, compare it with the Git `.platform` identity. The run also records the Code checkout revision and the declared Data and Reporting pins. [Logical and physical Fabric IDs](../../reference/fabric-item-identities.md).
4. Save the run link and observed IDs in the worksheet. For each Dev role, record its Git connection, pending updates and uncommitted workspace edits so you know what must be reconciled at the publishing handoff. [Dev preflight record](resources/dev-preflight-record.md).

**Expected result** The release identity reads the intended Dev workspace names and the six existing Tiny Sales items. You have a live baseline to compare with the first publish.

### 3. Inspect the exported relationships

Use the pinned source files and the live inventory to collect the shape of each relationship before publishing. For each one, record the file and field name, the form of the reference, and the intended live item. Use the existing bindings recorded in Unit 4 as a cross-check.

| Relationship | Where to inspect |
| --- | --- |
| Notebook to lakehouse | The metadata block in `notebook-content.py`. Compare its default lakehouse reference with the Data Dev lakehouse in the inventory. |
| Pipeline to notebook and library | The pipeline's definition. Find the Notebook activity and the expressions or references for the library parameters. |
| Semantic model to SQL analytics endpoint | The source expression in the model definition. Check which Data Dev endpoint it identifies. |
| Report to semantic model | `definition.pbir`. Record whether the model reference uses `byPath` or `byConnection`. |

Check the current active set in the Dev Variable Library and record what the workspace shows. These observations help identify which references the deployment must preserve or resolve. [Unit 4 solution record](../../section-03-team-delivery/unit-04-connect-orchestration-configuration-and-reporting/resources/dev-solution-record.md).

### If a check fails

| Symptom | What to check |
| --- | --- |
| Dev preflight job was skipped | Run from `refs/heads/dev`. Check the branch shown for the run. |
| Azure CLI task cannot sign in | Confirm the service connection name, pipeline authorization and federation setup with the facilitator. |
| Fabric returns HTTP 401 or 403 | Confirm the tenant setting, the caller's identity and the workspace role assignment. |
| The workspace name differs | Compare the configured GUID and expected name with the assigned inventory. Resolve the discrepancy before publishing. |
| An expected item is missing or appears twice | Inspect the workspace and the item role, type and name in the mask. Record the actual inventory before selecting a publish target. |

### Part A checkpoint

- [ ] The authenticated run verified all three Dev workspace names and recorded the expected item IDs.
- [ ] The worksheet records the Code revision, Data and Reporting pins, and the CI and preflight runs.
- [ ] The workspace Git state, active value set and exported references are recorded for the publishing handoff.

[Previous unit](../unit-07-configure-and-preview-release/README.md) · [Tutorial index](../../README.md)
