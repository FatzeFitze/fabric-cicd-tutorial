# Unit 5 preparation and pilot checks

10 November 2026. The organizer accepted the revised Unit 5 lesson after completing all steps without issue, including the first PR into `dev`. The organizer confirmed the export path and format as `build_sales.Notebook/notebook-content.py`. Park the lesson body at `348d885`. The walkthrough report supplies no exact commit IDs, duration, full export or Spark run results.

Participant entry point: [Unit 5](../tutorial/section-03-team-delivery/unit-05-make-a-local-feature-change/README.md). Evidence worksheet: [feature record](../tutorial/section-03-team-delivery/unit-05-make-a-local-feature-change/resources/feature-record.md). Shared explainer: [Fabric item IDs](../tutorial/reference/fabric-item-identities.md).

## Selected scope and prerequisites

- Preserve the current three-repo pilot; clone only the Code repo and branch from `dev`. Data/Reporting source revisions remain pinned separately. No topology migration, new workspace or competing Dev writer.
- Edit the actual Fabric-exported `notebook-content.py` in an ordinary local VS Code folder. Preserve `.platform`, generated cell metadata, lakehouse/workspace bindings and notebook settings. The original Unit 1 fixture implementation remains canonical in `sample/tiny-sales`; the unit supplies only the changed expression, not a duplicate notebook.
- Keep returned rows and set their `revenue` to zero. With the P01 price of 2490 cents, expect gross 357.20 and revenue 204.70, with rows/orders 6/6 and quantity/returns 13/2. Earlier drafts that restored the fixture need to capture the revised Unit 4 baseline before branching.
- Complete the reviewed PR from `feature/exclude-returned-orders` into `dev`. The participant path suggests squash where permitted. Record the actual resulting `dev` commit. Honor any existing review or build requirements and collect the resulting policy status.
- Learners use Git diff review and a whitespace check in this unit. Record the 204.70 value as a feature expectation until a deployed run verifies it.
- The organizer confirmed the Python path used by Unit 6. Keep the full export and relevant markers available if a project check reports a mismatch during the next pilot.

## Walkthrough evidence needed

1. Git/VS Code availability and version, sign-in flow, repo contribution access, clone/push/PR permissions, installation restrictions and sign-in delay. Keep tool installation outside the 45–55 minute learner estimate.
2. Exact Code repo mapping, `dev` base commit, notebook folder/path and format, including relevant generated markers and parameter/guard ordering. Prefer a sanitized real export or narrow relevant excerpts; retain private workspace IDs/URLs outside published sources.
3. Successful branch creation/edit/diff/commit/push and full feature commit ID. Verify `.platform`, metadata/bindings and non-notebook files remain unchanged.
4. Correct PR source and target, review evidence, merge type, Completed status and full resulting `dev` revision. Record any completion blocker and how the learner satisfied it.
5. Compare the merged `dev` revision with the live notebook and persisted 357.20 baseline. Record the incoming Git update status for the later publishing handoff.
6. Actual learner duration and unclear steps. A solo learner is the required path; pairs can follow together. Independent review/enforcement is a later control boundary, not established by self-review in a training sandbox.

## Unit 6 preparation gate

Unit 6 uses the confirmed path as the default CI input and the documented Unit 5 expression for a bounded source contract. [Unit 6 pilot notes](unit-06-pilot-notes.md).

Build the first reusable validation starter here before offering its exercise. It must validate the actual exported representation without executing Fabric imports, guards or table writes offline. Design a meaningful check against the selected business transformation; a second hardcoded calculation that never exercises the feature cannot establish its correctness. Separate checks of source structure/configuration from business behavior and later Spark/runtime validation. If useful business validation requires extracting testable logic, make that explicit, preserve the exported-notebook path and keep the added learner work within the time budget.

Start a second PR from the merged `dev`. Rehearse registering the supplied YAML and making it a required build check, including any facilitator permissions needed to set the policy. Demonstrate that the policy blocks the defective revision and allows completion once the corrected revision passes. Carry the resulting source into the configuration and publishing exercises.

## Local verification of this preparation draft

- Inserted the lesson's exact replacement expression and expected-value edit into the canonical starter in memory and parsed the result as Python. The original four cell boundaries and fixture block were preserved. This checks the snippet's syntax in context, not an actual Fabric Git import or Spark evaluation.
- Independently joined the fixtures using integer cents with Unit 4's P01 price of 2490. The result was 6 rows and orders, quantity 13, two returns, gross 357.20 and revenue 204.70.
- Local review covers source syntax, links and fixture arithmetic. The merge and Fabric runtime are pilot checkpoints.

## ID teaching follow-up

Unit 2 introduces IDs, the shared reference gives the full distinction now, Unit 4 separates repo references from deployed item links, and Unit 5 preserves logical identity. Units 7–10 must show how the selected tooling correlates source identity and target physical IDs in configuration, resolved plans and logs/release evidence. Do not assume every tool honors logical IDs identically or that all dependency references are logical.

Controls: MS-02/03 source and review, MS-04 source/runtime isolation, MS-06 preserved environment metadata, MS-08 expected checks and evidence limits, MS-14 fixed source revisions/PR. Workload identities, target deployment and enforced approval boundaries remain untested.

## Sources

- [Notebook Git representation](https://learn.microsoft.com/en-us/fabric/data-engineering/notebook-source-control-deployment#notebook-representation-in-git).
- [Azure Repos cloning](https://learn.microsoft.com/en-us/azure/devops/repos/git/clone?view=azure-devops) · [Complete a pull request](https://learn.microsoft.com/en-us/azure/devops/repos/git/complete-pull-requests?view=azure-devops#complete-a-pull-request).
- [Fabric source identities](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/source-code-format#platform-file), [Get Item](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/get-item) and [dependency binding](https://learn.microsoft.com/en-us/fabric/cicd/cross-workspace-dependency-binding).
