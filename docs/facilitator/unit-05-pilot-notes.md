# Unit 5 preparation and pilot checks

4 November 2026. Participant lesson and feature record authored after the organizer accepted Unit 4 as its first version, with a narrow clarification about where to find physical versus logical IDs. Unit 5 has not been run in the organizer's Azure DevOps project or local work-PC setup. Do not infer clone/authentication/PR success or feature runtime success from the authored instructions.

Participant entry point: [Unit 5](../tutorial/section-03-team-delivery/unit-05-make-a-local-feature-change/README.md). Evidence worksheet: [feature record](../tutorial/section-03-team-delivery/unit-05-make-a-local-feature-change/resources/feature-record.md). Shared explainer: [Fabric item IDs](../tutorial/reference/fabric-item-identities.md).

## Selected scope and prerequisites

- Preserve the current three-repo pilot; clone only the Code repo and branch from `dev`. Data/Reporting source revisions remain pinned separately. No topology migration, new workspace or competing Dev writer.
- Edit the actual Fabric-exported `notebook-content.py` in an ordinary local VS Code folder. Preserve `.platform`, generated cell metadata, lakehouse/workspace bindings and notebook settings. The original Unit 1 fixture implementation remains canonical in `sample/tiny-sales`; the unit supplies only the changed expression, not a duplicate notebook.
- Feature: keep returned rows, zero their `revenue`, retain `gross_revenue` and schema. Expected gross 342.20, revenue 189.70, rows/orders 6/6, quantity/returns 13/2. The report's Total Revenue measure needs no edit. If Unit 4's temporary fixture was not restored, stop and restore the baseline first.
- Push `feature/exclude-returned-orders` and open a **draft PR into `dev`**. Hold integration until Unit 6's checks. Draft PR build validations do not run automatically; Unit 6 must explicitly Publish and verify the policy/check, not wait indefinitely for a draft-policy run.
- No Spark/Python runtime installation is required to complete this source-editing unit. `git diff --check` is a whitespace/conflict-marker check, not a business/runtime test. Do not record 189.70 as a Fabric execution result yet.
- Unit 4 acceptance does not establish retained raw exports or a particular source/connection identity. Current documentation supports the `.py` export, but capture the actual exported path/markers from the organizer before designing Unit 6's loader/validation.

## Walkthrough evidence needed

1. Git/VS Code availability and version, sign-in flow, Basic/repository contribution access, clone/push/PR permissions, installation restrictions and sign-in delay. Keep tool installation outside the 35–45 minute learner estimate.
2. Exact Code repo mapping, `dev` base commit, notebook folder/path and format, including relevant generated markers and parameter/guard ordering. Prefer a sanitized real export or narrow relevant excerpts; retain private workspace IDs/URLs outside published sources.
3. Successful branch creation/edit/diff/commit/push and full feature commit ID. Verify `.platform`, metadata/bindings and non-notebook files remain unchanged.
4. Correct PR source/target and Draft status, with explicit pending validation and no auto-complete. Capture actual Azure Repos menu labels and any policy blocking draft creation.
5. Shared Dev remains on `dev` with the prior definition and 342.20 runtime/report baseline. A source branch alone provides no pre-merge Fabric runtime isolation; do not switch shared Dev to the feature as an ad hoc test.
6. Actual learner duration and unclear steps. A solo learner is the required path; pairs can follow together. Independent review/enforcement is a later control boundary, not established by self-review in a training sandbox.

## Unit 6 preparation gate

Build the first reusable validation starter here before offering its exercise. It must validate the actual exported representation without executing Fabric imports, guards or table writes offline. Design a meaningful check against the selected business transformation; a second hardcoded calculation that never exercises the feature cannot establish its correctness. Separate checks of source structure/configuration from business behavior and later Spark/runtime validation. If useful business validation requires extracting testable logic, make that explicit, preserve the exported-notebook path and keep the added learner work within the time budget.

Use the existing open feature PR to show a wrong variant failing and the corrected feature passing. Confirm Azure Pipelines registration/authentication, the correct repo/base branch and build-validation policy before proceeding. The shared-Dev update mechanism remains a later single-publisher decision; no merge-to-runtime guarantee is introduced here.

## Local verification of this preparation draft

- Inserted the lesson's exact replacement expression and expected-value edit into the canonical starter in memory and parsed the result as Python. The original four cell boundaries and fixture block were preserved. This checks the snippet's syntax in context, not an actual Fabric Git import or Spark evaluation.
- Independently joined the canonical fixtures in SQLite using integer cents: rows/orders 6/6, quantity/returns 13/2, gross 342.20 and feature revenue 189.70. This verifies the expected result independently; it does not execute or validate the Spark expression's runtime behavior.
- Relative Markdown links and code fences checked locally; canonical Unit 1 source and the parked Unit 3 lesson remain unchanged. No Azure DevOps clone, push, draft PR, cloud notebook or report execution was performed here.

## ID teaching follow-up

Unit 2 introduces IDs, the shared reference gives the full distinction now, Unit 4 separates repo references from deployed item links, and Unit 5 preserves logical identity. Units 7–10 must show how the selected tooling correlates source identity and target physical IDs in configuration, resolved plans and logs/release evidence. Do not assume every tool honors logical IDs identically or that all dependency references are logical.

Controls: MS-02/03 source and review, MS-04 source/runtime isolation, MS-06 preserved environment metadata, MS-08 expected checks and evidence limits, MS-14 fixed source revisions/PR. Workload identities, target deployment and enforced approval boundaries remain untested.

## Sources

- [Notebook Git representation](https://learn.microsoft.com/en-us/fabric/data-engineering/notebook-source-control-deployment#notebook-representation-in-git).
- [Azure Repos cloning](https://learn.microsoft.com/en-us/azure/devops/repos/git/clone?view=azure-devops) and [draft PR behavior](https://learn.microsoft.com/en-us/azure/devops/repos/git/pull-requests?view=azure-devops#create-draft-prs).
- [Fabric source identities](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/source-code-format#platform-file), [Get Item](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/get-item) and [dependency binding](https://learn.microsoft.com/en-us/fabric/cicd/cross-workspace-dependency-binding).
