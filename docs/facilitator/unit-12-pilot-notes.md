# Unit 12 pilot notes

Draft prepared 17 November 2026. [Participant lab](../tutorial/section-05-operate-and-reuse/unit-12-shared-deployment-starter/README.md) · [Canonical deployment starter](../../deployment_starter/README.md).

## Local verification

Python 3.12 with PyYAML 6.0.3 parsed all starter and wrapper YAML. A temporary fixture used three real local Git repositories and simulated Fabric reads and writes. It exercised the missing-measure diagnostic, corrected pin and plan ordering, read-only Test preflight, rejection of mismatched validation evidence before writes, creation of the additional report in the Test inventory, same-candidate Prod promotion, and rejection of a changed starter version before writes.

## Live rehearsal

1. Confirm Fabric exports a thin report created over Reporting Dev's model with a sibling-relative `datasetReference.byPath`. Inspect the actual exported measure declaration and adjust the example check if its format differs.
2. Save and queue the CI and Test wrappers in Azure DevOps. Verify template expansion, checkout authorization for both dependency repos, artifact transfer between jobs, and Test service connection authorization. Confirm failed CI and corrected source both produce readable evidence.
3. Queue Test preflight, then publish. Check all bound targets, new report inventory and the physical semantic model shown in Reporting Test lineage. Run Tiny Sales and verify **Returned Orders = 2** on the new report.
4. If exercising the separate Prod wrapper, validate pipeline resource selection, reviewed run ID, protected service connection approval and identity, the promoted candidate and starter version, and post-deployment report binding and runtime. Unit 12's hands-on path finishes in Test.

The branch's local simulation uses a publisher substitute. Azure Pipelines template expansion, managed identity login, and actual Fabric item definitions and bindings require the live checks above.
