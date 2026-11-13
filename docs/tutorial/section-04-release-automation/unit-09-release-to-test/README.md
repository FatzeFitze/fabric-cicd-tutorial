# Unit 9 — Publish Tiny Sales to Test

Allow **45–55 minutes**. In one Azure Pipeline run, verify the reviewed source and the Test workspaces, then publish Tiny Sales under the Test deployment identity. Compare the before and after item IDs in the release evidence.

### Before you begin

Complete the [Unit 8 Dev preflight](../unit-08-publish-shared-dev/README.md). Keep the Data and Reporting pins from the reviewed release mask. In Data Test, confirm the `sales` table from [Unit 3](../../section-02-model-a/unit-03-native-promotion/README.md) is visible in the lakehouse's SQL analytics endpoint. In Code Test, locate the native `build_sales` notebook and record its displayed owner or creator if the workspace exposes one. The existing lakehouse and notebook are the starting point for this release. Use this pipeline as the writer for the exercise.

Have the assigned Test UAMI name, the Azure subscriptions and resource groups for the identity and connection, and the names and IDs of your Code, Data and Reporting Test workspaces. You need Admin on those workspaces to grant the Test identity access.

### 1. Set up the Test deployment identity

1. Follow [Unit 8’s service connection steps](../unit-08-publish-shared-dev/README.md#1-create-your-dev-service-connection) with the supplied **Test** values and the name `sc-tiny-sales-test`. Leave **Grant access permission to all pipelines** clear.
2. Follow [Unit 8’s workspace access steps](../unit-08-publish-shared-dev/README.md#2-grant-the-deployment-identity-access-in-fabric) to give the **Test UAMI** the **Contributor** role in your Code, Data and Reporting **Test** workspaces. Check all three entries in **Manage access**.

**Expected result** The Test connection uses the Test UAMI, and that identity has Contributor in your three Test workspaces. The Dev preflight keeps using its own Dev connection.

### 2. Add the Test release pipeline

1. Update your local Code `dev` branch and create a branch for this change.

   ```powershell
   git switch dev
   git pull --ff-only origin dev
   git switch -c feature/test-release
   ```

2. Copy these starters into your Code checkout. Use the current preflight module from the tutorial if your copy predates the Test inventory support.

   | Starter | Destination |
   | --- | --- |
   | [Test environment settings](../../../../config/environments/test.yml) | `config/environments/test.yml` |
   | [Preflight command](../../../../toolkit/fabric_preflight.py) | `toolkit/fabric_preflight.py` |
   | [Test release command](../../../../toolkit/test_release.py) | `toolkit/test_release.py` |
   | [Shared Tiny Sales publisher](../../../../toolkit/tiny_sales_release.py) | `toolkit/tiny_sales_release.py` |
   | [Release dependencies](../../../../toolkit/requirements-release.txt) | `toolkit/requirements-release.txt` |
   | [Test release pipeline](../../../../.azuredevops/pipelines/test-release.yml) | `.azuredevops/pipelines/test-release.yml` |
   | Validation notebook files [`.platform`](../../../../sample/tiny-sales/validate_release.Notebook/.platform) and [`notebook-content.py`](../../../../sample/tiny-sales/validate_release.Notebook/notebook-content.py) | `validate_release.Notebook/` |

3. In `config/environments/test.yml`, enter the Test UAMI, connection and exact workspace display names. Verify the IDs under `environments.test.workspaces` in your release mask. In `test-release.yml`, replace `REPLACE_WITH_DATA_REPO` and `REPLACE_WITH_REPORTING_REPO` with the repository names in `sources.data.repository` and `sources.reports.repository` in the mask.

   The Test service connection name comes from the environment template. Azure Pipelines requires a literal value for `resources.repositories[].name`, so you enter the two repository names in the pipeline definition as well as in the mask. The declaration lets Azure DevOps identify and authorize the repositories for checkout. The mask gives the release command the exact commit to select from each repository's `dev` history. The command checks both the repository name and the pinned commit before publishing. [Azure Pipelines repository resources](https://learn.microsoft.com/en-us/azure/devops/pipelines/yaml-schema/resources-repositories-repository?view=azure-pipelines).

   For this exercise, copying two names keeps setup simple. A team that provisions many pipelines can generate the checkout declarations from the release mask before Azure DevOps loads the YAML. That gives the repository names a single source of truth while still supplying the literal values Azure DevOps requires.

4. Prepare the validation notebook's source identity before staging the files.

   - Make sure the metadata file is named exactly `.platform`. If your browser saved it as `.platform.txt`, remove the trailing `.txt` and keep the leading dot. In Windows File Explorer, turn on **View → Show → File name extensions** to see the full filename. From the Code repo root you can also rename it in PowerShell.

     ```powershell
     Rename-Item -LiteralPath '.\validate_release.Notebook\.platform.txt' -NewName '.platform'
     ```

   - Run this once in a **PowerShell terminal**, such as the PowerShell tab in VS Code.

     ```powershell
     [guid]::NewGuid().ToString()
     ```

   - Open `validate_release.Notebook/.platform`. Under `config.logicalId`, replace `REPLACE_WITH_STABLE_GUID` with the printed GUID and keep the surrounding quotes. Commit that value with `notebook-content.py` before the first deployment. Because `validate_release` is a new source item, a freshly generated, unique, nonzero GUID is enough to establish its logical identity. Keep that same value for the notebook across releases and environments. Fabric assigns a physical item ID when it creates the notebook in a workspace. For an existing item exported from Fabric, preserve its existing logical ID. [Logical and physical IDs in Fabric](../../reference/fabric-item-identities.md#assign-a-logical-id-to-a-new-source-item).
5. Stage, commit and push the change.

   ```powershell
   git add -- config/environments/test.yml toolkit/fabric_preflight.py toolkit/test_release.py toolkit/tiny_sales_release.py toolkit/requirements-release.txt .azuredevops/pipelines/test-release.yml validate_release.Notebook
   git diff --cached --name-only -- validate_release.Notebook
   git diff --cached --check
   git commit -m "Add the managed Test release"
   git push -u origin feature/test-release
   ```

   The staged file list should show `validate_release.Notebook/.platform` and `validate_release.Notebook/notebook-content.py`.

6. Open a PR into `dev` titled **Add the managed Test release**. Complete it after the required CI check passes.

   ```markdown
   ## Change
   Check the selected source and targets, then publish Tiny Sales to Test under the Test deployment identity.

   ## Validation
   Review required CI for this PR. After merge, run the Test release and retain the deployment evidence.
   ```

**Expected result** The release pipeline, configuration and new notebook are reviewed and merged into `dev`.

### 3. Authorize and run the Test release

1. In **Pipelines → New pipeline → Azure Repos Git**, select your Code repository and **Existing Azure Pipelines YAML file**. Select `dev` and `/.azuredevops/pipelines/test-release.yml`. Use the menu next to **Run** to select **Save**, then use **… → Rename/move** to name it **Tiny Sales - Test Release**. [Pipeline settings](https://learn.microsoft.com/en-us/azure/devops/pipelines/customize-pipeline?view=azure-devops#pipeline-settings).
2. Under **Project settings → Pipelines → Service connections**, open your Test connection and choose **… → Security**. Keep access restricted under **Pipeline permissions**, choose **Add pipeline** (**+**), and select **Tiny Sales - Test Release**. A connection Administrator authorizes the pipeline. An operator with **Queue builds** permission can start it. The authorized task uses the Test UAMI, whose Fabric workspace role controls what it can publish. [Who can authorize, queue and deploy?](../../reference/release-service-connections.md#who-can-authorize-queue-and-deploy).
3. Authorize **Tiny Sales - Test Release** to check out both the Data and Reporting repositories. Choose either option.

   - **On the first run.** If the run waits for repository access, open the pending resource request and select **Permit** for the requested repositories. The run can proceed once both are authorized. [First-run repository authorization](https://learn.microsoft.com/en-us/azure/devops/pipelines/security/secure-access-to-repos?view=azure-devops#protect-access-to-repositories-in-yaml-pipelines).
   - **Before the first run.** With permission to manage the repository, open **Project settings → Repositories → your Data repository → Security → Pipeline permissions**. Select **+** and add **Tiny Sales - Test Release**. Repeat for Reporting. Keep access scoped to the intended pipelines. [Preauthorize a repository resource](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/repository-resource?view=azure-devops#add-pipeline-permissions-to-a-repository-resource).

   Repository authorization controls which pipeline can use the repository. The Azure DevOps build identity also needs **Read** access for checkout. The Test UAMI in the service connection is the identity that publishes to Fabric. [Pipeline repository access](https://learn.microsoft.com/en-us/azure/devops/pipelines/security/secure-access-to-repos?view=azure-devops).

4. In **Run pipeline**, select `dev`. The **Publish to Test after preflight** checkbox is clear by default. Leave it clear for an optional read-only run. The artifact then shows `status: preflight_passed` and records the source and starting inventory. To complete the exercise, select the checkbox and run after any previous Test release finishes. The pipeline reruns preflight for the selected revision and publishes only after those checks pass. [Azure Pipelines runtime parameters](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/runtime-parameters?view=azure-devops) · [Multi-repo checkout](https://learn.microsoft.com/en-us/azure/devops/pipelines/repos/multi-repo-checkout).
5. In **Preflight and publish Tiny Sales to Test**, look for `TEST PREFLIGHT PASSED`, then `TEST RELEASE PUBLISHED`. The release uses a temporary copy of the definitions. It resolves the Test lakehouse and SQL endpoint, publishes Code items with Test bindings and the `Test` value set, then publishes the semantic model and report. [Fabric publishing and parameterization](https://microsoft.github.io/fabric-cicd/1.4.0/how_to/parameterization/).

The checkbox makes intent explicit when someone queues a manual release into a shared environment. An automated delivery flow can use a reviewed branch or release trigger to request publishing. For Prod, a resource administrator can also require an approval or a branch check on the deployment environment or service connection. [Approvals and checks](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/approvals?view=azure-devops).

**Expected result** Tiny Sales definitions are deployed across Code, Data and Reporting Test. The run publishes a `test-release-evidence` artifact with the source revisions, workspace and item IDs, value set and outcome.

### 4. Review what changed

The Model B **MS-14 Release evidence** control asks you to connect the source state, deployment and validation result. Use the manifest for the source and deployment evidence, then add your validation observations to the same release record. [Fabric Minimum Standard](../../../source-guidelines/fabric-minimum-standard.md#minimum-standard-by-operating-model).

1. Open `test-release.json` in the run artifact. Check `status` is `published`, compare the three verified source revisions with the selected source, and check `active_value_set` is `Test`. For help reading the fields and examples of how teams use this evidence in reviews, see [Read and design a release manifest](../../reference/release-manifests.md).
2. Compare `before_item_ids` with `published_items`. Find the existing `build_sales` physical ID and the new `validate_release` physical ID. Inspect any owner or creator field the workspace shows for each notebook. Record the field's exact label and value. If the UI has no field, record that observation. [Fabric item ownership](https://learn.microsoft.com/en-us/fabric/fundamentals/item-ownership-take-over).
3. Open `sales_overview` in Reporting Test and confirm it uses `sales_model` in Reporting Test. Record the run and your observations. [Test release record](resources/test-release-record.md).

The artifact records deployment evidence. If time allows, run `run_sales` in Code Test, then run `validate_release` to check the refreshed table for **357.20 gross** and **204.70 revenue**. Record both run links and the smoke result separately. A later release can automate the check, persist pass/fail run metadata and use evidence for the exact candidate as a PR gate to `main`.

### If a check fails

| Symptom | What to check |
| --- | --- |
| The pipeline needs permission to use the connection | Check that **Tiny Sales - Test Release** is listed under the connection's restricted **Pipeline permissions**. |
| The run passed with `status: preflight_passed` | Select **Publish to Test after preflight** when queuing the release you intend to deploy. |
| Azure DevOps cannot find a repository | Check the two literal repository names under `resources.repositories` in `test-release.yml` and confirm the pipeline has access to both repositories. |
| `test_release.py: error: unrecognized arguments: --mode preflight` | Check the Code revision shown for the run. In Azure Repos, open `toolkit/test_release.py` at that revision and look for the `--mode` argument. Merge the matching pipeline and Python starters into `dev`, then queue a new run from `dev`. |
| Python cannot import `toolkit.tiny_sales_release` | Copy the Test command and the shared publisher from the same tutorial revision. Verify both are committed at the queued Code revision. |
| The release cannot find the validation notebook's `.platform` file | Check the committed filename in Azure Repos and remove any trailing `.txt` before committing the file. |
| Fabric returns HTTP 403 or an unexpected workspace name | Compare the Test UAMI’s workspace roles and the physical IDs and expected names with your assigned Test inventory. |
| The preflight rejects a pin or a source definition | Check the pinned commit is in the corresponding `dev` history and the definition matches the bindings inspected in Unit 8. |
| The preflight rejects the notebook activity reference | Check the `TridentNotebook` activity in `run_sales.DataPipeline/pipeline-content.json` on the run's Code revision. A same-workspace Git binding uses the all-zero `workspaceId` with the `notebookId` from `build_sales.Notebook/.platform` (`config.logicalId`). An explicit workspace reference uses the Code Dev workspace ID in the release mask. The release resolves the physical Code Test IDs before publishing the activity. |
| A publish step fails | Open the run log and the artifact's `phase`. Inspect the target items before retrying the same revision. Earlier publish phases can have completed. |

### Completion checkpoint

- [ ] The Test pipeline passed its preflight and published the solution.
- [ ] The release artifact records the selected source, target IDs and `Test` value set.
- [ ] The worksheet records the report's Test model and the observable differences between creating and updating an item.

[Previous unit](../unit-08-publish-shared-dev/README.md) · [Tutorial index](../../README.md) · [Next: Approve and publish Tiny Sales to Prod](../unit-10-release-to-prod/README.md)
