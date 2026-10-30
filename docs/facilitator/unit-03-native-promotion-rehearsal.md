# Unit 3 preparation — prove native promotion into Test

Prepared 29 October; updated 30 October 2026. Status: organizer reports the Test rehearsal worked, with corrections to target-stage navigation and rule explanations. Actual Test source revisions/outputs and duration were not supplied. Prod is untested. The complete participant lesson is now [Unit 3](../tutorial/section-02-model-a/unit-03-native-promotion/README.md); retain this file as the Test rehearsal/evidence reference.

This rehearsal tested the [curriculum's native gate](../planning/curriculum.md): Data/Code separation, a fresh Test lakehouse, shared environment-aware source and a default-lakehouse rule. It required no Azure Pipeline, Variable Library or extra workspace. The participant lesson incorporates the reported Test result and adds a Prod extension whose validation is still pending.

## What is supported by documentation and what needs observation

- Native notebook rules can specify the target default lakehouse by lakehouse ID/name/workspace ID, overriding auto-binding. See [Notebook in deployment pipelines](https://learn.microsoft.com/en-us/fabric/data-engineering/notebook-source-control-deployment#notebook-in-deployment-pipelines).
- Rules belong to the target stage; rule editing requires the relevant item ownership. See [Create deployment rules](https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/create-rules).
- Lakehouse deployment does not copy runtime tables/data. See [Lakehouse lifecycle management](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-git-deployment-pipelines).
- The exact first-deployment/rule sequence below is an experiment in the organizer's tenant. A documentation match or successful local target-guard test does not pass V03/V04/V07.

## 1. Make the source guard usable in every environment

1. Retain the Unit 2 source-baseline worksheet. Confirm Code Dev has no unknown pending changes and nobody is editing the notebook elsewhere.
2. In the Code Dev `build_sales` notebook, replace **only its first PySpark code cell** with [environment-aware-target-cell.py](../../sample/tiny-sales/environment-aware-target-cell.py). Keep the introductory Markdown and the other three code cells unchanged.
3. Replace all six workspace-name placeholders with the assigned Code/Data Dev/Test/Prod names. Each Code workspace maps to exactly one Data workspace and environment. Do this once in the common source; do not edit separate Test/Prod source copies later.
4. Run the cells in Code Dev. The guard must identify `dev` and Data Dev, and `UNIT_01_PASS` must still report the same data result.
5. Save and commit the notebook through Code Dev Git integration, with a message such as **Make Tiny Sales target checks environment aware**. Record the new Code commit; retain the Data commit. Review the resulting diff against the previous Code baseline.
6. Close saved notebook editors before promotion. Keep the same source definitions for all stages; the only stage-specific binding below is deployment configuration.

Expected result: Dev still works, the guard allows only the three declared workspace pairs, and the selected Code source includes all environments. The helper retains `check_target()`, `TABLE_NAME`, `Decimal`, `json` and `F`, which the remaining cells use. This is sample-specific explicit configuration, not the future generic deployment toolkit.

## 2. Create the two native Deployment pipelines

Create native pipelines for these existing workspace triplets:

| Pipeline name example | Stage 1: Dev | Stage 2: Test | Stage 3: Prod |
| --- | --- | --- | --- |
| `tiny-sales-data` | Data Dev | Data Test | Data Prod |
| `tiny-sales-code` | Code Dev | Code Test | Code Prod |

Use the same stage positions in both pipelines. Assign the existing workspaces; avoid creating additional auto-generated target workspaces. Pipeline permissions and workspace assignment permissions are separate. See [Get started with Deployment pipelines](https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/get-started-with-deployment-pipelines).

Record any UI differences, licensing/assignment problem or pre-existing pipeline assignment. Do not replace a workspace or detach someone else's pipeline to force progress.

## 3. Deploy the Data prerequisite into Test

1. In the Data Deployment pipeline view, click the **Test target stage**, verify **Deploy from = Data Dev**, select the source `sales` Lakehouse shown there, review source/target and deploy into the existing Data Test workspace.
2. Open the resulting **Lakehouse** item in Data Test, not its SQL analytics endpoint. Confirm schema support/default `dbo` exists and that the sample `sales` table/data has not been copied from Dev.
3. Record its lakehouse item ID, display name and Data Test workspace ID from its actual item/workspace URL. These are target configuration for the notebook rule, not a source logical ID.

Expected result: Data Test has an empty matching lakehouse definition. If the target lacks the expected schema support, stop and record that behavior; do not silently recreate a different lakehouse or introduce manual business data.

## 4. Establish the Test notebook and its lakehouse rule

1. Deploy `build_sales` from Code Dev to Code Test in the Code Deployment pipeline. This establishes the target item so its target-stage rule can be inspected/configured. **Do not run all cells yet.**
2. Inspect the target notebook's default lakehouse without changing its source. Record what native promotion selected. Do not assume that a reference to Data Dev was remapped simply because deployment succeeded.
3. In the **Code Deployment pipeline view**, select its **Test target stage** and open the stage's **Deployment rules** pane. Select **build_sales → Default lakehouse**; this is not in the notebook editor. Choose **Other** for the target and enter the **Data Test lakehouse's** ID, name and workspace ID collected above. If rules are unavailable, check item ownership and pipeline permissions before continuing. The rule explicitly declares the target and overrides auto-binding; it does not mean all cross-workspace references always require manual rules. The participant lesson explains IDs/binding and native auto-binding separately.
4. Save the rule, then redeploy the same selected Code Dev notebook to Code Test so the rule is applied. Keep any "continue if items fail" option off; inspect a failed deployment before proceeding.
5. Close any old Test notebook editor; reopen the notebook from Code Test after deployment. If a prior session exists, restart it before checking a changed default lakehouse.
6. Run **Cell 1 only**. It must identify environment `test`, Code Test and Data Test's lakehouse `sales`. Verify the logged physical IDs against the target lakehouse. If it still references Dev, the guard should stop; correct the deployment rule rather than weakening the guard or editing target notebook source.

Expected result: a repeatable target-stage rule binds the notebook to the separate Data Test workspace, using the same notebook code as Dev. If the initial deployment or subsequent redeploy cannot complete, record the exact error and the rule state. That is an unresolved feasibility result, not permission to invent a different topology.

## 5. Execute and repeat in Test

1. Once Cell 1 identifies the correct Test target, run Cells 2–4 in order. Confirm `UNIT_01_PASS`, six persisted rows and revenue 342.20.
2. Inspect `Data Test → sales → Tables → dbo → sales` and verify the result is present there. Check that the Code Test item is the promoted notebook and not a newly hand-created substitute.
3. Repeat the Code Dev → Code Test deployment without changing source or the configured rule. Reopen/restart as needed, run again, and confirm the target pairing and six-row result remain correct. Data overwrite comes from notebook execution; definition promotion itself must not be described as copying data.
4. Record how changes in the deployment comparison were presented. Do not infer code drift merely because lakehouse binding metadata differs intentionally between stages.

The organizer reports this Test-first slice worked. Continue with **Section 6** of the participant Unit 3 only after confirming that the same source/configuration remains in place. It adds deliberate Prod promotion, a separate Prod rule and smoke check; those steps are authored but not yet reported successful.

## Report back

Keep the following in your private training notes and share the non-secret outcome needed to refine the lesson:

- Approximate preparation time and UI differences.
- New Code baseline commit plus existing Data baseline (per-repo source selection).
- Whether native Data deployment preserved schema support and created the intended empty Test lakehouse.
- Notebook default target after first promotion, and whether the explicit target-stage rule was available and worked after redeployment.
- Cell 1 Test context and final metrics; whether repeat deployment/rerun kept the expected target and six-row result.
- Exact failed step/error if a checkpoint could not be completed. A sanitized file listing/default-lakehouse metadata excerpt is useful if it affects pairing or binding; do not send tokens or credentials.

The 30 October feedback supports Test target binding/bootstrap/repeat execution by organizer report. It does not establish Prod success, an automation identity or enforced productive controls. Keep V03/V04/V07 evidence scoped accordingly in [the backlog](../planning/backlog.md).
