# Decision register

Date: 28 October 2026. Explicit user decisions are recorded below. Other recommendations remain proposals.

## Confirmed from the organizer's brief

- 15–20 people, individually or in teams of two.
- Two days with 10–12 working hours available.
- Mixed prior ALM experience.
- Azure DevOps required for the event and subsequent company work.
- Desired progression from native Fabric Deployment pipelines to managed team delivery; subsequent discussion limits Model C to explainers.
- Workspaces, capacity, Azure DevOps resources, managed identities, and Confluence can be provisioned.
- Workshop workspaces will not have private links.
- Documentation and code should be versioned together; section/unit Markdown is acceptable.
- Reusable components should eventually support community reuse.

## Confirmed in the scoping discussion

- Hands-on scope is Models A and B. Cover Model C only in explainers.
- Prefer shared Dev plus local feature-branch development where possible. Cover feature workspaces in explainers; do not require them for the mock project.
- Interpret shared Dev as shared within each team; this is a planning assumption pending any contrary instruction.
- The organizer supplied DataOps Principles & Scope, Solution Classification Framework, and Fabric Minimum Standard, all Working Version 1. Preserve that status; steering approval is not established by this discussion.
- The event is less than a month away. Exact date remains to be recorded.
- Validation setups can be provisioned immediately by the organizer. Actual test access/configuration still needs arranging.
- g-IT workspace-role separation and permissions are confirmed in principle. Detailed permissions have not been supplied; identity/network design is still open.
- Participants will have admin access to their workshop workspaces.
- This preparation repository contains tutorial/support assets. Each participant or pair starts with an unpopulated Azure DevOps project/repository; manual UI creation of Fabric assets and initial Git synchronization are intended learning activities.
- The organizer is considering a full DevOps project per participant/pair, separate repositories versus role folders, and a sequential one-developer tutorial rather than required concurrent feature development. The recommendations below address these open choices.
- The organizer supplied the GitHub destination `FatzeFitze/fabric-cicd-tutorial` and the desired commit author details. Remote and repository-local author settings are configured. Initial publication to `main` succeeded on 28 October 2026. The organizer accepted an active checkout outside OneDrive and versioned project guidance alongside the code. The repository was relocated to `C:\Users\matth\sw_dev\git_repos\fabric-cicd-tutorial` on 28 October 2026; files, commit history, and clean Git status were verified. App project/folder attachment requires the user-facing folder selection step.

## Proposals to review

| ID | Recommendation | Reason | Review trigger |
| --- | --- | --- | --- |
| D01 | One local repository, then a private GitHub remote | Start immediately and keep docs/code aligned | Confirm generic content and remote ownership |
| D02 | Azure Pipelines files from the start | Target the eventual delivery platform | First real Azure DevOps run |
| D03 | One repository with an independently structured toolkit | Fast workshop iteration and later extraction | Second small sample uses the toolkit |
| D04 | One evolving synthetic sales project | Visible outcomes and meaningful dependencies | Confirm relevance to migration asset mix |
| D05 | Nine core hours, 1.5 hours reserve, optional extensions | Protect the complete learning path | Timed pilot |
| D06 | Prepared Model B starter with participant modifications | Managed team delivery is achievable within the event | Pilot across experience levels |
| D07 | Thin reusable layer over supported tooling | Avoid rebuilding deployment and parameterization support | Compare current code with fabric-cicd and native features |
| D08 | Small typed dependency contract only for demonstrated gaps | Express target state without hardcoding project names | Cross-workspace experiment |
| D09 | Markdown is authoritative; Confluence is a published copy | Avoid manual divergence | Confirm publishing workflow |
| D10 | Deployment identities, workspace identities, and runtime identities are specified separately | Identity availability is operation- and runner-specific | Identity and permissions experiment |
| D11 | Native pipeline suitability is assessed by requirements | Simplicity and network visibility do not alone establish suitability | Apply supplied classification and minimum standard |
| D12 | One Azure DevOps project per participant/pair, with one solution repo and code/data/reports folders | Clear team boundary and one versioned source state for connected assets | Validate workspace-to-folder mappings and ownership needs |
| D13 | Manual Fabric/bootstrap steps, then add selected starter files gradually | Match day-to-day adoption without handing out a completed solution | Rehearse from an empty participant repo |
| D14 | Core tutorial follows one developer sequentially; pair concurrency is optional | Reduce branches and runtime states needed for teaching and rehearsal | Timed solo and pair pilot |
| D15 | Prefer pipeline-published integration Dev for the Model B local feature, subject to feasibility | Use one controlled publisher and one selected source revision | Compare with current code; controlled Git-update Dev remains an alternative |

## Missing inputs, in priority order

A [dated learning-project handover](handoff-review.md) supplies historical architecture and g-IT context. The subsequently supplied test-project source ZIP is now retained and assessed in the [initial codebase review](initial-codebase-review.md). Original raw cloud evidence and complete original authoring/source documents remain unavailable. These imports introduce no new accepted workshop architecture decisions.

1. Retained cloud release evidence and original tutorial state/curriculum/authoring sources where relevant. Current test-project source is supplied and initially reviewed; do not request it again as missing.
2. Exact workshop date and the first arranged Azure DevOps/Fabric validation setup. Provisioning is available now.
3. Any omitted infrastructure/permission setup or prior run results needed to reproduce the supplied source's historical behavior; code entry points, reuse choices and observed local gaps are documented in the codebase assessment.
4. Detailed g-IT role/permission mapping: placement of each item type, ownership, shared versus environment-specific resources, connections, networking, agent location, and identity approach. Workspace-role separation and permissions are already confirmed in principle.
5. Participant profile: Git/Python/Power BI/Fabric experience, expected asset types, laptop software, installation restrictions, and access/licensing constraints.
6. Delivery operations: final pairing mix, facilitator capacity, budget/capacity SKU, provisioning owner, and who can change tenant settings and DevOps policies.
7. Source-sharing rules and eventual community license/ownership. Do not assume current company implementation can be published privately or publicly.

## Assumptions to test

| ID | Assumption | Consequence if false |
| --- | --- | --- |
| A01 | The final layout means three environments times three roles per team | Recalculate workspace inventory and transition exercises |
| A02 | A supported report/model combination works in both the introductory and advanced paths | Adapt format, storage mode, or intro sample before authoring |
| A03 | The chosen runner can authenticate with an approved noninteractive identity | Change runner or identity design and rerun end-to-end tests |
| A04 | The capacity can support realistic team concurrency | Reduce runtime work, stagger starts, or adjust capacity |
| A05 | A small set of required dependency types can be inspected after deployment | Narrow validation promises or change the asset path |
| A06 | Company Azure DevOps validation is completed before curriculum freeze | Keep Model B stage readiness explicitly unresolved until tested |
| A07 | Mandatory features can be edited locally without feature workspaces | Change the feature or explicitly review the development-workspace boundary |
| A08 | A team can coordinate the few unavoidable shared-Dev UI operations | Simplify the required feature and retain isolated UI authoring as explanation |

## Decision procedure

For each decision, record the selected option, rationale, evidence, date, and implications for existing units or templates. Do not change a proposal to accepted simply because code was written against it. Update this register when the organizer resolves a choice.
