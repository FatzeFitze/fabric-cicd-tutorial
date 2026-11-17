# From Tiny Sales to production

Finance needs the sales report each morning. Orders now come from an upstream system, and a missing or duplicated batch could change a decision. Use this scenario to decide which checks belong in your release process and which belong in daily operation. Start with the impact of an error, the people who depend on the result, and the time you have to recover. Use that assessment to choose the operating model and its controls. [Solution Classification Framework](../../source-guidelines/solution-classification-framework.md) · [Fabric Minimum Standard](../../source-guidelines/fabric-minimum-standard.md#minimum-standard-by-operating-model).

## Choose what to verify

| Check | What you practiced in Tiny Sales | An example for a real project |
| --- | --- | --- |
| **Static checks in CI** | The notebook source check and release preview caught a deliberate source defect and a conflicting workspace mapping. | Check configuration types, required fields and dependency declarations while reviewing the PR. Return an error that identifies the file and setting to fix. |
| **Unit tests** | You reviewed the expected returned-order result and later ran assertions over a fixed dataset in Fabric. | Test the revenue calculation in isolation with small inputs. Include a completed and a returned order, and assert gross and recognized revenue separately. Run it in CI so the author gets feedback before deployment. |
| **Integration tests** | Live preflight used the managed identity to inspect the target. The workload used in-memory fixtures as its sales input. | From Test, read a representative batch through the real connector using the intended runtime and data-access identities. Verify the network path, permissions and source schema so you can diagnose a failure at the system boundary. |
| **Runtime and data-quality checks** | You manually ran the Fabric pipeline and smoke notebook, then checked the persisted table and report. | Automate a smoke run after deployment and check the report or model against a known result. On regular loads, check for duplicate order IDs, missing input batches and freshness against Finance's deadline. Define which failures should stop publication and which should alert an owner. |

The Model B column of **MS-08** calls for automated technical and runtime validation in Test and after Prod deployment. The workshop's manual checks give you an example of the evidence such checks can produce. Link results to the exact released revisions and target, so reviewers can tell which candidate passed. [Static validation](static-fabric-validation.md) · [Release manifests](release-manifests.md) · [Fabric Minimum Standard](../../source-guidelines/fabric-minimum-standard.md#minimum-standard-by-operating-model).

## Decide how to run and recover it

- **Access and approval.** Name who can change the source or environment settings, approve a release, and operate the workload. Compare the broad training workspace roles with the grants those roles need in your project. Check the agent-to-Fabric path and the workload-to-source path separately.
- **Operational ownership.** Assign someone to receive failed-run and stale-data alerts. Give them the run link, the affected dataset and a way to tell whether Finance is seeing the current batch.
- **Rebuild and recovery.** The workshop seeds Test and Prod. The Test recovery lab rehearses a configuration fix caught before publishing. For a real project, establish how you would bootstrap a fresh target and how you would inspect a partial publish. Decide how to restore definitions and bindings, and whether to replay a batch, restore data or reconcile external side effects. Check whether replay can create duplicates.

Pick one likely failure. Describe where you would catch it, what evidence the check would produce, and who would act on the result. For example, a missing batch could trigger a freshness alert before Finance opens the report. The support owner can then inspect the last successful batch and decide whether a replay is safe.

For a workload that accumulates history, consider what a release may write, how to test at realistic scale, and how to restore or replay data. [Looking ahead — protecting historical data](persisted-data-in-production.md).

[Back to the closing recap](../closing-recap.md) · [Tutorial index](../README.md)
