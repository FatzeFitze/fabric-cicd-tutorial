# DNA Fabric Days: workshop planning

Workshop preparation started 28 October 2026. Agreed direction: Models A and B are hands-on; Model C and feature workspaces are explainer topics. Use local feature branches and shared Dev workspaces where supported. Units 0–5 and Tiny Sales starters are available. Units 3–4 are accepted as their first working versions by the organizer. Unit 5's local feature/draft PR path and later managed deployment/ownership experiments await pilot validation.

## Start here

- [Participant tutorial](docs/tutorial/README.md): begin with Unit 0 to observe and understand the pre-provisioned setup.
- [Unit 1: create a tiny sales solution](docs/tutorial/section-01-foundation/unit-01-create-a-tiny-sales-solution/README.md): successful organizer walkthrough reported; deterministic sample and corrected OneLake catalog attachment steps.
- [Unit 2: capture the solution in Git](docs/tutorial/section-01-foundation/unit-02-capture-the-solution-in-git/README.md): successful organizer walkthrough reported; commit-diff review and open-editor update guidance refined.
- [Unit 3: native promotion](docs/tutorial/section-02-model-a/unit-03-native-promotion/README.md): full native chain accepted as first working version on 4 November.
- [Unit 4: connect configuration, orchestration and reporting](docs/tutorial/section-03-team-delivery/unit-04-connect-orchestration-configuration-and-reporting/README.md): first version accepted; source/deployed-ID wording clarified.
- [Unit 5: make a local feature change](docs/tutorial/section-03-team-delivery/unit-05-make-a-local-feature-change/README.md): clone Code source, edit in an IDE, preserve metadata/IDs and open a draft PR; walkthrough pending.
- [Logical and physical Fabric IDs](docs/tutorial/reference/fabric-item-identities.md): source identity versus deployed instance, lookup locations and later release evidence.
- [Optional conflict recovery](docs/tutorial/auxiliary/aux-01-recover-from-source-conflicts/README.md): concepts and entry point; intentional-conflict lab awaits rehearsal after Unit 5's local Git workflow.
- [Later identity/ownership experiment](docs/planning/identity-and-ownership-experiment.md): create a new Test/Prod asset through managed identities, compare creation with updates and verify runtime/access implications.
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
