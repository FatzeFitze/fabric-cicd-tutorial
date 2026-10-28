# Solution Classification Framework

**Status:** Working Version 1  
**Purpose:** Determine whether the productive DataOps framework applies and, where applicable, which minimum operating model is required.

## 1. Classification principle

Classification is performed in two stages:

```text
Gate 0 — Applicability
Is the solution exploratory, a PoC/pilot, or productive?
        ↓
If productive:
        ↓
Gate 1 — Operating Model
Model A, B or C?
```

This separation prevents small experiments from being subjected to unnecessary production controls while ensuring that genuinely productive solutions cannot avoid governance merely by being called a prototype or MVP.

---

## 2. Gate 0 — Applicability assessment

### Exploration / Sandbox

The full DataOps standard does not apply where the activity remains:

- temporary and disposable;
- non-critical;
- without productive downstream dependencies;
- without meaningful business reliance;
- within approved security and data-handling boundaries.

Only the basic hygiene requirements defined in the DataOps Principles & Scope apply.

---

### PoC / Pilot

A reduced DataOps baseline applies where a solution is being evaluated but has not yet become an established business dependency.

The solution must at least have:

- an owner;
- appropriate security and access;
- controlled use of data;
- source control where appropriate;
- understood identities and connections;
- documented limitations;
- an expected end/review date;
- a documented decision before transition to normal productive use.

A PoC or pilot may deliberately operate without the full productive environment, CI/CD, monitoring and recovery model.

---

### Productive

The full DataOps Minimum Standard applies once the solution becomes part of normal business operation or creates meaningful dependency.

Examples of productive-use triggers include:

- recurring business usage;
- regular management or operational decision support;
- scheduled or unattended productive processing;
- downstream productive consumers;
- significant consequence of incorrect output;
- meaningful availability expectation;
- compliance/regulatory implications.

The project label is not decisive.

An MVP used by the business in normal operation is treated as productive.

---

## 3. Productive operating models

Every productive Fabric solution must be assigned one of three approved operating models:

- **Model A — Fabric Native / Lightweight**
- **Model B — Managed Team Delivery**
- **Model C — Enterprise / Critical**

The objective is not to reward solutions for reaching Model C.

> **The correct model is the least complex operating model that adequately controls the solution's risk.**

The solution owner proposes the classification.

Mandatory escalation criteria define the minimum acceptable model. Selection of a weaker model requires an explicitly approved exception.

---

## 4. Classification dimensions

### Business criticality

Consider:

- What happens if the solution is unavailable?
- What happens if it produces incorrect results?
- Does it support an important operational or financial process?
- How many users, business units or dependent processes rely on it?
- Could failure or incorrect results create compliance, regulatory or legal consequences?

### Delivery complexity

Consider:

- How many developers contribute?
- Is parallel development expected?
- Do multiple teams contribute?
- How frequently is the solution changed and released?

### Dependency footprint

Consider:

- Is the solution isolated or a shared data product?
- How many downstream solutions consume its outputs?
- Would an incompatible change affect other teams or systems?

### Data and security sensitivity

Consider:

- Does the solution process confidential, personal or otherwise restricted information?
- Are specific security controls required?
- Are private-network or restricted-access patterns required?

Security classification itself should come from the relevant security and Data Governance framework rather than being redefined by DataOps.

### Operational requirements

Consider:

- How quickly must failures be detected?
- What availability is required?
- How difficult is recovery?
- Are defined recovery-time or recovery-point expectations required?
- Is formal production support required?

---

## 5. Model selection

### Model A — Fabric Native / Lightweight

Model A may be selected for productive solutions where **all relevant risk dimensions remain comparatively low** and no Model C escalation trigger exists.

Typical characteristics:

- one or very few developers;
- limited development concurrency;
- low-to-moderate business impact;
- limited downstream dependency;
- relatively infrequent releases;
- no strong separation-of-duty requirement;
- some manual deployment or recovery activity is acceptable.

Model A remains a governed productive DataOps model.

It must not be confused with the Exploration/Sandbox exemption.

---

### Model B — Managed Team Delivery

Model B is the **default model for normal productive team-developed solutions**.

Typical triggers include:

- multiple developers;
- parallel development;
- regular release activity;
- important business usage;
- shared datasets or downstream consumers;
- need for automated CI validation;
- controlled release orchestration;
- need for stronger deployment traceability.

Model B introduces formal branch/PR controls, CI validation, explicit deployment identity, controlled release execution and runtime validation.

---

### Model C — Enterprise / Critical

Model C is required where stronger enterprise controls are justified.

Hard escalation triggers should include at least:

- high business criticality;
- significant regulatory or compliance obligations affecting delivery controls;
- required separation of duties;
- substantial cross-organizational or shared-platform dependency;
- stringent audit/evidence requirements;
- stringent availability or recovery requirements.

Model C normally extends Model B rather than introducing an unrelated delivery technology.

Its distinguishing feature is stronger **control boundaries**, for example workload identities, independently controlled production approvals, least privilege, stronger validation, monitoring, evidence retention and recovery procedures.

---

## 6. Decision logic

Version 1 deliberately avoids a numerical scoring model.

The proposed rule is:

```text
Gate 0

Disposable exploration
        → Sandbox / basic hygiene

Temporary controlled evaluation
        → PoC / reduced baseline

Meaningful business dependency
        → Productive
             ↓

Gate 1

All relevant risk dimensions low
and no enterprise escalation trigger
        → Model A permitted

Normal productive team solution
or meaningful collaboration/dependency complexity
        → Model B

Enterprise escalation trigger present
        → Model C
```

User counts and duration may be used as **review indicators**, not as hard governance boundaries.

For example:

- >10 regular users should trigger a review of an Exploration classification;
- >25 pilot users should trigger a review of a PoC classification;
- >3 months may trigger an Exploration review;
- >6 months may trigger a PoC review.

Crossing these values does not automatically make a solution productive. Equally, staying below them does not make a business-critical solution non-productive.

---

## 7. Classification record

Every productive solution should record at minimum:

```text
Solution:
Solution owner:
Classification date:

Applicability:
  Exploration / PoC-Pilot / Productive

Business criticality:
Delivery complexity:
Dependency footprint:
Data/security sensitivity:
Operational requirements:

Minimum required model:
Selected model:

Escalation triggers:
Exceptions / rationale:
Approver where required:
```

For Exploration and PoC/Pilot solutions, the record may be reduced to:

```text
Owner:
Purpose:
Applicability:
Expected review/end date:
Known limitations:
Data/security constraints:
Reason full productive standard does not yet apply:
```

---

## 8. Reclassification

Classification is not permanent.

It must be reconsidered when the solution changes materially.

Typical triggers include:

- a prototype becomes regularly used;
- a pilot extends significantly beyond its planned duration;
- additional developers or teams join;
- a local solution becomes a shared data product;
- sensitive or regulated data is introduced;
- downstream dependencies increase;
- scheduled productive processing is introduced;
- operational expectations increase.

Moving:

```text
Exploration → PoC → Productive
```

or:

```text
Model A → Model B → Model C
```

should be treated as normal solution evolution rather than architectural failure.

---

## 9. Framework lifecycle

Version 1 should initially be validated against real project classifications.

The framework should be revised if:

- many projects repeatedly require exceptions;
- Exploration/PoC/Productive boundaries prove ambiguous;
- Model A/B/C boundaries prove ambiguous;
- temporary solutions routinely become unmanaged production;
- materially different solution patterns emerge;
- operational incidents show systematic under-classification.

The preferred evolution is to clarify **decision rules and escalation triggers**, not to continuously add scoring dimensions.

A numerical scoring system should only be introduced if practical experience shows that the simpler model is insufficient.
