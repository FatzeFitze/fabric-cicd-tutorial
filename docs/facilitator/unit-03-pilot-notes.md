# Unit 3 pilot notes

Updated 30 October 2026. Participant lesson: [Unit 3](../tutorial/section-02-model-a/unit-03-native-promotion/README.md). The [Test rehearsal](unit-03-native-promotion-rehearsal.md) retains the initial technical sequence and its evidence basis.

## Observed/reported evidence

The organizer reports that everything in the Test rehearsal worked. Two teaching corrections were supplied:

1. The new UI starts a deployment by selecting the **target Test stage**, then selecting the source item with **Deploy from = Data Dev**. Earlier wording implied selecting the item in the Dev stage.
2. Learners need explicit navigation to **Deployment pipeline view → target stage → Deployment rules → notebook**, plus an explanation of why rules/resource IDs matter. The notebook editor is not the rule entry point.

This supports the environment-aware source, two-role native Test setup, explicit target rule and repeatable Test execution by organizer report. Exact source revisions, raw runtime output, initial auto-binding target and elapsed time were not supplied. Do not infer a failed automatic binding merely because an explicit rule was used. No independent assistant cloud action was performed.

## Current lesson scope and remaining pilot

The organizer delegated whether to include Prod now. The chosen implementation completes native **Dev → Test → simulated Prod** in Unit 3, as the existing curriculum envisaged, so Model A has a complete release example before Model B automation. The Test material is refined from feedback; **Section 6 Prod is authored and untested**. New concept/navigation text has not been separately timed or replayed.

For the current organizer, do not require a duplicate Test setup. Verify the existing source, target context/rules and Test result, then start Section 6. Confirm both target selections use **Deploy from = Data Test / Code Test**, a distinct Prod lakehouse rule is applied by redeployment, Cell 1 identifies Prod, and the actual Data Prod table has six rows/revenue 342.20. Capture the authorization/source/configuration/runtime record and duration. Report any UI difference or first-target/schema/rule behavior before advancing to the next unit.

The full unit keeps its original 60-minute planning allowance; timing remains unmeasured. Concepts and the Prod extension may require reserve for mixed-experience learners. Adjust from evidence rather than silently omit binding/runtime checks.

## Teaching changes and technical limits

- Explain repeated item names, source logical IDs, concrete workspace/item IDs, and the difference between choosing a target and granting access.
- Distinguish supported native auto-binding from explicit target rules. Rule precedence is documented; a rule is repeatable configuration, not a manual source patch per release.
- Say explicitly that native Deployment pipelines promote saved workspace items, not an automatically pinned Git commit. Source is committed and held unchanged through the manual release; later Model B addresses stronger source selection.
- Treat per-environment metadata changes as intentional configuration only after inspecting their fields. Never assert byte-identical exported definitions across rules just because Python logic is unchanged.
- Initial Code deployment creates the target notebook; its rule is then configured and applied by another deployment before any full target run. Keep the target guard active throughout.
- Preserve deterministic overwrite as a tiny training-data bootstrap, not general productive data recovery. Do not equate Admin lab success with enforced approvals/least privilege.

## MS-control touchpoints

| Controls | Exercise evidence / limitation |
| --- | --- |
| MS-01–03 / MS-14 | Named owner, recorded per-repo source, source held unchanged, deployment/runtime record; no automated content provenance guarantee |
| MS-04 / MS-06 | Environment mapping, physical target IDs, explicit stage rules; Test reported passed, Prod pending |
| MS-05 / MS-08 | Fresh target, runtime validation, repeat Test deployment/rerun; full-chain Prod validation pending |
| MS-07 / MS-12 / MS-13 | Interactive identity, access/capacity prerequisites and public training path; workload identity/private route/least-privilege enforcement not established |
| MS-09 | Deliberate manual Prod authorization; no independent enforced approval gate in this model/lab exercise |
| MS-10 / MS-11 | Runtime/history checks, responsible contact and bootstrap/recovery explanation; no tested general data restore or complete operations monitoring |

The release worksheet is unit-specific lightweight evidence, not the schema for the generic Model B toolkit. Keep source-guideline obligations unchanged. Source documentation informs this design; only reported/retained experiment evidence establishes a passed checkpoint.
