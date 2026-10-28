# Fabric Minimum Standard

**Status:** Working Version 1  
**Purpose:** Define the mandatory minimum engineering controls for productive Microsoft Fabric solutions and the required implementation level for each approved DataOps operating model.

## Applicability

The full Fabric Minimum Standard applies to solutions classified as **Productive** under the Solution Classification Framework.

Exploration/Sandbox activities are subject to the basic hygiene requirements defined in the DataOps Principles & Scope.

PoCs and pilots may use the reduced baseline defined there while they remain genuinely evaluative and have not created meaningful productive business dependency.

Once productive-use criteria are reached, the solution must be classified as Model A, B or C and comply with the corresponding requirements below.

---

## Minimum Standard by operating model

| Control | Purpose / justification | Model A — Fabric Native / Lightweight | Model B — Managed Team Delivery | Model C — Enterprise / Critical |
|---|---|---|---|---|
| **MS-01 Ownership** | Productive solutions require clear accountability for change and operation. | Solution owner and technical/operational responsibility identified. | Named solution, technical and operational owners with defined responsibilities. | Formal ownership and support responsibilities; escalation and service responsibilities documented where relevant. |
| **MS-02 Source control** | Productive definitions must have a controlled and traceable source state. | Deployable definitions and custom code in approved Git where technically supported. | Git required; development follows defined branch and integration workflow. | Same as B, with stronger repository governance and protected release state. |
| **MS-03 Change control & traceability** | Production changes must be reconstructable and attributable. | Changes traceable to a source state; lightweight review acceptable. | Feature branch + pull request + review expected; automated validation before integration. | Formal PR/review controls, stronger separation of duties and additional mandatory gates where required. |
| **MS-04 Environment separation** | Development must not unintentionally change productive state. | Productive environment separated from normal development. Separate TEST based on risk. | DEV / TEST / PROD expected reference topology. | DEV / TEST / PROD or stricter topology; additional isolation where security or organizational boundaries require it. |
| **MS-05 Reproducible deployment** | Productive environments must be rebuildable and changes repeatable. | Documented repeatable deployment/promotion process; Fabric-native deployment acceptable. Must support bootstrap into a new/recovered environment. | Automated or centrally orchestrated deployment expected. Bootstrap/redeployment path validated. | Fully controlled repeatable deployment through governed automation; rebuild/recovery procedure tested where critical. |
| **MS-06 Environment configuration** | Code and target-specific configuration are different state. | Environment-specific settings identified and documented. | Configuration separated from deployable definitions and managed per environment. | Governed configuration model with controlled changes, stronger auditability and recovery expectations. |
| **MS-07 Identity model** | Deployment, runtime and data access require explicit identity boundaries. | Relevant human/workspace/runtime identities identified. Personal deployment may be acceptable where risk permits. | CI/CD execution, deployment identity, runtime identity and data-access identity explicitly separated. Non-human deployment identity preferred. | Approved workload identities required where supported; least privilege and separation between non-production and production identities expected. |
| **MS-08 Release validation** | Successful deployment does not prove successful operation. | Basic post-deployment smoke or functional validation. | Automated technical/runtime validation in TEST and after PROD deployment. | Stronger validation gates appropriate to business risk, potentially including data-quality, integration and negative-path checks. |
| **MS-09 Production authorization** | Productive change must be deliberate and authorized. | Explicit controlled production promotion; same developer may perform it where risk permits. | Production approval required and separated from normal development workflow. | Independent approval/separation of duties required; production capability protected independently from ordinary pipeline code where appropriate. |
| **MS-10 Operational visibility** | Failures must be observable. | Basic execution history or status sufficient for support needs. | Defined monitoring of important jobs/processes; failures actionable by an owner. | Proactive monitoring/alerting, defined support expectations and retained operational evidence appropriate to criticality. |
| **MS-11 Recovery** | Source rollback does not restore every kind of state. | Documented approach for recovering from an incorrect deployment. | Definition, configuration and relevant runtime recovery considered explicitly. | Tested recovery procedures where required; data and external-side-effect recovery included where applicable. |
| **MS-12 Security & least privilege** | Convenience should not drive excessive privileges. | Access limited to what the small-team operating model reasonably requires. | Developer, deployment and runtime permissions explicitly separated where applicable. | Strong least privilege, separation of duties and independently governed production privileges required. |
| **MS-13 Network & execution prerequisites** | CI/CD must actually be able to reach Fabric and its dependencies. | Public/native connectivity may be sufficient where allowed. | Required network path for deployment agents and dependent systems explicitly validated. | Private/restricted connectivity incorporated into the delivery architecture; network-connected agents and DNS/routing controls validated where required. |
| **MS-14 Release evidence** | Teams must be able to determine what was released and validated. | Basic deployment/change history retained. | Release evidence should correlate source state, deployment and validation result. | Centrally retained auditable evidence with retention appropriate to regulatory/operational requirements. |

---

## Interpretation of the model columns

The table defines the **minimum expected implementation strength**, not three completely separate standards.

The progression should generally be understood as:

```text
Model A
Minimum controlled productive delivery
        ↓
Model B
Repeatable team delivery with CI/CD and explicit control boundaries
        ↓
Model C
Enterprise-strength separation, governance, evidence and recovery
```

Model B and Model C inherit the underlying requirement from the preceding model and strengthen its implementation.

Projects may implement controls above their required model where useful.

They must not implement a weaker control than required by their classification unless an explicit exception is approved.

---

## Minimum readiness check

Before productive operation, every solution must be able to answer:

```text
[ ] Applicability assessed
[ ] Productive operating model selected
[ ] Ownership assigned
[ ] Source-control approach established
[ ] Change-control approach established
[ ] Environment topology defined
[ ] Deployment process defined
[ ] Fresh-environment/bootstrap path understood
[ ] Environment-specific configuration identified
[ ] Deployment identity defined
[ ] Runtime/data-access identities defined
[ ] Release validation defined
[ ] Production authorization defined
[ ] Operational visibility defined
[ ] Recovery approach defined
[ ] Network/execution prerequisites validated
[ ] Release evidence requirements defined
```

Where a requirement cannot currently be fulfilled because of a platform or organizational constraint, the exception, associated risk and compensating control must be documented explicitly.

---

## Transition from PoC / Pilot to productive operation

Before a PoC or pilot enters productive use, it must:

1. complete the productive classification;
2. select Model A, B or C;
3. assess itself against the corresponding Minimum Standard column;
4. close or formally accept identified gaps;
5. establish productive ownership and operating responsibilities.

Existing prototype implementation may be reused.

The objective is not to force a rebuild, but to prevent experimental shortcuts from silently becoming permanent production architecture.

---

## Standard lifecycle

The Minimum Standard should remain deliberately compact.

The control matrix should be reviewed when:

- reference implementations demonstrate that a requirement is impractical or insufficient;
- repeated exceptions appear;
- security, audit or regulatory requirements change;
- incidents expose a systemic gap;
- Fabric capabilities materially change.

Changes should normally take one of two forms:

- **clarification** — refine wording or examples without materially changing obligations;
- **new control requirement** — materially increase expectations and therefore require steering approval and an appropriate transition period.

Best practices that are useful but not mandatory should remain outside the Minimum Standard and be maintained in implementation guidance or reference architectures.
