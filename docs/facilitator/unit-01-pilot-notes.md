# Unit 1 preparation and pilot checks

Date: 29 October 2026. Status: organizer reports successful Unit 1 completion in approximately 20–30 minutes including reading. Picker wording corrected after the walkthrough; starter code unchanged.

Participant entry point: [Unit 1](../tutorial/section-01-foundation/unit-01-create-a-tiny-sales-solution/README.md). Canonical starter: [unit-01-notebook.py](../../sample/tiny-sales/unit-01-notebook.py). The [authoring guide](tutorial-authoring-guide.md) records the clean participant-document convention.

## Implemented exercise design

- Create the schema-enabled `sales` lakehouse in Data Dev, and `build_sales` PySpark notebook in Code Dev.
- Attach and pin the separate-workspace lakehouse before starting the session.
- Manually copy four source sections into notebook cells, with two explicit Dev workspace-name settings.
- Inspect runtime context, construct three small in-memory fixtures, join/validate, overwrite one disposable Delta table and validate the persisted data.
- Rerun without duplicating rows; keep the source/data in place for Unit 2. No Git commit, deployment, package installation, external ingestion, Variable Library or data-pipeline creation is part of Unit 1.

This file is starter source rather than a Fabric item export. Do not present it as a Git-syncable definition. Unit 2 must capture the actual participant-created `.platform` and notebook definition representation.

## Local checks and their limits

Local verification should parse the starter, independently calculate its fixture metrics and expected returned-order feature result, and exercise the target guard against matching/mismatched/missing context values. Check lesson links and expected-result consistency. These checks do not execute PySpark, Delta writes, NotebookUtils, the picker or cross-workspace permissions. Record actual check results in the pilot log; do not treat local fixture arithmetic as V04/V07 passing.

Unit 1 has six distinct orders, quantity 13, two returned orders, gross revenue and revenue 342.20, and zero invalid rows. Unit 4 carries forward a revised price and 357.20 gross. Unit 5 applies returned-order exclusion to that revised fixture and expects 204.70 revenue.

## Organizer walkthrough outcome

The organizer reports that everything worked, with one UI correction: attaching a lakehouse uses **Add data items → From OneLake catalog**. This supports the initial Dev notebook/lakehouse execution and rerun path as organizer-reported behavior, not independent assistant observation. Exact session outputs, item links and followed commit were not supplied. A deliberate wrong-target run and a separate non-provisioner account test were not reported.

Section 2 now uses that observed path. Official notebook attachment examples document the same menu, with **Connect** or **Add** as the picker confirmation label. They also warn to choose the Lakehouse item, not the SQL analytics endpoint. The revised text has not had a separate walkthrough. Keep the participant estimate/budget of 45 minutes for mixed experience; the 20–30 minute result is the organizer's first measured range, not a novice-class average.

## Checklist for subsequent walkthroughs

1. The Fabric creation/picker labels and schema-enabled lakehouse choice match the instructions.
2. The notebook is in Code Dev and can select Data Dev's lakehouse with the participant account. Report whether the account differs from the provisioner's; do not infer it.
3. Runtime context exposes `currentWorkspaceName`, `defaultLakehouseWorkspaceName` and `defaultLakehouseName` as expected; correct names pass, a wrong setting stops before persistence.
4. `saveAsTable("sales")` resolves to the attached schema-enabled Data Dev lakehouse's `dbo.sales`, and its preview contains the expected six rows. Record any schema/session or cross-workspace catalog differences instead of adding a substitute Code lakehouse.
5. The target check, prepared-result check and persisted-result check all pass; rerun still produces six rows. Record the final success message and item locations.
6. Record total learner time, Spark startup/wait separately, code-copy friction, unclear wording and exact failures. Compare with the organizer's 20–30 minute range and the 45-minute planning allowance; startup time was not separately supplied for the first attempt.

Collect enough evidence for V04/V07 at this initial Dev stage, but do not mark their clean-target deployment requirements passed. Stop the Spark session when the learner is finished if useful for capacity; preserve notebook/lakehouse/data.

## Control touchpoints

| Control | Teaching/evidence here | Limit |
| --- | --- | --- |
| MS-01 | Learner/team identified as initial solution owner/contact in notebook description | Formal support arrangements later |
| MS-04 | Code/Data roles and Dev selected explicitly | No Test/Prod deployment yet |
| MS-06 | Default lakehouse and two target-name settings made explicit | Temporary Dev configuration; reusable config comes later |
| MS-07 / MS-12 | Interactive participant identity needs both workspaces | Admin lab permissions; workload identity not tested |
| MS-08 | Expected metrics checked before and after persistence; unit completed by organizer report | No raw runtime outputs supplied; no promoted-target validation yet |
| MS-05 / MS-11 | Deterministic overwrite and rerun discussed | Not a proven fresh-target bootstrap or productive data recovery |

## Dependencies for later units

- Unit 2 needs actual notebook-definition export/Git behavior from this setup, not a guessed `.platform` file. Repo topology remains an explicit separate decision; Unit 1 does not depend on changing the three-repo pilot.
- The two expected workspace-name values are deliberately Dev-only. Before Unit 3, introduce a validated target-aware configuration/input mechanism while retaining target checks and identical controlled definitions across stages. Do not hand-edit promoted notebook source separately in Test/Prod or remove the guard as an undocumented workaround. Resolve this with V03/V04 native feasibility.
- Unit 4 adds the Code-role Variable Library and pipeline consumer. It must not become an unmentioned prerequisite for Unit 1.
- Shared-Dev local feature development must account for the actual Fabric-exported source format. The sample's `revenue` column is intentionally compatible with later returned-order logic.

## Documentation basis

Official notebook/lakehouse, schema, runtime-context and updated picker references are linked in the participant lesson and registered in [sources.md](../planning/sources.md). Organizer-reported completion supports the Dev slice; target deployment, automated identities and other broader experiments remain pending.
