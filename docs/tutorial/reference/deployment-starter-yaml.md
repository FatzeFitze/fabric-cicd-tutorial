# Read the deployment starter YAML

In Unit 6, Notebook CI ran a source check. In Units 9 and 10, separate pipelines released Tiny Sales to Test and Prod. Unit 12 keeps those pipeline registrations and gives them a common implementation. Open the Test wrapper and follow `extends.template` to see where a project decision becomes a pipeline step. [Unit 12](../section-05-operate-and-reuse/unit-12-shared-deployment-starter/README.md#3-install-the-starter-and-replace-the-two-pipeline-files).

## Start with the wrappers

Each wrapper supplies the resources Azure DevOps must authorize and the values the shared template needs. A path such as `/deployment_starter/templates/release.yml` starts at the Code repo root. The files in the sample directory are the copy sources for your registered pipeline YAML files. [Azure Pipelines templates](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/templates?view=azure-devops).

| Wrapper | What to follow in the YAML |
| --- | --- |
| [CI](../../../sample/tiny-sales/unit-12/ci.yml) | `extends` selects `ci.yml` and passes the mask path. The existing build validation policy queues this pipeline for the PR. |
| [Test](../../../sample/tiny-sales/unit-12/test.yml) | The queue option **Publish to Test after preflight** sets `deployToTest`. The wrapper passes that as `deploy` with `target: test`. Clearing the option still runs validation and live preflight. |
| [Prod](../../../sample/tiny-sales/unit-12/prod.yml) | `target: prod` and `deploy: true` select the Prod publish path. The `tested` resource supplies the specific Test run selected when you queue Prod. Its `source` is the registered Test pipeline name. |

In each wrapper, `data` and `reports` are repository aliases. Fill in their actual Azure Repos names. Their `dev` refs give the agent access to the branches containing the reviewed commits. The Python preparation step checks out the exact Data and Reporting pins from the mask. [Multiple repository checkouts](https://learn.microsoft.com/en-us/azure/devops/pipelines/repos/multi-repo-checkout?view=azure-devops) · [Pipeline resources](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/resources?view=azure-devops).

## Follow the shared templates

| File | What it does | What to look for in a run |
| --- | --- | --- |
| [`ci.yml`](../../../deployment_starter/templates/ci.yml) | Defines the `Validate` job and calls `validate-steps.yml` with the mask. | The PR build's **Validate** job. |
| [`checkout.yml`](../../../deployment_starter/templates/checkout.yml) | Places Code, Data and Reporting in `s/code`, `s/data` and `s/reports` under the agent's pipeline workspace. Fetches full history so the Python code can verify that a reviewed commit belongs to the expected branch history. Selects Python 3.12. | Checkout log for each repo and the Python setup task. |
| [`validate-steps.yml`](../../../deployment_starter/templates/validate-steps.yml) | Installs planning dependencies, calls `deployment_starter.release validate` and uploads `candidate-validation`. Both CI and Test call these steps, so the same checks run on the PR candidate and the actual Test candidate. | **Validate the graph, pinned exports and project check**, then `candidate-validation/validation.json`. |
| [`release.yml`](../../../deployment_starter/templates/release.yml) | Defines the Test validation stage and the Test or Prod release stage. Loads the environment settings, checks the run branches, downloads evidence and invokes `deployment_starter.release publish` through `AzureCLI@2`. | The branch check, artifact download, Azure CLI task and `test-release-evidence` or `prod-release-evidence`. |

Read the timing in `release.yml`. Azure DevOps expands `${{ ... }}` as it builds the run plan. The conditional under `stages` includes **Validate** for Test. The same expansion selects `config/environments/test.yml` or `prod.yml` and supplies the service connection to the Azure CLI task. At runtime, `$(resources.pipeline.tested.runID)` supplies the selected run ID to the Prod task. The `env` block names values for Bash. For example, `RELEASE_MODE` becomes `$RELEASE_MODE` in the script and is passed to Python as `--mode`. [Azure Pipelines expressions](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/expressions?view=azure-devops).

## Follow the evidence between jobs

- **Test** starts from Code `dev`. The Release stage follows successful validation and uses `download: current` to get `validation.json` from the same run. It checks out and prepares the candidate again in its own job. The report about a PR build is useful to the reviewer. The same-run validation is the evidence that the shared Test release actually consumes.
- **Prod** starts its release definition from Code `main` and checks that the selected Test run came from `dev`. It uses `download: tested` to retrieve `test-release.json`. Python checks that this manifest represents the approved completed Test publish and resolves its exact candidate.
- **For failures**, `condition: succeededOrFailed()` lets the artifact upload run after a failing step in that job. Look for the JSON if the script reached the point where it could write it. An authorization or checkout failure can occur earlier, so start with the failing job or task log in that case. [Pipeline conditions](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/conditions?view=azure-devops).

The service connection field selects the login used by the Azure CLI task. The connection's pipeline permissions and approvals live in Azure DevOps. The Test and Prod workspace IDs are read later from the release mask. This starter uses a regular Azure Pipelines job called `Release`. Unit 11 adds deployment history by explicitly declaring a deployment job that targets an Azure DevOps Environment. [Service connections and identities](release-service-connections.md) · [Unit 11](../section-05-operate-and-reuse/unit-11-recover-a-test-release/README.md).

When a run fails, find the last successful handoff. A missing measure points to the **Validate** job and its diagnostic. A workspace name mismatch points to the release task and its live preflight evidence. [Follow the Python release](deployment-starter-python.md) · [Read a release manifest](release-manifests.md).
