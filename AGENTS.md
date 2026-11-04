# DNA Fabric Days project guidance

## Current scope

- Develop the participant tutorial sequentially with the organizer as the first learner. Use docs/tutorial/README.md and docs/facilitator/pilot-log.md; record actual checkpoints before claiming a unit passed. Prepare the next unit from the reported results rather than assuming cloud success.
- Participants begin with Unit 0 to observe/test the setup. The facilitator pre-provisions nine workspaces (code/data/reporting × Dev/Test/Prod); provisioning instructions are in docs/facilitator/project-and-environment-provisioning.md. Unit 0 is parked. Units 1–2 and the full Unit 3 native chain are reported successful; Unit 3 is accepted as its first version on 4 November. Preserve its lesson body at 2fde5c0 (navigation links may evolve). Automated identities remain untested.
- Write new units directly for participants using docs/facilitator/tutorial-authoring-guide.md. Keep organizer validation notes in facilitator/planning files or chat. Unit 1's canonical code lives in sample/tiny-sales; do not duplicate its fixtures/implementation across lessons.
- Create a dedicated tutorial unit folder with README entry point from the first preparation/rehearsal draft, linking canonical resources. Keep it available through GitHub so the organizer can open/test on the work PC. Unit 4 is docs/tutorial/section-03-team-delivery/unit-04-connect-orchestration-configuration-and-reporting/README.md; shared parameter/DAX starters are in sample/tiny-sales. Local checks passed; cloud walkthrough is pending. Selected pilot model mode is Direct Lake on SQL via browser creation into Reporting Dev.
- Unit 2's commits and Markdown-only Git round trip completed successfully by organizer report in the existing three-repo pilot. Added commit-diff review after the web edit and saved-editor close/update/reopen guidance; exact warning cause and Unit 2 duration remain unknown. Final event/Model B repo topology remains open. Before finalizing Unit 3, prove target-aware configuration/native bindings; do not hand-edit promoted source or drop the target guard to bypass Unit 1's Dev-only settings. See docs/facilitator/unit-02-pilot-notes.md.
- Unit 3 native chain worked by organizer report, first version accepted 4 November. Select the target stage first and verify Deploy from. Rules are in the Deployment pipeline target-stage view. Explain IDs, binding, auto-binding limits and source versus environment state. Retain facilitator evidence/history; no automation-identity success follows from native human delivery.
- Required later coverage: create at least one fresh target asset through managed-identity-only Test/Prod deployment and inspect ownership/runtime implications. Plan: Unit 4 human baseline, Unit 9 new validation notebook first-created in Test, Unit 10 same selected source first-created in Prod; compare existing-item updates and repeat deployment. See docs/planning/identity-and-ownership-experiment.md (V20). Do not assume creator, owner, associated/default identity, deployer, runtime and connection identities coincide or generalize behavior across item types. Do not pre-create/take over target assets as a workaround.

- Read README.md and docs/planning/decisions.md before substantive work.
- Hands-on workshop scope is Model A and Model B. Model C is explainer material only.
- Prefer local feature branches with shared Dev within each team. Feature workspaces are explainer material, not required infrastructure.
- This repository prepares the workshop. Participants start with separate unpopulated Azure DevOps projects/repos, manually create initial Fabric assets, and add starter files gradually.
- Recommend one participant solution repo with separate code/data/reports folders. Separate repos are a tradeoff explainer, not a required exercise.
- Design mandatory exercises for one developer sequentially; pairs may follow together. Concurrent feature development is optional.
- Choose and validate one Model B Dev update mechanism; explain Git-connected versus pipeline-published Dev without implementing both required paths.
- Code, data, and reporting workspace roles are confirmed in principle; detailed permissions, identities, runner/network design, and deployment mechanisms need validation.
- Participants are workspace admins in their training environments. Document the difference between demonstrated workflow and enforced productive controls.
- The event is less than a month after 28 October 2026; the exact date is not recorded. Test setups can be provisioned now.

## Sources and evidence

- docs/source-guidelines contains the organizer-supplied Working Version 1 baseline. Do not silently rewrite its obligations while implementing tutorial guidance.
- Use MS-01 through MS-14 to trace tutorial coverage.
- Distinguish proposals, accepted user decisions, documentation evidence, and observed tenant behavior.
- The current repository contains planning and historical reference source. Do not describe imported reference code as a validated workshop implementation or unrun cloud checks as working.
- Read docs/planning/initial-codebase-review.md before extracting reusable code. Keep reference/initial-lab separate from the active toolkit. Its networking helpers, deployment commands and private probes are not offline tests.
- Record durable choices and experiment results in repository files so separate chats can resume reliably.
- For prior learning context, read docs/planning/handoff-review.md and its dated snapshot links. Earlier Section 3 success is historical reported evidence; it does not validate this workshop. Distinguish DataOps Models A/B/C from g-IT service Targets A/B.

## Implementation direction

- Markdown is the documentation source. Each tutorial unit has a folder with README.md and any unit-specific resources; shared code/assets stay in canonical toolkit/sample/pipeline/example locations. Confluence is a publishing target. Unit 0 is parked after organizer review; retain its content unless new feedback requires changes.
- Azure DevOps/Azure Pipelines is the delivery target regardless of where Git is hosted.
- Prefer a thin reusable layer around supported tooling. Prove cross-workspace bindings before expanding custom abstractions.
- Separate sample business logic from reusable components and environment configuration.
- Validate selected source revisions consistently across release stages; source rollback does not imply data recovery.
