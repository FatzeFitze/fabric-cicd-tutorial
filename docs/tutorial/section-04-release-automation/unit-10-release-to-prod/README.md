# Unit 10 - Approve and publish Tiny Sales to Prod

Allow **30 minutes** once the Prod connection and release branch are ready, plus **5–10 minutes** for the recap. Use the Test release from Unit 9 to select the same Code, Data and Reporting commits for an approved release to simulated Prod. Then verify that the Prod managed identity created `validate_release` and that Tiny Sales runs against the Prod data.

You will connect a Test run to a Prod approval, verify both workspace bindings and item identities, and use Fabric runtime evidence to check the release.

### Before you begin

- Open your completed [Unit 9 Test release](../unit-09-release-to-test/README.md). Keep the run link, its `test-release.json` artifact and the Test runtime results. If you skipped runtime checks, run them in Test and record the result against that release before asking for Prod approval. If Test has since been redeployed, verify which snapshot is live before using new smoke results.
- Use the three simulated Prod workspaces from [Unit 3](../../section-02-model-a/unit-03-native-promotion/README.md#6-authorize-and-promote-to-simulated-prod). Confirm `sales` exists and its table is queryable at the Data Prod SQL analytics endpoint. Locate `build_sales` in Code Prod and record its physical ID and any visible ownership information. Check that `validate_release` is absent from Code Prod. Leave its creation to the managed release.
- Bring your assigned Prod workspace names and IDs, Prod user-assigned managed identity (UAMI) name, and the Azure subscription and resource group selections from Unit 8's setup. Arrange a PR reviewer and coordinate with the service connection administrator and the designated Prod approver. You or the facilitator need **Edit policies** on the Code repository's `main` branch.

### How one release spans three repositories

Each repo has its own `dev` history. The Test run records one **release candidate** made up of three exact commits that were deployed together. The Code repo also holds the release mask that names the Data and Reporting repos and pins their commits. A pin is a full commit hash, so a later change on either `dev` branch cannot change the contents of the candidate. [Read the release manifest](../../reference/release-manifests.md#read-the-unit-9-artifact).

| Repo | What Test selects | What you promote for Prod in Unit 10 |
| --- | --- | --- |
| **Code** | A commit from Code `dev`, including the notebooks, pipeline and release mask. | Merge the tested commit into Code `main`, then add the Prod pipeline and settings through a second PR to `main`. Prod runs that pipeline from `main` and reads the Fabric definitions and mask from the original tested Code commit. |
| **Data** | The pinned commit in Data `dev` history, including the lakehouse definition. | Prod deploys that exact Data commit. The exercise uses its existing `dev` history as the source for checkout and requires no Data PR to `main`. |
| **Reporting** | The pinned commit in Reporting `dev` history, including the semantic model and report. | Prod deploys that exact Reporting commit. The exercise uses its existing `dev` history as the source for checkout and requires no Reporting PR to `main`. |

1. **Integrate changes in the repos they belong to.** Review and merge changes into the relevant `dev` branches. When a change spans repos, agree on the data contract first. For example, if a notebook writes a new field that a report uses, coordinate the Code and Reporting changes against the same field name and type. Once the intended Data and Reporting commits are available, put their hashes in the Code release mask and merge the Code candidate into `dev`. Reuse the pins for repos whose selected definitions still fit the release.
2. **Deploy and validate the combination in Test.** Queue the Code `dev` candidate in Unit 9. The pipeline checks out the two pins and records all three commits. Run the Test validation against that combination. If you decide to include a newer change in any repo, select the new combination in Code `dev` and validate it in Test before promoting it.
3. **Promote Code, then approve one Prod run.** Bring the tested Code commit into Code `main` and merge the Prod pipeline settings there. Select the matching Test run and request approval. Prod fetches the Data and Reporting `dev` histories and checks out the recorded commits. Both pins must still be reachable from their respective `dev` branches. The one run publishes the Data, Code and Reporting definitions to their respective Prod workspaces.

For example, if a report-only change lands on Reporting `dev` after Test, the existing candidate still contains the earlier report. To ship the new report, update the Reporting pin in a Code PR to `dev`, run Test again, and promote the resulting Code candidate. The Code PR coordinates the release even when the notebook and Fabric Data Pipeline definitions stay the same.

If your team requires protected `main` branches in all three repos, add a promotion PR in each affected repo that preserves the tested commit. For a dependent change, you can review and merge the prerequisite Data change before the Code and Reporting consumers. Configure the release pipeline to verify the tested pins against those protected branches, and start the coordinated Prod release once all required PRs are complete. The PR sequence governs source review, while the release pipeline governs deployment and binding order.

### 1. Select the tested snapshot and check the Prod targets

1. In the Test artifact, check `environment: test`, `mode: deploy`, `status: published`, `phase: complete` and `active_value_set: Test`. Copy `run_id` and all three full hashes under `verified_source_revisions` to your release record. Include the run name and link from the Test run page. Link the required Code PR check from your earlier review and the Test runtime results. [Prod release record](resources/prod-release-record.md) · [Read the release manifest](../../reference/release-manifests.md).
2. In Azure Repos, open `config/tiny-sales-release.yml` **at the verified Code commit**. Confirm that the two repository names and pins match the Test artifact, and that `environments.prod.workspaces` lists your three assigned Prod IDs with `value_set: Prod`. Compare each ID and role with the facilitator's inventory. Keep the [Unit 7 Prod overrides](../unit-07-configure-and-preview-release/README.md) in view. The expected runtime values are `prod` and `tiny_sales_prod`.
3. In the workspace UI, check the Prod names and IDs independently. Record the Data Prod lakehouse and SQL endpoint separately. Each has its own ID. The publisher will resolve the target IDs again after approval. [Logical and physical IDs](../../reference/fabric-item-identities.md).

**Expected result** Your release record identifies one tested source snapshot, three distinct Prod targets and the expected Prod settings. This applies Model B **MS-02 Source control**, **MS-03 Change control & traceability**, **MS-04 Environment separation** and **MS-06 Environment configuration**. [Fabric Minimum Standard](../../../source-guidelines/fabric-minimum-standard.md#minimum-standard-by-operating-model).

### 2. Protect main and promote the tested Code commit

Unit 6 added Notebook CI to `dev`. Set up `main` now because the Prod pipeline will run from it. The `main` policies govern what gets merged. The Prod service connection approval in section 4 governs whether a specific deployment can proceed. [Azure DevOps basics](../../pre-reads/azure-devops-basics.md#pull-requests-and-branch-policies).

1. In Azure Repos, open **Repos → Branches** in the **Code** repository. If `main` does not exist, have the repository maintainer create it from the agreed earlier Code baseline. The promotion PR will bring in the tested commit.
2. Open the **…** menu on `main`, select **Branch policies**, and set the following. If you lack **Edit policies**, have the facilitator apply the settings with you.

   | Policy | Settings |
   | --- | --- |
   | **Require a minimum number of reviewers** | Require **1** reviewer. Keep **Allow requestors to approve their own changes** clear. Select **Reset all approval votes** when new changes are pushed. |
   | **Limit merge types** | Enable **Basic merge (no fast-forward)** as the allowed merge type. This preserves the tested Code commit in the history. |
   | **Build validation** | Add **Tiny Sales - Notebook CI**, the pipeline from Unit 6. Leave **Path filter** blank. Choose **Automatic**, **Required**, and **Immediately when main is updated** for build expiration. Use **Tiny Sales source validation** as the display name. |

   This build runs the source checks on the proposed merge. For this exercise, link the live Test results in the PR and have the reviewer verify them against the candidate. An automated Test evidence check would need to match the PR source commit and both repo pins to a successful Test deployment and smoke result. The current Test runtime checks are manual. [Azure Repos branch policies](https://learn.microsoft.com/en-us/azure/devops/repos/git/branch-policies?view=azure-devops).

   If you already promoted the tested commit before setting up these policies, go to step 6 and record the existing PR.
3. In your local Code repository, refresh the remote branch tips and print the current `dev` hash. Compare it with the Code hash from your Test manifest. [Git commands for release commits](../../pre-reads/git-basics.md#check-which-commit-is-being-released).

   ```powershell
   git fetch origin
   git rev-parse origin/dev
   ```

   If the hashes match, open a PR from **`dev` into `main`**. If `dev` has moved, branch from the exact tested Code hash and use that branch as the PR source.

   ```powershell
   $testedCodeCommit = 'PASTE_FULL_CODE_HASH_FROM_TEST_MANIFEST'
   git branch release/unit-10 $testedCodeCommit
   git push origin release/unit-10
   ```

4. Title the PR **Promote tested Tiny Sales to main** and adapt this body. Ask the reviewer to confirm that the PR source tip still matches the tested Code hash before completion. If `dev` moves during review, open the PR from the branch at the tested commit.

   ```markdown
   ## Change
   Promote the Tiny Sales Code commit tested in [Test run](<run-url>) to main.
   - Code: <full Code hash>
   - Data: <full Data hash>
   - Reporting: <full Reporting hash>

   ## Validation
   - [Test runtime results](<results-url>): <observed result>
   - [Notebook CI for this PR](<ci-run-url>): <observed result>
   ```

5. Verify that Notebook CI passed on the PR and that the required review is complete. Update **Validation** with the observed results and links. Complete the PR with **Merge (no fast forward)**. If the source branch is `dev`, leave **Delete source branch** clear. [Complete an Azure Repos PR](https://learn.microsoft.com/en-us/azure/devops/repos/git/complete-pull-requests?view=azure-devops#complete-a-pull-request).
6. Verify the tested commit is reachable from `main`, then record the completed PR and its resulting `main` revision.

   ```powershell
   $testedCodeCommit = 'PASTE_FULL_CODE_HASH_FROM_TEST_MANIFEST'
   git fetch origin
   git merge-base --is-ancestor $testedCodeCommit origin/main
   $LASTEXITCODE
   git rev-parse origin/main
   ```

   Expect exit code `0` from the ancestry check before continuing. `$LASTEXITCODE` displays the result of the preceding Git command.

**Expected result** The Code promotion PR puts the exact tested Code commit in `main` history. Data and Reporting stay pinned to their tested commits. This applies **MS-02 Source control**, **MS-03 Change control & traceability** and **MS-14 Release evidence**. [Fabric Minimum Standard](../../../source-guidelines/fabric-minimum-standard.md#minimum-standard-by-operating-model).

### 3. Prepare the Prod release pipeline

1. Follow the [Unit 8 connection steps](../unit-08-publish-shared-dev/README.md#1-create-your-dev-service-connection) using the assigned **Prod** UAMI and the name `sc-tiny-sales-prod`. Leave **Grant access permission to all pipelines** clear. Follow [Unit 8's workspace access steps](../unit-08-publish-shared-dev/README.md#2-grant-the-deployment-identity-access-in-fabric) in Code, Data and Reporting **Prod**, selecting **Contributor** for the Prod UAMI. Verify the three grants in **Manage access** and check that the service connection is bound to that UAMI. Azure DevOps authorizes the pipeline to use the connection. The connection supplies the identity for authentication, and Fabric authorizes that identity to publish. [Service connections and identities](../../reference/release-service-connections.md).
2. Create a feature branch from the `origin/main` you just verified.

   ```powershell
   git switch -c feature/prod-release origin/main
   ```

3. Copy the following files from the tutorial into the same paths in your Code checkout. Test and Prod are separate Python entry points. Test chooses a source from `dev` and can run a read-only preflight. Prod selects a completed Test run and verifies its commits before publishing. Both call the shared Tiny Sales publisher for staging, target bindings, publishing and inventory checks.

   | Starter | What to configure |
   | --- | --- |
   | [`config/environments/prod.yml`](../../../../config/environments/prod.yml) | Enter the Prod UAMI name, confirm the service connection name, and enter the exact Prod workspace names and the Test artifact's `run_id`. Prod uses the same identity settings as Dev and Test. The additional run ID ties Prod to the selected Test run. |
   | [`.azuredevops/pipelines/prod-release.yml`](../../../../.azuredevops/pipelines/prod-release.yml) | Set the two literal repo names from the tested mask. Match `source` under `resources.pipelines` to your saved Unit 9 pipeline name. |
   | [`toolkit/prod_release.py`](../../../../toolkit/prod_release.py) | Entry point for the approved release. Reads the Test manifest and checks out the tested snapshot. |
   | [`toolkit/tiny_sales_release.py`](../../../../toolkit/tiny_sales_release.py) and [`toolkit/test_release.py`](../../../../toolkit/test_release.py) | Use the versions from Unit 9. If you completed an earlier draft of Unit 9, copy both files from this revision together. The shared module uses the Tiny Sales item set and delegates Fabric publishing to `fabric-cicd`. |

   For this first release, the Prod tooling PR starts from `main` so you can set up the release pipeline while keeping the already tested snapshot. Changes to shared publishing code should normally go through a feature PR into `dev`, a Test release, and then promotion to `main`. The recovery exercise starts by bringing the Prod tooling added here back into `dev` through a reviewed PR and verifying the shared publisher in Test. The Prod service connection stays scoped to the authorized release pipeline.

4. Commit the added or updated files as **Add the approved Prod release**, push your feature branch and open a PR with the same title into `main`. Use the body below and update **Validation** with the observed results before completing the PR. Have the reviewer compare the Prod configuration with the assigned inventory. Complete the PR once the required review and Notebook CI pass. The Prod run will record the pipeline revision on `main` and use a separate checkout of the exact tested Code commit for the Fabric definitions and release mask.

   ```markdown
   ## Change
   Add the approved Prod pipeline for the snapshot from [Test run](<run-url>).

   ## Validation
   - [Completed Code promotion PR](<pr-url>) records the tested commits.
   - Prod workspace and service connection settings: <review result>
   - [Notebook CI for this PR](<ci-run-url>): <observed result>
   ```

**Expected result** The Prod pipeline settings are reviewed and versioned. The selected source stays fixed across environments, and the Prod publisher uses a separate managed identity. This applies **MS-03**, **MS-05 Reproducible deployment**, **MS-07 Identity model** and **MS-12 Security & least privilege**. This release starts from the Unit 3 lakehouse and notebook. A fresh rebuild also needs workspace provisioning, bootstrap and data preparation. [Fabric Minimum Standard](../../../source-guidelines/fabric-minimum-standard.md#minimum-standard-by-operating-model).

### 4. Authorize and approve the Prod run

1. Save the pipeline as **Tiny Sales - Prod Release** from the Code repo's `main` branch, using `/.azuredevops/pipelines/prod-release.yml`. Use the [Unit 9 save and authorization steps](../unit-09-release-to-test/README.md#3-authorize-and-run-the-test-release) for the Prod connection and the Data and Reporting repos. If Azure DevOps requests access to the referenced Test pipeline, have its resource administrator authorize the Prod pipeline. [Pipeline resource authorization](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/resources?view=azure-devops#resource-authorization).
2. As the connection administrator, open **Project settings → Service connections → sc-tiny-sales-prod → Approvals and checks**. Select **+** (or **Add check**), choose **Approvals**, then select **Next**. Add the designated reviewer under **Approvers**, clear **Allow approvers to approve their own runs**, and set a timeout that gives your reviewer time to act, for example **1 hour** in the workshop. Under **Instructions**, enter the example below and select **Create**. Have a different account queue the release. The check is configured on the connection and gates the stage that uses the Prod deployment credential. [Azure Pipelines approvals and checks](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/approvals?view=azure-devops#approvals).

   > Open the selected Tiny Sales Test run and confirm it published successfully. Compare the three commits in its manifest and the passing Test runtime results with the promotion PR. Confirm the Prod workspace names and IDs and the Prod service connection against the release record. Approve when these match. If something differs, reject the run and describe the mismatch.

3. Choose **Run pipeline** and select `main`. Keep **Require first creation of validate_release** selected for your first release. Continue past the parameters to **Pipeline artifacts** and open **Tiny Sales - Test Release [tested]**. In the picker, search for the Test **run name** shown on the Test run page. Confirm the run, `dev` branch and short Code hash, then choose **Use selected run**. Back in **Pipeline artifacts**, confirm the selected run name and select **Run** when the Prod workspaces are ready. The picker displays a run name such as `20261112.5`. The run URL and manifest carry its numeric ID, which is the value used by `approvedTestRunId`. A green status and a matching short commit can appear on more than one run, so check the exact run against your release record. [Manual resource version picker](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/resources?view=azure-devops#manual-resource-version-picker).
4. In the waiting run, the approver opens the pending check, applies its instructions, and records the decision, approver and time with the run link. After approval, look for `PROD PREFLIGHT PASSED` before publishing begins. The preflight compares all three Git checkouts to the Test manifest and uses the Prod service connection's authenticated session to query the assigned workspaces before issuing writes.

**Expected result** The Prod stage waits for the resource approval, then checks the exact tested snapshot and publishes through the Prod connection. This applies **MS-09 Production authorization** and exercises the **MS-13 Network & execution prerequisites** for the workshop's hosted runner and Fabric path. Workshop workspace Admins retain direct edit rights. Enforcing the production boundary also requires managing those rights and protecting the release branch and credential. [Fabric Minimum Standard](../../../source-guidelines/fabric-minimum-standard.md#minimum-standard-by-operating-model).

An **Azure DevOps Environment** is a named pipeline resource that a deployment job can target. Separate Test and Prod Environments can give several pipelines a common deployment history and a place for target-wide checks. Fabric workspace IDs still determine where the publisher sends definitions. This unit uses the Prod service connection approval because the exercise protects one release credential and already records the target in its manifest. The recovery exercise is a natural place to use an Environment's deployment history to find the last known-good run. [Azure DevOps Environments](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/environments?view=azure-devops).

### 5. Observe the first creation and the existing-item update

1. Open `prod-release.json` under **prod-release-evidence**. Confirm `status: published`, `phase: complete`, all three `verified_source_revisions`, `verified_workspaces`, `configured_release_identity`, `sql_endpoint_id` and `active_value_set: Prod`. Compare them with your release record.
2. Compare `before_item_ids` and `published_items`. For `validation`, expect a null before ID, a new physical item ID after publishing, and an entry in `created_items`. Compare the source `validation_logical_id` with the Test notebook's Git definition. The two environments use the same source logical ID and have separate physical item IDs. Check that the existing `build_sales` notebook and `sales` lakehouse kept their Prod physical IDs.
3. In Code Prod, open the item details or settings for both notebooks. Record any visible creator, owner or associated/default identity using the exact field labels. Record where you looked if a field is unavailable. Compare the new notebook with the existing one and with any equivalent Test observations. Keep ownership intact during the exercise. The manifest records the configured deployment identity. Use Fabric activity or audit evidence if you need to verify the caller independently. [Fabric item ownership](https://learn.microsoft.com/en-us/fabric/fundamentals/item-ownership-take-over).
4. Name the solution owner and the people responsible for releases and failed runs in your record. Discuss who can diagnose a failed notebook run when the developer who authored it is unavailable. This applies **MS-01 Ownership**, **MS-05**, **MS-07** and **MS-14 Release evidence**. [Fabric Minimum Standard](../../../source-guidelines/fabric-minimum-standard.md#minimum-standard-by-operating-model).

**Expected result** The manifest shows the first managed creation of `validate_release` in Prod and an update that preserved the existing `build_sales` ID.

### 6. Run Tiny Sales in Prod and retain the evidence

1. In **Code Prod**, inspect the `run_sales` Notebook activity. Confirm it points to the Prod `build_sales` item and note the connection choice shown. Run `run_sales` from Fabric. Open its run details and capture status, run link, notebook activity result and the observed values `prod` and `tiny_sales_prod`. Check that the notebook is bound to the **Data Prod** `sales` lakehouse. [Monitor pipeline runs](https://learn.microsoft.com/en-us/fabric/data-factory/monitor-pipeline-runs).
2. Open the published `validate_release` in **Code Prod**. Check its default lakehouse is **Data Prod** `sales`, then select **Run all**. Record the notebook run or session link and the output `SALES_SMOKE_PASSED` with **357.20 gross** and **204.70 revenue**. Record the signed-in operator who launched each run and any executor or data-access identity exposed by the run or connection settings. Where a connection exposes both its owner and its authentication identity, record them separately.
3. In **Reporting Prod**, use **Lineage view** to check that `sales_overview` uses the Prod `sales_model`. Follow the [Unit 4 model source inspection](../../section-03-team-delivery/unit-04-connect-orchestration-configuration-and-reporting/README.md#inspect-the-endpoint-model-mode-and-connection) to verify the model points to the Data Prod SQL endpoint. Open the report and check that **Total Revenue** is **204.70**. Retain the binding observation and the report result.
4. Keep the Test and Prod run links, manifests, approval, item observations and runtime results together in the [Prod release record](resources/prod-release-record.md). For a failure, keep the failed run link, last phase reached and the responsible person's next action. The live preflight is automated here. A Model B implementation also automates runtime validation in Test and after Prod deployment, as required by **MS-08 Release validation**. This record also applies **MS-10 Operational visibility** and **MS-14 Release evidence**. [Fabric Minimum Standard](../../../source-guidelines/fabric-minimum-standard.md#minimum-standard-by-operating-model).

**Expected result** Your record links the approved deployment to passing Prod pipeline, notebook and report observations.

### If a check fails

| Symptom | What to check |
| --- | --- |
| Run waits for access or approval | Check which protected resource is waiting. A resource administrator grants pipeline access. The designated approver decides whether the Prod stage can start. |
| The selected run, Code ancestry or pins fail verification | Compare the resource run ID and all three full hashes with the original Test manifest. Check that the tested Code commit is in `main` history and Data and Reporting pins remain reachable from their `dev` branches. |
| Authentication fails, or the workspace or active value set differs | Check the Prod connection's UAMI and its Fabric grants. Compare the expected workspace names, tested mask IDs and observed `sales_config` active set. Stop before runtime validation. |
| First-creation check fails or publish fails partway | Keep the manifest and log. Check the live inventory against `before_item_ids` and any available `published_code_items` or `published_items`. If the notebook already exists, use the original run evidence to establish how it was created. An approved repeat run with the same source can then verify that its physical ID is stable. |
| Deployment passes but a runtime or report check fails | Open the failing Fabric run and compare the target lakehouse, parameters, report binding and observed runtime/data-access permissions. Record the failing step and owner before deciding on recovery. |

For **MS-11 Recovery**, keep the known-good source revisions and target settings alongside the deployment record. Redeploying definitions can restore definitions and bindings. Data and side effects from runtime execution need their own recovery steps. [Fabric Minimum Standard](../../../source-guidelines/fabric-minimum-standard.md#minimum-standard-by-operating-model).

### Completion checkpoint

- [ ] `main` requires Notebook CI and a reviewer. The completed Code promotion PR preserved the exact tested commit in `main` history.
- [ ] The approved Prod run used the exact three Test revisions and the assigned Prod managed identity.
- [ ] The manifest shows first creation of `validate_release` and stable physical IDs for the existing items.
- [ ] The record links approval, deployment, ownership observations and the actual Prod runtime checks.
- [ ] You can explain who approved the run, who deployed the items and which identities the runtime evidence shows.

### Recap and discuss

#### What we built

You first used Fabric's native Deployment pipelines to promote a lakehouse and notebook (Model A). Then you put the expanded Tiny Sales solution under source control and released it through Azure Pipelines (Model B). The Model B release moves the same tested source through Test and Prod, with each environment supplying its own settings and access.

| Area | What we chose and what it controls |
| --- | --- |
| **Workspaces and repos** | Dev, Test and Prod each have Code, Data and Reporting workspaces. In the exercise, each role also has its own repo. Fabric Git integration updates shared Dev, and Azure Pipelines publishes to Test and Prod. Workspace boundaries control access to live items. Repo boundaries control who can change and review source. |
| **Source and review** | Feature PRs feed Code `dev`, where required Notebook CI checks the proposed change. The Code release mask pins one Data commit and one Reporting commit. Test records all three commits. Code `main` also requires Notebook CI and adds a required reviewer and a merge policy that preserves the tested commit. |
| **Targets and configuration** | The release mask declares workspace IDs and source pins. The environment settings name the service connection and expected workspaces. The shared Python publisher verifies the targets, binds the definitions to the target items, and checks the active Variable Library value set used at runtime. |
| **Release authority** | The Dev pipeline reads through its own connection. Test and Prod publish through separate managed identities and restricted connections. Prod also waits for an approval on its connection. Fabric workspace roles govern what each identity can do. You record the deployment identity separately from the item owner, runtime identity and data-access identity. |
| **Evidence** | PRs and CI runs show what was reviewed. The Test and Prod manifests show which commits were deployed, where they went and which items were created or updated. Fabric run results show whether the pipeline, notebook and report work in the target. |

#### Workshop choices and their limits

- **Manual release and runtime checks.** You select the Test run and start Prod deliberately. The pipeline automates source and target checks and publishing. You run the smoke checks in Fabric and attach the results to the release record. Model B calls for automated runtime validation in Test and Prod.
- **A short path to the first Prod release.** Code is the only repo promoted to `main` in this exercise. Data and Reporting deploy from tested pins in their `dev` histories. The first Prod tooling PR starts on Code `main` to preserve the already tested candidate. The next exercise brings that tooling into `dev` and uses Azure DevOps Environment deployment history during recovery.
- **A training sandbox.** Test and Prod start with the seeded items from Unit 3. Participants have workspace Admin access and can edit items directly. An empty-environment rebuild, stricter separation of duties, and private network execution are outside this exercise.

#### Discuss your project

Spend **5–10 minutes** on your own project or a familiar example. Write down one decision you would keep from Tiny Sales and one you would change.

| Discuss | Apply it to your project |
| --- | --- |
| **What did we build?** | Trace one change from a Git commit through Test, review on `main`, Prod approval and runtime evidence. Identify which files describe the Fabric items, which select versions and targets, and which execute the release. |
| **Where do we need separation of concerns?** | Decide who can edit a definition, change a target, approve a release, deploy it and run or support it. Which roles can overlap? Would one repo with role folders support that ownership, or would separate repos and commit pins help? |
| **What does each control enforce?** | Pick a mistake you want to prevent, such as a developer accidentally writing to Prod. Which combination of branch policy, pipeline permissions, service connection approval and Fabric access would block it? Which practices, such as recording a manual smoke result, help reviewers make a decision? |
| **What would we automate next?** | Pick a check to run automatically and a decision to keep with a person. For example, automate the smoke notebook and attach its output to the exact candidate, then have a reviewer decide whether to release it to Prod. If several pipelines can deploy to the same target, consider what an Azure DevOps Environment would add. |

Share one boundary you would enforce and one practice you would encourage. Name who owns each and what evidence would show it is working.

[Previous unit](../unit-09-release-to-test/README.md) · [Next unit](../../section-05-operate-and-reuse/unit-11-recover-a-test-release/README.md) · [Tutorial index](../../README.md)
