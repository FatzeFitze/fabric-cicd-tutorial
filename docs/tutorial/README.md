# DNA Fabric Days: participant tutorial

This tutorial is being developed through an organizer-led participant pilot. Follow one unit, report the observed result, and revise the instructions before proceeding. A written unit is not yet a validated exercise.

The working scenario is a small synthetic sales solution that progresses from controlled native promotion (Model A) to managed team delivery (Model B). Model C and feature workspaces remain explainer topics. The participant solution starts in its own Azure DevOps project/repository; this preparation repository supplies selected instructions and starter files as needed.

## Start here

| Unit | Outcome | Status |
| --- | --- | --- |
| [0. Observe and test the setup](section-01-foundation/unit-00-observe-and-test-the-setup/README.md) | Explain the components and inspect the provided workspace/repository layout | Parked as-is after organizer review; access checks reported successful; learner timing unmeasured |
| [1. Create a tiny sales solution](section-01-foundation/unit-01-create-a-tiny-sales-solution/README.md) | Create a cross-workspace lakehouse/notebook slice, validate six synthetic orders and rerun without duplication | Organizer reports successful walkthrough in 20–30 minutes including reading; OneLake picker wording corrected |
| [2. Capture the solution in Git](section-01-foundation/unit-02-capture-the-solution-in-git/README.md) | Capture real definitions, inspect identities/data boundaries, apply a Markdown-only Git update and record per-repo source revisions | Completed by organizer report; commit-diff review and open-editor guidance corrected; duration not supplied |
| [3. Native promotion](section-02-model-a/unit-03-native-promotion/README.md) | Promote the common-source Data/Code slice through Test and simulated Prod, with explicit bindings and runtime/release evidence | First working version accepted by organizer on 4 November; retain lesson content |
| [4. Connect orchestration, configuration and reporting](section-03-team-delivery/unit-04-connect-orchestration-configuration-and-reporting/README.md) | Consume library values through a pipeline/notebook, build a browser-authored Dev model/report and capture definitions/identity baseline | First version accepted by organizer on 4 November; clarified source logical IDs versus deployed physical IDs |
| [5. Make a local feature change](section-03-team-delivery/unit-05-make-a-local-feature-change/README.md) | Edit the returned-order rule locally, review and complete the first PR into `dev`, then compare the merged revision with live Dev | Accepted after successful organizer walkthrough on 10 November. |
| [6. Turn review into a required check](section-03-team-delivery/unit-06-required-pr-validation/README.md) | Add a reusable source validator and demonstrate a required PR check blocking a defect and passing after the fix | Starter checked locally. Azure Repos and hosted agent walkthrough pending. |

Reference: [Logical and physical IDs in Fabric](reference/fabric-item-identities.md). Introduced with Git capture, applied during local editing and revisited for target bindings/deployment evidence.

Optional companion: [Recover from source conflicts](auxiliary/aux-01-recover-from-source-conflicts/README.md). Concepts and recovery approach are available; the intentional-conflict lab is planned after Unit 5's local IDE/Git workflow and is outside required completion.

## Unit folder convention

Each participant unit has its own folder. `README.md` is the main lesson, with unit-specific resources kept alongside it. Create supporting folders only when they contain actual resources.

Create the unit folder and README entry point from the first preparation draft, including a rehearsal stage. Link existing rehearsal/shared assets rather than duplicating them. Commit/publish these files so the organizer can open the same materials from GitHub or the work-PC checkout; chat is not their only access route.

```text
docs/tutorial/
  section-01-foundation/
    unit-00-observe-and-test-the-setup/
      README.md
    unit-01-create-a-tiny-sales-solution/
      README.md
      resources/                # optional; create only for actual unit-specific files
```

Files needed only for one exercise belong in its unit folder. Reusable deployment code, shared sample definitions, pipeline templates and multi-unit examples remain in `toolkit/`, `sample/`, `pipelines/` or `examples/`, and units link to their canonical files. Avoid maintaining duplicate copies of shared code beside each lesson. The old setup-draft redirect is retained for historical links and is not an active participant unit.

From Unit 1 onward, lessons use a consistent participant-facing structure: outcomes/prerequisites, a short explanation, numbered assignments with expected results, troubleshooting, completion checkpoint and references. Organizer validation notes stay in [facilitator material](../facilitator/tutorial-authoring-guide.md).

## Agreed section and unit journey

The broad journey and minimal sample are organizer-approved. Future rows are planning references, not available or validated units:

Provisioning belongs to the [facilitator reference](../facilitator/project-and-environment-provisioning.md), outside learner exercise time. The earlier setup Unit 1 is superseded by the manual-asset Unit 1 linked above.

The [curriculum](../planning/curriculum.md) contains every unit's outcome, estimated time, MS-control touchpoints, asset-growth diagram/table and the staged introduction of reusable automation and parameterization.

| Section | Planned units | Outcome |
| --- | --- | --- |
| 1. Understand the setup and build the first result | 0–2: setup inspection, lakehouse/notebook, Git baseline | Working deterministic Dev result and traceable source |
| 2. Release the small solution with Model A | 3: native promotion and verification | Minimal two-role slice works in Test and simulated Prod |
| 3. Grow the solution and introduce team development | 4–6: Variable Library, orchestration/reporting, local feature, reusable CI/PR controls | Full Dev sample and a reviewed, validated source change |
| 4. Automate the Model B release | 7–10: environment/dependency configuration, shared Dev, Test, approved Prod | One selected source released with explicit target bindings and runtime evidence |
| 5. Operate, recover and reuse | 11–12: failure/recovery, starter reuse and control selection | Verified recovery and a small configuration-based reuse exercise |

The working time budget is nine core hours with 1.5 hours of support reserve, still to measure. The native lakehouse/notebook path, Variable Library consumer/active-set automation, later reporting format and Model B mechanisms need validation. Prepared generic components and their config examples are introduced in Units 6–10, after they have been built/tested here. Unit 0 remains parked; future units are not authored merely by appearing in this table.

Unit boundaries and timing will change with pilot feedback. No future unit should assume the old reference lab's cloud behavior applies to this sample.

## How to report a result

Use the checkpoint at the end of the unit. Report what happened, the approximate time, confusing wording and any exact error text. A failed checkpoint is useful evidence; it is not a reason to invent an undocumented workaround.

The facilitator keeps the [pilot record](../facilitator/pilot-log.md), including the document revision actually followed. Keep private setup details in local notes where needed.
