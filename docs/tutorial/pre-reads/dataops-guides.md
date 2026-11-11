# Our Fabric DataOps guides in brief

**Allow about 8 minutes.** This is a summary of the three internal **Working Version 1** guides used as the workshop baseline.

The guides ask two questions. Has this solution become something the business depends on? If so, what is the simplest operating model that adequately controls its risk? The answers determine how much engineering and operational control the solution needs.

## First decide whether the solution is productive

| Applicability | How to recognize it | What the guides expect |
| --- | --- | --- |
| **Exploration / Sandbox** | Temporary work you can delete without business impact. | An identifiable owner and purpose, an approved workspace, suitable access and data protection, and a review or deletion date. |
| **PoC / Pilot** | A time-bounded evaluation with a decision to make about its future. | An accountable owner, controlled access and data use, source control where appropriate, understood identities and connections, documented limitations, and a review date and decision. |
| **Productive** | Part of normal business operations or a meaningful dependency for decisions, reporting, scheduled processing or another system. | Classify the solution, select an approved operating model, apply the corresponding minimum controls and document approved exceptions. |

A report can become productive as soon as a team relies on it for a recurring decision, even if the project still calls it a pilot. User counts and duration can prompt a review. Business dependency and impact determine the classification. [DataOps Principles & Scope](../../source-guidelines/dataops-principles-and-scope.md).

## Then choose the operating model

The solution owner proposes a classification based on business criticality, delivery complexity, downstream dependencies, data and security sensitivity, and operational and recovery requirements.

| Model | When it fits | What it emphasizes |
| --- | --- | --- |
| **A · Fabric Native / Lightweight** | A productive solution with comparatively low risk across the relevant dimensions and no enterprise escalation trigger. | Traceable changes, separate production, a repeatable promotion process, basic runtime checks and documented recovery. Fabric-native deployment can be sufficient. |
| **B · Managed Team Delivery** | The default for normal productive team-developed solutions. Multiple contributors, regular releases or shared dependencies can make this the appropriate minimum. | Branch and PR controls, CI validation, explicit deployment and runtime identity boundaries, controlled releases, production approval and runtime validation. |
| **C · Enterprise / Critical** | High criticality, significant compliance obligations, required separation of duties, substantial cross-organization dependency, or stringent audit, availability or recovery needs. | Stronger production access and approval boundaries, least privilege, retained evidence, monitoring and recovery tested where required. |

Model A is a governed productive model. Models B and C strengthen the implementation of the same underlying controls. Revisit the classification when the audience, dependencies, data sensitivity or support expectations change. Any weaker control than the classification requires needs an explicit approved exception. [Solution Classification Framework](../../source-guidelines/solution-classification-framework.md).

## What every productive solution needs to work through

| Area | Questions to ask before going live |
| --- | --- |
| **Ownership and source** | Who owns changes and operations? Can we identify the source revision and reconstruct the change? |
| **Environments, deployment and configuration** | Where are changes developed and validated? Can we reproduce a deployment in a fresh environment with the right target settings? |
| **Identities and execution** | Who can deploy? Which identity runs the workload and accesses data? Can the deployment agent reach the target and its dependencies? |
| **Authorization and validation** | Who can authorize production changes? What checks confirm that the deployed solution actually works in the target? |
| **Operations, evidence and recovery** | Who sees a failure and acts on it? What release and run evidence is retained? How do we recover definitions, settings, affected data and external effects where relevant? |

The guides distinguish **code state**, **deployment state**, **environment state** and **runtime state**. For example, a known-good commit helps recover a definition, while restoring overwritten data requires its own recovery action. Use the Fabric Minimum Standard's full control matrix to check the expected implementation for your model or to identify gaps that require an exception. [DataOps Principles & Scope](../../source-guidelines/dataops-principles-and-scope.md) · [Fabric Minimum Standard](../../source-guidelines/fabric-minimum-standard.md).

[Back to the pre-read guide](README.md)
