# DNA Fabric Days project guidance

## Current scope

- Develop the participant tutorial sequentially with the organizer as the first learner. Use docs/tutorial/README.md and docs/facilitator/pilot-log.md; record actual checkpoints before claiming a unit passed. Prepare the next unit from the reported results rather than assuming cloud success.
- Participants begin with Unit 0 to observe/test the setup. The facilitator pre-provisions nine workspaces (code/data/reporting × Dev/Test/Prod); provisioning instructions are in docs/facilitator/project-and-environment-provisioning.md. Access checks are reported passed, while the new Unit 0 narrative/learner timing and actual Git sync/runtime remain untested. Next participant Unit 1 will create assets.

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
