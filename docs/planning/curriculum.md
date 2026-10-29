# Curriculum and sample growth

Status: organizer accepted the broad section/unit journey and minimal sample on 29 October 2026, with a Variable Library added to the core asset set and explicit gradual introduction of reusable automation and parameterization. Code-workspace placement and the consumer design below are implementation recommendations to validate. Timings remain estimates; mechanisms remain subject to the listed technical gates. Unit 0 is parked after organizer review. Unit 1 has a successful organizer-reported walkthrough in 20–30 minutes including reading; its OneLake picker wording was corrected afterward. Unit 2 completed by organizer report; web-commit review and open-editor update guidance were refined. Unit 2 duration was not supplied. Units 3–12 remain planning references, not available lessons.

## Teaching journey

Build a small working solution first, release it with native controls, then strengthen the delivery workflow as the fictional business dependency grows. Model A is a legitimate operating model for appropriate risk; participants are not trying to earn a higher model by accumulating tools.

All nine workspaces exist from the start. Assets go directly into their intended code, data or reporting role. We progressively use the layout rather than move items between workspace roles halfway through the workshop. The first native exercise deliberately covers only the lakehouse/notebook slice; reporting arrives later and does not have to support both required deployment paths.

The workshop is a training sandbox. The fictional solution is assessed as productive for teaching purposes. Participants' Admin rights mean the demonstrated delivery route can be bypassed; successful exercises do not establish productive enforcement.

## Sections and units

Times below include introductions, exercises and checkpoints. They are estimates to test, not observed learner durations. Starter snippets/templates enter when needed; participants do not implement a deployment library or an entire reporting solution from scratch.

### Section 1 — Understand the setup and build the first result

| Unit | Min | Work and observable checkpoint | Main controls |
| --- | ---: | --- | --- |
| **0. Observe and test the setup** | 20 | Inspect the nine workspaces, Azure DevOps resources, Git connections and access. Explain the three different kinds of pipeline and four types of state. Existing content stays parked. | MS-01, 04, 07, 12, 13 |
| **1. Create a tiny sales solution** | 45 | Manually create a lakehouse in Data Dev and notebook in Code Dev. Attach the cross-workspace lakehouse, add supplied deterministic input/logic, run it and check a known sales result. Record owner and intended operating model. | MS-01, 04, 06, 07, 08 |
| **2. Capture the solution in Git** | 25 | Commit supported definitions through Fabric using participant credentials. Inspect source, identities and role mappings; distinguish definitions from runtime state. Apply a Markdown-only Git edit back to Fabric, rerun checks and record per-repo source baselines. Participant estimate is 25–35 minutes; measure any reserve needed above this original slot. | MS-02, 03, 06, 14 |

### Section 2 — Release the small solution with Model A

| Unit | Min | Work and observable checkpoint | Main controls |
| --- | ---: | --- | --- |
| **3. Promote and verify with native Deployment pipelines** | 60 | Set up native promotion for the Data and Code workspace triplets. Deploy prerequisites before consumers, establish the target notebook/lakehouse binding through the validated mechanism, seed/run in Test, inspect the result, deliberately authorize simulated Prod promotion and repeat the smoke check. Record source, environment settings, promotion and a basic recovery/bootstrap procedure. | MS-02–11, 13, 14 |

This is a bounded two-asset exercise. The expected result is working Test/Prod output with verified target references, not simply green deployment status. No native Reporting pipeline is required. A fresh lakehouse definition must not be assumed to contain Dev data. A brief rerun of one small change shows repeatability; the fuller recovery exercise comes in Unit 11.

**Technical gate before authoring Unit 3:** prove this exact separated-workspace native path, including first deployment, target binding, repeat deployment and runtime validation. If it needs a manual target setting, make that setting a documented repeatable step and show its consequence. If it is too cumbersome for Model A teaching, revisit this unit's slice explicitly before building it; do not quietly add combined workspaces or present broken bindings as successful promotion.

### Section 3 — Grow the solution and introduce team development

| Unit | Min | Work and observable checkpoint | Main controls |
| --- | ---: | --- | --- |
| **4. Connect orchestration, configuration and reporting** | 60 | Create a Variable Library and Fabric Data Pipeline in Code Dev. Read a small runtime setting from the library in the pipeline and pass it to the notebook through the proven parameter route. Create one explicit semantic model over curated data and a one-page report in Reporting Dev using guided steps and small starter snippets. Run end to end, reconcile metrics and capture the new definitions in Git. Explain why regular changes/shared consumers motivate Model B. | MS-02, 04, 06–08, 10 |
| **5. Make a local feature change** | 35 | Clone the source, create a local feature branch and change the supplied revenue calculation to account for returned orders. Keep the output schema compatible with the existing report. Inspect the diff and open a PR; integration is deliberately held until the checks are configured. No feature workspace is needed. | MS-02, 03, 08 |
| **6. Add useful CI and PR controls** | 35 | Introduce the supplied validation starter and an Azure Repos build-validation policy. A deliberately wrong calculation fails a local/CI check; the corrected feature passes. Review and merge. Inspect the distinction between local checks and Fabric runtime tests. Shared Dev is not yet automatically updated. | MS-02, 03, 08, 14 |

Use one sales table and a few measures/visuals. Semantic-model storage mode, report representation and client prerequisites must be chosen before writing Unit 4. The core feature edits notebook/calculation source locally; it does not require simultaneous UI editing or local reproduction of Fabric Spark.

### Section 4 — Automate the Model B release

| Unit | Min | Work and observable checkpoint | Main controls |
| --- | ---: | --- | --- |
| **7. Describe environments and dependencies** | 45 | Add environment/configuration examples, extend the Variable Library with Dev/Test/Prod value sets and inspect the dependency plan. Distinguish runtime values, deployment bindings and Azure Pipeline parameters. Separate logical items from physical IDs; reject an absent value or forbidden Dev reference. Add these files through a reviewed change. | MS-03, 04, 06, 08, 12 |
| **8. Publish and validate shared Dev** | 65 | Add the prepared deployment entry point and Azure Pipelines template; configure their documented inputs and connect the validated runner/workload identity. Reconcile outstanding UI changes and retire the previous Dev writer. Deploy the selected source, explicitly establish/check the active Variable Library value set, inspect bindings, run/refresh as needed, and retain results. | MS-03, 05–08, 10, 12–14 |
| **9. Release the same source to Test** | 45 | Deploy all workspace roles using one selected source snapshot, with prerequisites, bindings and readiness checks in the proven order. Run the sample and verify report/model targets and expected metrics. Reject an intentionally invalid dependency in a safe preflight; inspect the evidence before proceeding. | MS-04–08, 10, 13, 14 |
| **10. Approve and release to simulated Prod** | 30 | Configure/use a real Azure DevOps resource approval, release the source already validated in Test, then run post-deployment checks. Read a release record connecting source, target items, approval and runtime results. Explain the limits of participant Admin access. | MS-03, 05, 07–10, 12, 14 |

The preferred Dev mechanism remains pipeline publishing, subject to validation. Controlled Git-update Dev is the alternative to assess, not a second required implementation. Native pipelines from Unit 3 become a comparison/reference path; normal Model B changes use the selected automation route. Do not keep competing native/manual and automated publishers active for the exercise.

The observed pilot has three repos, whereas the recommended participant architecture is one solution repo with role folders. Resolve the workshop choice before finalizing Unit 2 and local-development instructions. A final three-repo path needs a release record pinning each repo revision; a single commit cannot represent all three. Avoid a mandatory repository migration exercise merely to reconcile our pilot with the recommendation.

### Section 5 — Operate, recover and reuse

| Unit | Min | Work and observable checkpoint | Main controls |
| --- | ---: | --- | --- |
| **11. Diagnose a failure and recover** | 55 | Trigger a safe, rehearsed failure in Test after part of a release has succeeded. Use deployment/runtime evidence to identify the failed step, correct configuration or redeploy a known-good definition, and rerun to a verified state. Explain why source rollback does not restore data and why cross-workspace release is not a transaction. Record the owner and next action. | MS-01, 05, 06, 08, 10, 11, 14 |
| **12. Reuse the starter and choose the right controls** | 20 | Adapt a tiny supplied second example's configuration and project check; run its local validation/resolved-plan step without modifying toolkit internals. Locate the templates, configuration reference and support material. Classify a more critical scenario and identify Model C additions; explain when feature workspaces help. | MS-01–14 recap, especially 05, 09–12, 14 |

The second example is a small reuse check, not another complete cloud deployment. Full starter portability needs its own organizer feasibility test. Model C explainers cover independently protected production capability, separation of duties, stronger identity boundaries, monitoring/evidence retention, private execution where required, and risk-appropriate recovery. These remain obligations from the supplied guidelines, not claims that the sandbox implements them.

## How reusable automation enters the tutorial

Build, document and validate each starter here before its participant unit is offered. The learner path remains incremental: first observe the manual operation, then configure a small reusable component, then use it in a pipeline. Unit 0 is unaffected. The following is a delivery contract for preparation, not a claim that these components already exist.

| First unit | We prepare and test beforehand | Participant action / parameterization lesson |
| --- | --- | --- |
| 4 | Minimal Variable Library example and a proven pipeline-to-notebook parameter flow | Create the library manually; consume a value such as `environment_name` and inspect the received runtime value |
| 6 | Reusable validation entry point, project-specific assertions and a thin CI YAML example | Add the selected files, supply source/config/check locations, and see a meaningful failing/passing check |
| 7 | Small environment/dependency examples with documented fields, tool-native replacements and validation | Fill role/workspace mappings, allowed references and intended active value set; inspect a resolved plan before deployment |
| 8 | One reusable deployment/validation entry point plus a parameterized Azure Pipelines job/stage template | Wire a thin project pipeline to the starter; select environment/config/source inputs and understand identity setup; do not copy and modify the deployment implementation per environment |
| 9–10 | Tested Test/Prod stages, pinned-source handling, target checks and release record | Reuse the same implementation with the target's configuration; inspect approval and runtime evidence |
| 11–12 | Rehearsed fault/recovery and a second tiny example with different configuration/checks | Recover through the same entry point and demonstrate reuse without editing generic internals |

Keep three parameterization concerns explicit:

- **Runtime configuration:** the Variable Library holds a few non-secret values used by Fabric items. Start with `environment_name`; add target references only if a demonstrated consumer requires them. Proposed home: each environment's Code workspace beside the consuming Data Pipeline/notebook.
- **Deployment configuration:** versioned solution/environment files describe role routing, binding intent, target mappings and desired active value set. Resolve physical item IDs where supported instead of asking learners to copy all IDs. Do not rely on a library already existing to bootstrap its own deployment. If a fact appears in both a deployment map and a runtime value set, derive it or validate consistency rather than maintain contradictory sources.
- **Pipeline inputs and protected resources:** Azure Pipelines selects the environment and the already selected source snapshot and supplies documented config paths. Authentication uses the configured connection/identity; production approval is a resource check. Runtime parameters must not allow a release to substitute unvalidated source or bypass target/approval boundaries.

Use tool-native parameterization where it covers the need; add generic code only for proven gaps. Shared implementation belongs in `toolkit/` and `pipelines/`; sample logic and assertions in `sample/`; documented example settings in `config/` or `examples/`. Unit resources link to those canonical assets. The supported bootstrap must pin/version the starter and keep the same implementation/source selection throughout the release.

### Variable Library feasibility and teaching checkpoints

The required outcome is a real value consumed during execution, its definition visible in Git, the correct target value set selected, and a wrong/missing setting detected during validation. A UI-only tour is insufficient. Place the first demonstration in Unit 4 so Unit 3 stays a two-asset native exercise; Model B then deploys and validates the library with the other Code items. Recheck the 60-minute Unit 4 estimate during the pilot rather than quietly adding required hours.

Current [Variable Library lifecycle guidance](https://learn.microsoft.com/en-us/fabric/cicd/variable-library/variable-library-cicd) states that active value-set selection is workspace state, absent from Git, and initially Default on import. Explicitly establish/check the target selection before running consumers; do not assume successful definition deployment selected Test or Prod. The [NotebookUtils guidance](https://learn.microsoft.com/en-us/fabric/data-engineering/notebookutils/notebookutils-variable-library) restricts direct library reads to the same workspace and currently lists a service-principal limitation. Prefer proving a same-Code-workspace Data Pipeline consumer that passes a value to the notebook; direct notebook library reads are optional until validated for the actual runtime identity. Deployment identity and runtime identity must be tested separately. These documentation claims were checked 29 October 2026; no workshop runtime result is established.

## Timing and supporting material

- Units 0–6: **4 h 40 min**, proposed Day 1 core.
- Units 7–12: **4 h 20 min**, proposed Day 2 core.
- Total core: **9 hours**. Add **1.5 hours distributed reserve**, giving **10.5 working hours**. Breaks are additional; confirm that event scheduling treats them that way.
- Up to another 1.5 hours is optional only if a 12-hour working budget is confirmed. Do not spend the support reserve on compulsory extensions.

Pre-read/reference pages cover a short ALM/Git glossary, classification and four states, identity purposes, and a local-tool/access checklist. Recap concepts when used. Facilitator material holds provisioning, approvals/service-connection setup, solutions, checkpoint recovery and timing evidence. The learner must observe the identity/approval boundaries even when a facilitator performs an administrative step.

Optional material: independent repo ownership, direct Git-connected versus pipeline-published Dev, feature workspaces, pair concurrency and additional Fabric item types. Keep these outside the core completion path.

## The mock project

**Working title: Tiny Sales — from manual build to controlled release.** A fictional small reporting solution starts with a few synthetic orders and later becomes a shared team-maintained data product. No external source system or personal/business data is required.

Use small versioned customers, products and orders fixtures or an equivalent deterministic generator. The notebook creates a single curated `sales` table containing the fields needed by the report. Store expected counts and monetary totals with the fixtures; choose and verify the actual numbers when implementing Unit 1. Do not reuse the historical lab's expected totals without reproducing its data.

Unit 1 supplies the [canonical starter](../../sample/tiny-sales/unit-01-notebook.py): three customers/products and six orders, quantity 13, two returned orders, baseline gross revenue/revenue 342.20. Independent local fixture arithmetic confirms these numbers and the later returned-order feature result of 189.70. The organizer reports successful Dev execution/persistence and completion in 20–30 minutes; no raw runtime output was supplied. Keep the 45-minute mixed-experience unit budget for now. The fixture inputs are embedded in source and initially exist in memory, with only the curated table persisted.

| Item | Workspace role | First created | Important relationship |
| --- | --- | --- | --- |
| `sales` lakehouse | Data | Unit 1 | Holds deterministic inputs/curated sales; its SQL analytics endpoint is a platform-provided companion where the chosen model mode needs it |
| `build_sales` notebook | Code | Unit 1 | Reads/writes the intended environment's Data-role lakehouse |
| `sales_config` Variable Library | Code (recommended) | Unit 4 | Supplies non-secret runtime values to a same-workspace consumer; each target selects its active value set |
| `run_sales` Fabric Data Pipeline | Code | Unit 4 | Executes `build_sales`; connections/runtime permissions checked separately |
| `sales_model` semantic model | Reporting | Unit 4 | Reads the intended environment's curated sales; storage mode remains a feasibility decision |
| `sales_overview` report | Reporting | Unit 4 | Uses `sales_model`; a few visuals show revenue, order count and a basic quality result |

These names are illustrative, not implemented asset definitions. The accepted minimal sample now has six authored item types, including the required Variable Library. Do not make a custom Fabric Environment, Warehouse or Dataflow Gen2 mandatory without an explicit scope decision.

```mermaid
flowchart LR
    fixtures["Tiny synthetic inputs\nUnit 1"] --> notebook["Code: build_sales notebook\nUnit 1; feature in Unit 5"]
    pipeline["Code: run_sales pipeline\nUnit 4"] -->|executes| notebook
    library["Code: sales_config Variable Library\nUnit 4; value sets in Unit 7"] -.->|runtime values| pipeline
    notebook -->|writes| lakehouse["Data: sales lakehouse / curated table\nUnit 1"]
    lakehouse -->|queried by| model["Reporting: sales_model\nUnit 4"]
    model --> report["Reporting: sales_overview\nUnit 4"]
```

This shows data flow and execution, not an executable deployment-order graph. Each environment has its own corresponding items. The notebook depends on the lakehouse even though the data-flow arrow points from notebook to lakehouse.

### Creation and linking sequence

| When | What grows | How we establish/check the link |
| --- | --- | --- |
| Unit 0 | Infrastructure only: nine workspaces and the initial Azure DevOps resources | Inspect role/environment mappings and personal Git access; do not assume any solution assets exist |
| Unit 1 | Lakehouse, then notebook, then data | Explicitly attach the Data Dev lakehouse to the Code Dev notebook; execute and inspect expected output |
| Unit 2 | Versioned baseline | Capture definitions and inspect the lakehouse reference; compare Git with runtime data |
| Unit 3 | Minimal slice reaches Test and simulated Prod | Promote the lakehouse prerequisite, then notebook, configure/verify each target binding, execute in the target and verify environment isolation |
| Unit 4 | Variable Library, Data Pipeline, semantic model and report in Dev | Read the library through a same-Code-workspace consumer and pass the value to the notebook; model to Data Dev's table; report to model. Run end to end and capture definitions |
| Units 5–6 | Returned-order feature plus useful checks | Change recognized revenue while keeping the published table schema compatible; a deliberately wrong expected result fails CI |
| Unit 7 | Explicit environment/dependency configuration and library value sets | Inspect notebook/lakehouse, pipeline/notebook, pipeline/library, model/data and report/model relationships; distinguish desired active-set configuration from versioned library definitions |
| Unit 8 | Full Dev solution under one automated writer | Discover/create target items, resolve/inspect bindings, establish/check active value set, seed/run and refresh as required, then compare metrics |
| Units 9–10 | Full solution reaches Test and simulated Prod | Use pinned source, proven target-specific ordering/binding and runtime checks; confirm a Test/Prod run does not write into Dev |
| Units 11–12 | Recovery and portability evidence | Correct/redeploy and verify convergence; change a second example's config without changing generic implementation |

The actual automated order may include create-then-bind steps: storage prerequisites, deployable definitions, bindings/settings, runtime execution and consumption readiness are separate operations. Derive that order from V04–V07, not solely from this illustration. Do not assume deploying a semantic model also executes the notebook or makes its data ready.

## Decisions and evidence before detailed authoring

The next concrete preparation asset is the [organizer's native Test rehearsal](../facilitator/unit-03-native-promotion-rehearsal.md), with a locally checked candidate first-cell replacement. It addresses the Dev-only guard and explicit native target rule before we finalize participant Unit 3. It has no observed native result and is not an additional mandatory learner unit.

1. **Native boundary (V03/V04/V07):** prove the two-role lakehouse/notebook exercise and its target settings. Reporting is intentionally not a prerequisite for completing Model A in this proposal.
2. **Reporting path (V06):** select one model mode/report representation, required client tools, deployment/identity support and a fast authoring route. Validate it before committing to Unit 4 instructions.
3. **Source layout (V17):** settle one repo/role folders versus the current three-repo pilot. Preserve what the pilot actually demonstrated and document release revision selection accordingly.
4. **Model B writer and identity (V02/V16):** choose one Dev mechanism and validate the runner's authentication, required operations and runtime permissions. Managed identity provisioning is planned, not evidenced as complete.
5. **Checks and time (V08–V14):** rehearse clean-target release, repeat deployment, partial failure/recovery, representative capacity load and timed completion. Adjust unit sizes from evidence.
6. **Variable Library (V19):** prove same-workspace consumption under the chosen runtime identity, pipeline/notebook parameter flow, Git definition capture, fresh-target active-set configuration, repeat deployment and an invalid-setting check. Keep this required asset in scope; resolve mechanism gaps before authoring its exercise.

Microsoft's [cross-workspace definition-binding guidance](https://learn.microsoft.com/en-us/fabric/cicd/cross-workspace-dependency-binding) warns against assuming that cross-workspace item references will remap. The [native deployment process](https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/understand-the-deployment-process) also describes specialized cross-pipeline stage binding. The [notebook guidance](https://learn.microsoft.com/en-us/fabric/data-engineering/notebook-source-control-deployment) describes target-stage deployment rules. These are mechanism-specific documentation claims, checked 29 October 2026; none passes our exact tenant experiment.

Use the [validation backlog](backlog.md), [control coverage](control-coverage.md) and [pilot log](../facilitator/pilot-log.md) for evidence. Unit coverage above identifies teaching touchpoints, not a claim that every obligation of a listed MS control is implemented in that unit.
