# DNA Fabric Days: workshop planning

Workshop preparation started 28 October 2026. Agreed direction: Models A and B are hands-on; Model C and feature workspaces are explainer topics. Use local feature branches and shared Dev workspaces where supported. The repository contains planning documents, historical reference source, Units 0–3 and Tiny Sales starters. The organizer reports successful Units 1–2 and native Test promotion; Unit 3's Prod extension and workshop deployment automation remain untested.

## Start here

- [Participant tutorial](docs/tutorial/README.md): begin with Unit 0 to observe and understand the pre-provisioned setup.
- [Unit 1: create a tiny sales solution](docs/tutorial/section-01-foundation/unit-01-create-a-tiny-sales-solution/README.md): successful organizer walkthrough reported; deterministic sample and corrected OneLake catalog attachment steps.
- [Unit 2: capture the solution in Git](docs/tutorial/section-01-foundation/unit-02-capture-the-solution-in-git/README.md): successful organizer walkthrough reported; commit-diff review and open-editor update guidance refined.
- [Unit 3: native promotion](docs/tutorial/section-02-model-a/unit-03-native-promotion/README.md): full participant lesson with resource/binding explanations, target-stage rules and Dev → Test → simulated Prod; Test reported successful, Prod walkthrough pending.
- [Tutorial authoring convention](docs/facilitator/tutorial-authoring-guide.md): clean participant lessons with organizer validation notes kept separately.
- [Pilot record](docs/facilitator/pilot-log.md): access/feature checks reported passed; setup took about one minute, while Unit 0 is parked after organizer review and learner inspection timing remains unmeasured.
- [Provisioning feedback review](docs/facilitator/provisioning-review-2026-10-29.md): factory code, supplied run records, Git credentials and pilot-layout differences.

- [Scope and learning journey](docs/planning/scope.md): outcomes, sample project, timetable, reusable components, and repository design.
- [Sections, units and sample growth](docs/planning/curriculum.md): agreed broad journey and minimal sample including a Variable Library; staged introduction of reusable automation/configuration. Timings and technical mechanisms await pilot validation.
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
