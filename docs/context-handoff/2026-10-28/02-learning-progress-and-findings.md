# Learning progress and architecture findings

## Current learning state

The earlier tutorial's Sections 1–3 were reported completed. Section 3 closed on **27 October 2026**, with six units. Section 4 is parked to prioritize the workshop. Administration/governance topics were suggested for Section 4, but that suggestion is not an active delivery commitment.

The exact Section 1/2 curricula and complete Section 3 source code were not available in this export. Do not invent their detailed unit histories.

## Section 3 release architecture

The closing conversation describes this completed path:

```text
feature/* -> protected dev -> TEST deployment -> TEST runtime validation
          -> release candidate -> protected main -> Production approval
          -> Production UAMI / WIF -> PROD deployment
          -> PROD runtime validation -> governed forward recovery
```

UAMI means user-assigned managed identity; WIF means workload identity federation. The final architecture used separate non-production and production identities. `fabric-cicd` deployed definitions. Azure DevOps service connections, Environments and checks formed part of the control setup.

The recorded Production identity scope was no DEV/TEST access and Contributor on PROD. The Production service connection was described as WIF-backed, restricted to the Production pipeline, and protected with main-branch/branch-protection checks and approval. These are historical lab configuration statements, not universally sufficient Fabric permissions.

The organizer reported that bindings, deployment and identity use worked, and later confirmed that the final results worked as expected. The assistant closed the section on that basis. Raw manifests, tenant configuration and implementation were not independently inspected during this handoff.

## Findings to carry forward

### Reviewed content must match tested and released content

The earlier release correlated the TEST candidate and protected `main` through **repository tree hashes**. Merge commits can have different commit IDs while representing identical content. Keep both source provenance and content correlation in the evidence chain.

The closing design joined candidate, release plan, deployment and runtime evidence to the same tree and intended PROD workspace. Final success status was `PROD_RUNTIME_VALIDATED`, rather than merely deployment succeeded.

### Deployment success is separate from runtime success

The lab graph was target-local: Data Pipeline -> Notebook -> Lakehouse, plus a Variable Library. The release invoked the Fabric pipeline, polled execution, inspected activity evidence and parsed the notebook result. It also checked the audit row and environment identity in PROD.

Historical deterministic expectations were 30 raw/curated/aggregate rows, quantity 330, sales amount 45905.0, dates 2026-01-01 through 2026-01-10, and `environment_name = PROD`. These belong to the old lab; a new sales sample needs its own approved assertions.

The historical items were `lh_cicd_lab`, `nb_01_seed_and_transform_cicd_lab`, `pl_01_run_cicd_lab_transform` and `vl_cicd_lab_config`. Names are reference context, not required toolkit constants.

### Deployment identity does not establish all runtime identities

Authentication of the external Job API caller does not by itself prove the identity used by downstream notebook/data-source access. Runtime context, workspace identity, connections and source authorization need their own validation. Variable Library environment selection was also part of the observed configuration/runtime boundary.

### Protect the complete release window

The final Production stage included deployment, runtime validation and final evidence under one protected window. An Environment exclusive lock and `lockBehavior: runLatest` were added to control overlapping releases. Revalidate queue behavior when adopting that pattern; choose the desired policy for queued releases explicitly.

### Merge strategy affected reconciliation

A reconciliation merge completed using squash preserved files but discarded needed ancestry, leaving a `dev` -> `main` conflict. The old tutorial adopted Basic merge/no-fast-forward on both long-lived branches.

Preserve this lesson when retaining that branch model. Do not automatically impose the old two-long-lived-branch design on the workshop: the new plan prefers feature branches plus one integration branch unless experiments show a need for more.

### Recovery is a governed change

A harmless temporary notebook marker was introduced, then removed through a fresh branch, review, TEST validation and PROD release. This demonstrated forward recovery without direct PROD editing or a deliberate destructive data defect.

The earlier evidence filenames included `fabric-release-candidate.json`, `fabric-prod-release-plan.json`, `fabric-prod-deployment.json`, `fabric-prod-runtime-validation.json` and `fabric-prod-release.json`. The temporary marker was `S3_U06_FORWARD_RECOVERY_DRILL_V1`; the permanent marker was `S3_U06_PROD_RUNTIME_VALIDATION_V1`.

## Transfer limits

Historical success covered the old sample and its environment. It does not prove the new separated code/data/reporting topology, report/model compatibility, all managed-identity operations, private connectivity, arbitrary item types, data rollback or production-grade enforcement. Reuse the lessons and inspect the source; validate the workshop setup separately.
