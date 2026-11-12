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
   | [Release dependencies](../../../../toolkit/requirements-release.txt) | `toolkit/requirements-release.txt` |
   | [Test release pipeline](../../../../.azuredevops/pipelines/test-release.yml) | `.azuredevops/pipelines/test-release.yml` |
   | Validation notebook files [`.platform`](../../../../sample/tiny-sales/validate_release.Notebook/.platform) and [`notebook-content.py`](../../../../sample/tiny-sales/validate_release.Notebook/notebook-content.py) | `validate_release.Notebook/` |

3. In `config/environments/test.yml`, enter the Test UAMI, connection and exact workspace display names. Verify the IDs under `environments.test.workspaces` in your release mask. In `test-release.yml`, replace `REPLACE_WITH_DATA_REPO` and `REPLACE_WITH_REPORTING_REPO` with the repository names in `sources.data.repository` and `sources.reports.repository` in the mask.

   The Test service connection name comes from the environment template. Azure Pipelines requires a literal value for `resources.repositories[].name`, so you enter the two repository names in the pipeline definition as well as in the mask. The declaration lets Azure DevOps identify and authorize the repositories for checkout. The mask gives the release command the exact commit to select from each repository's `dev` history. The command checks both the repository name and the pinned commit before publishing. [Azure Pipelines repository resources](https://learn.microsoft.com/en-us/azure/devops/pipelines/yaml-schema/resources-repositories-repository?view=azure-pipelines).

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
   git add -- config/environments/test.yml toolkit/fabric_preflight.py toolkit/test_release.py toolkit/requirements-release.txt .azuredevops/pipelines/test-release.yml validate_release.Notebook
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
3. Run from `dev` after any previous Test release finishes. If Azure DevOps prompts for access to the Data or Reporting repository, authorize the pipeline for that repository. In **Preflight and publish Tiny Sales to Test**, look for `TEST PREFLIGHT PASSED`, then `TEST RELEASE PUBLISHED`. The release uses a temporary copy of the definitions. It resolves the Test lakehouse and SQL endpoint, publishes Code items with Test bindings and the `Test` value set, then publishes the semantic model and report. [Multi-repo checkout](https://learn.microsoft.com/en-us/azure/devops/pipelines/repos/multi-repo-checkout) · [Fabric publishing and parameterization](https://microsoft.github.io/fabric-cicd/1.4.0/how_to/parameterization/).

**Expected result** Tiny Sales definitions are deployed across Code, Data and Reporting Test. The run publishes a `test-release-evidence` artifact with the source revisions, workspace and item IDs, value set and outcome.

### 4. Review what changed

1. Open `test-release.json` in the run artifact. Check `status` is `published`, compare the three source revisions with the selected source, and check `active_value_set` is `Test`.
2. Compare `before_item_ids` with `published_items`. Find the existing `build_sales` physical ID and the new `validate_release` physical ID. Inspect any owner or creator field the workspace shows for each notebook. Record the field's exact label and value. If the UI has no field, record that observation. [Fabric item ownership](https://learn.microsoft.com/en-us/fabric/fundamentals/item-ownership-take-over).
3. Open `sales_overview` in Reporting Test and confirm it uses `sales_model` in Reporting Test. Record the run and your observations. [Test release record](resources/test-release-record.md).

The artifact records deployment evidence. If time allows, run `run_sales` in Code Test, then run `validate_release` to check the refreshed table for **357.20 gross** and **204.70 revenue**. Record both run links and the smoke result separately. A later release can automate the check, persist pass/fail run metadata and use evidence for the exact candidate as a PR gate to `main`.

### If a check fails

| Symptom | What to check |
| --- | --- |
| The pipeline needs permission to use the connection | Check that **Tiny Sales - Test Release** is listed under the connection's restricted **Pipeline permissions**. |
| Azure DevOps cannot find a repository | Check the two literal repository names under `resources.repositories` in `test-release.yml` and confirm the pipeline has access to both repositories. |
| The release cannot find the validation notebook's `.platform` file | Check the committed filename in Azure Repos and remove any trailing `.txt` before committing the file. |
| Fabric returns HTTP 403 or an unexpected workspace name | Compare the Test UAMI’s workspace roles and the physical IDs and expected names with your assigned Test inventory. |
| The preflight rejects a pin or a source definition | Check the pinned commit is in the corresponding `dev` history and the definition matches the bindings inspected in Unit 8. |
| A publish step fails | Open the run log and the artifact's `phase`. Inspect the target items before retrying the same revision. Earlier publish phases can have completed. |

### Completion checkpoint

- [ ] The Test pipeline passed its preflight and published the solution.
- [ ] The release artifact records the selected source, target IDs and `Test` value set.
- [ ] The worksheet records the report's Test model and the observable differences between creating and updating an item.

[Previous unit](../unit-08-publish-shared-dev/README.md) · [Tutorial index](../../README.md)
