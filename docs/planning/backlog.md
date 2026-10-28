# Validation and delivery backlog

Technical experiments and implementation work are unstarted. Scoping is in progress: the organizer supplied the guidelines and narrowed hands-on scope to A/B, with Model C and feature workspaces as explainers. Priorities describe proposed sequencing. No cloud tests have been run.

The [learning-project handover review](handoff-review.md) records earlier reported lab success and reusable lessons. These inform V01/V08/V10/V11 but do not pass them. Review candidate/content correlation, runtime evidence, release-window locking/queue behavior, and forward recovery against the actual old implementation. Preserve the simpler proposed workshop branch model unless evidence justifies a change.

## Technical experiments before detailed tutorial authoring

Record the tenant, date, tooling versions, runner, authentication method, source revision, steps, observed result, and evidence link for each experiment. Use synthetic data. A documentation citation informs an experiment; it does not pass it.

| ID | Priority | Experiment | Required evidence / pass condition |
| --- | --- | --- | --- |
| V01 | P0 | Guideline mapping and existing-code review | A/B controls mapped to exercises; Model C explainer boundary; older Section 3 checked for relevant implementation choices; retain/replace list |
| V02 | P0 | Identity and runner feasibility | Chosen noninteractive identity can perform each required operation from the intended agent; runtime access also demonstrated |
| V03 | P0 | Native stage asset compatibility | Selected report/model format and minimal project deploy through the intended stages and produce the expected target result |
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

Relationship support matrix to fill from V04–V06:

| Relationship | Source definition representation | Deployment/binding mechanism | Deploy identity | Runtime identity | Inspection method | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Notebook -> lakehouse | To inspect | To prove | To prove | To prove | To prove | Unvalidated |
| Pipeline -> notebook | To inspect | To prove | To prove | To prove | To prove | Unvalidated |
| Pipeline -> connection | To inspect | To prove | To prove | To prove | To prove | Unvalidated |
| Semantic model -> data source | Depends on chosen mode | To prove | To prove | To prove | To prove | Unvalidated |
| Report -> semantic model | Depends on chosen format | To prove | To prove | To prove | To prove | Unvalidated |

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
