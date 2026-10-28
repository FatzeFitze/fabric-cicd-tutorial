# Scope proposal

Status: scoping proposal updated with organizer decisions. Date: 28 October 2026.

Agreed scope: hands-on Models A and B. Model C appears only in explainer sections. Local feature-branch development plus shared Dev is the preferred path; feature workspaces are an explainer topic. See [control coverage](control-coverage.md).

## Purpose and constraints

Prepare 15–20 participants, working individually or in pairs, to choose and apply a suitable Microsoft Fabric ALM workflow. There are 10–12 hours available over two days. Participants have mixed prior ALM experience. The target automation platform is Azure DevOps.

The organizer can provision capacity-backed Fabric workspaces, Azure DevOps projects or repositories, managed identities, and Confluence pages. Workshop workspaces will not use private links. The g-IT separation into code, data, and reporting workspaces and its permissions are confirmed in principle; the detailed permission mapping has not yet been supplied. Identity and networking designs remain open. Participants will have admin access to their own workshop workspaces.

The organizer supplied the three Working Version 1 DataOps guidelines, now retained in [source-guidelines](../source-guidelines/README.md). These define the models and MS-01–MS-14. A historical handover and the current test-project code snapshot have now been imported; see the [source assessment](initial-codebase-review.md). The original cloud evidence and complete earlier authoring material remain unavailable. The event is less than a month away; test setups can be provisioned immediately. The exact event date is not yet recorded.

The lab itself is training/sandbox under Gate 0. It demonstrates controls for fictional productive solutions; workshop workspace admin permissions and public connectivity must be called out when assessing which controls are actually enforced. Workspace count and local-versus-public connectivity do not determine Model A/B/C classification.

## Observable outcomes

Every team should be able to:

1. Explain the roles of source control, pull requests, CI checks, deployment, runtime execution, and release approval.
2. Promote a small supported Fabric solution through native Deployment pipelines and explain the limits they encountered.
3. Make a small change on a branch, submit a pull request, and observe a useful automated check reject a deliberately faulty change.
4. Use a provided Azure Pipelines starter to release a known source revision into a target environment.
5. Verify that deployed items use the intended environment's dependencies, run a small data workload, and verify its output.
6. Diagnose one controlled failure, correct it, and rerun or redeploy a known-good code version.
7. Adapt the starter to another small project by editing documented configuration, without editing the generic deployment implementation.

The Model B stage should be hands-on with selected prepared starter components introduced gradually. Participants first populate an empty solution repository from manually created Fabric assets, then add configuration, checks and automation at the relevant unit. Teams build understanding by configuring, extending, testing, and operating the starter. Model C adds short explainers on stronger control boundaries, evidence, monitoring, and recovery; it does not add a mandatory implementation track.

## Repository and remote strategy

Use one preparation repository initially, with boundaries that support later extraction of a community toolkit. Develop locally and use a private GitHub remote for workshop material intended for that destination. Write Azure Pipelines YAML from the beginning; GitHub hosting does not require choosing GitHub Actions as the delivery system.

The preparation repository is separate from each learner's solution. Give each participant or pair an unpopulated Azure DevOps project/repository and let them build it during the tutorial. Recommend one solution repository with `/fabric/code`, `/fabric/data`, and `/fabric/reports` role folders. For workspaces using native Git integration, record their exact repository/branch/folder mapping [S14]. Separate repositories are an explainer for independent ownership/access/release needs. See [repository and bootstrap design](repositories-and-bootstrap.md).

When company access is available, import into an empty Azure Repos repository or transfer with ordinary Git remotes and retain history. Repository content transfers; Azure DevOps service connections, environment approvals, variable groups, branch policies, pipeline registration, agents, and permissions require destination setup. Validate pull-request triggering and policy behavior in Azure Repos rather than assuming GitHub behavior is identical.

Azure Pipelines can also run against a GitHub repository if an Azure DevOps organization becomes available before the repository moves [S1, S2]. This can bridge the transition where company policy permits. A new private Azure DevOps organization is an optional convenience, not a dependency for starting local work.

Use one authoritative remote for each release line rather than continuous two-way synchronization. Once company delivery starts, define how selected generic improvements return to the community source. Keep restricted company documents and configurations in company-controlled storage; private GitHub visibility alone does not authorize their transfer.

Proposed eventual implementation structure; current contents include planning documents and dated historical reference source:

```text
README.md
AGENTS.md                      # durable project working instructions
docs/
  planning/                    # scope, decisions, validation evidence
  prereads/                    # short ALM introduction and glossary
  tutorial/                    # section folders, one Markdown file per unit
  facilitator/                 # provisioning, timing, recovery, answer key
  reference/                   # starter configuration and component contracts
sample/
  data/                        # tiny deterministic synthetic inputs
  fabric/                      # source-controlled item definitions by role
  checks/                      # project-specific data assertions
toolkit/
  src/                         # reusable deployment and validation components
  schemas/                     # configuration contracts, if experiments justify them
  tests/                       # meaningful generic behavior and adapter checks
pipelines/
  azure/                       # Azure Pipelines entry points and templates
examples/                      # minimal and separated-workspace examples
config/                        # sanitized example environment mappings
```

Keep workshop narratives and sample business logic outside toolkit internals. The toolkit should have its own dependency definition and tests. Defer a second repository and package publishing until another small example proves the boundary. Three learning stages should reuse the same components with increasing configuration, rather than maintain three frameworks.

Markdown should use ordinary headings, relative links, tables, and portable images. A unit should contain its objective, time estimate, prerequisites, explanation, numbered exercise, expected observable result, troubleshooting, and checkpoint. Confluence export is a later publishing adapter. Record the Git revision used for publication and avoid independent edits to published copies.

## One evolving sample project

Proposed scenario: a small synthetic order-to-revenue solution. Inputs are orders, products, and customers. A notebook builds a curated sales table; a pipeline orchestrates execution; a semantic model and report display revenue, order count, and a simple quality indicator.

Use a deterministic generator or small versioned CSV files, with a known expected result. Avoid an external operational system, credentials for a public API, or network-dependent ingestion as a workshop prerequisite.

Target core asset set, subject to a successful compatibility experiment:

| Asset | Learning purpose | Scope control |
| --- | --- | --- |
| Lakehouse | Persistent data and environment isolation | Tiny seeded data; deployment is not a copy of data |
| Notebook | Transformation, tests, lakehouse binding | Short runtime and small output |
| Data pipeline | Orchestration and execution references | A small number of activities |
| Semantic model | Consumption dependency and refresh/readiness | Choose one validated storage mode |
| Report | Visible outcome and model binding | One page with a few visuals |
| Variable library or equivalent supported configuration | Environment-specific values | Include only if it simplifies the validated path |

An Environment, Warehouse, Dataflow Gen2, or Real-Time Intelligence asset can be an optional extension selected from actual migration needs. Do not add all of them to the mandatory path. Report format, semantic model mode, and deployment support must be proven together before committing to the exercise. In particular, current Deployment pipeline documentation lists PBIR report and Direct Lake binding limitations [S4].

Progress the same business solution through:

1. **Native promotion:** manually create a small introductory solution in Fabric, initialize the participant repository, capture supported definitions through Git integration, and compare/promote stages. Supplied input data can simplify setup; the normal path starts with an unpopulated participant repository.
2. **Source control and CI:** export or synchronize supported definitions, introduce a branch and pull request, run configuration and transformation checks, and connect a source change to a controlled deployment.
3. **Model B, separated workspaces and release control:** place data assets, executable assets, and reporting assets in their agreed roles. Resolve environment-specific references, deploy prerequisites in order, run readiness checks, and promote a pinned revision through Test and simulated Prod. Explain Model C escalation separately.

Model A includes a traceable Git source state for technically supported definitions, identified environment settings/identities, deliberate promotion, basic validation, and a documented bootstrap/recovery path. Git and control hygiene therefore begin in the introductory stage; feature branches, PR policies, and automated CI are introduced as Model B strengthens delivery.

The fictional scenario changes from a low-risk reporting solution to normal team delivery with regular changes and shared consumers. Participants explain why Model B becomes appropriate. The mandatory exercise follows one developer sequentially; simultaneous feature development is optional. They also discuss a hypothetical critical/regulatory use case that would require Model C without building it.

Provide starter and solution checkpoints for each stage as recovery resources. The normal path preserves the participant's work. Rehearse the transition to role folders and the final workspace layout, preserving intended logical identities and correcting path-based references. Use a documented helper or small guided change if needed; recovery checkpoints are a fallback, not a mandatory replacement of the learner-built repository. Preserve the earlier source revision for comparison.

Suggested change story: add a returns indicator, change the net-revenue calculation, and add a data assertion. Suggested failure story: a required configuration value is absent, or a target dependency points to Dev. CI/preflight rejects the invalid state; the team fixes it and observes a successful run. Include a known-good redeployment exercise without claiming that reverting code reverses data changes.

## Time budget

Proposed mandatory teaching and exercise time: 9 hours. Reserve 1.5 hours for support and overruns. Optional extensions fill up to another 1.5 hours if the full 12 hours are available. These are working-session hours; meal breaks are outside the estimate.

| Day | Block | Hours | Observable output |
| --- | --- | ---: | --- |
| 1 | Foundations, classification, four state types, and preflight | 0.5 | Everyone can access their team resources |
| 1 | Model A: manual asset creation, Git baseline and native promotion | 1.75 | Learner-built assets reach a target stage with a recorded source state |
| 1 | Model B: local feature branches, shared Dev, and pull requests | 1.0 | A reviewed change in the repository |
| 1 | CI and useful quality checks | 1.0 | One failing and one successful validation run |
| 1 | Guided consolidation challenge | 0.25 | Team can explain and repeat the simple release path |
| 2 | Workspace separation and dependency model | 0.75 | Team can identify target dependency bindings |
| 2 | Azure DevOps release path | 1.75 | A pinned revision reaches Test and simulated Prod |
| 2 | Failure, recovery, and rerun | 1.0 | Evidence of diagnosis and safe recovery |
| 2 | Starter reuse, handover, and Model C/feature-workspace explainers | 0.5 | Starter reused and limits understood |
| Both | Distributed support/overrun reserve | 1.5 | Recovery without cutting the final learning outcome |

Write the core tutorial for a single developer. Pairs follow together and rotate who operates; required concurrency or merge-conflict exercises are excluded. Review and approval can involve a partner or facilitator. Provide a short ALM pre-read, glossary, setup checklist, and optional Git practice beforehand. Introduce concepts briefly again during the relevant exercise so completion does not depend on perfect pre-read uptake.

## Workspace and provisioning design

If each team gets Dev/Test/Prod for each of code/data/reporting, the final layout is nine workspaces per team. Fifteen to twenty people imply 8–20 teams depending on pairing, or 72–180 workspaces. Pairing everyone gives 8–10 teams and 72–90 workspaces. Additional workspaces for the native stage, facilitator, or recovery would be extra unless deliberately reused.

Choose whether the native-stage workspace triplet is reused as one role in the final topology. This reduces provisioning but requires a rehearsed cleanup or transition with no stale bindings. Use team/environment/role naming consistently. Workshop Prod is simulated production containing synthetic data. Shared Dev means shared within a team; teams do not share one global mutable Dev environment. The preferred core path provisions no feature workspaces.

Participant admin access supports self-service pipeline/workspace setup. More precisely, workspace admin is required to assign a workspace to a Deployment pipeline; pipeline permissions are separate [S10]. Keep admin access for the lab as requested. Use a more restricted automation identity where supported and explain that broad human admin access can bypass its controlled route. Do not present the lab as proof of production permission enforcement.

Pre-provision and verify participant access, workspace roles, repo permissions, DevOps licenses/access levels, pipeline permissions, service connections, deployment identities, Fabric tenant settings, connection permissions, and agent availability. Capacity-backed workspaces alone do not guarantee participant access to every required authoring or consumption feature.

One organizer-owned capacity requires a representative concurrency trial: simultaneous notebook starts, pipeline execution, model readiness/refresh, and deployment. Workspace separation does not isolate shared compute capacity. Keep data small and provide controlled retry guidance and staggered starts if measured behavior warrants it.

For public-endpoint workshop workspaces, use runner connectivity appropriate to that setup. Describe private-network execution as an enterprise extension until the actual g-IT path is validated. Differentiate deployment automation identity, Fabric workspace identity, and runtime data-access identity. A managed identity's existence does not establish its usability from the chosen agent or for every operation.

## Reusable toolkit: the proposed cutoff

Start with a thin layer around supported Fabric capabilities and evaluate `fabric-cicd` against the current enterprise implementation. Its documentation already covers supported item deployment and parameterization [S6, S7]. Native Deployment pipelines, Git integration, and API-driven deployment are composable options; project size and workspace visibility alone should not determine which is appropriate.

Separate four concerns:

| Concern | Project author supplies | Generic implementation supplies |
| --- | --- | --- |
| Solution intent | Stable item keys, source locations, workspace roles, required relationships | Validation and a resolved deployment view |
| Environment values | Workspace/connection mappings and allowed external targets | Lookup, completeness checks, isolation checks |
| Deployment mechanics | Small supported options | Authentication integration, tool invocation, polling, bounded retries, logs |
| Business correctness | Transformation assertions and expected metrics | A consistent check runner and recorded results |

Keep stable project keys distinct from Fabric logical IDs and environment-specific physical item IDs. Logical IDs already present in Fabric definitions should remain authoritative. Resolve physical IDs through deployment outputs and unambiguous inventory lookup; do not ask participants to paste all target item IDs manually.

The desired configuration describes a **deployment dependency contract**, not a complete business entity-relationship model. Table relationships and data lineage may be relevant later, but they are different from notebook-to-lakehouse, pipeline-to-notebook, and report-to-model deployment references.

Use the smallest contract that the experiments show is necessary. Prefer native/library configuration for capabilities already supported. Add a schema-backed manifest only for gaps such as role routing, required external relationships, ordered execution prerequisites, and expected deployed state. Do not maintain duplicate dependency facts by hand if supported definitions expose them reliably.

Illustrative design language only; this is neither a supported Fabric format nor an implemented toolkit schema:

```yaml
schemaVersion: 1
items:
  curated_sales:
    type: Lakehouse
    workspaceRole: data
  build_sales:
    type: Notebook
    workspaceRole: code
bindings:
  - from: build_sales
    relationship: defaultLakehouse
    to: curated_sales
    environmentPolicy: sameEnvironment
```

Source paths, actual definition fields, and environment workspace mappings would be specified separately. A binding declaration expresses desired configuration; it does not provide API support. Each accepted relationship requires a proven resolver, deployment mechanism, and post-deployment inspection method.

The first supported contract should cover only relationships in the core sample. Validate missing targets, ambiguous keys, missing environment mappings, forbidden cross-environment references, and unsatisfied prerequisites. Reject unsupported relationships clearly. Not every runtime relationship is a deployment-order edge; model typed edges and reject cycles only in prerequisite graphs that must be acyclic. Some assets may need create-then-bind handling.

Provide a reviewable resolved plan showing selected revision, target workspaces, intended operations, prerequisite order, and checks. Confirm what the chosen deployment tool can actually predict; label any approximation. Serialize competing deployments to the same target. Record the source revision and resolved mappings in a release record. Validate and deploy the same pinned source snapshot; avoid rereading a moving branch between stages. Model B uses a distinct production approval step; stronger independently governed production capability is a Model C explainer. Azure DevOps resource checks are configured outside pipeline YAML [S11]; resource setup is part of the starter's provisioning documentation.

For multiple workspaces, track partial progress and support rerun or known-good redeployment. Do not imply a cross-workspace transaction. Provision or validate storage prerequisites, deploy supported definitions, bind dependencies, wait for readiness, seed/execute/refresh as required, and verify outputs in an order demonstrated by the experiment. Keep destructive cleanup outside the default release path.

Reuse profiles should be small examples over the same implementation: controlled native promotion for Model A and managed delivery for Model B, including the separated-workspace example. Model C extension guidance describes stronger controls over the same foundation. Avoid a universal plugin system or exhaustive asset coverage in the workshop release.

## Scope boundaries and completion

Mandatory: one tested A/B vertical slice starting from an empty participant repository, manual creation of introductory Fabric assets, Azure DevOps delivery, traceable native promotion, local feature branches with shared Dev, cross-workspace binding validation, deterministic sample data, practical quality checks, failure/recovery exercise, reusable starter, facilitator recovery material, and a timed single-developer pilot. Cover all fourteen minimum-control topics proportionately through exercises, reference material, or clearly identified lab limitations.

Optional: pair concurrency on separate local feature branches, an extra item type, generated dependency diagrams, and Confluence publishing automation. Model C, feature workspaces, separate-repository tradeoffs, and alternative Dev-sync mechanisms are explainer material; private-network runner implementation and advanced branching are outside the core scope.

Deferred: universal deployment framework, automatic lineage discovery for every Fabric item, production data migration/rollback automation, full infrastructure platform provisioning, package registry publishing, and comprehensive private-link replication.

Workshop readiness requires a fresh team to complete the core path from the participant instructions, within the available time, on the intended tenant and Azure DevOps setup. A local unit test, a documentation claim, or a facilitator demonstration is insufficient evidence by itself.

See [the backlog](backlog.md) for technical experiments and delivery gates, and [the decision register](decisions.md) for unresolved inputs. Source IDs refer to [sources.md](sources.md).
