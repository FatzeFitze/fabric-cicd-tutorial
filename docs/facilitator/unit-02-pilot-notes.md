# Unit 2 preparation and pilot checks

Date: 29 October 2026. Status: participant lesson/worksheet authored; Fabric-to-Git commit, Git-to-Fabric update and timing are not yet reported.

Participant entry point: [Unit 2](../tutorial/section-01-foundation/unit-02-capture-the-solution-in-git/README.md). Its [worksheet](../tutorial/section-01-foundation/unit-02-capture-the-solution-in-git/resources/source-baseline.md) is unit-specific evidence capture, not an implemented deployment schema.

## Starting evidence and bounded layout choice

- Unit 1 completed successfully by organizer report in 20–30 minutes including reading; starter source and corrected UI wording were pushed by the organizer. Local latest commit at Unit 2 authoring is `169a56e` (`finished first version of unit 1`). The organizer's statement establishes publication; do not claim a fresh remote comparison was performed here.
- Supplied provisioning records have three separate role repos on `dev`, Git directory `/`. Use these existing bindings for the pilot's first real commit/update. No repo migration, reconnect or new branch is required.
- This is an implementation choice for the current walkthrough, not organizer approval of three repos as the final workshop architecture. One solution repo with role folders remains the recommendation; settle the event/Model B layout before writing multi-repo release orchestration. Adapt the unit's mapping/examples if that choice changes, rather than require a migration exercise.
- Unit 2 direct commits are intentional Model A bootstrap. Do not enable a PR-only branch policy without supplying an approved bootstrap route. Model B policies come later; no bypass of a pre-existing policy is authorized by the lesson.

## New exercise boundary

Capture the Data lakehouse and Code notebook as supported definitions. Inspect real generated source and identities, then make one Markdown-only change in Azure Repos, apply it through Fabric Update, and rerun the existing workload. Record Data/Code commit IDs separately, with final Code SHA taken after the Markdown edit. No schema changes, business-rule changes, Feature workspace, Test/Prod deployment or automation identity is introduced.

The curriculum's original Unit 2 slot is 25 minutes. Participant guidance allows 25–35 minutes for the added round-trip check; measure the actual attempt and use the existing support reserve rather than silently changing the nine-hour core budget. If it is too slow, consider whether the round trip belongs in a later unit, explicitly preserving coverage of the first real update operation.

## Checks to collect during the walkthrough

1. Existing mapping and participant authentication allow the two full-item commits without reconnecting. Record whether the participant differs from the provisioner; author metadata alone does not prove the credential used.
2. Record exact Source control labels and generated folder/file lists for both assets. Expected current notebook format is `.platform` plus `notebook-content.py`; do not fabricate a full lakehouse file inventory from documentation.
3. Inspect the real notebook default-lakehouse reference: physical IDs, logical IDs and settings actually exported. No cross-workspace remapping claim follows from merely seeing `.platform`.
4. Confirm runtime rows/Delta files are absent from lakehouse Git capture and notebook output is absent, while embedded fixtures are present as source.
5. Verify the Markdown-only repo edit appears as a known incoming update, applies cleanly, preserves the target attachment and passes `UNIT_01_PASS` on rerun with six rows/revenue 342.20.
6. Capture final full commit IDs/links per repo, identity observations, total time and any UI/authentication/policy friction. Retain private source/context in appropriate local notes; do not publish raw company credentials or configs.

No raw export, sync result, commit IDs, cloud execution or independent identity run is supplied at authoring time. Local checks can validate Markdown links/structure only; they cannot pass these checkpoints.

## Control coverage and limits

| Control | Touchpoint | Remaining boundary |
| --- | --- | --- |
| MS-02 | Real definitions captured in approved participant Git location | Pilot pending; final event source layout unresolved |
| MS-03 | Meaningful messages, diff review and traceable source change | No PR policy/reviewer gate yet |
| MS-06 | Git mapping and explicit notebook attachment inspected | Environment-aware deployment config not built |
| MS-07 / MS-12 | Personal credentials/repo access distinguished from workspace permissions | Non-human deployment and separate-user test not established |
| MS-08 | Rerun validates the unchanged result after definition update | No target-environment release validation |
| MS-14 | Per-repo commit IDs, item identities and runtime checkpoint recorded | Worksheet is not the final automated release-evidence contract |

## Gate before Unit 3

Use the actual exported definitions and binding settings from Unit 2 in V03/V04 native feasibility. The Unit 1 Dev-only guard values still need a validated target-aware mechanism before promotion; do not remove the guard or hand-edit target source as a hidden workaround. Prove Data/Code native stage configuration, initial target creation, lakehouse binding/rules, repeat promotion and execution. Unit 2 completion alone does not pass those experiments.

Official Git integration, notebook/lakehouse source representation and Azure Repos references are linked in the lesson and registered in [sources.md](../planning/sources.md). They support authoring assumptions, not observed pilot success.
