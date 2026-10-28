# Enterprise platform context

## Two unrelated uses of A/B naming

Do not confuse **DataOps Models A/B/C** with **g-IT Target A/Target B**.

- DataOps models classify required control strength for a solution.
- g-IT targets describe who provides and operates platform capabilities.

A solution can use Model B controls on either platform-service target.

## g-IT enablement proposals

The 8 October 2026 discussion and subsequent target-picture drafts considered:

| Area | Target A — Coordinated g-IT service | Target B — Minimum g-IT enablement |
| --- | --- | --- |
| Organization/projects | Central governance and request-based project provisioning | g-IT supplies organizations; divisions create/manage projects within delegated authority |
| Identities | Requestable deployment identities/access | Divisions create identities/federation in an approved Azure scope |
| Repos/pipelines | Teams own solution automation | Teams own solution automation |
| Agents | Defined central service | Minimum agreed hosting/connectivity with explicit operating split |
| Fabric privileged setup | Fulfilment process or bounded delegation | Delegation plus a small residual request process |

A proposed split in Target B had g-IT own hosts/OS/networking and divisions own agent software/tooling. It was explicitly a proposal, not an agreement. Minimum central work transfers effort and accountability to divisions; it does not remove total work.

The organizer's later email proposal favored starting with Target B while evaluating Target A in parallel. The starter would include Azure DevOps organization/admin authority, an Azure identity-management scope/subscription arrangement, billing and access to network-connected agents for private Fabric. This is the organizer's proposed direction, not proof of g-IT approval or availability.

Possible future movement away from Azure DevOps was the organizer's strategic expectation, not a confirmed platform roadmap. Azure DevOps remains the workshop requirement.

## Architectural distinctions to retain

- Azure Pipelines orchestrates deployment jobs; Fabric executes solution workloads. An agent does not run the whole Fabric workload.
- Azure Pipelines and native Fabric Deployment pipelines are different products.
- Interactive Fabric Git integration, agent-driven API deployment and native promotion are distinct integration paths.
- Identity federation configuration, Azure identity-management rights and Fabric authorization are separate permission domains.
- Human authoring identity, DevOps job identity, deployment identity, agent-host account, workspace identity and runtime connection/data-access identity have separate purposes.
- Proposed private-only baseline: agent checks out an approved revision, authenticates with a federated deployment identity and calls supported Fabric APIs over validated connectivity. Exact API/item/identity support needs proof.
- Creating identities is different from granting target access. A generic Contributor assumption is insufficient for every provisioning/admin operation.

Organization count and service centralization are separate decisions. Production approvers, protected resources, agent trust/isolation, onboarding, support, costs and retirement all need explicit owners.

## Relationship to the workshop

The workshop uses public endpoints and participant admins. It can demonstrate the release workflow while explaining private-network execution and independently governed production capability as enterprise extensions. Do not claim it validates the enterprise network or final productive permission model.

The enterprise role split into code/data/reporting workspaces is confirmed in principle. The workshop must still prove item placement, cross-workspace bindings, runtime access and environment isolation on its selected sample.
