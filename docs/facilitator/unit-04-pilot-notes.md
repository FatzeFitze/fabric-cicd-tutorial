# Unit 4 preparation and pilot checks

4 November 2026. Status: participant lesson/resources authored; no Variable Library consumption, pipeline execution, model/report creation or Git capture for these new items has been run here. Unit 3 is accepted as the first working version by organizer report; preserve its lesson content.

Participant entry point: [Unit 4](../tutorial/section-03-team-delivery/unit-04-connect-orchestration-configuration-and-reporting/README.md). Shared starters: [two parameter cells](../../sample/tiny-sales/unit-04-parameter-cells.py) and [five DAX measures](../../sample/tiny-sales/sales-model-measures.dax). Unit-specific evidence: [Dev solution record](../tutorial/section-03-team-delivery/unit-04-connect-orchestration-configuration-and-reporting/resources/dev-solution-record.md).

## Chosen pilot path

- Continue the existing three-repo pilot and current Code/Data/Reporting role layout. No workspace/repo migration is part of this unit. Final event/Model B repo topology remains open.
- Add a simple notebook parameter cell before the existing guard and runtime-parameter validation after it, leaving existing fixture/transformation/write code intact. The pipeline passes scalar library variables; the notebook does not call NotebookUtils Variable Library APIs directly.
- Create `sales_config` and `run_sales` in Code Dev. Start with active Default values and human organizational-account notebook activity authentication. Test/Prod alternative value sets and managed runtime are separate later work.
- For the browser reporting path, explicitly choose **Direct Lake on SQL** through the Data Dev lakehouse's **SQL analytics endpoint → New semantic model** dialog, then save the model/report to **Reporting Dev**. Current documentation says that creation entry point supports selecting both Direct Lake types and that defaults vary; do not silently accept OneLake mode and claim this chosen path was tested.
- One curated `sales` table, five simple measures, three cards and one product chart. No Desktop, external source, extra Fabric Environment or complex model relationships. Record actual Git report/model format instead of fabricating exports.

These are implementation selections informed by official documentation, not evidence of success in this tenant. They must pass the organizer walkthrough and later clean-target/managed-identity release tests before the Model B starter is considered validated. Unit 4 is human-authored Dev only; do not manually promote the new items into Test/Prod and accidentally erase the later first-create identity experiment.

## Walkthrough observations needed

1. Confirm parameter-cell menu/parameter discovery, exact pipeline Library variables pane/picker and generated expressions. The documented reference pattern is `@pipeline().libraryVariables.<referenceName>`; notebook parameter names remain separate.
2. Confirm actual runtime output contains the non-default label from the library, a changed label is observed, and wrong `environment_name=test` in Code Dev fails before writes. Restore correct values, rerun and capture the final success.
3. Record the Notebook activity's actual connection/authentication UI, runtime principal if inspectable, and permission outcomes. Do not equate pipeline creator/owner, last editor and selected connection automatically; actual authentication settings determine the supported runtime route.
4. Verify the SQL endpoint sees the Spark-created `dbo.sales`, offers the chosen Direct Lake on SQL mode, and creates `sales_model` in Reporting Dev. Record source endpoint/database reference, connection configuration/SSO, ownership labels and whether refresh/framing works.
5. Confirm web New measure/New report/save UI and Reporting Dev destination. Exact values: Revenue 342.20, Order Count 6, Sample Check PASS; product totals Backpack 245.00, Travel mug 59.70, Lunch box 37.50. Quantity/returns checks remain 13/2.
6. Confirm Code library/pipeline/notebook and Reporting model/report can be captured in Git. Retain actual filenames/reference fields and full per-repo source revisions privately. New TMDL/PBIR or connection support limitations are blockers to resolve before release automation, not a reason to publish assumed bindings.
7. Measure total learner time and startup/readiness waits. The inherited 60-minute slot includes four new authored items and may need simplification or use of reserve; do not quietly remove runtime/binding checks to fit.

## Local checks versus cloud evidence

Parse the parameter source and exercise its pure validator with valid Dev/Test/Prod inputs, mismatched/unknown/missing environment and empty label. Independently recalculate product/overall metrics from the canonical Unit 1 fixtures. Check local lesson/resource links. These checks do not execute Fabric pipelines, compile DAX, create a semantic model/report, prove SQL metadata readiness or validate Git export formats.

The measure `Sample Check` deliberately checks only sample row/quantity/returns counts in the current filter context. It does not prove monetary correctness or source identity; those are separate notebook/source/runtime checks. The upcoming returned-order feature keeps the table schema and report's Revenue measure compatible.

## Ownership thread

The user requested a later first-create experiment under managed Test/Prod deployment. [The experiment plan](../planning/identity-and-ownership-experiment.md) links Unit 4's human baseline to a new validation notebook in Units 9–10, plus comparison with updates to pre-existing human-created items. This is required future coverage (V20), not an inference that all asset types use the creator as every kind of owner/identity.

## Controls and next gate

MS-02/03: actual definitions/revisions; MS-04/06: role mapping and library/parameter/source relationships; MS-07/12: human baseline versus connection/query identity; MS-08/10: useful failure, runtime/report reconciliation and evidence; MS-14: Dev solution record. The sandbox does not establish least-privilege productive enforcement.

Resolve V05/V06/V19 from the walkthrough, then validate their target/identity variants before release templates are finalized. No feature workspaces or simultaneous UI editing is required. Unit 5 can reuse the actual exported notebook source only after these observations are recorded.
