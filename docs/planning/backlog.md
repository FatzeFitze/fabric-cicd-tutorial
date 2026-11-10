# Validation and delivery backlog

V01 has an initial source inventory, targeted review and passing local checks; see the [codebase assessment](initial-codebase-review.md). Units 1–5 have organizer-reported success. Units 3–5 are accepted first versions. The Unit 6 Azure DevOps exercise and managed deployment experiments await pilot evidence. Hands-on scope is A/B; C is explainer material.

W06 authoring/W08 piloting proceed incrementally. Provisioning/access and Units 1–4 are reported successful; Unit 0 remains parked. Units 3–4 remain first versions, with Unit 4's narrow ID clarification/navigation added. See the [pilot record](../facilitator/pilot-log.md). Detailed exports/target evidence, clean automated targets and workload identities require further validation.

[Unit 1](../tutorial/section-01-foundation/unit-01-create-a-tiny-sales-solution/README.md) and its four-cell starter have local checks plus organizer-reported successful Dev completion in 20–30 minutes including reading. Corrected the attachment wording to Add data items → From OneLake catalog; no runtime code changed. [Unit 1 facilitator notes](../facilitator/unit-01-pilot-notes.md) distinguish this initial Dev success from V04/V07's still-pending clean-target deployment requirements, and identify the Dev-only guard configuration to evolve before native promotion. Raw run outputs and a separately replayed corrected lesson were not supplied.

[Unit 2](../tutorial/section-01-foundation/unit-02-capture-the-solution-in-git/README.md) is authored for the existing Dev bindings: first full-item commits, real source/identity inspection, a Markdown-only Git-to-Fabric round trip and per-repo revision worksheet. [Pilot notes](../facilitator/unit-02-pilot-notes.md) cover source/credential observations needed for V17. Organizer reports successful commits/update/runtime validation after adding the introductory cell. Updated web-commit diff review and editor coordination guidance; no actual export/commit IDs or Unit 2 duration supplied. Final event repo topology and V03/V04 promotion/configuration gates remain open.

Unit 3: the full native lesson is accepted as its first working version on 4 November. Human/native source, target rules and runtime path are reported successful; exact raw outputs/revisions/duration were not supplied. [Pilot notes](../facilitator/unit-03-pilot-notes.md) preserve the evidence boundary. This is not proof of the Model B API/managed identity path.

The [learning-project handover review](handoff-review.md) records earlier reported lab success and reusable lessons. These inform V01/V08/V10/V11 but do not pass them. Review candidate/content correlation, runtime evidence, release-window locking/queue behavior, and forward recovery against the actual old implementation. Preserve the simpler proposed workshop branch model unless evidence justifies a change.

Unit 4: revised [participant lesson](../tutorial/section-03-team-delivery/unit-04-connect-orchestration-configuration-and-reporting/README.md) accepted as its first version; screenshot confirms pipeline success and injected library label, and the organizer confirmed Connection unselected. Clarified source logical IDs versus physical IDs in deployed item links/APIs and added a shared reference. Actual exports/source revisions and separate run records for every revised step are not retained here. See [pilot notes](../facilitator/unit-04-pilot-notes.md) for partial V05/V06/V19 evidence and target/identity gates. V20 reserves new-item ownership in Units 9–10. Optional conflict recovery has an [entry point](../tutorial/auxiliary/aux-01-recover-from-source-conflicts/README.md) and [rehearsal plan](../facilitator/source-conflict-exercise-plan.md), with no deliberate conflict run yet.

Unit 5: [local feature lesson](../tutorial/section-03-team-delivery/unit-05-make-a-local-feature-change/README.md), feature record and [pilot checks](../facilitator/unit-05-pilot-notes.md) authored. The source edit expects 204.70 revenue and 357.20 gross. Unit 5 now completes the first PR into dev and records the resulting revision. The organizer completed the first merge and confirmed the Python export path. V16 also needs deployment and runtime evidence.

Unit 6 now supplies a reusable notebook validator, the Tiny Sales source check and CI YAML. The local checker passes the reviewed source and rejects the deliberate defect. Verify the automatic required policy and its failing and passing runs in the participant project. [Unit 6 pilot notes](../facilitator/unit-06-pilot-notes.md).

## Technical experiments before detailed tutorial authoring

Record the tenant, date, tooling versions, runner, authentication method, source revision, steps, observed result, and evidence link for each experiment. Use synthetic data. A documentation citation informs an experiment; it does not pass it.

| ID | Priority | Experiment | Required evidence / pass condition |
| --- | --- | --- | --- |
| V01 | P0 | Guideline mapping and existing-code review | A/B controls mapped to exercises; Model C explainer boundary; older Section 3 checked for relevant implementation choices; retain/replace list |
| V02 | P0 | Identity and runner feasibility | Chosen noninteractive identity can perform each required operation from the intended agent; runtime access also demonstrated |
| V03 | P0 | Native stage asset compatibility | Minimal Data/Code lakehouse/notebook slice deploys through the intended stages with correct target binding and expected runtime result; reporting is introduced later and validated in V06 |
| V04 | P0 | Notebook to separate-workspace lakehouse | Clean target deployment uses the target-environment lakehouse and successfully writes a known result |
| V05 | P0 | Pipeline to notebook and connection dependencies | Activity targets and connections resolve to intended items; execution succeeds under runtime identity |
| V06 | P0 | Semantic model and report dependencies | Chosen model mode reaches target data; report uses target model; any refresh/readiness steps are explicit |
| V07 | P0 | Definition versus data lifecycle | Fresh deployment starts without assumed data; deterministic seeding/schema setup gives the expected outcome |
| V08 | P0 | Full Azure DevOps release | PR policy/check, pinned source revision, Test verification, configured approval, simulated Prod deployment and release evidence all work |
| V09 | P0 | Bad config and dependency isolation | Missing mapping, missing target, and Dev reference in a Test/Prod release are rejected or detected before exposure; expected exceptions are explicit |
| V10 | P0 | Partial failure and recovery | Deliberate failure after one workspace deployment produces useful evidence; correction and rerun converge without unintended data loss |
| V11 | P0 | Repeat deployment and source drift | Same source can be redeployed; concurrent releases to the same target are controlled; stale target references are detected within declared scope |
| V12 | P1 | Azure Repos transfer | Branches/tags/history available as intended; destination pipeline registered; policies, permissions, checks, and connections configured and tested |
| V13 | P0 | Capacity and concurrency | Representative team count and operations measured on intended capacity, including start-up latency and throttling |
| V14 | P1 | Starter reuse | A second small example changes documented configuration and project checks without editing toolkit internals |
| V15 | P1 | Optional asset extension | Added only after core path is reliable; actual support and connectivity demonstrated; private networking remains explainer-only |
| V16 | P0 | Local feature branches with shared Dev | Required feature edits locally, PR checks run without a feature workspace, merge updates shared Dev through one chosen mechanism, and integration tests record the selected revision |
| V17 | P0 | Empty-repository bootstrap and Model B transition | One learner creates introductory Fabric assets manually, captures them in Git, transitions to role folders without losing identities, and uses one chosen Dev update mechanism; pair concurrency is not a core pass condition |
| V18 | P1 | Optional pair concurrency | If offered, two local feature branches integrate in sequence with meaningful checks; deliberate conflicts and feature workspaces stay outside required completion |
| V19 | P0 | Variable Library lifecycle and consumption | Code-role library captured in Git; same-workspace consumer passes a value to notebook under the chosen runtime identity; target active set explicitly configured/verified after fresh deployment and preserved/checked on rerun; wrong/missing setting detected; no assumption that deployment identity establishes runtime support |
| V20 | P0 | Fresh target creation and ownership under managed delivery | New asset absent before first managed-identity Test/Prod release; actual caller/physical IDs and exposed owner/associated/runtime/connection identities recorded; compare update of existing human-created item and rerun behavior; runtime/access validated. See [experiment plan](identity-and-ownership-experiment.md); no assumed universal ownership rule or beta API prerequisite. |

Relationship support matrix to fill from V04–V06:

| Relationship | Source definition representation | Deployment/binding mechanism | Deploy identity | Runtime identity | Inspection method | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Notebook -> lakehouse | Actual exported representation not supplied | Native target-stage rule, full Unit 3 reported working | Human/native path; automation pending | Interactive path; independent identity test pending | Target context and persisted table | Unit 3 accepted; API/workload path pending |
| Pipeline -> notebook | Actual export to retain | Dev authored; target automation to prove | Automation pending | Human Submitter shown; full context to retain | Successful activity/notebook run | Dev reported working; targets pending |
| Pipeline -> Variable Library -> notebook parameter | Actual export to retain | Dev consumption reported; target active set to prove | Automation pending | Human baseline; workload variant pending | Injected tiny_sales_dev value shown | Dev progress; fresh target/rerun pending |
| Pipeline -> connection | Connection unselected by organizer confirmation; export to retain | Default human-context Dev run successful by report; target route pending | Automation pending | Last editor/default versus explicit connection to record | UI selection, last editor and run Submitter | Unselected-Connection Dev path confirmed; workload variant pending |
| Semantic model -> data source | Direct Lake on SQL selected; expression/export to retain | Dev authored; target binding to prove | Automation pending | Actual connection/SSO to retain | New endpoint/connection/TMDL inspection steps | Dev reported working; expanded checks pending |
| Report -> semantic model | Actual format/reference to retain | Dev authored; target binding to prove | Automation pending | Workload variant pending | Report reconciliation; new price-change exercise pending | Dev reported working; targets pending |

## Delivery workstreams

| ID | Deliverable | Depends on | Done when |
| --- | --- | --- | --- |
| W01 | Agreed scope and architectural decisions | Supplied guidelines, existing technical reference, and organizer decisions | A/B scope, Model C explainers, shared-Dev/local-branch workflow, and remaining architecture choices are recorded |
| W02 | Tested minimal vertical slice | V02–V07 and V16–V17 | One representative local feature change reaches shared Dev and a clean target, executes, and shows the correct report result |
| W03 | Reusable deployment starter | W02 and current-code review | Required bindings/configuration supported, validation meaningful, versions pinned, second example viable |
| W04 | Azure Pipelines templates | W03 and Azure DevOps access | V08–V11 pass and release metadata is useful |
| W05 | Reproducible sample and checkpoints | W02 | The manual learner-built path works from an empty repo, selected starter files enter gradually, and each stage has a recovery checkpoint |
| W06 | Tutorial units and pre-reads | W01, W04, W05 | Instructions use verified commands and observable expected results; links and times reviewed |
| W07 | Participant provisioning and facilitator guide | W01 and V13 | Fresh team access verified; inventory, reset procedure, troubleshooting and solutions ready |
| W08 | Timed pilot and revisions | W04–W07 | Representative novice solo learner completes the core from an empty repo within budget; a pair can follow together without required parallel feature work |
| W09 | Workshop release | W08 and required validation | Named release/tag, frozen dependencies, recovery checkpoints, recorded known limitations |
| W10 | Community extraction and publication preparation | W09, V14, ownership/license decision | Toolkit usable without workshop or private company configuration; publication terms selected |

### Prepare before learner introduction

The organizer accepted gradual adoption of generic components/configuration on 29 October. Follow the [curriculum phasing contract](curriculum.md#how-reusable-automation-enters-the-tutorial): prove Variable Library consumption before Unit 4 (V19); build/test reusable checks before Unit 6; document/validate environment and dependency inputs before Unit 7; prove one deployment entry point and parameterized Azure Pipelines template before Unit 8; prove pinned Test/Prod release and active-value-set checks before Units 9–10; rehearse recovery/reuse before Units 11–12. W02 must include V19 in its full-solution feasibility evidence. These are preparation gates, not participant tasks to write framework internals. The revised 9 h 10 min core is an estimate to verify during piloting.

## Configurable validation candidates

Before expanding the toolkit, choose checks that developers can configure through the project mask. Start with checks whose inputs and failure messages can be demonstrated on Tiny Sales and a second project.

| Stage | Candidate reusable helper | Project-supplied inputs |
| --- | --- | --- |
| CI | Check item inventory, required definition files, parseable metadata and logical ID uniqueness within a workspace's item set. | Role folders, expected items and supported item types. |
| CI | Check the mask and dependency declarations for missing roles, unknown item references and disallowed mappings. | Required roles, permitted dependencies and environment constraints. |
| Planning or post-deploy | Check that resolved dependency IDs point to the intended target workspaces and items. | Binding declarations and resolved or observed IDs from the supported deployment tooling. |
| Project tests | Provide a standard way to invoke a project's tests and report their results. | Representative data, expected business outcomes and runtime requirements. |

The Unit 6 AST comparison remains a teaching check for Tiny Sales. Use the second-example exercise to prove which helpers can be reused by changing configuration and which assertions belong with the project's code or runtime tests.

## Readiness gates

1. **Architecture gate:** apply the supplied model/control definitions and agree sample, workspace roles, local development workflow, supported dependencies, identities, runner, and required A/B controls. Keep Model C and feature workspaces as explainers.
2. **Feasibility gate:** pass the clean end-to-end slice in the intended tenant and delivery environment. Choose deployment tooling from evidence before committing to a manifest or rewriting the current codebase.
3. **Reuse gate:** pass the second-example test and settle the configuration boundary. Avoid embedding sample item names in toolkit code.
4. **Teaching gate:** run from participant instructions and checkpoints, then time the pilot with a less experienced participant or pair.
5. **Event gate:** validate team access and concurrency, freeze the release, retain repair and known-good redeployment paths, and publish the matching documentation revision.

Each gate should end with an explicit decision and evidence. If g-IT details are late, parameterize the agreed role mapping and document the workshop's demonstrated limits. Do not claim the workshop reproduces an untested enterprise network or permission model.

## Planning effort

Do not commit to a total preparation estimate before reviewing Section 3 and the existing code. Treat the feasibility slice as the first bounded piece of engineering work, then estimate remaining toolkit changes and tutorial authoring from measured results. Schedule external access, policy changes, identity provisioning, and the pilot as explicit dependencies; these can dominate elapsed time.

## Preparation sequence for the remaining month

The event is less than a month away and test setups can be provisioned now. Use the following proposed sequence, then attach calendar dates once the exact event date is known:

1. **Next few working sessions:** review the current code and detailed role/permission mapping; select one sample feature; validate local editing, native promotion, identity access, and the cross-workspace end-to-end path. Make the major tooling and model-mode choices here.
2. **Following preparation block:** implement the smallest A/B starter, environment configuration and checks; provide clean sample checkpoints; prove the second-example configuration boundary. Develop foundations/pre-reads alongside this work.
3. **Next block:** write the tested step-by-step units, facilitator provisioning/recovery material, and short Model C/feature-workspace explainers. Run a realistic concurrency/access rehearsal.
4. **Reserve the final week before the event:** run a timed participant pilot, fix problems, freeze versions and documentation, and verify provisioned team access. Do not reserve the final week for discovering the first cross-workspace binding behavior.

If the critical feasibility path takes longer, reduce optional item coverage and presentation polish first. Retain source traceability, actual Model B validation/approval, recovery, and a timed pilot. Any remaining hands-on scope reduction should be explicit.
