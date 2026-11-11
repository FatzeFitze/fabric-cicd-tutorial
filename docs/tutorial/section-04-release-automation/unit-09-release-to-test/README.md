# Unit 9 — Release the same source to Test

## Part A. Prepare Test and record its starting state

Allow **25–30 minutes**. You will create the Test service connection, give the Test deployment identity access to your workspaces and capture what already exists. Keep this record so you can distinguish a first creation from an update when you release to Test.

### Before you begin

Complete the [Unit 8 Dev preflight](../unit-08-publish-shared-dev/README.md) and keep its run link. Have the assigned Test UAMI name, the subscriptions and resource groups for the identity and service connection, and the names and IDs of your Code, Data and Reporting Test workspaces. You need the Admin role in those three workspaces.

### 1. Set up the Test deployment identity

1. Follow [Unit 8’s service connection steps](../unit-08-publish-shared-dev/README.md#1-create-your-dev-service-connection) with the supplied **Test** values and the name `sc-tiny-sales-test`. Leave **Grant access permission to all pipelines** clear.
2. Follow [Unit 8’s workspace access steps](../unit-08-publish-shared-dev/README.md#2-grant-the-deployment-identity-access-in-fabric) to give the **Test UAMI** the **Contributor** role in your Code, Data and Reporting **Test** workspaces. Check all three entries in **Manage access**.

**Expected result** The Test connection uses the Test UAMI, and that identity has Contributor in your three Test workspaces. The Dev preflight keeps using its own Dev connection.

### 2. Add the Test baseline pipeline

1. Update your local Code `dev` branch and create a branch for this change.

   ```powershell
   git switch dev
   git pull --ff-only origin dev
   git switch -c feature/test-release-baseline
   ```

2. Copy these files into the matching paths in your Code checkout. Replace the existing preflight script with the updated copy. The Test pipeline uses its inventory mode so it can list workspaces that contain only the earlier native deployment or are still empty.

   | Starter | Destination |
   | --- | --- |
   | [Test environment settings](../../../../config/environments/test.yml) | `config/environments/test.yml` |
   | [Preflight command](../../../../toolkit/fabric_preflight.py) | `toolkit/fabric_preflight.py` |
   | [Test baseline pipeline](../../../../.azuredevops/pipelines/test-release-baseline.yml) | `.azuredevops/pipelines/test-release-baseline.yml` |

3. Set `releaseUamiName` to the assigned Test UAMI and `releaseServiceConnection` to the Test connection you created. Enter the exact Test workspace display names in `config/environments/test.yml` and compare their IDs from your inventory with `environments.test.workspaces` in the release mask.
4. Stage, commit and push the change.

   ```powershell
   git add -- config/environments/test.yml toolkit/fabric_preflight.py .azuredevops/pipelines/test-release-baseline.yml
   git diff --cached --check
   git commit -m "Record the Test baseline before release"
   git push -u origin feature/test-release-baseline
   ```

5. Open a PR into `dev` titled **Record the Test baseline before release**. Complete it after the required CI check passes.

   ```markdown
   ## Change
   Verify the assigned Test workspace IDs and capture the item inventory using the Test deployment identity.

   ## Validation
   Review required CI for this PR. After merge, run the Test baseline and record the verified workspaces and item inventory.
   ```

**Expected result** The Test pipeline and environment settings are reviewed and merged into `dev`.

### 3. Run the baseline and inspect ownership

1. In **Pipelines → New pipeline → Azure Repos Git**, select the Code repository and **Existing Azure Pipelines YAML file**. Select `dev` and `/.azuredevops/pipelines/test-release-baseline.yml`. Save the pipeline and name it **Tiny Sales - Test Baseline**.
2. Run from `dev`. If prompted, select **View → Permit**, then confirm **Permit** for this pipeline. In **Read Test workspace and item identities**, find `PREFLIGHT PASSED`. Compare `verified_workspaces` with your inventory and the configured identity with the Test connection you created. [Authorize a single pipeline](https://learn.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops#authorize-pipelines).
3. In `workspace_items.code`, check whether the `validate_release` notebook is absent. Find `build_sales` from the earlier native promotion and record its physical ID if present. In Code Test, use item details or the workspace list to inspect any owner or creator field exposed for `build_sales`. Record the exact label and what you saw. If no such field is exposed, record that observation. Keep both notebooks untouched so the later release can distinguish creation from update. [Fabric item ownership](https://learn.microsoft.com/en-us/fabric/fundamentals/item-ownership-take-over).
4. Save the run link and observations in the worksheet. The logged Code checkout and declared Data and Reporting pins describe the input to the baseline. The release will use the exact snapshot validated in Dev. Keep its three revisions with the release evidence when that snapshot is selected. [Test release record](resources/test-release-record.md).

**Expected result** You have a live inventory from the Test identity and an ownership baseline for the comparison item. The baseline reads workspace and item information.

### If a check fails

| Symptom | What to check |
| --- | --- |
| Fabric returns HTTP 403 or an unexpected workspace name | Compare the Test UAMI’s workspace roles and the physical IDs and expected names with your assigned Test inventory. |
| The fresh notebook already exists or `build_sales` is missing | Record the actual state and ask the facilitator to reconcile it before the release comparison. |

### Part A checkpoint

- [ ] The Test connection and three workspace role assignments are recorded.
- [ ] The Test baseline run verified all three workspaces.
- [ ] The record shows whether `validate_release` was absent and captures the existing comparison item's ID and any ownership information visible.

[Previous unit](../unit-08-publish-shared-dev/README.md) · [Tutorial index](../../README.md)
