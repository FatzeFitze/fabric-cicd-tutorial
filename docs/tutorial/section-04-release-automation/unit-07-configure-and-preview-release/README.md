# Unit 7 — Configure and preview a release

Allow **45 minutes** with Azure Pipelines available. You will version a release mask, add the Test and Prod Variable Library value sets, and review a release preview in your PR.

## What you will learn

- Identify the source revisions and target workspace IDs for a release.
- Declare which items depend on each other and which value set each environment should use.
- Use the same preview command to reject an invalid mapping and review the corrected release intent.

## Before you begin

Use the participant Code checkout with the completed Unit 6 PR and its required build policy. Bring the Data and Reporting source revisions from the Unit 4 solution record and the IDs of your assigned Code, Data and Reporting workspaces in Dev, Test and Prod. Open each workspace from its workspace list to confirm its role and environment. In a Fabric URL containing `/groups/<workspace-id>/`, use the workspace GUID after `/groups/`. Use your assigned workspace inventory if the link is ambiguous. [Unit 6](../../section-03-team-delivery/unit-06-required-pr-validation/README.md) · [Workspace and item IDs](../../reference/fabric-item-identities.md).

## How the pieces fit

The mask is a versioned YAML form. It tells the release tools where to get source, which workspace receives each role, and which dependencies to establish. `sales_config` supplies runtime values such as `environment_name` to the Fabric pipeline. The mask selects the **desired** value set. The active choice lives in each workspace and will be checked during publishing. [Variable Library lifecycle](https://learn.microsoft.com/en-us/fabric/cicd/variable-library/variable-library-cicd).

The preview works offline. It checks declared workspace IDs for duplicate assignments, orders item prerequisites and reads the exported library files to check the environment value. It reports planned workspace IDs. The release later looks up or creates physical item IDs, verifies access and checks the actual bindings.

The duplicate-ID check is a deliberately simple teaching example. Each role and environment in this lab has its own workspace, so reusing a GUID catches a likely copy-and-paste error. A different but incorrect GUID can still pass. In Unit 8, you use the Fabric API to compare the workspace returned for a configured GUID with the expected name from your assigned inventory. [Fabric Get Workspace API](https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces/get-workspace).

## 1. Branch from `dev` and add the value sets

1. In a clean Code checkout, pull the Unit 6 merge and branch for the configuration change.

   ```powershell
   git switch dev
   git pull --ff-only origin dev
   git switch -c feature/release-configuration
   ```

2. Find `sales_config.VariableLibrary` or its actual item folder in the export. Inspect `variables.json` and confirm the defaults `environment_name = dev` and `run_label = tiny_sales_dev`.
3. Inside that item folder, create `valueSets/Test.json` with this definition.

   ```json
   {
     "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/variableLibrary/definition/valueSet/1.0.0/schema.json",
     "name": "Test",
     "variableOverrides": [
       {"name": "environment_name", "value": "test"},
       {"name": "run_label", "value": "tiny_sales_test"}
     ]
   }
   ```

4. Create `valueSets/Prod.json` in the same item folder.

   ```json
   {
     "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/variableLibrary/definition/valueSet/1.0.0/schema.json",
     "name": "Prod",
     "variableOverrides": [
       {"name": "environment_name", "value": "prod"},
       {"name": "run_label", "value": "tiny_sales_prod"}
     ]
   }
   ```

5. Edit the existing `settings.json` so `Test` and `Prod` each appear once in `valueSetsOrder`. For a library with no other alternative sets, the file looks like this. If your export contains other settings or value sets, keep them and update only the array.

   ```json
   {
     "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/variableLibrary/definition/settings/1.0.0/schema.json",
     "valueSetsOrder": ["Test", "Prod"]
   }
   ```

   Match the capitalization of the file names, their `name` fields and the array entries. Keep the default values in `variables.json` and preserve `.platform`. [Variable Library definition format](https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/definitions/variable-library-definition).

**Expected result** Git contains alternative Test and Prod definitions. Dev uses its existing Default value set. Leave the Fabric workspaces at their current revision while reviewing the changes in Git.

## 2. Fill the release mask

Copy the three starters into your Code checkout at the paths below.

| Starter | Destination |
| --- | --- |
| [Tiny Sales release mask](../../../../config/tiny-sales-release.yml) | `config/tiny-sales-release.yml` |
| [Read-only planner](../../../../toolkit/release_plan.py) | `toolkit/release_plan.py` |
| [Planner dependency](../../../../toolkit/requirements-planning.txt) | `toolkit/requirements-planning.txt` |

Fill and review these fields in `config/tiny-sales-release.yml`.

| Mask field | What to enter or inspect |
| --- | --- |
| `sources` | Keep `code.revision: checkout`. For Data and Reporting, enter the Azure Repos repository names and full 40-character commits from the solution record. Use `.` if items are at the repo root. Otherwise enter the recorded role folder. |
| `environments.*.workspaces` | Enter your nine assigned workspace GUIDs. Check each role and environment against the inventory before copying it. |
| `environments.*.value_set` | Use `Default`, `Test` and `Prod` for `dev`, `test` and `prod`, respectively. These names match the versioned library definitions. |
| `items` | Compare the item names and roles with your exports. The keys are short names for the plan. `bindings` declares which item each consumer needs in its target, and `after` adds an ordering prerequisite. |
| `variable_library` | Set `folder` to the actual item folder relative to `sources.code.folder`. Keep `environment_name` as the variable the planner checks. |
| `project_checks` | `checks.validate_tiny_sales` records the project check. The existing Unit 6 pipeline step runs it. The preview displays this declaration. |

The mask records identifiers such as repository names, commit IDs and workspace GUIDs. The preview reads those identifiers from the checkout. You will set up authentication when the pipeline connects to Fabric in Unit 8. The mask also describes intended relationships. For example, `items.notebook.bindings.default_lakehouse` names the `lakehouse` plan item. A Dev plan assigns that item to Data Dev, and a Test plan assigns it to Data Test.

The Data and Reporting pins let the Code repo select one combination to test and later release. When a new Data or Reporting commit should be part of a release, review the new pin in the Code repo so Test can validate that combination. [How one release spans three repositories](../unit-10-release-to-prod/README.md#how-one-release-spans-three-repositories).

**Expected result** The mask has concrete workspace IDs and source revisions. It describes the six Tiny Sales items and their target relationships.

## 3. Add the preview to the required build

Append this step to the existing `steps` list in `.azuredevops/pipelines/notebook-ci.yml`. Keep the Unit 6 check above it. Use the existing **Tiny Sales - Notebook CI** pipeline and Code repo `dev` policy.

```yaml
  - bash: |
      set -e
      python -m pip install --disable-pip-version-check -r toolkit/requirements-planning.txt
      python -B -m toolkit.release_plan --mask config/tiny-sales-release.yml --checkout-revision "$CHECKOUT_REVISION"
    displayName: Preview Tiny Sales release targets
    workingDirectory: $(Build.SourcesDirectory)
    env:
      # Record the Git revision this build is evaluating.
      CHECKOUT_REVISION: $(Build.SourceVersion)
```

The agent loads the mask and the Code export from the proposed PR merge. It displays that checkout revision and the two external revision pins. After PR completion, the actual `dev` commit is the source revision to record for release. The Data and Reporting pins are checked for format here. The later release will fetch the selected revisions and check their contents. [Azure Repos PR build behavior](https://learn.microsoft.com/en-us/azure/devops/pipelines/repos/azure-repos-git?view=azure-devops#pr-triggers).

**Expected result** The required build can validate the notebook and then preview the declared release targets using Python on the existing agent.

## 4. Reject a cross-environment mapping, then fix it

1. Save your correct Test Data ID in the release worksheet. For the failure exercise, put the Dev Data ID into `environments.test.workspaces.data`. Review and stage the Unit 7 changes, then commit and push them. Use **Add release preview with a deliberate workspace conflict** as the commit message. [Release preview worksheet](resources/release-preview-record.md).
2. Open an active PR into `dev` titled **Configure and preview Tiny Sales releases**. Use this description to tell the reviewer what changed and how to read the first build.

   ```markdown
   ## Change
   Add the release mask, Test and Prod value sets, and a CI preview.

   ## Validation
   The first run should reject the deliberate Dev Data ID in the Test mapping.
   After correcting it, I'll verify that the preview lists all three targets.
   ```
3. On the PR's **Overview**, open the required build and inspect **Preview Tiny Sales release targets**. Expect `PLAN INVALID` and a message that `environments.test.workspaces.data` reuses the workspace ID assigned to `environments.dev.workspaces.data`. Record the failed run.
4. Restore the Test Data ID. Use **Restore the Test Data workspace mapping** as the commit message and push to the same PR. Wait for the new required build and find `PLAN VALID`. Inspect the plan before completing the PR.

   - `sources` shows the Code checkout revision and both external pins.
   - `definition_order` puts the lakehouse ahead of the notebook, the library and notebook ahead of the pipeline, and the model ahead of the report. The model also follows the pipeline in the declared order. The later release adds execution and data-readiness checks before publishing reporting items.
   - `targets` shows the planned item workspace IDs and expected environment values from `Default`, `Test` and `Prod`.

5. Update **Validation** in the PR description with what actually happened and links to both runs. Review the final diff and complete the PR after its required check passes. Record the resulting `dev` commit and the Data and Reporting pins.

**Expected result** The same policy blocks the conflicting mapping and accepts the corrected one. The merged mask and its preview give the next unit an agreed release intent to verify against Fabric.

## If something does not work

| Symptom | What to check |
| --- | --- |
| The preview step is missing | Check its indentation under the YAML `steps` list and verify the PR uses the existing registered pipeline. |
| `expected a list of variableOverrides` or missing value set file | Check the `valueSets` folder, JSON key names and exact `Test.json` / `Prod.json` names. The hosted Linux agent uses case-sensitive paths. |
| A value set supplies `dev` in Test or Prod | Check the named override for `environment_name`. Omitted overrides inherit Default. |
| A mapping reuses another workspace ID | Compare both indicated fields with your assigned workspace inventory. |
| The build stops during dependency installation | Check agent access to the approved Python package index with the facilitator. The planner uses the pinned version from `toolkit/requirements-planning.txt`. |

## Completion checkpoint

- [ ] The Code repo contains the release mask, planner and alternative value-set definitions.
- [ ] The required check rejected the duplicated Dev Data workspace mapping, then passed after correction.
- [ ] You can distinguish the source revisions, planned workspace IDs, desired value sets and the deployed state the next unit will verify.
- [ ] Your worksheet records the merged `dev` commit, external pins and both runs.

[Previous unit](../../section-03-team-delivery/unit-06-required-pr-validation/README.md) · [Tutorial index](../../README.md) · [Next unit](../unit-08-publish-shared-dev/README.md)
