# Follow the deployment starter Python

Both pipeline paths call [`deployment_starter/release.py`](../../../deployment_starter/release.py). Start with its two commands. `validate` prepares a candidate and calls your project check. `publish` prepares the candidate again, compares it with earlier evidence, and then does live preflight or deployment. The common modules underneath it still do the planning and Fabric work introduced in Units 7–10. [Follow the calling YAML](deployment-starter-yaml.md).

Start with one question from the Unit 12 PR. How does the Python code know that **Returned Orders** is missing from the candidate? First it has to find the right model, in the right repository, at the exact revision under review. Follow one report from the mask to the staged export, then see how the same selection is recorded in the evidence. This trace is also useful when the measure exists on someone’s branch and CI still reports it missing.

## Read `prepare`: turn the mask into a verified candidate

| Step | What to read | What it establishes |
| --- | --- | --- |
| Resolve the plan | `build_preview` in [`release_plan.py`](../../../toolkit/release_plan.py) and `validate_contract` in `release.py` | The planner resolves source revisions, orders item keys by their dependencies and resolves target workspace IDs and value sets. The starter checks that this plan fits the Tiny Sales roles, item types and supported binding shapes. |
| Verify the actual source | `checkout_pins` in [`tiny_sales_release.py`](../../../toolkit/tiny_sales_release.py) | Code must match the chosen commit. Data and Reporting must match the configured repository names and contain their reviewed commits in the checked-out history. The function switches each dependency repo to its pin and checks the final hash and tracked worktree. |
| Stage and inspect the exports | `stage_items` and `read_bindings` in the same module | Only tracked files for declared items are copied into a temporary directory. The code checks the `.platform` metadata and unique logical IDs, then reads the actual references inside the exports. The temporary copies are where target bindings can be applied during release. |
| Record the candidate | `starter_version` and the `snapshot` in `prepare` | The evidence captures the mask path, declared sources, verified commit hashes and Git object IDs for the starter directory and shared toolkit files used by the release. |

The [release mask](../../../config/tiny-sales-release.yml) holds the source pins, item graph, workspace IDs and desired value sets. The [Test environment file](../../../config/environments/test.yml) supplies expected display names for those IDs, the Azure DevOps service connection reference and the configured UAMI label. The label is recorded in evidence. The task's signed-in session supplies the credentials used for Fabric calls.

### Trace one edge from the graph to an export

The [Unit 12 mask additions](../../../sample/tiny-sales/unit-12/mask-additions.yml) give `returns_overview` the key `returns_report` and declare `bindings: {semantic_model: model}`. In the plan this places the report after its model. For the binding to work, the report's `definition.pbir` must also point to `../sales_model.SemanticModel`, the sibling model folder. `read_bindings` checks that export reference. The publisher submits both staged definitions together to the Reporting workspace.

A `bindings` edge describes a reference that the starter understands. An `after` edge declares ordering, such as the existing model's prerequisite on `pipeline`. It accepts dependencies from earlier publish phases. The publisher uses those fixed phases, and running `run_sales` to verify data remains a separate exercise step. To support a new kind of asset or reference, extend the starter's validation and publish logic and verify it against a real export. [Logical and physical IDs](fabric-item-identities.md).

## Read `run_project_check`: add a project rule

The mask entry `project_checks.static: checks.validate_candidate` selects [the project's entry point](../../../sample/tiny-sales/unit-12/validate_candidate.py). The starter loads that tracked Python file and calls `run(repositories, plan)`. The first argument maps role names to local repo paths. The second is a copy of the resolved plan. To add another check, define a helper in the project and call it from `run`. Read the source and plan without changing them.

In the sample, `run` first calls the existing Unit 6 notebook contract. It then calls [the returns report check](../../../sample/tiny-sales/unit-12/validate_returns.py), which uses the plan to find the pinned model's `definition/tables` folder and looks for a measure named `Returned Orders` in its TMDL files. Returning normally passes the check. Raising an exception fails validation and writes the diagnostic into `validation.json`. Changing the expected name to `Returns Count` demonstrates the failure on the same source. The Test report and notebook checks later verify what actually runs. [Static validation for Fabric items](static-fabric-validation.md).

## Read `publish`: verify before writing

In Test, `publish` compares the prepared candidate with `validation.json` from the same run. In Prod, `source_candidate` checks the selected run ID against `approvedTestRunId` in the [Prod settings](../../../config/environments/prod.yml), verifies the completed Test publish and its Code commit, then opens that commit in a temporary Git worktree. This gives the Prod job two Code revisions with distinct roles.

| Revision in the Prod evidence | Used for |
| --- | --- |
| `release_definition_revision` | The running release definition and reviewed Prod environment file on `main`. |
| `verified_source_revisions.code` | The tested candidate's mask and Fabric source exports. Its Data and Reporting pins are verified as well. |

The running starter must match the starter recorded with the candidate. Its fingerprint includes the whole `deployment_starter/` directory, so comments and its README count as version changes. Use one starter revision across Test and Prod. If you adopt changed starter files, generate fresh Test publish evidence for that revision before promoting it.

Once the evidence matches, `run_release` reads the target workspaces by ID, verifies their names and inventories the items. In deploy mode it publishes in phases. It reads the target lakehouse and SQL endpoint for notebook and model bindings, uses the target notebook ID for the pipeline activity, and checks the active Variable Library value set. The final inventory records created items such as `returns_report` and verifies that existing item IDs stayed stable. A failed release record can show completed phases. Use it and the live inventory when assessing how far a run got. [Read and design a release manifest](release-manifests.md).

To trace one real run, pick `returns_report` in the resolved plan, find its Reporting source revision and then find the physical ID under `published_items`. Open the report in Fabric and check its semantic-model binding and returned-order count. Those checks connect the source declaration, the published item and the result a report reader sees. [Unit 12 Test checks](../section-05-operate-and-reuse/unit-12-shared-deployment-starter/README.md#7-preflight-and-publish-through-the-existing-test-pipeline).

## Decide where a fix belongs

Use three changes to navigate the code. If a check expects the wrong measure name, start in the project’s check module. If a supported report points to the wrong model folder, inspect its export and mask together. If a team needs a new binding shape, start by tracing what the shared planner and publisher currently accept. A project rule belongs with the team that owns the measure. A change to a shared binding also needs review from the people maintaining the release code.

For a Prod candidate, ask which tested source and which release implementation you’re authorizing. The evidence can identify both. Use the smoke run and report result to see how the deployed definition behaves.
