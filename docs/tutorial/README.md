# DNA Fabric Days: participant tutorial

This tutorial is being developed through an organizer-led participant pilot. Follow one unit, report the observed result, and revise the instructions before proceeding. A written unit is not yet a validated exercise.

The working scenario is a small synthetic sales solution that progresses from controlled native promotion (Model A) to managed team delivery (Model B). Model C and feature workspaces remain explainer topics. The participant solution starts in its own Azure DevOps project/repository; this preparation repository supplies selected instructions and starter files as needed.

## Start here

Coming to DNA Fabric Days? The [participant prep guide](pre-reads/README.md) covers what you'll get, what to set up and which background reading to pick.

| Unit | Outcome | Status |
| --- | --- | --- |
| [0. Observe and test the setup](section-01-foundation/unit-00-observe-and-test-the-setup/README.md) | Explain the components and inspect the provided workspace/repository layout | Setup exercise parked after organizer review; access checks reported successful; learner timing unmeasured |
| [1. Create a tiny sales solution](section-01-foundation/unit-01-create-a-tiny-sales-solution/README.md) | Create a cross-workspace lakehouse/notebook slice, validate six synthetic orders and rerun without duplication | Organizer reports successful walkthrough in 20–30 minutes including reading; OneLake picker wording corrected |
| [2. Capture the solution in Git](section-01-foundation/unit-02-capture-the-solution-in-git/README.md) | Capture real definitions, inspect identities/data boundaries, apply a Markdown-only Git update and record per-repo source revisions | Completed by organizer report; commit-diff review and open-editor guidance corrected; duration not supplied |
| [3. Native promotion](section-02-model-a/unit-03-native-promotion/README.md) | Promote the common-source Data/Code slice through Test and simulated Prod, with explicit bindings and runtime/release evidence | First working version accepted by organizer on 4 November; retain lesson content |
| [4. Connect orchestration, configuration and reporting](section-03-team-delivery/unit-04-connect-orchestration-configuration-and-reporting/README.md) | Consume library values through a pipeline/notebook, build a browser-authored Dev model/report and capture definitions/identity baseline | First version accepted by organizer on 4 November; clarified source logical IDs versus deployed physical IDs |
| [5. Make a local feature change](section-03-team-delivery/unit-05-make-a-local-feature-change/README.md) | Edit the returned-order rule locally, review and complete the first PR into `dev`, then compare the merged revision with live Dev | Accepted after successful organizer walkthrough on 10 November. |
| [6. Turn review into a required check](section-03-team-delivery/unit-06-required-pr-validation/README.md) | Add a reusable source validator and demonstrate a required PR check blocking a defect and passing after the fix | Accepted after organizer walkthrough on 10 November. |
| [7. Configure and preview a release](section-04-release-automation/unit-07-configure-and-preview-release/README.md) | Fill the release mask, version the alternative value sets and review a read-only plan through the required PR check | Lesson accepted with a clarification about the static check. Exact run evidence pending. |
| [8. Verify the shared Dev workspaces](section-04-release-automation/unit-08-publish-shared-dev/README.md) | Use the Dev identity to verify workspace names, item IDs and exported bindings | Organizer reports the live preflight passed and logical IDs matched. |
| [9. Publish Tiny Sales to Test](section-04-release-automation/unit-09-release-to-test/README.md) | Run the preflight and managed publish together, then review evidence and item ownership | Managed Test publish verified from run 643. Manual Test pipeline and notebook checks reported successful. Ownership and rerun observations pending. |
| [10. Approve and publish Tiny Sales to Prod](section-04-release-automation/unit-10-release-to-prod/README.md) | Approve the tested snapshot, publish with the Prod managed identity and record first creation and runtime results | First lesson version accepted at `b723a58`. Prod run 654 published the tested snapshot and runtime checks passed by organizer report. Shared publisher refactor awaits a live rerun. |
| [Publish the Tiny Sales baseline](section-05-operate-and-reuse/README.md) | Reconcile the release tooling, validate in Test and publish the Code tag and release note for both advanced labs | Organizer reports a successful rehearsal. |
| [11. Diagnose and recover a failed Test release](section-05-operate-and-reuse/unit-11-recover-a-test-release/README.md) | Track deployments, diagnose a live workspace name mismatch and verify a corrected release | First lesson version accepted at `b3ed5e0`. Live walkthrough pending. |
| [12. Use a shared deployment starter](section-05-operate-and-reuse/unit-12-shared-deployment-starter/README.md) | Extend Tiny Sales with a report and project check, then verify the shared release path in Test | First draft. Local fixture checks passed; live Test walkthrough pending. |

Reference: [Logical and physical IDs in Fabric](reference/fabric-item-identities.md). Introduced with Git capture, applied during local editing and revisited for target bindings/deployment evidence.

Explore which checks can run from Git, where they help and when live evidence is needed. [Static validation for Fabric items](reference/static-fabric-validation.md).

See how a pipeline signs in as a managed identity and where to grant permissions. [Service connections, managed identities and federation](reference/release-service-connections.md).

Read the Test release artifact and see how its fields support review, automated gates and recovery. [Read and design a release manifest](reference/release-manifests.md).

Trace Unit 12 from pipeline entry points to tests and publishing. [Deployment starter YAML](reference/deployment-starter-yaml.md) · [Deployment starter Python](reference/deployment-starter-python.md).

Where a step demonstrates a DataOps control, look for its **MS** number and the practical evidence it produces. Use the Solution Classification Framework to choose the operating model for a real solution, then read the matching column of the Fabric Minimum Standard. [DataOps guidelines](../source-guidelines/README.md).

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

Files needed only for one exercise belong in its unit folder. Reusable deployment code, shared sample definitions, pipeline templates and multi-unit examples remain in `toolkit/`, `sample/`, `.azuredevops/pipelines/` or `examples/`, and units link to their canonical files. Avoid maintaining duplicate copies of shared code beside each lesson. The old setup-draft redirect is retained for historical links and is not an active participant unit.

From Unit 1 onward, lessons use a consistent participant-facing structure: outcomes/prerequisites, a short explanation, numbered assignments with expected results, troubleshooting, completion checkpoint, recap and references. Organizer validation notes stay in [facilitator material](../facilitator/tutorial-authoring-guide.md).

## Agreed section and unit journey

Use the status in the unit list above to see which lessons are available and what has been verified. The section map below includes planned work.

Provisioning belongs to the [facilitator reference](../facilitator/project-and-environment-provisioning.md), outside learner exercise time. The earlier setup Unit 1 is superseded by the manual-asset Unit 1 linked above.

The [curriculum](../planning/curriculum.md) contains every unit's outcome, estimated time, MS-control touchpoints, asset-growth diagram/table and the staged introduction of reusable automation and parameterization.

| Section | Planned units | Outcome |
| --- | --- | --- |
| 1. Understand the setup and build the first result | 0–2: setup inspection, lakehouse/notebook, Git baseline | Working deterministic Dev result and traceable source |
| 2. Release the small solution with Model A | 3: native promotion and verification | Minimal two-role slice works in Test and simulated Prod |
| 3. Grow the solution and introduce team development | 4–6: Variable Library, orchestration/reporting, local feature, reusable CI/PR controls | Full Dev sample and a reviewed, validated source change |
| 4. Automate the Model B release | 7–10: environment/dependency configuration, shared Dev, Test, approved Prod | One selected source released with explicit target bindings and runtime evidence |
| [Closing recap](closing-recap.md) | After Unit 10 | Choose one control to take into your own project. |
| [5. Operate, recover and reuse](section-05-operate-and-reuse/README.md) | Publish the baseline, then pick Unit 11 or Unit 12 | A retrievable source version and a verified recovery or shared-starter release |

The working time budget is nine core hours with 1.5 hours of support reserve, still to measure. The status table above records the observed native, Test and Prod checkpoints and the remaining live checks. Prepared generic components and their config examples are introduced in Units 6–10, after they have been built/tested here. Unit 0 remains parked; future units are not authored merely by appearing in this table.

Unit boundaries and timing will change with pilot feedback. No future unit should assume the old reference lab's cloud behavior applies to this sample.

## Pause and recap

Each unit ends with a short question about the result you just observed. At the turning points, take a little more time to look across the units.

- Trace the manual release and the full Dev solution before you start working from a local feature branch. [After Unit 4](section-03-team-delivery/unit-04-connect-orchestration-configuration-and-reporting/README.md#what-weve-built-so-far).
- Compare what source checks, preview and preflight can tell you before you deploy to Test. [After Unit 8](section-04-release-automation/unit-08-publish-shared-dev/README.md#what-you-can-now-explain).
- Follow a change through review, Test and approved Prod. Discuss where your own project would use different controls. [After Unit 10](section-04-release-automation/unit-10-release-to-prod/README.md#recap-and-discuss).
- Choose the first control you'd add to a real project. Do this after Unit 10 or return to it later when you have a project in mind. [Standalone closing recap](closing-recap.md) · [Production follow-up](reference/from-tiny-sales-to-production.md).

## Carry evidence from one unit to the next

Use the supplied records to link work you will reuse. A PR link can carry the diff and its review results. A manifest link can carry the deployed revisions, IDs and value set. Add your own notes when they explain an observation or connect a runtime result to the release.

| From | Carry forward | Where you use it |
| --- | --- | --- |
| Units 0–3 | Assigned workspaces and Git mappings, captured source and native release record | Units 4 and 5 build from the Dev baseline. Units 9 and 10 use the seeded target items and compare their IDs. |
| Units 4–6 | Dev definitions and runtime baseline, completed feature PR, notebook path and CI pipeline | Units 7 and 8 reuse the registered CI check, pinned revisions and observed dependencies. |
| Units 7–8 | Passing release preview and live Dev preflight, including the binding observations | Unit 9 compares the intended Test deployment with the Dev source relationships. |
| Units 9–10 | Test manifest, Test runtime results and Prod tooling PR | Unit 10 reviews the tested revisions for Prod. Section 5 uses the evidence to reconcile and validate a baseline. |
| Section 5 opener | Code tag, source pins and release note | Units 11 and 12 start from the same tagged source and check the team's Test setup against the evidence. |

## How to report a result

Use the checkpoint at the end of the unit. Report what happened, the approximate time, confusing wording and any exact error text. A failed checkpoint is useful evidence; it is not a reason to invent an undocumented workaround.

The facilitator keeps the [pilot record](../facilitator/pilot-log.md), including the document revision actually followed. Keep private setup details in local notes where needed.
