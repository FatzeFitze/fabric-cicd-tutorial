# DataOps Principles & Scope

**Status:** Working Version 1  
**Purpose:** Initial standard for approval by project steering and subsequent validation through reference implementations.

## 1. Objective

The Fabric DataOps framework establishes the minimum engineering and operational principles required to develop, deploy and operate productive Microsoft Fabric solutions in a controlled and reproducible manner.

The framework is intentionally **risk- and value-based**.

It does not require every Fabric activity to use the same controls, nor should experimental work carry the governance overhead of a productive business solution.

Instead:

> **DataOps controls must be proportional to solution risk, maturity and business dependency while maintaining an appropriate minimum level of engineering discipline.**

Productive solutions must use an approved DataOps operating model appropriate to their complexity, criticality and operational impact.

---

## 2. Scope

Within the Fabric rollout, DataOps covers:

- source control and change management;
- development and environment strategy;
- continuous integration and technical validation;
- deployment and release management;
- environment-specific configuration;
- deployment, workspace and runtime identities;
- production approval and access boundaries;
- runtime validation;
- monitoring and operational ownership;
- change and release traceability;
- recovery principles.

DataOps therefore includes CI/CD but is not limited to CI/CD.

The framework defines the engineering lifecycle and its interfaces to security, platform administration, Data Governance and operations. It does not replace those disciplines.

---

## 3. Applicability of the DataOps standard

Not every Fabric asset must immediately comply with the full productive DataOps standard.

Three applicability states are distinguished.

### Exploration / Sandbox

Typical examples:

- individual experimentation;
- technology exploration;
- training or learning;
- short-lived prototypes;
- disposable analyses.

These activities are outside the full DataOps standard if they remain genuinely non-productive.

Typical characteristics are:

- one or very few contributors;
- small, known internal audience;
- short expected lifetime;
- no productive downstream dependency;
- no business process relies on continued availability or correctness;
- no material regulatory or compliance consequence;
- the solution can be deleted without business impact.

Indicative guideposts such as **≤10 users** or **≤3 months expected lifetime** may help identify this category, but they are not hard classification criteria.

A minimum hygiene baseline still applies:

- identifiable owner;
- known purpose;
- use of an approved workspace/environment;
- appropriate access and data protection;
- defined review or deletion date.

Exploration must not become unmanaged production through continued use.

---

### PoC / Pilot

A Proof of Concept or pilot validates whether a solution, architecture or business capability is viable before full productive adoption.

Reduced DataOps controls may be appropriate.

A PoC or pilot does not necessarily require:

- full DEV/TEST/PROD separation;
- complete CI/CD automation;
- independent production approval;
- full operational monitoring;
- production-grade recovery procedures.

It should nevertheless have:

- an accountable owner;
- source control where meaningful;
- appropriate access and security controls;
- understood identities and connections;
- separation from established productive solutions where appropriate;
- documented limitations and assumptions;
- a planned end date or review point;
- a defined outcome: discontinue, extend, or transition into productive operation.

Indicative guideposts such as **≤25 pilot users** or **≤6 months duration** may be used as review triggers, but should not themselves determine whether a solution is productive.

---

### Productive Solution

The full DataOps framework applies when a Fabric solution is used as part of normal business operation or creates meaningful business dependency.

This includes solutions used repeatedly for:

- operational processes;
- financial or management decisions;
- regular reporting;
- automated data processing;
- shared data products;
- downstream system consumption.

Once a solution becomes productive, it must:

1. be classified using the Solution Classification Framework;
2. use an approved DataOps operating model;
3. comply with the Fabric Minimum Standard;
4. document any approved exceptions.

---

## 4. Mandatory transition to the productive standard

The label attached to an initiative does not determine its governance level.

A solution described as a “PoC”, “pilot” or “MVP” must transition into the productive framework when meaningful business dependency exists.

Typical triggers include:

- users rely on the solution for recurring business activities or decisions;
- another productive solution consumes its output;
- unattended or scheduled processing becomes part of normal operations;
- failure or incorrect results create meaningful business impact;
- compliance, regulatory or legal consequences become relevant;
- sensitive data introduces additional control requirements;
- continued availability is expected rather than optional;
- the solution is intended to remain in operation beyond its evaluation phase.

> **Productive use is determined by actual dependency and risk, not by project terminology.**

---

## 5. Architectural state model

Fabric solutions must distinguish four types of state:

| State | Examples |
|---|---|
| **Code state** | Git branches, commits, Fabric definitions, scripts, pipeline definitions |
| **Deployment state** | Definitions currently deployed or synchronized into a Fabric workspace |
| **Environment state** | Connections, permissions, identities, configuration and environment-specific settings |
| **Runtime state** | Executions, data, tables, logs, history and external side effects |

These states are related but independent.

A Git merge changes code state. It does not by itself deploy Fabric resources.

A successful deployment changes deployment state. It does not prove that environment configuration or runtime execution is correct.

---

## 6. DataOps principles

### Risk-based controls

Controls increase with solution maturity, complexity, criticality and business dependency.

Governance should reduce material risk without introducing unnecessary delivery overhead.

### Source-controlled change

Deployable solution definitions and custom code must be traceable through approved source control wherever technically supported.

### Reproducible deployment

Productive environments must be reproducible from controlled definitions and configuration. Normal operation must not depend on manually rebuilding solutions.

### Environment isolation

Development activity must not unintentionally modify productive deployment, configuration or runtime state.

### Explicit identity boundaries

Identity must be designed according to purpose.

Relevant concerns may include:

- developer identity;
- CI/CD execution identity;
- deployment identity;
- Fabric workspace identity;
- runtime identity;
- downstream data-access identity.

These concepts must not automatically be collapsed into one identity.

A Fabric workspace identity is primarily a workspace-scoped runtime/data-access capability and must not be assumed to replace external deployment identities or all other non-human identities.

### Controlled production change

Productive changes must be deliberate, authorized and traceable.

Approval and separation-of-duty requirements increase with solution criticality.

### Deployment requires validation

Successful deployment is not sufficient proof of a successful release.

Appropriate post-deployment or runtime validation must be performed.

### Operability

Every productive solution must have defined ownership and an understood operational response when important processing fails.

### Recovery is multi-layered

Definition recovery, environment recovery, runtime/data recovery and recovery from external side effects are different concerns and must be treated accordingly.

---

## 7. Framework lifecycle

This document represents the initial baseline.

It should be reviewed when:

- significant Fabric platform capabilities or limitations change;
- reference implementations reveal that a principle is impractical or incomplete;
- incidents expose a control gap;
- recurring exceptions indicate that the framework does not match actual solution patterns;
- applicability rules repeatedly misclassify experimental or productive solutions;
- a periodic architecture review is performed.

Minor clarifications may be incorporated into the current version.

Changes that materially alter scope, mandatory responsibilities or control expectations should result in a new major version and steering approval.

The standard should evolve from **validated operating experience**, not from theoretical completeness.
