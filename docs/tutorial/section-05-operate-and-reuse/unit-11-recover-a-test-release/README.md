# Unit 11 - Diagnose and recover a failed Test release

Allow **about 60 minutes** with an available Azure Pipelines agent and reviewer.

Unit 9 gave you a Test manifest, and Unit 10 used release evidence to support a Prod decision. Now try reading that evidence from the point of view of the person on call. You’ll introduce one wrong workspace name and follow the failed attempt from the Azure DevOps Environment history to the configuration that caused it. Then you’ll fix it through Git and verify the recovered release.

### What you will learn

- Use deployment history, logs and a release manifest to identify where a run failed.
- Fix a Test configuration value through Git, then verify the corrected deployment and runtime results.
- Explain what redeploying definitions can restore and which data and configuration checks still matter.

### Before you begin

Use your team's [published Tiny Sales baseline](../README.md#start-an-advanced-lab-from-the-baseline). Open its Test record for the established source pins, Test wiring and smoke checks. Use the **Code** repo, the existing **Tiny Sales - Test Release** pipeline, and your assigned Test workspaces and authorized managed identity from [Unit 9](../../section-04-release-automation/unit-09-release-to-test/README.md). Arrange permission to create and authorize an Azure DevOps Environment, or have the facilitator do that step with you.

### Find the last known good state before retrying

It’s tempting to see a red Test run and choose **Rerun**. First, predict what would happen if the next attempt reads the same wrong workspace name from the same commit. The live comparison still has the same two inputs. Waiting a minute won’t change either one. The error message gives you a reason to inspect the configuration in Git before trying again.

When you’re on call, three views help you decide where to look. The Azure DevOps Environment history tells you which deployment jobs were recorded against the Test Environment and when. The manifest tells you what source and Fabric targets the publisher selected and which phase it reached. Fabric itself can tell you what items are present and what their last execution did. You’ll practice moving between those views using one controlled fault.

One decision belongs with the person diagnosing the failure, and another belongs with whoever can authorize a change. Here you’ll fix the expected name in Git and send it through review. The reviewer can see the narrow fix and its evidence. The operator then starts a fresh deployment from the corrected commit and verifies recovery.

### 1. Track Test deployments in Azure DevOps

When several pipelines can deploy to the same target, a support engineer needs to know which one last touched it and whether that attempt succeeded. An Azure DevOps Environment gives the target its own deployment history across the jobs that declare it. It also gives the target owner a place to restrict which pipelines can use it and to add target-wide approvals or checks when needed. In this unit, use that history during recovery to find the last known-good run. Then use its manifest to verify the exact Fabric workspaces, revisions and item IDs. The release mask chooses the actual Fabric targets, and the service connection supplies the identity. [Azure DevOps Environments](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/environments?view=azure-devops#view-deployment-history) · [Approvals and checks](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/approvals?view=azure-devops).

1. In your Azure DevOps project, open **Pipelines → Environments** and select **New environment** or **Create environment**. Name it **Tiny Sales - Test** and create it without a resource. If your team already has that Environment, open the existing one. In the environment's **Security → Pipeline permissions**, restrict access to **Tiny Sales - Test Release**. [Azure DevOps Environments](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/environments?view=azure-devops).
2. In your clean **Code** checkout, create the lab branch from the baseline tag you fetched in the section opener.

   ```powershell
   git switch -c feature/test-release-recovery refs/tags/tiny-sales-v1.0.0
   ```

3. Copy these starters into your participant Code repo.

   | Starter | Destination and settings |
   | --- | --- |
   | [Test recovery pipeline](../../../../.azuredevops/pipelines/test-release-recovery.yml) | Replace `.azuredevops/pipelines/test-release.yml`. Copy back your existing literal Data and Reporting repository names under `resources.repositories`. Keep the existing Test config and service connection. |
   | [Test entry point](../../../../toolkit/test_release.py) | `toolkit/test_release.py` |
   | [Shared publisher](../../../../toolkit/tiny_sales_release.py) | `toolkit/tiny_sales_release.py` |

   The registered pipeline keeps the same YAML path. The new YAML uses a deployment job so Azure DevOps can record deployments against **Tiny Sales - Test**. Keep the Test service connection and its permissions from Unit 9. [Deployment job with runOnce](https://learn.microsoft.com/en-us/azure/devops/pipelines/yaml-schema/jobs-deployment-strategy-run-once?view=azure-pipelines).
4. Use the Git review, stage, commit and push workflow from Unit 5. Commit as **Track Test deployments in Azure DevOps** and open a PR into `dev` with the same title. Update the validation results before completion.

   ```markdown
   ## Change
   Record Test deployments in the Tiny Sales - Test environment and retain evidence of completed publish phases.

   ## Validation
   - Reviewed the Test connection and repo resource names: <result>
   - [Notebook CI for this PR](<run-url>): <result>
   - After merge, record the successful baseline, deliberate failure and verified recovery runs.
   ```

**Expected result** The existing Test pipeline uses the reviewed recovery definition on `dev`. You can find runs of its deployment job from the Environment's **Deployments** tab. This applies **MS-10 Operational visibility**. [Fabric Minimum Standard](../../../source-guidelines/fabric-minimum-standard.md#minimum-standard-by-operating-model).

### 2. Establish the known-good Test release

1. Queue **Tiny Sales - Test Release** from `dev`. Select **Publish to Test after preflight**. If the first run asks for Environment permission, authorize the existing Test pipeline on **Tiny Sales - Test**.
2. In **Pipelines → Environments → Tiny Sales - Test → Deployments**, find the run. Open **test-release-evidence → test-release.json**. Record the full verified Code, Data and Reporting hashes, the Test value set and the relevant physical item IDs. Expect `status: published`, `phase: complete` and **Test** active.
3. Run `run_sales` in Code Test and confirm the activity parameters `test` and `tiny_sales_test`. Run `validate_release` and expect `SALES_SMOKE_PASSED` with **357.20 gross** and **204.70 revenue**. Open the report and confirm the Test model binding and **204.70 Total Revenue**. Record the runtime results and identify the owner who would respond to a failed Test run. [Unit 9 Test checks](../../section-04-release-automation/unit-09-release-to-test/README.md#4-review-what-changed) · [Recovery record](resources/test-recovery-record.md).

**Expected result** You have one known-good run with its exact Git revisions, deployed state and separate runtime evidence. This applies **MS-01 Ownership**, **MS-08 Release validation** and **MS-14 Release evidence**. The workshop captures manual runtime results. Model B calls for automated technical and runtime validation in Test and after Prod deployment. [Fabric Minimum Standard](../../../source-guidelines/fabric-minimum-standard.md#minimum-standard-by-operating-model).

### 3. Diagnose a rejected Test deployment

1. Fetch `origin` and start `feature/rehearse-test-name-mismatch` from `origin/dev` at the known-good Code commit from section 2. Edit only `codeWorkspaceName` in `config/environments/test.yml`. Append `-typo` to the exact assigned name. Keep the workspace IDs, service connection, source pins and Fabric workspaces as recorded for the baseline. This simulates a configuration typo or a stale expected name after a workspace rename. Commit as **Rehearse a Test workspace name mismatch**, push the feature branch and open a PR into `dev` with the same title. Tell the reviewer this is a deliberate workshop fault and complete it once the diff and normal CI checks have been reviewed.

   ```markdown
   ## Change
   Add a deliberate typo to the expected Code Test workspace name for the recovery exercise.

   ## Validation
   - Only codeWorkspaceName changed: <diff review result>
   - [Notebook CI for this PR](<run-url>): <result>
   - The next Test publish should reject the name mismatch during live preflight.
   ```

2. Queue **Tiny Sales - Test Release** from the resulting `dev` commit with **Publish to Test after preflight** selected. Find the failed run in the Environment history. In the release task log, look for `TEST RELEASE FAILED during preflight` and a message with the Code workspace ID, the expected name with `-typo`, and the actual name returned by Fabric. The release reached the live workspace check. The Unit 6 notebook check and Unit 7 offline preview work from Git, so a well-formed but incorrect workspace name can get through those checks.
3. Use the Environment history from section 1 to reopen the known-good run. Compare its manifest with the failed `test-release.json`. Expect `status: failed`, `phase: preflight`, a new Code hash and the same Data and Reporting hashes. The log shows the mismatch before `TEST PREFLIGHT PASSED`, and the manifest has no completed publish phases. The earlier Test report and table can still be present. Use deployment evidence to decide what this run changed and record who owns the fix. [Recovery record](resources/test-recovery-record.md) · [Release manifests](../../reference/release-manifests.md).

**Expected result** The Test history records an attempted deployment that the live target check stopped before publishing. You can trace the failure to one configuration value in Git. This applies **MS-06 Environment configuration**, **MS-10 Operational visibility** and **MS-11 Recovery**. [Fabric Minimum Standard](../../../source-guidelines/fabric-minimum-standard.md#minimum-standard-by-operating-model).

### 4. Fix the configuration and verify the release

1. Use the same fetch-and-branch pattern to start `feature/fix-test-workspace-name` at the current `dev`. Restore `codeWorkspaceName` to the exact assigned name, using the known-good configuration and workspace inventory as references. Commit as **Restore the Code Test workspace name**, push the feature branch and open a PR into `dev` with the same title. Check that the diff contains only the intended fix. Complete the PR after review and CI, then record the corrected Code commit.

   ```markdown
   ## Change
   Restore the expected name of the assigned Code Test workspace.

   ## Validation
   - [Failed Test preflight](<run-url>) showed <expected and actual names>.
   - Confirmed the corrected name against the known-good configuration and Fabric inventory.
   - [Notebook CI for this PR](<run-url>): <result>
   ```

2. Queue a **new** Test publish run from the corrected `dev` commit. Compare the manifest with the baseline and failed run. Expect `status: published`, `phase: complete`, **Test** active, and the same physical IDs for existing items. Verify that the Data and Reporting pins are unchanged and record which Code commit supplied the corrected settings.
3. Repeat the runtime checks from section 2. Record the recovered run, its validation results and who signs off the recovery. Use the three linked runs to explain the diagnosis and why the recovered release is ready for use.

This failure occurred before any Fabric writes. If a run fails during publishing, inspect the last completed phase, the failed phase and each affected workspace before deciding whether to retry or redeploy a known-good definition. A publish call that fails can still have made changes. Redeploying definitions restores definitions and bindings. Running `run_sales` separately regenerates the synthetic table. Historical data and external side effects need their own recovery actions. This applies **MS-05 Reproducible deployment** and **MS-11 Recovery**. [Fabric Minimum Standard](../../../source-guidelines/fabric-minimum-standard.md#minimum-standard-by-operating-model).

**Expected result** The history shows a successful baseline, a rejected attempt and a successful release from the corrected commit. Your record connects each run to its source, the fix and the verified runtime results.

### If a check fails

| Symptom | What to check |
| --- | --- |
| The run cannot use the Environment | Confirm the name matches exactly and the existing Test pipeline is listed in the Environment's pipeline permissions. |
| The typo run publishes successfully | Compare the run's Code revision with the deliberate change and check that the pipeline still uses the Unit 11 YAML and the checked-in Test config. |
| The run fails for a different reason | Read the failed task and manifest phase if one was produced. Resolve access or setup failures before comparing the expected and actual workspace names. |
| Definitions published but the smoke check failed | Check the latest `run_sales` result, parameter values and Data Test binding before interpreting the smoke notebook or report. |

### Completion checkpoint

- [ ] The lab branch started at the published Tiny Sales baseline.
- [ ] The Test Environment records the baseline, deliberate failure and recovery.
- [ ] You can show where preflight rejected the deployment and trace the corrected Code commit with the same Data and Reporting pins.
- [ ] You retained the recovered item IDs, runtime results and recovery owner in your record.

### What you built and where it leads

Put the known-good, failed and recovered runs in order. In the failed run you can point to a target mismatch during preflight. The exercise stopped before publishing, so the existing report can still display the result of the previous successful run. This is an important diagnostic habit. An old result can still look right when the new release failed to reach it.

Imagine a different run that reached publishing and failed after updating Code. Would you start with the same fix? Look at the completed phases and check the live workspace before deciding what to retry. A partially updated solution might need a controlled retry, a redeployment from a known-good snapshot, or a coordinated fix to the affected configuration. Use the live state to choose the recovery.

Give your recovery evidence to someone who didn’t see the exercise. They should be able to identify the bad input, the reviewed fix, the new deployment and the fresh runtime check. Tiny Sales can rebuild its synthetic table from the notebook. If a real workload already changed historical data or sent results elsewhere, the recovery decision also needs a plan for those effects. [Looking ahead — protecting historical data](../../reference/persisted-data-in-production.md).

[Publish and use the baseline](../README.md) · [Closing recap](../../closing-recap.md) · [Tutorial index](../../README.md)
