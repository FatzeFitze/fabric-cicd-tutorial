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

- 11 November. Use the existing-UAMI **Managed identity** connection form and facilitator-provided Azure subscription and resource group selections. Teams grant their deployment UAMI Fabric Contributor in the assigned workspaces. Start with shared Dev, Test and Prod UAMIs. Per-team identities may be automated later. The live Dev preflight passed by organizer report and logical IDs matched `.platform`. Start Unit 9 with Test setup and the before-release inventory. [Unit 8 pilot notes](../facilitator/unit-08-pilot-notes.md) · [Unit 9 pilot notes](../facilitator/unit-09-pilot-notes.md).

- 10 November. Learners create their own Azure DevOps service connections, starting with the Dev connection in Unit 8. The facilitator provides the UAMIs and prepares Azure and Fabric access. Use the same guided pattern for later environment-specific connections. The scope and minimum Azure access for the chosen task still need pilot evidence. [Unit 8 pilot notes](../facilitator/unit-08-pilot-notes.md).

- 10 November. Keep participant- and project-specific values in versioned configuration. The release mask carries repository references, source pins and workspace IDs. Use `config/environments/<environment>.yml` for release identity and connection names and expected workspace display names. Bind protected Azure DevOps resources at pipeline expansion. Repository resources that require a literal name belong in the project's pipeline entry point. [Repository resource schema](https://learn.microsoft.com/en-us/azure/devops/pipelines/yaml-schema/resources-repositories-repository).

- 10 November. The organizer accepted Unit 7's lesson with a clarification about the teaching example. Explain the purpose and limits of simplified logic at the point of use. Unit 8 starts with live Dev name and item checks. The publishing continuation depends on the observed runner identity and export bindings. [Unit 8 pilot notes](../facilitator/unit-08-pilot-notes.md).

- 10 November. The organizer reported a smooth Unit 6 walkthrough and requested optional readings when a topic benefits from exploring choices. Place reusable readings in the tutorial reference folder and link them from the relevant unit. Unit 7 uses the observed three-repo setup for an offline preview of declared source pins, workspace IDs, dependencies and desired value sets. [Static Fabric validation](../tutorial/reference/static-fabric-validation.md) · [Unit 7 pilot notes](../facilitator/unit-07-pilot-notes.md).

- 10 November. The organizer accepted Unit 5 after completing its revised first-merge walkthrough and confirmed the Python export path. Pin the Unit 5 lesson body at `348d885` and proceed to the required CI exercise. Unit 6 uses a standard-Python source contract with a reusable notebook validator and a separate Tiny Sales check. Spark and Fabric runtime validation follow in Unit 8. [Unit 6 pilot notes](../facilitator/unit-06-pilot-notes.md).

- 10 November. Keep Unit 4's 357.20 gross baseline for Unit 5 and complete the first reviewed merge into `dev` in Unit 5. Expected revenue after excluding returns is 204.70. This supersedes the earlier restore-and-hold-draft plan. The organizer wants a modular function suite and configuration mask in the remaining curriculum. The proposed YAML form, second PR for required CI, and separate Dev publishing exercise are recorded for review. [Curriculum and Unit 12 target state](curriculum.md#target-state-after-unit-12).

- 4 November Unit 4 acceptance and Unit 5 request: organizer accepts Unit 4 as its first version, except Section 7 must distinguish logical IDs found in Git from physical IDs found in deployed items/URLs/APIs. Add a shared participant ID explainer now, link it from Units 2/4/5, and revisit source-to-target ID correlation in Units 7–10 logs/manifests. Acceptance does not supply raw per-item IDs, source exports or an independent replay of every revised step.
- Unit 5 implementation: retain the current Code-repo/dev pilot; ordinary local IDE feature edit, reviewed commit/push and **draft PR into dev**, held for Unit 6's checks. Keep shared Dev on its existing branch/source/runtime baseline. Preserve actual Fabric export markers and logical identity; no mandatory Python/Spark installation or local runtime execution here. Unit 6 must publish the draft before expecting automatic build-policy validation. This is an authored pilot path, not reported Azure Repos/local-workflow success.

- 4 November Unit 4 feedback: organizer reports successful progress, with suitable scope/length and UI/measure-name issues. Correct new-item **Pipeline**, Base parameters **Name/Type/Value**, expected runtime-injected override cell, model autosave and **Total Revenue** measure. Expand read-only endpoint/type/authentication inspection. Add a temporary P01 price change and corresponding expected totals to make report refresh visible, then restore the canonical 342.20 baseline before Git capture. The organizer subsequently confirmed leaving Connection unselected for the successful pipeline run. Revised inspection guidance and the new data-change exercise await replay; this does not validate workload-identity execution. See [Unit 4 pilot notes](../facilitator/unit-04-pilot-notes.md).
- Unit 5 retains the already planned IDE-based feature development in an ordinary local Git checkout. Explain that Fabric VS Code VFS saves update a live workspace. Park intentional conflict creation/recovery as an optional auxiliary unit after that foundation; use one developer sequentially and rehearse preservation/recovery first. This adds neither mandatory pair concurrency nor feature workspaces. See [conflict rehearsal plan](../facilitator/source-conflict-exercise-plan.md).

- 4 November: organizer reports Unit 3 now works nicely, accepts it as the first version and requests Unit 4. Park the lesson body at `2fde5c0`; its next-unit navigation link may be added. This is successful full native-chain behavior by organizer report, not proof of the upcoming automated/workload-identity path.
- 4 November: reserve a later exercise that creates at least one new Fabric target item when Test/Prod deployment is exclusively through managed identities, then inspects human versus non-human ownership and implications. The [identity/ownership experiment](identity-and-ownership-experiment.md) places the human baseline in Unit 4, fresh validation-notebook creation in Unit 9 and the corresponding Prod creation in Unit 10. Item-specific owner/default/runtime/connection identities must be observed, not assumed identical.
- Unit 4 implementation selection: same-Code-workspace pipeline consumes `sales_config` scalar references and passes notebook parameters; browser semantic-model creation uses Direct Lake on SQL and saves model/report in Reporting Dev. These are documentation-informed pilot choices awaiting actual tenant evidence, not blanket architectural standards. Existing three-repo bindings are retained for this walkthrough; final event/Model B topology remains open.

- 30 October Unit 3 feedback: organizer reports the native Test rehearsal worked. Correct deployment instructions to select the target stage first and check Deploy from; rules must be located explicitly in the Deployment pipeline view, not the notebook editor. Expand conceptual teaching about resource IDs, linkage and environment configuration, including what may be hidden in a centrally managed on-premises setup.
- Organizer delegated whether Unit 3 should include Prod now. Selected full native Dev → Test → simulated Prod, consistent with the curriculum's Model A outcome. Full participant lesson and release worksheet now include a separate Prod rule, deliberate authorization and runtime checks. Test is reported passed; Prod/revised prose remain untested. This does not approve additional Fabric item types or change Model B's later automation scope.

- 30 October: organizer needs every new unit/preparation draft in a dedicated repository folder immediately, with a README entry point and all linked materials available through GitHub/work-PC synchronization. Unit 3 now has its own tutorial folder linking the existing canonical rehearsal and sample cell. This is a discoverability/publishing convention, not acceptance of untested native behavior.

- 29 October Unit 2 completion: organizer added the missing introductory cell, synced and completed the rest successfully. Updated guidance reviews the completed Azure Repos commit before Fabric Update, closes saved notebook editors before external updates, and preserves unsaved work before refresh/reopen if a version warning appears. Exact editor-warning cause and availability of pre-commit diff across editor versions remain unverified; reported workaround was browser refresh. Unit 2 timing/actual source revisions not supplied. Organizer authorizes committing/pushing these documentation adaptations, then proceeding toward Unit 3.

- 29 October Unit 2 request: organizer reports pushing the first Unit 1 version and asks to continue. Unit 2 is authored against the already-provisioned three-role-repo pilot without changing its bindings; this preserves the reported setup rather than approving three repos as the final event/Model B layout. It captures both directions through a Markdown-only round trip and records each participating repo's revision separately. No actual Git sync result is reported yet.

- 29 October Unit 1 walkthrough: organizer reports everything worked in approximately 20–30 minutes including reading. Correct the notebook attachment UI to **Add data items → From OneLake catalog**; the lesson and source evidence are updated. This is organizer-reported Dev runtime success, not proof of Git sync, target promotion or workload identity. Keep the 45-minute mixed-experience planning allowance until further pilot timing exists.
- 29 October Unit 1 authoring request: write unit Markdown directly for tutorial participants, including explainers, official references and step-by-step assignments. Keep organizer checks in chat or separate facilitator material. Adopted working format is recorded in [the authoring guide](../facilitator/tutorial-authoring-guide.md). Unit 1 was authored with a Tiny Sales starter and explicit expected results; its later reported walkthrough outcome is recorded above.

- 29 October curriculum follow-up: organizer accepted the five-section/Units 0–12 journey and minimal sales sample, with a Variable Library required as a sixth authored item type. Code-workspace placement was suggested; the implementation plan recommends it beside its consumers, subject to validation. Introduce the library in Unit 4 and extend environment-specific use in Units 7–10; these detailed placements are implementation recommendations. Additional Fabric item types can be considered later.
- Reusable CI/deployment components, Azure Pipelines templates and their parameterization must be built and tested in this preparation repo before the corresponding learner exercise. Introduce them gradually with explicit configuration examples; participants configure and reuse them rather than implement the generic layer from scratch. See the phasing table in [curriculum.md](curriculum.md). Broad journey acceptance does not validate timings, source layout, deployment mechanisms or runtime support.

- 29 October: organizer reviewed Unit 0 as looking good and asked to park it as-is and proceed. Each participant unit will have its own folder, with a README.md lesson and optional colocated resources. Shared reusable assets remain in canonical repository locations. No learner walkthrough time or additional runtime results were supplied with this review.

- 29 October follow-up: organizer confirmed workspace/repository access, Dev Source control access, empty workspaces and native Deployment pipelines availability. DevOps access was added separately and works; provisioning took about one minute without private endpoints. Managed identity creation is planned for a later factory extension, not reported complete.
- Participants start with Unit 0, observing/testing the supplied setup and learning component interactions. Move provisioning detail to facilitator documentation; introduce manual asset creation in the next participant Unit 1. Existing access checks are reported passed, while the new explanatory text and learner timing await feedback.

- 29 October 2026 pilot provisioning feedback: supplied factory manifest and three successful create records describe nine workspaces, one Azure DevOps project, three role-specific repos, default/integration branch `dev`, and initialized Dev Git bindings. This is the observed pilot layout, not acceptance of three repositories as the final tutorial architecture. Access checks were subsequently confirmed as above; actual Fabric item synchronization remains to be tested. See docs/facilitator/provisioning-review-2026-10-29.md.

- The organizer acts as the first participant in fresh Fabric workspaces and a fresh Azure DevOps project. Develop units sequentially, refine from reported results, and persist assets/feedback here. The setup inspection is reported successful; Unit 0's revised teaching content and subsequent asset work remain pending.

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
| D04 | Accepted 29 October: one evolving synthetic sales project, now including a Variable Library | Visible outcomes and meaningful dependencies | Asset mechanisms and timed pilot still to validate |
| D05 | 9 h 10 min core, 90 minutes reserve, optional extensions | Protect the complete learning path | Timed pilot |
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
| D16 | Provision the nine role/environment workspaces from Unit 1; introduce their use gradually | Address the organizer's request to consider the full layout immediately and avoid a later topology-migration exercise | Pilot timing and explicit native-promotion/dependency experiment |
| D17 | Broad journey accepted 29 October: five sections and Units 0–12, minimal native lakehouse/notebook slice followed by orchestration, Variable Library and reporting | Make asset/control growth and reusable-automation adoption explicit | [curriculum.md](curriculum.md): mechanisms, detailed placement and timing await validation |

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
| A02 | A supported report/model combination works in the full Model B path; the accepted introductory native slice omits reporting | Adapt format/storage mode or the reporting exercise before authoring |
| A03 | The chosen runner can authenticate with an approved noninteractive identity | Change runner or identity design and rerun end-to-end tests |
| A04 | The capacity can support realistic team concurrency | Reduce runtime work, stagger starts, or adjust capacity |
| A05 | A small set of required dependency types can be inspected after deployment | Narrow validation promises or change the asset path |
| A06 | Company Azure DevOps validation is completed before curriculum freeze | Keep Model B stage readiness explicitly unresolved until tested |
| A07 | Mandatory features can be edited locally without feature workspaces | Change the feature or explicitly review the development-workspace boundary |
| A08 | A team can coordinate the few unavoidable shared-Dev UI operations | Simplify the required feature and retain isolated UI authoring as explanation |

## Decision procedure

For each decision, record the selected option, rationale, evidence, date, and implications for existing units or templates. Do not change a proposal to accepted simply because code was written against it. Update this register when the organizer resolves a choice.
