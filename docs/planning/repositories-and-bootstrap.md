# Repositories, participant bootstrap, and Dev synchronization

Updated 28 October 2026. The organizer confirmed the separation between workshop preparation and participant work. Repository layout and the precise Model B synchronization mechanism remain recommendations to validate.

## Two different purposes

| Context | Owner | Starting point | Contents |
| --- | --- | --- | --- |
| Workshop preparation repository | Organizer/maintainers | This local repository, then private GitHub | Tutorial Markdown, facilitator material, reusable code, Azure Pipelines templates, sample definitions, example configs, checks and recovery checkpoints |
| Participant Azure DevOps project | One participant or pair | A provisioned project with an empty/default unpopulated repository and working resource permissions | The solution they build during the tutorial and the automation/configuration they add along the way |

Participants do not start by cloning this preparation repository as their finished solution. They first create a small working solution in Fabric, establish source control, and then add selected starter components at the relevant unit. Copying a documented file or snippet manually is acceptable. Identify the preparation release/tag that supplied it. A facilitator recovery checkpoint can restore progress when needed without becoming the normal starting point.

The organizer provisions prerequisites such as capacity-backed workspaces, participant access and the permissions needed to register/use pipeline resources. The learner creates the solution's initial source content. An empty project should not mean that the first hour is spent resolving avoidable access problems.

## Recommended participant layout

Give each participant or pair a separate Azure DevOps project, and use one solution repository inside it. The project can hold more repositories later, but workspace roles do not require separate repositories.

Example Model B layout:

```text
solution/
  README.md
  fabric/
    code/                 # notebook and orchestration definitions
    data/                 # persistent-data item definitions
    reports/              # semantic model and report definitions
  src/                    # locally testable business code, if needed
  config/                 # sanitized environment maps and dependencies
  tests/                  # meaningful source/configuration checks
  deployment/             # selected reusable starter components
  pipelines/              # Azure Pipelines YAML
```

`data/` here stores Fabric item definitions; runtime tables and lakehouse data are not automatically stored in Git. Model A can start with a single `/fabric/initial` folder before an explicit, rehearsed transition to role folders. The exact introductory asset subset and transition remain to be proven.

For connected Dev workspaces, use the same solution repository and integration branch with a different Git folder for each role:

| Workspace role | Example Git folder |
| --- | --- |
| Dev code | `/fabric/code` |
| Dev data | `/fabric/data` |
| Dev reporting | `/fabric/reports` |

Microsoft recommends a common repository/branch with distinct Git folders for workspaces within one solution [S14]. Store deployment scripts and workflow YAML outside those Fabric-sync folders. Treat each workspace-to-folder mapping as a recorded configuration choice; validate it during setup and before synchronization. Do not connect every workspace to the repository root or to overlapping role folders.

A common repository gives one PR and one selected source revision for coordinated code/data/reporting changes. It does not make deployments across workspaces atomic.

### When separate repositories may be appropriate

Consider separate repositories when components are independently owned products with different access boundaries, release cadences, or lifecycles. Folder separation is not a substitute for repository access isolation. In that case, define compatibility contracts and a release manifest that pins each repository revision; do not build a release from whichever branch heads happen to be current.

For this small, tightly connected sample, the additional PRs, version coordination and pipeline checkouts would increase teaching and rehearsal work. Separate repositories are reference material rather than a second required implementation.

## Manual bootstrap as a learning activity

Proposed learner sequence:

1. Open the provisioned Azure DevOps project and create or initialize the solution repository. A short README can establish the initial branch.
2. Create the introductory Fabric assets through the UI and run the smallest useful result. Provide deterministic input data and concise asset-building instructions.
3. Connect the Dev workspace to its designated repository, branch and Git folder. For the initial single-workspace stage use its explicit introductory folder. Other files such as the root README sit outside that folder.
4. During initial synchronization, inspect the proposed direction and establish Git definitions from the intended workspace content. Do not treat an initial-sync prompt as permission to overwrite unrelated existing work.
5. Inspect the generated definitions and identifiers, record the initial source revision, and perform native promotion plus a smoke check. Explain which state was versioned and which runtime/configuration state was not.
6. Add starter validation/configuration/pipeline files gradually. Show what each file contributes rather than copying a complete framework unexplained.
7. Transition to the agreed Model B integration process and role-folder layout. Apply branch protections only after the intentional bootstrap commits are complete.

The native-to-role-split transition needs its own validated checkpoint: preserve intended logical identities, repair any path-based report references, and prove environment bindings. Avoid asking participants to improvise folder moves or regenerate logical IDs to resolve a conflict.

## Should Model B Dev remain Git-connected?

Git hosting, a workspace's Git connection, and the mechanism that deploys definitions are separate choices. Model B does not prescribe one Fabric synchronization feature.

| Option | Dev workspace behavior | Main tradeoff |
| --- | --- | --- |
| Git-connected integration Dev | Merged source is applied through a controlled Git-update process; each role maps to a folder | Familiar Fabric integration and source visibility; must manage sync state, bindings and timing |
| Pipeline-published integration Dev | Automation publishes a pinned revision through supported tooling/APIs; Dev need not be Git-connected | Consistent automated deployment path; UI edits require a deliberate export/capture route |

For the workshop, prefer demonstrating UI-to-Git bootstrap in Model A, then using a pipeline-published integration Dev for the locally edited Model B feature, if the feasibility slice validates that path. This is a proposal, not a platform requirement. Keeping Dev Git-connected with controlled updates remains a valid fallback if it better fits the existing implementation.

Choose one mechanism for the required Model B path. A Git connection by itself is not continuous automatic synchronization. Do not have uncontrolled UI synchronization and an independent publisher both managing the same target. After transition, routine changes enter via feature branches and PRs; normal releases do not depend on uncommitted UI state. Test and simulated Prod use the selected automated release mechanism and a pinned revision.

Explain the other Dev option in a short comparison. Implementing and rehearsing two complete Model B paths would spend time without adding a necessary core outcome.

## One-person core; optional pair concurrency

Recommendation: write and rehearse every mandatory exercise for one developer proceeding sequentially. A pair uses the same team project and solution, rotates the operator, and discusses/reviews the work together. A solo learner can use a facilitator/reviewer arrangement where review or approval is needed. Do not disable meaningful release controls simply because there is one learner.

The mandatory Model B exercise still includes a feature branch, PR, checks, integration and release. It does not require two simultaneous feature branches, a merge conflict, or parallel Fabric execution. Group-level capacity rehearsal remains necessary because many teams will run the tutorial at once.

Optional extension: two partners take independent changes on separate local branches, open PRs, integrate in sequence, and inspect the results. Deliberate merge conflicts and feature-workspace provisioning are not core completion criteria. Separate branches isolate source changes; a shared workspace still has shared runtime state.
