# DevOps and CI/CD

**Allow about 10 minutes.**

A team changes how an inventory report counts reserved stock. The change takes ten minutes to write. Getting it safely into use takes longer. Someone needs to agree what “available” means, check the result against known cases, release the change to the right environment and know what to do if tomorrow's numbers look wrong.

**DevOps** is the way development and operations work together across that lifecycle. It includes how a team makes changes, shares ownership, delivers releases and learns from running the system. **Application lifecycle management (ALM)** covers the broader management of a solution from planning through retirement. In a data system, the lifecycle also includes data dependencies, data quality, permissions and recovery of affected data. [What is DevOps?](https://learn.microsoft.com/en-us/devops/what-is-devops) · [ALM overview](https://learn.microsoft.com/en-us/power-platform/alm/overview-alm).

## What CI and CD do

| Term | Meaning | Inventory example |
| --- | --- | --- |
| **Continuous integration (CI)** | Integrate small changes frequently and use automated checks to get feedback early. A PR can run the checks before integration. Teams may also check the shared branch after merge. | A test gives the calculation 10 units on hand and 3 reserved. It expects 7 available and flags a change that returns 10. |
| **Continuous delivery (CD)** | Keep a change ready for release through a repeatable process. Production rollout can depend on a deliberate decision or approval. | Take the revision that passed CI, deploy it in Test, verify the report and make that revision available for an approved production release. |
| **Continuous deployment** | A delivery practice where qualifying changes proceed to production automatically after passing the required checks. People also use “CD” for this practice. | A low-risk change can reach production automatically once the required checks pass. |

CI gives the team feedback about a proposed or integrated change. Delivery takes a known version through release steps and records how it performed in the target environment. [Continuous delivery overview](https://learn.microsoft.com/en-us/devops/deliver/what-is-continuous-delivery).

## What happens between a PR and production?

1. **Review and validate the change.** A reviewer checks the business logic and the scope of the diff. Automated checks can verify syntax, configuration and expected results on known inputs.
2. **Choose an exact version.** Record a commit ID or an immutable build artifact. If the solution spans repositories, record the set of revisions that belongs together.
3. **Deploy to a representative Test environment.** Use the same selected version with Test-specific configuration, credentials and data. Check that it connects to the intended resources.
4. **Validate and authorize the release.** Run a targeted functional check, such as comparing the Test report with a known result. Production approval, where used, gives someone a chance to review the evidence and release timing.
5. **Deploy and verify in Prod.** Record what went out, the settings or configuration revision used, who or what performed the deployment, and the outcome. Monitoring and an identified owner help the team respond if a later scheduled run fails.

Teams may call these environments **Dev**, **Test** and **Prod**. Dev is where changes are developed and integrated. Test is where a candidate is exercised with controlled settings and dependencies. Prod serves the real users or processes. Environment boundaries protect those users from work in progress. Exact layouts depend on the system and its risk.

## Why do the extra work?

A reliable workflow takes an upfront investment. Someone has to write representative tests, maintain target configuration, arrange permissions and keep the release process working. Every gate adds time, so it helps to know which failure it can catch.

| Control | What the effort buys |
| --- | --- |
| **Reviewable changes** | A teammate can see that a change to the export also touched an unrelated calculation. |
| **Automated checks** | The same edge cases are checked on every relevant change. A defect can be fixed while the author still has the change in mind. |
| **Repeatable deployment** | The team can apply the same steps to a fresh environment or a later release and see which step failed. |
| **Release history and monitoring** | Support can connect an unexpected result with a release, identify the version and see whether a scheduled run failed or produced a surprising result. |

The investment tends to pay off faster when changes are frequent, several people contribute or downstream users depend on the results. A disposable analysis may need little beyond basic versioning. A recurring export that drives replenishment decisions benefits from known-result tests, a controlled release and a recovery plan. Start from the cost of a mistake and the cost of detecting and fixing it.

## What does a green result actually prove?

A static check can confirm that source parses and a configuration field exists. An integration test can show that the workload reaches the right dependencies. A small **smoke test** after deployment can verify that a critical path runs and returns a sensible result. Each check covers a different failure mode.

Suppose the new inventory job writes incorrect quantities before anyone notices. Releasing a known-good definition can repair future runs. The quantities already written may need to be rebuilt or restored, and a downstream export may need to be regenerated. Keep track of source, deployed definitions, environment settings and runtime effects when planning recovery.

[Back to the pre-read guide](README.md)
