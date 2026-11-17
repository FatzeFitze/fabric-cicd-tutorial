# Unit 12 pilot notes

Draft prepared 17 November 2026. [Participant lab](../tutorial/section-05-operate-and-reuse/unit-12-shared-deployment-starter/README.md) · [Canonical deployment starter](../../deployment_starter/README.md).

## Local verification

Python 3.12 with PyYAML 6.0.3 parsed all starter and wrapper YAML. A temporary fixture used three real local Git repositories and simulated Fabric reads and writes. It exercised the missing-measure diagnostic, corrected pin and plan ordering, read-only Test preflight, rejection of mismatched validation evidence before writes, creation of the additional report in the Test inventory, same-candidate Prod promotion, and rejection of a changed starter version before writes. The migration follow-up also verified that the composed project check still rejects the Unit 6 notebook-rule regression and rejects a missing report measure independently.

A local fixture called the candidate entry point through the starter's existing hook loader. It accepted the valid candidate and independently rejected a notebook contract regression, the wrong returns measure name and a missing report declaration.

## Live rehearsal

Run **666** on PR **265** failed during Azure Pipelines YAML expansion at `deployment_starter/templates/ci.yml` line 5. That line was the template-root `pool:`. The shared CI and release templates now declare the Ubuntu image on their jobs. The run stopped before the project check. Re-run the PR validation to confirm it reaches that check. [Azure Pipelines job schema](https://learn.microsoft.com/en-us/azure/devops/pipelines/yaml-schema/jobs-job?view=azure-pipelines).

1. Confirm Fabric exports a thin report created over Reporting Dev's model with a sibling-relative `datasetReference.byPath`. Inspect the actual exported measure declaration and adjust the example check if its format differs.
2. Replace the Code YAML at the original CI and Test paths. Verify that the existing required PR build uses the wrapper and can read both dependency repos. Confirm template expansion, artifact transfer between jobs, and the Test service connection authorization. Check that the original notebook rule and the new missing-measure diagnostic both fail the validation job on their faulty inputs.
3. Queue Test preflight, then publish. Check all bound targets, new report inventory and the physical semantic model shown in Reporting Test lineage. Run Tiny Sales and verify **Returned Orders = 2** on the new report.
4. If exercising the separate Prod wrapper, validate pipeline resource selection, reviewed run ID, protected service connection approval and identity, the promoted candidate and starter version, and post-deployment report binding and runtime. Unit 12's hands-on path finishes in Test.

The branch's local simulation uses a publisher substitute. Azure Pipelines template expansion, managed identity login, and actual Fabric item definitions and bindings require the live checks above.
