# Unit 9 preparation and pilot checks

11 November 2026. The organizer completed the live Dev preflight and asked to begin Unit 9. Part A lets the team set up the Test deployment identity and capture an authenticated, read-only inventory before the first managed release. [Unit 9 Part A](../tutorial/section-04-release-automation/unit-09-release-to-test/README.md).

12 November 2026. The organizer reached the PR step and asked to demonstrate granting access before the first run. The lesson now has learners save the pipeline and add it to the restricted service connection. Rehearse with a connection administrator granting access and a different user who has permission to queue the pipeline. [Azure DevOps service connection pipeline permissions](https://learn.microsoft.com/en-us/azure/devops/pipelines/policies/permissions?view=azure-devops#set-service-connection-pipeline-permissions).

The core exercise uses the managed Test release. The same run checks pinned source and workspace IDs before writes, captures the item inventory, publishes, and records the outcome. The standalone baseline YAML is available for pilot troubleshooting. [Unit 9](../tutorial/section-04-release-automation/unit-09-release-to-test/README.md).

The manual Test pipeline defaults to preflight. **Publish to Test after preflight** opts the run into writes after the same checks. Capture `mode` and `status` from the evidence during the pilot. The parameter records operator intent. Protected resource approvals and branch checks can govern when an automated or production release may proceed. [Runtime parameters](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/runtime-parameters?view=azure-devops) · [Approvals and checks](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/approvals?view=azure-devops).

The organizer reported first-run permission prompts for Data and Reporting. After granting access, the run reached the Azure CLI task and signed in. Python rejected `--mode preflight` during argument parsing. The log shows the updated YAML passed the parameter and the loaded script lacked that argument. Confirm both starter files at the Code revision for the next run. Preemptive repository authorization is documented by Microsoft and awaits rehearsal in this project. [Repository resource permissions](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/repository-resource?view=azure-devops#add-pipeline-permissions-to-a-repository-resource).

On the next attempt, both pinned checkouts completed. Source validation rejected the `TridentNotebook` workspace reference before Fabric writes. The earlier lab export uses the all-zero workspace GUID with the notebook's `.platform` logical ID for same-workspace binding. The Test release now accepts that pair and explicit Code Dev references, and reports the actual workspace ID for other GUIDs. The failed run's exact source values are still unconfirmed. [Fabric dependency binding](https://learn.microsoft.com/en-us/fabric/cicd/cross-workspace-dependency-binding).

## Live Test release, 12 November 2026

Azure Pipelines run **643** produced `test-release.json` with `environment: test`, `mode: deploy`, `status: published`, `phase: complete` and `active_value_set: Test`. The script ran for about 51 seconds. All three verified checkouts match the declared revisions.

| Source | Verified revision |
| --- | --- |
| Code | `dddafe661b0bf0e2f9e785f154f4f89005b5cc9a` |
| Data | `c29098701d4741edfd6f31816d5f3b6cd7a6b289` |
| Reporting | `070bc93f8ac168353833a0f52847c3666c52d2c8` |

- The artifact records three verified Test workspaces, the configured Test service connection and UAMI, and the existing Test SQL endpoint. The `sales` lakehouse and `build_sales` notebook kept their physical item IDs. `sales_config`, `run_sales`, `sales_model`, `sales_overview` and `validate_release` were absent from the starting inventory and present after publishing. `logicalId` was absent or null in Fabric's returned inventory for the new items. The Git definitions carry their source logical IDs separately.
- The organizer manually ran `run_sales` in Test, observed the intended notebook parameters and reported that `validate_release` passed. The starter checks **357.20 gross** and **204.70 revenue**. Exact runtime logs, run links and executing principal were not supplied. The manual runs provide runtime evidence for this pilot. Automated smoke validation remains follow-on work.
- The artifact confirms first creation of `validate_release` through the managed Test release path. It records the configured identity names; the authenticated caller's principal ID, displayed ownership fields, repeat deployment and live inspection of the report's semantic model binding remain open. See the [ownership experiment](../planning/identity-and-ownership-experiment.md).
- Reuse the selected source revisions for the Unit 10 rehearsal. Keep the original deployment artifact and runtime run links in the pilot Azure DevOps project. The participant explanation uses field and item names without the pilot's workspace and item IDs. [Release manifest reference](../tutorial/reference/release-manifests.md).

## Remaining checks and prior local rehearsal

- Rehearse the connection save with participant Azure permissions and confirm that the team can add the Test UAMI as Contributor in its three assigned Test workspaces. Run the Test baseline from `dev`. Retain the actual run link, verified workspace names and IDs, and the Test identity binding. Check the workspace UI for ownership metadata on `build_sales` and record the exact label and inspection method.
- Part A collects inventory with Fabric GET operations. Empty Reporting Test and partial Test content are valid inputs. The baseline records its Code checkout and declared Data and Reporting pins for traceability. Select the release source separately from the completed Dev rehearsal and verify all three revisions.
- Local checks exercised both YAML entry points with mocked Fabric responses and a valid release mask. Dev still requires all six declared items. Test accepted a partial inventory and empty Reporting Test, followed pagination, recorded the checkout and connection names, and stopped before listing items when a workspace name differed.
- The workshop starts with the Test lakehouse, SQL-visible `sales` table and `build_sales` notebook from Unit 3. Inspect the deployed report's model binding and compare ownership observations for the existing and newly created notebook. Test a rerun against the same item IDs.
- Local checks used temporary Git repos and mocked Fabric responses. They verified ancestor pin checkout, staging only tracked files, rejection before writes for a wrong workspace or missing native item, rebinding the supplied notebook and pipeline shapes, report sibling staging and stable physical IDs.
- Unit 9 covers MS-01, MS-04, MS-05, MS-06, MS-07, MS-12 and MS-14. A later exercise can add a smoke-test gate and retain pass/fail run metadata, including failures that occur before a notebook can write its own row. For PR-to-`main` gating, bind the evidence to the exact candidate and control writes to the shared Test target. [Azure Repos branch policies](https://learn.microsoft.com/en-us/azure/devops/repos/git/branch-policies#build-validation).
