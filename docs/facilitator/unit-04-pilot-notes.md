# Unit 4 preparation and pilot checks

4 November 2026. Status: organizer reports progressing through Unit 4 successfully apart from the UI/measure-name issues below; scope and length judged appropriate, exact duration not supplied. The screenshot independently shows a successful pipeline notebook run and parameter injection. The assistant has not executed these cloud actions. Revised connection/inspection guidance and the newly added price-change exercise need another walkthrough. Unit 3 remains parked as its first working version.

Participant entry point: [Unit 4](../tutorial/section-03-team-delivery/unit-04-connect-orchestration-configuration-and-reporting/README.md). Shared starters: [two parameter cells](../../sample/tiny-sales/unit-04-parameter-cells.py) and [five DAX measures](../../sample/tiny-sales/sales-model-measures.dax). Unit-specific evidence: [Dev solution record](../tutorial/section-03-team-delivery/unit-04-connect-orchestration-configuration-and-reporting/resources/dev-solution-record.md).

## Chosen pilot path

- Continue the existing three-repo pilot and current Code/Data/Reporting role layout. No workspace/repo migration is part of this unit. Final event/Model B repo topology remains open.
- Add a simple notebook parameter cell before the existing guard and runtime-parameter validation after it, leaving existing fixture/transformation/write code intact. The pipeline passes scalar library variables; the notebook does not call NotebookUtils Variable Library APIs directly.
- Create `sales_config` and `run_sales` in Code Dev. Start with active Default values and the default human-context notebook activity route, leaving Connection unselected where supported. Explicit connection-based authentication, Test/Prod alternative value sets and managed runtime are separate later work. The exact Connection choice used by the organizer is awaiting clarification.
- For the browser reporting path, explicitly choose **Direct Lake on SQL** through the Data Dev lakehouse's **SQL analytics endpoint → New semantic model** dialog, then save the model/report to **Reporting Dev**. Current documentation says that creation entry point supports selecting both Direct Lake types and that defaults vary; do not silently accept OneLake mode and claim this chosen path was tested.
- One curated `sales` table, five simple measures, three cards and one product chart. No Desktop, external source, extra Fabric Environment or complex model relationships. Record actual Git report/model format instead of fabricating exports.

The original Dev walkthrough is successful by organizer report. That supports the pilot direction without validating clean-target/managed-identity release tests. Unit 4 is human-authored Dev only; do not manually promote the new items into Test/Prod and accidentally erase the later first-create identity experiment.

## Feedback and corrections after revision 5ff16e1

- New item is labeled **Pipeline**, not Data Pipeline. Base parameters exposes **Name / Type / Value**; reference aliases appear inside Value expressions rather than in another field.
- Connection showed `Select…`, `No results found`, Browse and Use Dynamic Content. The successful run does not by itself establish the exact connection selection. Removed the instruction to create an arbitrary organizational-account connection. The REST definition marks TridentNotebook's `externalReferences` optional; Microsoft documents the default pipeline context as the last modifying user. The revised baseline leaves it unselected, verifies execution/Submitter and stops for facilitator diagnosis if that route is unavailable. Confirm the organizer's actual choice and separately test a different participant account before event freeze. An empty list alone does not establish why no connection is eligible/visible.
- The supplied successful run snapshot contains authored defaults followed by Fabric's generated runtime assignments: `interactive` is overridden with `tiny_sales_dev`. This matches documented injection behavior; it is not a source duplication. A human Submitter is visible, but no conclusion about every downstream identity follows. Do not publish the raw company account/screenshot.
- Browser model edits autosave. Removed the model Save instruction. The `Revenue` measure name conflicts with the existing `revenue` column; starter and lesson now consistently use **Total Revenue** while preserving the column/schema. The organizer's exact workaround/final measure name was not supplied.
- Added precise endpoint/settings/connection inspection and read-only TMDL connector checks, with exported-source fallback. These new directions have not been replayed. The creation selection and actual source expression must agree; a Direct Lake storage-mode label alone cannot distinguish the two types.
- Added a temporary P01 price change (1990 → 2490 cents) and both expected monetary totals (342.20 → 357.20), report refresh verification (mug 59.70 → 74.70), then restoration before Git capture. This is new, locally calculated content; no cloud run of the changed fixture/refresh is claimed. Preserve canonical Unit 1 source and the final 342.20 baseline for Unit 5.
- Local IDE/Git development stays in Unit 5. An [optional conflict unit](../tutorial/auxiliary/aux-01-recover-from-source-conflicts/README.md) and [rehearsal plan](source-conflict-exercise-plan.md) distinguish local merges, Fabric item conflicts and stale editors. Intentional cloud-conflict recovery is not validated or part of core completion.

## Walkthrough observations needed

1. Confirm parameter-cell menu/parameter discovery, exact pipeline Library variables pane/picker and generated expressions. The documented reference pattern is `@pipeline().libraryVariables.<referenceName>`; notebook parameter names remain separate.
2. Confirm actual runtime output contains the non-default label from the library, a changed label is observed, and wrong `environment_name=test` in Code Dev fails before writes. Restore correct values, rerun and capture the final success.
3. Record the Notebook activity's actual connection/authentication UI, runtime principal if inspectable, and permission outcomes. Do not equate pipeline creator/owner, last editor and selected connection automatically; actual authentication settings determine the supported runtime route.
4. Verify the SQL endpoint sees the Spark-created `dbo.sales`, offers the chosen Direct Lake on SQL mode, and creates `sales_model` in Reporting Dev. Record source endpoint/database reference, connection configuration/SSO, ownership labels and whether refresh/framing works.
5. Confirm corrected web New measure/autosave guidance and Reporting Dev destination. Exact final values: Total Revenue 342.20, Order Count 6, Sample Check PASS; product totals Backpack 245.00, Travel mug 59.70, Lunch box 37.50. Quantity/returns checks remain 13/2. Rehearse the temporary 357.20/74.70 result and restoration.
6. Confirm Code library/pipeline/notebook and Reporting model/report can be captured in Git. Retain actual filenames/reference fields and full per-repo source revisions privately. New TMDL/PBIR or connection support limitations are blockers to resolve before release automation, not a reason to publish assumed bindings.
7. Measure total learner time and startup/readiness waits. The inherited 60-minute slot includes four new authored items and may need simplification or use of reserve; do not quietly remove runtime/binding checks to fit.

## Local checks versus cloud evidence

Parse the parameter source and exercise its pure validator with valid Dev/Test/Prod inputs, mismatched/unknown/missing environment and empty label. Independently recalculate product/overall metrics from the canonical Unit 1 fixtures. Check local lesson/resource links. These checks do not execute Fabric pipelines, compile DAX, create a semantic model/report, prove SQL metadata readiness or validate Git export formats.

The measure `Sample Check` deliberately checks only sample row/quantity/returns counts in the current filter context. It does not prove monetary correctness or source identity; those are separate notebook/source/runtime checks. The upcoming returned-order feature keeps the table schema and report's Total Revenue measure compatible.

Feedback-revision local verification, 4 November: checked 91 relative links across changed/new Markdown and balanced code fences. Independent Decimal arithmetic using the canonical fixtures confirms original → changed → restored totals of 342.20 → 357.20 → 342.20 and Travel mug totals of 59.70 → 74.70 → 59.70; row/quantity/returns counts stay 6/13/2. Canonical Unit 1 source and the parked Unit 3 lesson are unchanged. No Fabric refresh, new DAX evaluation or intentional conflict recovery was executed by these checks.

## Ownership thread

The user requested a later first-create experiment under managed Test/Prod deployment. [The experiment plan](../planning/identity-and-ownership-experiment.md) links Unit 4's human baseline to a new validation notebook in Units 9–10, plus comparison with updates to pre-existing human-created items. This is required future coverage (V20), not an inference that all asset types use the creator as every kind of owner/identity.

## Controls and next gate

MS-02/03: actual definitions/revisions; MS-04/06: role mapping and library/parameter/source relationships; MS-07/12: human baseline versus connection/query identity; MS-08/10: useful failure, runtime/report reconciliation and evidence; MS-14: Dev solution record. The sandbox does not establish least-privilege productive enforcement.

V05/V06/V19 have organizer-reported Dev progress; retain actual exports/source revisions and resolve connection/format gaps before finalizing automated bindings. New walkthrough changes and target/identity variants still need validation. No feature workspaces or simultaneous UI editing is required. Unit 5 should use the actual exported notebook representation, not an invented export layout.
