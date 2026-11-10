# Unit 8 — Prepare the shared Dev release

## Part A. Verify the targets with Fabric

Allow **35–40 minutes**. You will create a Dev service connection and run an Azure Pipeline that checks the shared Dev workspaces and records the physical IDs of the existing Tiny Sales items. This is the read-only checkpoint before the publishing handoff.

### Before you begin

Use your Code checkout with the Unit 7 release mask merged into `dev`. Bring your assigned Dev workspace names and IDs, the Dev user-assigned managed identity (UAMI) name, client ID and tenant ID, and the Azure subscription name and ID supplied by the facilitator. You need permission to create service connections in your Azure DevOps project. The facilitator prepares the Azure access for the UAMI and its Fabric access for these reads, including at least Viewer on the three Dev workspaces. [Unit 7](../unit-07-configure-and-preview-release/README.md) · [Fabric API identity support](https://learn.microsoft.com/en-us/rest/api/fabric/articles/identity-support).

### Understand the two checks

Unit 7 catches repeated GUIDs from Git. This checkpoint asks Fabric which workspace each configured GUID identifies, then compares the returned name with your assigned inventory. A valid GUID for someone else's workspace can pass a static uniqueness check. Comparing with an independently recorded name catches many of those mistakes, and the item inventory adds context. A production release can use a protected inventory of approved workspace IDs and apply its own deployment permissions. [Get Workspace](https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces/get-workspace) · [List Items](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/list-items).

A service connection is a named Azure DevOps project resource that tells an authorized pipeline task how to sign in. Here the UAMI is the release identity. Its federated credential tells Microsoft Entra which pipeline assertion it can exchange for a short-lived token. The Azure CLI task signs in as the UAMI and the preflight requests a Fabric token from that session. The Fabric workload may later use a different runtime or data-access identity. [Service connections, managed identities and federation](../../reference/release-service-connections.md).

Put the Dev UAMI name, service connection name and expected workspace names in `config/environments/dev.yml`. The release mask holds workspace IDs and repository references. Azure DevOps expands the service connection name from the environment file when it prepares the pipeline, before it starts the job. The UAMI name records the expected identity in the evidence. Check the service connection in Azure DevOps to confirm which identity it uses. [Azure Pipelines variable templates](https://learn.microsoft.com/en-us/azure/devops/pipelines/yaml-schema/variables-template?view=azure-pipelines) · [Template expressions for service connection inputs](https://learn.microsoft.com/en-us/azure/devops/pipelines/tasks/reference/azure-powershell-v5?view=azure-pipelines#inputs).

### 1. Create your Dev service connection

1. In Azure DevOps, open **Project settings → Service connections → New service connection**. Select **Azure Resource Manager**, then **App registration or Managed identity (manual)** and **Workload identity federation**.
2. In **Basics**, enter a Dev-specific **Service Connection Name**, such as `sc-tiny-sales-dev`, select **Azure Cloud**, and enter the assigned **Directory (tenant) ID**. Select **Next**. Under **Scope Level**, select **Subscription** and enter the assigned subscription ID and name. In **Application (client) ID**, enter the UAMI's **client ID**. Leave **Grant access permission to all pipelines** clear so you can permit only the preflight pipeline. Copy the generated **Issuer** and **Subject identifier**, then select **Keep as draft**.
3. In the Azure portal, open the assigned Dev UAMI and go to **Settings → Federated credentials → Add credentials**. Choose **Other issuer** and **Explicit subject identifier**. Paste the issuer and subject exactly as displayed in Azure DevOps, keep the token-exchange audience `api://AzureADTokenExchange`, and give the credential a name such as `fic-tiny-sales-dev`. Select **Add**. If the facilitator manages credentials for your UAMI, give them the issuer and subject from your draft so they can complete this step.
4. Return to your draft connection in Azure DevOps and select **Finish setup → Verify and save**. Record the connection name and check that the client ID matches your assigned Dev UAMI. [Microsoft’s manual setup guide](https://learn.microsoft.com/en-us/azure/devops/pipelines/release/configure-workload-identity?tabs=managed-identity&view=azure-devops#set-a-workload-identity-service-connection).

**Expected result** Your project has a verified, federated Dev service connection. The Azure subscription is the connection's Azure context. You will verify access to the Fabric workspaces separately by running the preflight.

### 2. Add the Dev preflight to Git

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

### 3. Register and run the preflight pipeline

1. In **Pipelines → New pipeline → Azure Repos Git**, choose your Code repository, then **Existing Azure Pipelines YAML file**. Select `dev` and `/.azuredevops/pipelines/dev-release-preflight.yml`. Save the pipeline. On its details page, use **… → Rename/move** and set its name to **Tiny Sales - Dev Preflight**. [Register an existing YAML pipeline](https://learn.microsoft.com/en-us/azure/devops/pipelines/get-started/clone-import-pipeline?view=azure-devops#clone-or-copy-a-pipeline) · [Pipeline settings](https://learn.microsoft.com/en-us/azure/devops/pipelines/customize-pipeline?view=azure-devops#pipeline-settings).
2. Run the pipeline manually from `dev`. When Azure DevOps reports that the pipeline needs permission to use the connection, open **View → Permit** and confirm **Permit**. This authorizes the preflight pipeline to use the connection. [Authorize a single pipeline](https://learn.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops#authorize-pipelines).
3. Open **Read Dev workspace and item identities** in the run log. Find `PREFLIGHT PASSED` and inspect the JSON. Compare `configured_release_identity` with the assigned UAMI and service connection. Compare the three verified names and IDs with your inventory. Find the physical item ID and workspace ID for `build_sales` and `sales`. Where Fabric also supplies `logicalId`, compare it with the Git `.platform` identity. The run also records the Code checkout revision and the declared Data and Reporting pins. [Logical and physical Fabric IDs](../../reference/fabric-item-identities.md).
4. Save the run link and observed IDs in the worksheet. For each Dev role, record its Git connection, pending updates and uncommitted workspace edits so you know what must be reconciled at the publishing handoff. [Dev preflight record](resources/dev-preflight-record.md).

**Expected result** The release identity reads the intended Dev workspace names and the six existing Tiny Sales items. You have a live baseline to compare with the first publish.

### 4. Inspect the exported relationships

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
| **Verify and save** fails | Compare the UAMI's client and tenant IDs and the credential's issuer, subject and audience with the draft connection. If verification reports an Azure access error, ask the facilitator to confirm access at the assigned scope. |
| Dev preflight job was skipped | Run from `refs/heads/dev`. Check the branch shown for the run. |
| Azure DevOps cannot resolve the service connection | Check `releaseServiceConnection` in the Dev environment file and confirm that this pipeline has permission to use the connection. |
| Azure CLI reports that the subscription does not exist or is unavailable | Check the connection's subscription ID and ask the facilitator to confirm that the UAMI can see that subscription. |
| Fabric returns HTTP 401 or 403 | Confirm the tenant setting, the caller's identity and the workspace role assignment. |
| The workspace name differs | Compare the configured GUID and expected name with the assigned inventory. Resolve the discrepancy before publishing. |
| An expected item is missing or appears twice | Inspect the workspace and the item role, type and name in the mask. Record the actual inventory before selecting a publish target. |

### Part A checkpoint

- [ ] You created and verified the federated Dev service connection and authorized the preflight pipeline to use it.
- [ ] The authenticated run verified all three Dev workspace names and recorded the expected item IDs.
- [ ] The worksheet records the Code revision, Data and Reporting pins, and the CI and preflight runs.
- [ ] The workspace Git state, active value set and exported references are recorded for the publishing handoff.

[Previous unit](../unit-07-configure-and-preview-release/README.md) · [Tutorial index](../../README.md)
