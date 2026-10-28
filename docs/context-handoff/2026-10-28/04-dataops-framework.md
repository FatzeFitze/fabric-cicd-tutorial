# DataOps framework and governance

Source baseline: the three Working Version 1 files in [reference-guidelines](reference-guidelines/). They were supplied by the organizer and already copied into the preparation repository. Formal organizational approval is not established.

## Distinguish lifecycle, controls and service ownership

The latest governance discussion compared a KPMG process-centric lifecycle with the organizer's principles/control-centric approach. The organizer questioned a detailed persona/RACI model for solutions usually staffed by one or two people.

The assistant's recommendation was to retain the end-to-end data-solution lifecycle as surrounding context, with the DataOps framework defining engineering and operational controls throughout it. Responsibilities and control boundaries should precede elaborate role catalogs. This recommendation was not subsequently recorded as an approved organizational decision.

DataOps includes DevOps engineering practices plus data-specific concerns such as quality, schema/contracts, lineage, freshness, runtime data recovery and downstream consumers. Demand qualification, portfolio decisions and business ideation belong to the wider lifecycle rather than becoming the core definition of DataOps.

## Gate 0 before Models A/B/C

First decide whether the full productive standard applies:

| Applicability | Expected treatment |
| --- | --- |
| Exploration/Sandbox | Basic hygiene for genuinely disposable experimentation |
| PoC/Pilot | Reduced baseline, named owner, limits and review/end date |
| Productive | Full minimum standard with selected Model A/B/C implementation strength |

Actual business dependency matters more than a label. An MVP used for normal decisions or scheduled productive processing is productive. Small audience and short duration are not exemptions from criticality, security or regulatory obligations. Numeric user/time examples in the classification framework are review indicators, not automatic cutoffs.

## Productive model selection

| Model | Meaning |
| --- | --- |
| A — Fabric Native / Lightweight | Low-risk controlled productive delivery; limited concurrency/dependencies; some manual work acceptable |
| B — Managed Team Delivery | Default for normal team-developed productive solutions, regular changes and shared consumers; PR/CI and controlled releases |
| C — Enterprise / Critical | Stronger boundaries for high criticality, separation of duties, regulatory obligations, substantial dependencies or stringent evidence/recovery requirements |

Choose the least complex model that adequately controls risk. Model C normally strengthens B instead of requiring an unrelated delivery technology. Escalation criteria set a minimum; a weaker choice needs an explicit exception under the framework.

## Minimum-standard controls

The source control matrix defines common requirements with stronger model-specific implementation. Do not replace the detailed matrix with this index.

| ID | Topic | ID | Topic |
| --- | --- | --- | --- |
| MS-01 | Ownership | MS-08 | Release validation |
| MS-02 | Source control | MS-09 | Production authorization |
| MS-03 | Change control/traceability | MS-10 | Operational visibility |
| MS-04 | Environment separation | MS-11 | Recovery |
| MS-05 | Reproducible deployment/bootstrap | MS-12 | Security/least privilege |
| MS-06 | Environment configuration | MS-13 | Network/execution prerequisites |
| MS-07 | Identity model | MS-14 | Release evidence |

The workshop should map each control to an exercise, reference explanation or explicit lab limitation. A training coverage map is not productive compliance certification.

## Four state types

- **Code:** versioned definitions, scripts, YAML and configuration references.
- **Deployment:** definitions actually installed in a target workspace.
- **Environment:** connections, identities, permissions, networking and target settings.
- **Runtime:** jobs, data, logs, refreshes and external side effects.

A merge changes code state. A deployment changes installed definitions. Neither proves target configuration or successful execution, and neither guarantees data recovery.

## Source-control wording clarification

After the Working Version 1 matrix was drafted, the phrase “where technically supported” was questioned. The assistant suggested: “Solution definitions and custom code that can be represented in source control must be stored in the approved Git repository. Environment-specific and runtime state are managed separately.”

This is a proposed clarification from the later conversation, not an edit to the preserved guideline. Git should capture source-representable definitions/code; credentials, actual data, execution history and parts of environment state need separate management.
