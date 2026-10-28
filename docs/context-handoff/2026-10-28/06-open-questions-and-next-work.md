# Open questions and next work

## Inputs still needed

1. Exact event date, pairing mix, participant experience, laptop tools/restrictions and facilitator availability.
2. Existing Section 3 repository/scripts and retained evidence, in an authorized location. Historical sandbox download links are not a portable source checkout.
3. Detailed g-IT item placement, workspace permissions, connections, identity approach, networking and runner design.
4. Actual workshop test access, Azure DevOps permissions/service connections, Fabric tenant settings and capacity details.
5. Sample acceptance: relevant item types, report format, model storage mode and representative local feature change.
6. Approved source-sharing boundary, eventual community ownership/license and company configuration location.

Already known: A/B hands-on boundary, Model C/feature-workspace explainers, ability to provision test resources, participant workspace-admin access, and principle of code/data/reporting separation. Do not ask for these again as if unresolved.

## First bounded engineering task

Review the old implementation against the workshop requirements and build the smallest clean-target vertical slice before writing the full curriculum or a universal deployment toolkit.

Proposed order:

1. Inventory old scripts, configuration, deployment entry points, supported items and evidence schemas. Identify reusable pieces, hardcoded sample assumptions and missing cross-workspace support.
2. Choose the smallest representative sample and required local edit. Test native promotion compatibility for the chosen report/model/item set.
3. Prove authentication from the intended runner for every required operation, and verify runtime access separately.
4. Deploy notebook -> separate-workspace lakehouse; pipeline -> notebook/connections; semantic model -> data; report -> semantic model. Inspect actual bindings and run deterministic checks.
5. Bootstrap from an empty learner repository and fresh target. Validate definition versus data lifecycle, seeding/readiness and identity preservation during folder/topology transition.
6. Choose one shared-Dev update mechanism. Demonstrate feature branch -> review/CI -> integration without feature workspaces or competing workspace writers.
7. Carry a pinned source through TEST, approval and simulated PROD. Capture deployment plus runtime evidence, prevent Dev references, serialize releases and rehearse partial failure/rerun/recovery.

The existing preparation backlog calls these V01–V18; use its canonical IDs rather than creating a competing experiment register. Historical Section 3 findings reduce research effort but do not automatically pass those workshop experiments.

## Design choices to settle from evidence

- Pipeline-published versus controlled Git-update integration Dev.
- One solution repo with role folders versus exceptional separate-repo needs.
- Reuse of initial workspace triplet and clean transition to role split.
- Report/model format and storage mode supported across both teaching stages.
- Supported relationship types, inspection methods and genuinely necessary extra manifest fields.
- Minimal identity/permission requirements, production approval setup and concurrency/queue policy.

Do not require both Dev-update mechanisms, all Fabric asset types or a universal dependency discovery system. Narrow optional coverage if feasibility takes longer; preserve traceability, Model B approval/runtime validation, recovery and a timed pilot.

## Readiness gates

| Gate | Required evidence |
| --- | --- |
| Architecture | Sample, scope, identities, topology, workflow and controls explicitly selected |
| Feasibility | Clean end-to-end slice works on intended tenant and Azure DevOps setup |
| Reuse | Second small example works through documented configuration without toolkit edits |
| Teaching | Fresh learner follows instructions from an empty repo within the time budget |
| Event | Team access and realistic capacity concurrency tested; versions/checkpoints/docs frozen |

Reserve the final week before the event for pilot fixes and readiness rather than first discovery of cross-workspace behavior. Calendar dates depend on the exact workshop date.
