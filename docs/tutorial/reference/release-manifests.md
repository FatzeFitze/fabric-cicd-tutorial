# Read and design a release manifest

A release manifest is a structured record of one release attempt. It gives reviewers and operators a way to answer three questions without searching the entire pipeline log. Which source revisions ran? What happened in the target environment? What did the pipeline verify?

In Tiny Sales, `config/tiny-sales-release.yml` is an input that declares the release plan. The Test pipeline writes `test-release.json` as evidence of what happened during the run. Open it under **test-release-evidence** on the pipeline run page. [Unit 9](../section-04-release-automation/unit-09-release-to-test/README.md) · [Azure Pipelines artifacts](https://learn.microsoft.com/en-us/azure/devops/pipelines/artifacts/pipeline-artifacts?view=azure-devops).

## Read the Unit 9 artifact

| Question | Fields to read | What they tell you |
| --- | --- | --- |
| Did this run publish? | `run_id`, `mode`, `status`, `phase`, UTC timestamps | `deploy` / `published` / `complete` identifies a completed publish. `preflight_passed` records a read-only run. On failure, use `phase` to find the relevant log entry and decide what to inspect before retrying. |
| Which definitions were selected? | `declared_sources`, `verified_source_revisions` | Compare the requested source with the checked-out commits for **Code, Data and Reporting**. A branch name such as `dev` can point to a different commit tomorrow. |
| Where did the release run, and under which configuration? | `verified_workspaces`, `configured_release_identity`, `active_value_set`, `sql_endpoint_id` | Check the target workspace IDs and names, the configured connection and UAMI, and the observed `Test` value set. The SQL endpoint has its own ID. The configured identity fields record connection settings. Capture the authenticated principal separately when you need evidence of who called Fabric. |
| What changed in Fabric? | `workspace_items`, `before_item_ids`, `published_items`, `created_items` | `workspace_items` is the starting inventory. The same physical ID before and after shows the release preserved the item. An absent item (`null` in `before_item_ids`) that appears after publishing counts as a creation in this run. |

Try this with `build_sales` and `validate_release`. Find the physical ID of the existing notebook before and after, then locate the fresh validation notebook in `created_items`. If `published_items` shows `logicalId: null`, Fabric's inventory response did not supply a value. Look in the item’s `.platform` at the verified source revision for the Git logical ID. [Logical and physical IDs in Fabric](fabric-item-identities.md).

`published` confirms that the publishing steps and final inventory checks completed. Record runtime evidence separately. In Unit 9, keep the `run_sales` and `validate_release` run links with the observed parameter values and smoke-test result. Inspect the report’s actual semantic model binding and record ownership fields where Fabric exposes them.

The DataOps guidelines distinguish code, deployment, environment and runtime state. This artifact ties the first three together through the source revisions, deployed item IDs and observed environment settings. Adding a linked validation result addresses the Model B evidence expected by **MS-14 Release evidence**. The manual smoke exercise gives you a validation result to link. Model B’s **MS-08 Release validation** calls for automated technical and runtime validation in Test and after Prod deployment. [DataOps Principles & Scope](../../source-guidelines/dataops-principles-and-scope.md#5-architectural-state-model) · [Fabric Minimum Standard](../../source-guidelines/fabric-minimum-standard.md#minimum-standard-by-operating-model).

## Decide what to capture

Start with the decisions people or automation need to make after a release. For each field, ask who will read it, what decision it supports and where its value comes from.

- **Start small.** Capture a run ID and timestamps, the exact source revisions, the target environment and relevant workspace and item IDs, and the outcome with the last phase reached. Include a configuration value when it affects behavior you need to verify, as the active value set does here.
- **Capture the result where it was measured.** The Unit 9 record distinguishes declared inputs from verified checkouts and workspace observations. If you automate a smoke test, capture its outcome and execution ID or link. Have the orchestrator record timeouts and launch failures too, since those may happen before the notebook can report a result.
- **Keep the manifest readable and shareable within the project.** Link detailed logs or test results from the run. The workshop’s small starting inventory helps explain creation versus update. On a larger project, consider keeping only in-scope items in the manifest and retaining broader diagnostics separately when needed. Leave tokens, secrets and business data out of the artifact.
- **Plan for retention and consumers.** If code reads the manifest, give the format a schema version and define what missing or `null` fields mean. Azure Pipelines artifacts follow run retention, and deleting a run also deletes its artifacts. Choose a retention period that covers your review and recovery needs. [Azure Pipelines artifact retention](https://learn.microsoft.com/en-us/azure/devops/pipelines/artifacts/pipeline-artifacts?view=azure-devops#publish-artifacts) · [Azure Pipelines retention policies](https://learn.microsoft.com/en-us/azure/devops/pipelines/policies/retention?view=azure-devops).

## Use it in reviews and automation

- **Review a release candidate.** Link the run in the PR. A reviewer can check that the three verified revisions belong to the candidate, confirm the target and inspect the associated validation result.
- **Turn the evidence into a gate.** A required validation pipeline could download the manifest from the designated Test run and check the expected candidate revisions and target IDs, `published` status and a linked passing smoke result for that candidate. Treat missing, failed or stale evidence as a failed check. Azure Repos enforces the required check through branch policy. Unit 9 supplies the deployment record for this pattern. [Azure Pipelines artifact download](https://learn.microsoft.com/en-us/azure/devops/pipelines/artifacts/pipeline-artifacts?view=azure-devops#download-artifacts) · [Azure Repos build validation](https://learn.microsoft.com/en-us/azure/devops/repos/git/branch-policies?view=azure-devops#build-validation).
- **Investigate a partial release.** Start with the failed phase and compare the starting inventory with the live workspace. A step may already have changed an item before a later failure. The previous successful manifest gives you the source revisions and target IDs for comparison.

[Unit 9](../section-04-release-automation/unit-09-release-to-test/README.md) · [Tutorial index](../README.md)
