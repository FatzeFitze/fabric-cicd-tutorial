# Initial codebase: salvage assessment

Date: 28 October 2026. Scope: source inventory, targeted static review and local definition/configuration validation. This is not an exhaustive audit or a cloud feasibility result.

## Source and placement

The organizer supplied the test project's ZIP and delegated reuse/placement choices. The [dated reference](../../reference/initial-lab/2026-10-28/README.md) preserves the source layout with neutral environment examples. Its [manifest](../../reference/initial-lab/2026-10-28/IMPORT-MANIFEST.json) records archive and file checksums. Original extracted source remains in ignored `work/`.

Inventory: four Fabric items (Lakehouse, Notebook, DataPipeline, VariableLibrary), four pipeline YAML files, fourteen top-level Python scripts, four archived scripts, one notebook source, a networking PowerShell helper, two configuration files and a requirements file. Six compiled cache files were excluded. There are no reporting assets, raw release-result artifacts or Git history.

## Reuse map

| Source | Salvage decision | Destination after adaptation and tests |
| --- | --- | --- |
| `tutorial_config.py` | Keep strict loading, nonempty-name/separation checks, config hashing and evidence. Replace its fixed one-workspace-per-environment schema. | Toolkit configuration and examples |
| `validate_fabric_repo.py` | Keep parsing, logical-ID consistency and dependency checks. Replace fixed names/directories and source-string assertions with configurable and sample-specific rules. | Offline validator and sample checks |
| `fabric_test_deploy.py`, `fabric_prod_deploy.py` | Keep thin fabric-cicd wrapping, isolated staging, version recording and inventory comparison. Consolidate duplication; add clean bootstrap and role routing. | Shared deployment component |
| TEST/PROD runtime validators | Keep polling, activity/result extraction and run correlation. Separate transport from fixed business metrics and environment names. | Runtime runner and assertion contract |
| Candidate, PROD preflight and finalization scripts | Keep source/configuration/deployment/runtime correlation; simplify the Model B contract. | Release evidence and optional stronger-control examples |
| `fabric_identity_preflight.py` | Keep diagnostics for the identity actually presented. Token-claim inspection is not independent authorization proof or proof of runtime identity. | Identity diagnostic/facilitator reference |
| Shared functions in `fabric_nonprod_release.py` | Extract neutral Git, REST, operation and evidence utilities. Current scripts import this older orchestrator to share helpers; remove that coupling. | Small common modules |
| Native Deployment pipeline preflight/deploy | Keep stage/workspace mapping and verification examples; UI promotion does not require all this automation. | Optional native adapter/reference |
| CI YAML | Keep separate syntax/configuration/definition checks. Adapt paths and branch-policy setup. | Minimal participant CI template |
| Nonprod/prod release YAML | Keep explicit deployment/runtime steps and evidence publication. Consolidate repeated setup and old branch/candidate-run assumptions. | Model B templates |
| Four Fabric definitions | Use as the first concrete feasibility sample: deterministic data, environment markers, audit and structured notebook results. Prove role split before promotion. | Sample/checkpoints |
| Private probe and YAML | Reference for optional enterprise explanation, outside mandatory public-endpoint labs and unit-test discovery. | Reference only |
| Public-inbound helper | Retain as networking history; do not run or include in participant provisioning. | Reference only |
| Archived release automation | Preserve context without reviving competing deployment engines. | Archived reference only |

These choices do not change the minimum standard or settle pending architecture decisions. No code was promoted into active `toolkit/`, `sample/` or workshop pipeline directories during import.

## Concrete adaptation gaps

1. **TEST clean bootstrap is blocked.** Before publishing, `fabric_test_deploy.py` resolves the complete expected target inventory. `expected_item_inventory` requires all four items to exist, so an empty workspace fails before `publish_all_items`. Apply ID-stability checks only to previously existing items. Inspect the PROD bootstrap boundary too.
2. **Topology is one workspace per environment.** Configuration contains Dev/Test/Prod names and the wrappers publish the same four items to one target. Add role-by-environment mappings, binding resolution, ordering and target checks for the workshop.
3. **Offline validation covers only part of the managed inventory.** It hardcodes three items/one activity and excludes VariableLibrary from its expected-item validation. Notebook string checks do not prove business behavior. `EXPECTED_AGGREGATE_COLUMNS` is duplicated.
4. **CI trigger paths omit `99_admin/`.** A variable-library-only change can be missed by that push-trigger configuration. Validate Azure Repos PR build policies separately.
5. **Git provenance is tied to the current remote head.** `validate_git_state` fetches the expected branch and compares its current state to the checkout. A branch advancing can reject a valid queued snapshot. Decide immutable release semantics explicitly while retaining authenticity checks.
6. **Transport needs review before generic reuse.** Inspected workspace/item-list helpers consume one page. Add pagination. The shared request helper retries 429/5xx regardless of HTTP method; assess operation-specific retry/idempotency behavior for state-changing calls, bounded server delays and total deadlines.
7. **Business expectations are duplicated in TEST/PROD validators.** Separate the job/result handling from sample metrics. Environment marker checks alone do not establish which identity accessed which physical resource.
8. **External controls and execution evidence are absent.** Service connections, environments/checks, agent trust and permissions are referenced, but the ZIP does not prove their configuration or enforcement.

## Extraction sequence

1. Prove existing-target deployment versus clean-target bootstrap with the retained sample in a disposable setup. Adapt code separately from this reference.
2. Prove notebook-to-separate-workspace-lakehouse and pipeline/variable-library relationships before expanding dependency configuration.
3. Extract one configuration/inventory contract and one parameterized deployment wrapper, preserving source/configuration/item identity in evidence.
4. Extract runtime handling with sample assertions and connect minimal Model B YAML.
5. Verify the empty-learner-repository path and second-example reuse before calling the starter workshop-ready.

V01 now has an initial source assessment. Deeper extraction, controlled cloud experiments, report/model support and a timed pilot remain unfinished. The workshop keeps A/B hands-on scope; stronger Model C controls/private networking remain explanation topics.

## Verification performed

- All 19 Python sources parsed without executing them; all 13 source JSON/.platform files parsed.
- The inspected offline validator and configuration lookup passed against both original and adjusted snapshots.
- A limited literal credential-pattern scan found no matches. Environment examples were neutralized in eight files; logical IDs remain consistent. Per-file checksums document the adjustments.
- No dependency installation, YAML execution/schema validation, Git fetch via imported scripts, cloud authentication, deployment, notebook execution or network-policy change was performed.

The historical dependency pin is `fabric-cicd==1.2.0`, with bounded azure-identity/requests versions. Select and test the workshop version later; no current-version/platform-compatibility claim is made here.
