# Workshop scope and decisions

## Confirmed constraints and direction

- DNA Fabric Days workshop/hackathon: 15–20 people, alone or in pairs; two days with 10–12 working hours.
- Mixed prior ALM experience; short pre-reads can introduce concepts, but exercises should explain them again as needed.
- Event is less than a month after 28 October 2026; exact date is not recorded.
- Azure DevOps is required for the workshop and subsequent company work.
- Organizer can provision workspaces, organizer-owned capacity, Azure DevOps resources, managed identities and Confluence resources. Test setups can be provisioned now; access is not thereby confirmed.
- Workshop workspaces have no private links. Participants have workspace-admin access.
- Hands-on scope is **Model A and Model B**. Model C and feature workspaces are explainers.
- Prefer local feature branches and shared Dev within a team. Do not require a workspace per feature.
- Learners start with unpopulated Azure DevOps projects/repos, manually create initial Fabric assets, capture them in Git and add starter files gradually.
- Code/data/reporting workspace roles are confirmed in principle; detailed placement, permissions, identities, connectivity and deployment design still need validation.

## Recommendations that remain proposals

1. One Azure DevOps project per participant/pair and one solution repo with `/fabric/code`, `/fabric/data` and `/fabric/reports` folders.
2. Required exercises follow one developer sequentially; pairs rotate together. Simultaneous development is optional.
3. One evolving synthetic order-to-revenue sample: orders/products/customers, lakehouse, transformation notebook, pipeline, semantic model and one-page report. Select model mode/report format through experiments.
4. One preparation repository initially, with a separable toolkit for possible later community extraction.
5. Nine core hours plus 1.5 hours support reserve; optional extensions only if time remains.
6. Prefer pipeline-published shared integration Dev if feasible; controlled Git-update Dev remains an alternative. Select and teach one mechanism.

The canonical repository decision register retains the detailed D01–D15 proposals. These recommendations must not be relabeled accepted merely because they appear here.

## Intended learning journey

1. Foundations: classification, four state types, access and setup.
2. Model A: manually create small assets, capture supported definitions in Git, perform controlled native promotion, record source/configuration, check runtime and discuss bootstrap/recovery.
3. Model B: local change -> PR/review/CI -> shared Dev -> pinned TEST release and checks -> approval -> simulated PROD and runtime evidence.
4. Separate code/data/reporting roles, resolve dependencies to the correct environment, diagnose a controlled failure and recover.
5. Reuse starter components and explain stronger enterprise controls and feature-workspace tradeoffs.

The role split is a topology choice, not an automatic reason for Model C. Model A is still governed productive delivery; it is not a Git-free exemption.

## Important lab boundaries

Shared Dev is a team integration runtime. Local branches isolate source files, not Fabric runtime/data. The chosen path has no isolated pre-merge Fabric execution unless explicitly added. Do not switch shared Dev between each developer's feature branch.

Choose one writer for each workspace. Transitioning from native Git bootstrap to pipeline publishing must reconcile pending changes and stop competing writers. Serialize deployment/testing to shared targets.

Participant admins can bypass the demonstrated release path. Actual approval checks should still be configured, but successful lab runs do not prove independent production enforcement. Workshop PROD contains synthetic data and is simulated production.

Nine workspaces per team follow from three environments times three roles. At 8–20 teams that means 72–180 workspaces; pairing everyone means roughly 72–90. Reuse of introductory workspaces and final pairing remain choices. Workspace separation does not isolate shared capacity compute.

## Reusable component boundary

Project authors supply stable item keys, source locations, workspace roles, environment mappings, required relationships and business assertions. Generic code resolves configuration, invokes supported tooling, polls jobs, records results and validates declared constraints.

The proposed manifest describes deployment dependencies, not a full business entity-relationship model. Prefer supported definition/library configuration; introduce extra schema only for demonstrated gaps. Stable project keys, Fabric logical IDs and target physical IDs are different concepts. Resolve physical IDs from deployment results or unambiguous inventory rather than requiring all IDs to be pasted manually.

No cross-workspace transaction is assumed. Capture partial progress and provide convergent rerun/known-good redeployment. Keep destructive cleanup outside normal release.
