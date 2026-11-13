# Unit 11 - Diagnose and recover a partial Test release

Allow **55 minutes** with an available Azure Pipelines agent and reviewer. Bring the release tooling into `dev`, track a successful Test deployment, and recover from a run that stops between publishing Code and Reporting.

### What you will learn

- Use deployment history and a release manifest to identify which steps completed.
- Rerun the same reviewed snapshot and verify the recovered Test items and runtime results.
- Explain what redeploying definitions can restore and which data and configuration checks still matter.

### Before you begin

Complete [Unit 10](../../section-04-release-automation/unit-10-release-to-prod/README.md). Bring your Test and Prod run links and release records. You will use the **Code** repository, the existing **Tiny Sales - Test Release** pipeline and the same three Test workspaces and Test managed identity from [Unit 9](../../section-04-release-automation/unit-09-release-to-test/README.md). Arrange permission to create and authorize an Azure DevOps Environment, or have the facilitator do that step with you. Keep other Test deployments and shared Test edits paused for the three runs in this exercise.

### 1. Bring the Prod tooling into Code dev

1. In Azure Repos, review the changes added to Code `main` since the Unit 10 promotion. From a clean Code checkout, create a feature branch from the latest shared `dev`.

   ```powershell
   git status --short
   git fetch origin
   git switch -c feature/reconcile-release-tooling origin/dev
   ```

   `git status --short` lists local edits. Start when it prints nothing. Fetch refreshes your remote branch references. The switch starts a new branch at `origin/dev`. [Git basics](../../pre-reads/git-basics.md#get-updates-and-handle-overlaps).
2. If the reviewed Prod tooling is the only change to bring back, run `git merge origin/main` on the feature branch. This combines the reviewed `main` history with your Dev starting point. If `main` includes other changes, bring over only the Unit 10 tooling and Prod settings on the feature branch and review the diff before committing as **Reconcile Prod release tooling into dev**. If Git reports a conflict, inspect both sides with the reviewer and preserve current Dev definitions and release mask pins. If the tooling is already reconciled, record the existing PR and continue to section 2. [Conflict recovery](../../auxiliary/aux-01-recover-from-source-conflicts/README.md).
3. Push with `git push -u origin feature/reconcile-release-tooling` and open a PR into `dev` titled **Reconcile Prod release tooling into dev**. The `-u` option sets the upstream branch for later pushes. Review the PR files, preserve the current Dev pins and complete after required CI passes. Replace the placeholders with what you observed.

   ```markdown
   ## Change
   Bring the reviewed Unit 10 release tooling from main into dev.

   ## Validation
   - Reviewed current Dev definitions and source pins: <result>
   - [Notebook CI for this PR](<run-url>): <result>
   ```

**Expected result** The shared publisher and both release entry points are available on Code `dev`. The Prod pipeline continues to get its authorized release tooling from Code `main`. This applies **MS-03 Change control & traceability**. [Fabric Minimum Standard](../../../source-guidelines/fabric-minimum-standard.md#minimum-standard-by-operating-model).

### 2. Track Test deployments in Azure DevOps

1. In your Azure DevOps project, open **Pipelines → Environments** and select **New environment** or **Create environment**. Name it **Tiny Sales - Test**. Create it without a resource. In the environment's **Security → Pipeline permissions**, restrict access to **Tiny Sales - Test Release**. An empty Azure DevOps Environment gives the pipeline a place to record deployment history. Fabric workspace IDs still come from your release mask, and the Test service connection still supplies the deployment identity. [Azure DevOps Environments](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/environments?view=azure-devops).
2. Create a feature branch from the updated Code `dev`.

   ```powershell
   git fetch origin
   git switch -c feature/test-release-recovery origin/dev
   ```

3. Copy these starters into your participant Code repo.

   | Starter | Destination and settings |
   | --- | --- |
   | [Test recovery pipeline](../../../../.azuredevops/pipelines/test-release-recovery.yml) | Replace `.azuredevops/pipelines/test-release.yml`. Copy back your existing literal Data and Reporting repository names under `resources.repositories`. Keep the existing Test config and service connection. |
   | [Test entry point](../../../../toolkit/test_release.py) | `toolkit/test_release.py` |
   | [Shared publisher](../../../../toolkit/tiny_sales_release.py) | `toolkit/tiny_sales_release.py` |

   The registered pipeline keeps the same YAML path. The new YAML uses a deployment job so Azure DevOps can record deployments against **Tiny Sales - Test**. Keep the Test service connection and its permissions from Unit 9. The rehearsal option defaults to off. [Deployment job with runOnce](https://learn.microsoft.com/en-us/azure/devops/pipelines/yaml-schema/jobs-deployment-strategy-run-once?view=azure-pipelines).
4. Commit as **Track Test deployments and add a recovery rehearsal**, push the feature branch and open a PR into `dev` with the same title. Update the validation results before completion.

   ```markdown
   ## Change
   Record Test deployments in the Tiny Sales - Test environment and add a manual rehearsal stop before Reporting.

   ## Validation
   - Reviewed the Test connection and repo resource names: <result>
   - [Notebook CI for this PR](<run-url>): <result>
   - After merge, record the successful baseline, deliberate failure and verified recovery runs.
   ```

**Expected result** The existing Test pipeline uses the reviewed recovery definition on `dev`. You can find runs of its deployment job from the Environment's **Deployments** tab. This applies **MS-10 Operational visibility**. [Fabric Minimum Standard](../../../source-guidelines/fabric-minimum-standard.md#minimum-standard-by-operating-model).

### 3. Establish the known-good Test release

1. Queue **Tiny Sales - Test Release** from `dev`. Select **Publish to Test after preflight**, leave **Rehearse a failure before Reporting** clear, and leave the expected Code commit as `current`. If the first run asks for Environment permission, authorize the existing Test pipeline on **Tiny Sales - Test**.
2. In **Pipelines → Environments → Tiny Sales - Test → Deployments**, find the run. Open **test-release-evidence → test-release.json**. Record the full verified Code, Data and Reporting hashes, the Test value set and the relevant physical item IDs. Expect `status: published`, `phase: complete` and **Test** active.
3. Run `run_sales` in Code Test and confirm the activity parameters `test` and `tiny_sales_test`. Run `validate_release` and expect `SALES_SMOKE_PASSED` with **357.20 gross** and **204.70 revenue**. Open the report and confirm the Test model binding and **204.70 Total Revenue**. Record the runtime results and identify the owner who would respond to a failed Test run. [Unit 9 Test checks](../../section-04-release-automation/unit-09-release-to-test/README.md#4-review-what-changed) · [Recovery record](resources/test-recovery-record.md).

**Expected result** You have one known-good run with its exact Git revisions, deployed state and separate runtime evidence. This applies **MS-01 Ownership**, **MS-08 Release validation** and **MS-14 Release evidence**. The workshop captures manual runtime results. Model B calls for automated technical and runtime validation in Test and after Prod deployment. [Fabric Minimum Standard](../../../source-guidelines/fabric-minimum-standard.md#minimum-standard-by-operating-model).

### 4. Diagnose the deliberate partial release

1. Queue the same Test pipeline from `dev`. Select **Publish to Test after preflight** and **Rehearse a failure before Reporting**. Enter the full Code hash from the known-good manifest in **Expected full Code commit**. The pipeline checks the queued commit before publishing. The two other revisions come from the release mask at that Code commit. If `dev` has advanced, use the exact-commit option in section 5.
2. Open the failed run from the Environment history. In the release task log, find **Deliberate Test rehearsal stop after Data and Code publishing**. Open its `test-release.json`. Compare `verified_source_revisions` with the known-good run and locate `status: failed`, `phase: rehearsal stop before Reporting` and `completed_publish_phases`. The manifest lists the Data lakehouse, Code library and notebooks, and Code Data Pipeline publish calls that returned. The rehearsal stops before sending a publish request to Reporting.
3. Compare the starting IDs in the failed manifest and the observed Code items with the live Test inventory. Open the existing Test report and find its model. The report can still be present from the baseline. Its presence does not establish that the failed run published it. Record the last successful step, the first unfinished step and the recovery action. [Recovery record](resources/test-recovery-record.md) · [Release manifests](../../reference/release-manifests.md).

**Expected result** The history shows a failed deployment after several successful publish calls. You can explain why the affected workspaces need to be checked independently. This applies **MS-10** and **MS-11 Recovery**. [Fabric Minimum Standard](../../../source-guidelines/fabric-minimum-standard.md#minimum-standard-by-operating-model).

### 5. Recover and verify the result

1. Queue a **new** run with **Publish to Test after preflight** selected, **Rehearse a failure before Reporting** clear and the same expected Code hash. If `dev` has advanced, ask the facilitator to queue the saved commit on `dev` with the same parameters. Confirm the run uses the same three hashes before treating its result as recovery evidence. [Queue a pipeline at a commit](https://learn.microsoft.com/en-us/cli/azure/pipelines?view=azure-cli-latest#az-pipelines-run).
2. Compare the new manifest with the baseline and failed run. Expect all publish phases, `status: published`, the same physical IDs for existing items and **Test** active. Find the model and report in Reporting Test and inspect their bindings.
3. Repeat the runtime checks from section 3. Record the recovered run, its validation results and who signs off the recovery.

The exercise repeats the same source because the deliberate failure interrupted publishing. In a real incident, first establish whether the cause was a transient failure, bad source, or target configuration. That determines whether you retry, correct the configuration, or select a previously verified release. A definition redeploy restores definitions and bindings. A rerun of `run_sales` regenerates the synthetic table. Historical data and external side effects need their own recovery actions. This applies **MS-05 Reproducible deployment**, **MS-06 Environment configuration** and **MS-11 Recovery**. [Fabric Minimum Standard](../../../source-guidelines/fabric-minimum-standard.md#minimum-standard-by-operating-model).

**Expected result** The successful, failed and recovered runs appear in Test deployment history. The manifests and runtime results show that the same reviewed snapshot was recovered.

### If a check fails

| Symptom | What to check |
| --- | --- |
| The run cannot use the Environment | Confirm the name matches exactly and the existing Test pipeline is listed in the Environment's pipeline permissions. |
| The Code revision check stops the run | Compare the full expected hash with the run's Code commit. Queue the baseline commit and keep the guard in place. |
| The run fails before the rehearsal stop | Read the failed task and manifest phase if one was produced. Resolve that failure before collecting rehearsal evidence. |
| Definitions published but the smoke check failed | Check the latest `run_sales` result, parameter values and Data Test binding before interpreting the smoke notebook or report. |

### Completion checkpoint

- [ ] The release tooling is reconciled into Code `dev` through review.
- [ ] The Test Environment records the baseline, deliberate failure and recovery.
- [ ] You can point to the last completed phase in the failed manifest and show the same three hashes in the recovered release.
- [ ] You retained the recovered item IDs, runtime results and recovery owner in your record.

[Previous unit](../../section-04-release-automation/unit-10-release-to-prod/README.md) · [Tutorial index](../../README.md)
