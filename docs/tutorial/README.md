# DNA Fabric Days: participant tutorial

This tutorial is being developed through an organizer-led participant pilot. Follow one unit, report the observed result, and revise the instructions before proceeding. A written unit is not yet a validated exercise.

The working scenario is a small synthetic sales solution that progresses from controlled native promotion (Model A) to managed team delivery (Model B). Model C and feature workspaces remain explainer topics. The participant solution starts in its own Azure DevOps project/repository; this preparation repository supplies selected instructions and starter files as needed.

## Start here

| Unit | Outcome | Status |
| --- | --- | --- |
| [0. Observe and test the setup](section-01-foundation/unit-00-observe-and-test-the-setup/README.md) | Explain the components and inspect the provided workspace/repository layout | Parked as-is after organizer review; access checks reported successful; learner timing unmeasured |

## Unit folder convention

Each participant unit has its own folder. `README.md` is the main lesson, with unit-specific resources kept alongside it. Create supporting folders only when they contain actual resources.

```text
docs/tutorial/
  section-01-foundation/
    unit-00-observe-and-test-the-setup/
      README.md
    unit-01-<topic>/             # created when the next unit is authored
      README.md
      resources/                # optional inputs, snippets or diagrams for that unit
```

Files needed only for one exercise belong in its unit folder. Reusable deployment code, shared sample definitions, pipeline templates and multi-unit examples remain in `toolkit/`, `sample/`, `pipelines/` or `examples/`, and units link to their canonical files. Avoid maintaining duplicate copies of shared code beside each lesson. The old setup-draft redirect is retained for historical links and is not an active participant unit.

## Proposed sequence after Unit 0

The following are planning placeholders, not available or validated units:

Provisioning belongs to the [facilitator reference](../facilitator/project-and-environment-provisioning.md), outside learner exercise time. The earlier setup Unit 1 is superseded; the first manual-asset unit will be Unit 1 and has not yet been authored.

1. Create the first lakehouse and notebook manually; run deterministic synthetic data.
2. Capture supported definitions in Azure Repos and inspect source versus runtime state.
3. Promote with native Fabric Deployment pipelines and verify target behavior.
4. Make a local feature change, introduce PR review and useful CI checks.
5. Coordinate releases across the pre-provisioned workspace roles and validate explicit dependency/environment mappings.
6. Automate a pinned release through Test, approval and simulated Prod with runtime evidence.
7. Diagnose a controlled failure, recover, and reuse the starter configuration.

Unit boundaries and timing will change with pilot feedback. No future unit should assume the old reference lab's cloud behavior applies to this sample.

## How to report a result

Use the checkpoint at the end of the unit. Report what happened, the approximate time, confusing wording and any exact error text. A failed checkpoint is useful evidence; it is not a reason to invent an undocumented workaround.

The facilitator keeps the [pilot record](../facilitator/pilot-log.md), including the document revision actually followed. Keep private setup details in local notes where needed.
