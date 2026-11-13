# Unit 8 — Verify the shared Dev workspaces

Allow **35-40 minutes** for the preflight and inspection. You will create a Dev service connection and run a read-only Azure Pipeline that verifies the shared Dev workspaces and records the physical IDs of the existing Tiny Sales items. Fabric Git integration provides the Dev update path. After the preflight, you can optionally sync the merged changes and try a smoke check in Dev.

### Before you begin

Use your Code checkout with the Unit 7 release mask merged into `dev`. Bring your assigned Dev workspace names and IDs, the Dev user-assigned managed identity (UAMI) name, and the Azure subscription and resource group names for both the UAMI and the service connection scope. The facilitator supplies those Azure details and prepares Azure-side access. You need permission to create service connections in your Azure DevOps project and the Admin role in your three assigned Dev workspaces. [Unit 7](../unit-07-configure-and-preview-release/README.md).

### Understand the checks and the update

Unit 7 catches repeated GUIDs from Git. This checkpoint asks Fabric which workspace each configured GUID identifies, then compares the returned name with your assigned inventory. A valid GUID for someone else's workspace can pass a static uniqueness check. Comparing with an independently recorded name catches many of those mistakes, and the item inventory adds context. A production release can use a protected inventory of approved workspace IDs and apply its own deployment permissions. [Get Workspace](https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces/get-workspace) · [List Items](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/list-items).

The preflight checks the live workspace and item inventory. The revisions in its log describe the Code checkout and the pins in the release mask. To see which Git changes have reached a Dev workspace, check Fabric **Source control**. To see which logic actually ran, check the Fabric execution and its output.

A service connection is a named Azure DevOps project resource that tells an authorized pipeline task how to sign in. Here the UAMI is the release identity. Its federated credential tells Microsoft Entra which pipeline assertion it can exchange for a short-lived token. The Azure CLI task signs in as the UAMI and the preflight requests a Fabric token from that session. The Fabric workload may later use a different runtime or data-access identity. [Service connections, managed identities and federation](../../reference/release-service-connections.md).

Put the Dev UAMI name, service connection name and expected workspace names in `config/environments/dev.yml`. The release mask holds workspace IDs and repository references. Azure DevOps expands the service connection name from the environment file when it prepares the pipeline, before it starts the job. The UAMI name records the expected identity in the evidence. Check the service connection in Azure DevOps to confirm which identity it uses. [Azure Pipelines variable templates](https://learn.microsoft.com/en-us/azure/devops/pipelines/yaml-schema/variables-template?view=azure-pipelines) · [Template expressions for service connection inputs](https://learn.microsoft.com/en-us/azure/devops/pipelines/tasks/reference/azure-powershell-v5?view=azure-pipelines#inputs).

### 1. Create your Dev service connection

1. In Azure DevOps, open **Project settings → Service connections → New service connection**. Select **Azure Resource Manager → Next**, then set **Identity type** to **Managed identity**.
2. In **Managed Identity details**, select **Subscription for managed identity**, **Resource group for managed identity**, and the assigned Dev UAMI under **Managed Identity**. These fields locate the existing identity in Azure.
3. In **Azure scope**, select **Subscription** as the scope level, then select the supplied **Subscription for service connection** and **Resource group for Service connection**. This second resource group is the Azure scope for the connection. You will grant access to the Fabric workspaces in the next assignment.
4. In **Service connection details**, enter `sc-tiny-sales-dev` as the **Service Connection Name**. Leave **Grant access permission to all pipelines** clear and select **Save**. Azure DevOps creates the federated credential on the selected UAMI. Record the connection name and the UAMI you selected. [Connect an existing user-assigned managed identity](https://learn.microsoft.com/en-us/azure/devops/pipelines/library/connect-to-azure?view=azure-devops#create-a-service-connection-for-an-existing-user-assigned-managed-identity).

**Expected result** Your project has a federated service connection that signs in as the assigned Dev UAMI.

### 2. Grant the deployment identity access in Fabric

1. In Fabric, open your **Code Dev** workspace. Select **Manage access → Add people or groups**. Search for the exact assigned Dev UAMI name and select its service principal.
2. Select **Viewer**, then **Add**. In **Manage access**, verify the Dev UAMI has Viewer or higher.
3. Repeat in your **Data Dev** and **Reporting Dev** workspaces. Record the three assignments in the worksheet.

You use your workspace Admin role to grant access. Azure DevOps controls which pipeline may sign in through the service connection. Fabric checks what that UAMI may do in each workspace. Viewer is enough for these reads. Unit 9 grants the separate Test UAMI Contributor so it can publish. [Manage workspace access](https://learn.microsoft.com/en-us/power-bi/collaborate-share/service-give-access-new-workspaces) · [Fabric workspace roles](https://learn.microsoft.com/en-us/fabric/fundamentals/roles-workspaces).

**Expected result** The assigned Dev UAMI can read all three Dev workspaces.

### 3. Add the Dev preflight to Git

1. Start from the reviewed Unit 7 merge.

   ```powershell
   git switch dev
   git pull --ff-only origin dev
   git switch -c feature/dev-release-preflight
   ```

2. Copy the supplied files into the matching paths in your Code checkout.

   | Starter | Destination |
   | --- | --- |
   | [Dev environment settings](../../../../config/environments/dev.yml) | `config/environments/dev.yml` |
   | [Preflight command](../../../../toolkit/fabric_preflight.py) | `toolkit/fabric_preflight.py` |
   | [Release planner](../../../../toolkit/release_plan.py) | `toolkit/release_plan.py` |
   | [Dev preflight pipeline](../../../../.azuredevops/pipelines/dev-release-preflight.yml) | `.azuredevops/pipelines/dev-release-preflight.yml` |

3. In `config/environments/dev.yml`, set `releaseUamiName` to your assigned UAMI name and `releaseServiceConnection` to the name of the connection you created. Enter the three exact workspace display names from the assigned inventory. Compare the inventory with `environments.dev.workspaces` in your release mask. The pipeline reads the environment file for the connection name and the preflight reads it for the expected names.
4. Stage, commit and push the four files.

   ```powershell
   git add -- config/environments/dev.yml toolkit/fabric_preflight.py toolkit/release_plan.py .azuredevops/pipelines/dev-release-preflight.yml
   git diff --cached --check
   git diff --cached --stat
   git commit -m "Add read-only Fabric preflight for shared Dev"
   git push -u origin feature/dev-release-preflight
   ```

5. Open a PR into `dev` titled **Add the shared Dev release preflight**. Use the following description. Record the PR build result, then complete the PR when the required checks pass.

   ```markdown
   ## Change
   Check the planned Dev workspace IDs against the assigned names and record the existing Tiny Sales item IDs.

   ## Validation
   Review the required CI run for this PR. After merge, run the separate preflight from dev and record its result.
   ```

**Expected result** The preflight files are reviewed and merged into `dev`. The PR build runs the existing offline checks.

### 4. Register and run the preflight pipeline

1. In **Pipelines → New pipeline → Azure Repos Git**, choose your Code repository, then **Existing Azure Pipelines YAML file**. Select `dev` and `/.azuredevops/pipelines/dev-release-preflight.yml`. Save the pipeline. On its details page, use **… → Rename/move** and set its name to **Tiny Sales - Dev Preflight**. [Register an existing YAML pipeline](https://learn.microsoft.com/en-us/azure/devops/pipelines/get-started/clone-import-pipeline?view=azure-devops#clone-or-copy-a-pipeline) · [Pipeline settings](https://learn.microsoft.com/en-us/azure/devops/pipelines/customize-pipeline?view=azure-devops#pipeline-settings).
2. Run the pipeline manually from `dev`. When Azure DevOps reports that the pipeline needs permission to use the connection, open **View → Permit** and confirm **Permit**. This authorizes the preflight pipeline to use the connection. [Authorize a single pipeline](https://learn.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops#authorize-pipelines).
3. Open **Read Dev workspace and item identities** in the run log. Find `PREFLIGHT PASSED` and inspect the JSON. Compare `configured_release_identity` with the assigned UAMI and service connection. Compare the three verified names and IDs with your inventory. Find the physical item ID and workspace ID for `build_sales` and `sales`. Where Fabric also supplies `logicalId`, compare it with the Git `.platform` identity. The run also records the Code checkout revision and the declared Data and Reporting pins. [Logical and physical Fabric IDs](../../reference/fabric-item-identities.md).
4. Save the run link and observed IDs in the worksheet. For each Dev role, record its Git connection, pending updates and uncommitted workspace edits so you can decide whether to apply the optional update in section 6. [Dev preflight record](resources/dev-preflight-record.md).

**Expected result** The preflight identity reads the intended Dev workspace names and the six existing Tiny Sales items. You have a live baseline and know where to check Git synchronization status.

### 5. Inspect the exported relationships

Use the pinned source files and the live inventory to collect the shape of each relationship before publishing. For each one, record the file and field name, the form of the reference, and the intended live item. Use the existing bindings recorded in Unit 4 as a cross-check.

| Relationship | Where to inspect |
| --- | --- |
| Notebook to lakehouse | The metadata block in `notebook-content.py`. Compare its default lakehouse reference with the Data Dev lakehouse in the inventory. |
| Pipeline to notebook and library | The pipeline's definition. Find the Notebook activity and the expressions or references for the library parameters. |
| Semantic model to SQL analytics endpoint | The source expression in the model definition. Check which Data Dev endpoint it identifies. |
| Report to semantic model | `definition.pbir`. Record whether the model reference uses `byPath` or `byConnection`. |

Check the current active set in the Dev Variable Library and record what the workspace shows. These observations help identify which references the deployment must preserve or resolve. [Unit 4 solution record](../../section-03-team-delivery/unit-04-connect-orchestration-configuration-and-reporting/resources/dev-solution-record.md).

### 6. Optionally sync and test in shared Dev

This is where you can apply the feature merge from Unit 5. Fabric detects incoming changes on a workspace's connected branch. You can trigger the update manually, and Fabric applies the item definitions for you. Use your signed-in Fabric account for this step. The Dev preflight uses its Viewer identity to inspect the workspace. [Unit 5 Dev handoff](../../section-03-team-delivery/unit-05-make-a-local-feature-change/README.md#7-compare-merged-source-with-live-dev) · [Update a workspace from Git](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-get-started#update-workspace-from-git).

1. Open **Source control** in each Dev workspace and confirm the expected repo, `dev` branch and folder. Review incoming changes before updating. If teammates have uncommitted edits, coordinate with them and preserve that work before resolving conflicts. If there are no incoming changes, inspect the synced state and continue. [Unit 2 update walkthrough](../../section-01-foundation/unit-02-capture-the-solution-in-git/README.md#5-apply-a-harmless-git-change-back-to-fabric) · [Recover from source conflicts](../../auxiliary/aux-01-recover-from-source-conflicts/README.md).
2. Where the reviewed definitions are pending, close any saved item editors, select **Updates → Update all**, then confirm. Start with Data Dev if it has prerequisite changes, then Code Dev, then Reporting Dev if it has dependent changes. For the Unit 5 feature, the notebook change is in Code Dev. Wait for **Synced** and reopen the affected items. Each workspace follows its own connected branch tip. Before a combined Dev test, record the revisions you updated from and compare them with the combination you intended to test. [Update a workspace from Git](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-get-started#update-workspace-from-git).
3. Check that `build_sales` points to **Data Dev** and that `sales_config` has **Default** active. Run `run_sales` in Code Dev and check that the activity passes `dev` and `tiny_sales_dev`. Inspect the refreshed sales table and open `sales_overview` in Reporting Dev. For the Unit 5 feature, expect **357.20 gross** and **204.70 revenue**. The Git update applies definitions. The Fabric run recalculates the data, and the active value set is workspace configuration. Record the sync state and any runtime results in your worksheet. [Unit 4 runtime walkthrough](../../section-03-team-delivery/unit-04-connect-orchestration-configuration-and-reporting/README.md#4-run-the-pipeline-and-prove-the-configuration-is-used) · [Variable Library and Git integration](https://learn.microsoft.com/en-us/fabric/cicd/variable-library/variable-library-cicd#variable-libraries-and-git-integration).

### Choose how to use Dev

| Project situation | How you might use Dev |
| --- | --- |
| **Small team with occasional changes** | Use one shared Dev setup. Update from Git after a reviewed merge, then run a small manual check for the affected notebook, pipeline or report. |
| **Several contributors or dependent repos** | Keep feature work on branches. Coordinate shared Dev updates and record the revision in each repo before cross-workspace testing. Consider an isolated workspace when an experiment would disrupt the shared setup or needs a different branch. |
| **Frequent changes or repeated manual setup** | Use a pipeline to call Fabric's **Update From Git** API and then run suitable checks, subject to the identity, connection and item permissions for the Git operation. If Dev itself needs managed deployment with controlled bindings, define which pipeline updates which items and give the team a single update path for them. [Automate Git integration](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-automation) · [Update From Git API](https://learn.microsoft.com/en-us/rest/api/fabric/core/git/update-from-git). |

### If a check fails

| Symptom | What to check |
| --- | --- |
| The subscription, resource group or UAMI is missing from the form | Confirm you are using the supplied names and Azure DevOps project. Ask the facilitator to check your Azure discovery permissions. |
| **Save** fails with an Azure permission error | Ask the facilitator to check your permission to create the federated credential on the selected UAMI and the Azure access at the service connection scope. |
| **Save** reports a concurrent write conflict | Wait for the other team's credential creation on the shared UAMI to finish and retry. |
| Dev preflight job was skipped | Run from `refs/heads/dev`. Check the branch shown for the run. |
| Azure DevOps cannot resolve the service connection | Check `releaseServiceConnection` in the Dev environment file and confirm that this pipeline has permission to use the connection. |
| Azure CLI reports that the subscription does not exist or is unavailable | Check the connection's subscription ID and ask the facilitator to confirm that the UAMI can see that subscription. |
| Fabric returns HTTP 401 or 403 | Confirm the tenant setting, the caller's identity and the workspace role assignment. |
| The workspace name differs | Compare the configured GUID and expected name with the assigned inventory. Resolve the discrepancy before publishing. |
| An expected item is missing or appears twice | Inspect the workspace and the item role, type and name in the mask. Record the actual inventory before selecting a publish target. |
| Dev is synced but the report still shows the earlier total | Check that `run_sales` succeeded in Code Dev after the sync and refreshed the Data Dev table. Then refresh the report visuals and verify the model binding. |

### Completion checkpoint

- [ ] You created and verified the federated Dev service connection and authorized the preflight pipeline to use it.
- [ ] The Dev UAMI has at least Viewer in your Code Dev, Data Dev and Reporting Dev workspaces.
- [ ] The authenticated run verified all three Dev workspace names and recorded the expected item IDs.
- [ ] The worksheet records the Code revision, Data and Reporting pins, and the CI and preflight runs.
- [ ] You recorded the workspace Git state, active value set and exported references. If you synced and tested Dev, you also recorded the revisions and runtime result.

For the demonstration, we now proceed directly to a complete, structured **Test deployment** in Unit 9. The pipeline takes the reviewed Git revisions, verifies the Test targets, applies the bindings and records what it published. The optional Dev sync gives you a place to try the merged changes, and the Test release can proceed from Git either way.

[Previous unit](../unit-07-configure-and-preview-release/README.md) · [Next unit](../unit-09-release-to-test/README.md) · [Tutorial index](../../README.md)
