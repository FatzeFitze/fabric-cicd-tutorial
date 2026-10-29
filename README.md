# DNA Fabric Days: workshop planning

Initial scoping baseline, 28 October 2026. Agreed direction: Models A and B are hands-on; Model C and feature workspaces are explainer topics. Use local feature branches and shared Dev workspaces where supported. Other recommendations remain proposals. This repository contains planning documents and historical reference source; it contains no validated workshop deployment implementation or exercises.

## Start here

- [Participant tutorial](docs/tutorial/README.md): begin with Unit 0 to observe and understand the pre-provisioned setup.
- [Pilot record](docs/facilitator/pilot-log.md): access/feature checks reported passed; setup took about one minute, while Unit 0 is parked after organizer review and learner inspection timing remains unmeasured.
- [Provisioning feedback review](docs/facilitator/provisioning-review-2026-10-29.md): factory code, supplied run records, Git credentials and pilot-layout differences.

- [Scope and learning journey](docs/planning/scope.md): outcomes, sample project, timetable, reusable components, and repository design.
- [Decision register](docs/planning/decisions.md): proposed decisions, assumptions, and missing inputs.
- [Validation and delivery backlog](docs/planning/backlog.md): technical experiments, evidence requirements, delivery sequence, and readiness gates.
- [Control coverage and development workflow](docs/planning/control-coverage.md): A/B exercises, Model C explainers, and shared-Dev constraints.
- [Repository and bootstrap design](docs/planning/repositories-and-bootstrap.md): empty participant projects, manual Fabric creation, folder mappings, Dev sync choices, and a one-person core path.
- [GitHub setup](docs/planning/github-setup.md): publish this existing local preparation repository.
- [Project files and collaboration context](docs/planning/project-layout.md): what to version, local checkout placement, and portable versus personal settings.
- [Sources](docs/planning/sources.md): official documentation consulted and the limits of that evidence.
- [Supplied guidelines](docs/source-guidelines/README.md): the organizer's three Working Version 1 documents.
- [Learning-project handover review](docs/planning/handoff-review.md): imported historical findings, confidence limits, and how they inform the workshop; links to the preserved dated snapshot.
- [Initial codebase assessment](docs/planning/initial-codebase-review.md): retained source, reuse decisions, bootstrap/topology gaps and local verification results.

## Working agreement proposed for this project

Markdown in Git is the editable source for documentation. Confluence pages are published copies with a recorded source revision. Company-specific configuration and credentials stay outside the community starter. Azure Pipelines is the target automation platform even while development uses a GitHub remote.

Keep decisions and validation results in files so future chats can resume from the repository. Separate proven behavior from proposed design, documentation claims, and unresolved questions. The supplied guidelines define Models A/B/C; the older target-picture Section 3 and current implementation remain inputs for technical review.

The preparation baseline is published on `main` in [fabric-cicd-tutorial](https://github.com/FatzeFitze/fabric-cicd-tutorial). Local Git author details are configured as supplied by the organizer. The active checkout has been relocated outside OneDrive to the local development folder recorded in the project-layout guide. No license or public release policy has been selected.

This is the organizer's preparation repository. Each participant or pair starts with its own unpopulated Azure DevOps project/repository and builds the solution through the units. The recommended participant layout is one solution repository with separate Fabric role folders. Core exercises follow one developer sequentially; pairs can follow together, and simultaneous feature work is optional.
