# Azure DevOps basics

**Allow about 10 minutes.**

Azure DevOps is a Microsoft platform for planning work, hosting source, reviewing changes and running delivery workflows. A typical Azure DevOps Services setup has an **organization** that contains **projects**. A project groups resources for a team or initiative, such as repositories, work items and pipelines. Within a project, access to individual resources can be controlled separately. [What is Azure DevOps?](https://learn.microsoft.com/en-us/azure/devops/user-guide/what-is-azure-devops?view=azure-devops).

## Where to look

| Service | What it does | A question it can answer |
| --- | --- | --- |
| **Azure Boards** | Tracks work items such as features, bugs and tasks. | Why are we changing the export? |
| **Azure Repos** | Hosts Git repositories and provides branches, PRs, review and policies. | Which files changed, and who reviewed them? |
| **Azure Pipelines** | Runs automated validation, builds and releases. | Did the tests pass, and what version was deployed? |
| **Azure Artifacts** | Hosts packages that projects can publish and consume. | Which version of the shared library are we using? |
| **Azure Test Plans** | Helps teams plan and track manual and exploratory testing. | Which scenarios did the testers cover? |

## Pull requests and branch policies

In Repos, a **pull request** proposes merging one branch into another. Reviewers can discuss individual lines, and the PR shows the check results. A **branch policy** applies conditions to a target branch, such as a minimum reviewer count or a required successful build. Azure Repos calls the latter **build validation**, even when the pipeline only runs checks and produces no compiled application. [Azure Repos branch policies](https://learn.microsoft.com/en-us/azure/devops/repos/git/branch-policies?view=azure-devops).

For example, someone changes a script that exports inventory. The PR targets the shared branch. A required pipeline tests the output columns and a reviewer checks how the new column is populated. You can open the pipeline run from the PR to see which check failed and inspect its logs. Once the required conditions are met, the PR can be completed.

## How a pipeline runs

A pipeline definition can live in a **YAML** file in Git. YAML is a human-readable format for structured configuration. In Azure Pipelines, the definition can describe stages, jobs and steps.

| Term | What it means |
| --- | --- |
| **Trigger** | A rule that starts a run, such as a change to a branch. A run can also start manually or be queued through a PR build-validation policy. |
| **Stage** | A larger phase, such as Validate, Deploy to Test or Release to Prod. |
| **Job** | A group of steps scheduled together. An agent runs the steps in an agent job. |
| **Step** | A task or script, such as running a Python test or calling an API. |
| **Agent and pool** | The agent is the worker that executes the job. A pool is a group of agents available to run jobs. Microsoft-hosted agents and self-hosted agents offer different choices for installed tools and network access. |
| **Run** | One execution of the pipeline, with a status and logs for the work it performed. A run may publish artifacts such as reports or deployable files. |

If a job sits in the queue, look at the pool and available agents. If the job runs but a step fails, open that step's log. If a stage is waiting for a check or approval, inspect that resource's check status. Each points to a different next action. [Azure Pipelines overview](https://learn.microsoft.com/en-us/azure/devops/pipelines/get-started/what-is-azure-pipelines?view=azure-devops) · [Agents](https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/agents?view=azure-devops).

## How a release reaches another service

A **service connection** configures how an authorized pipeline connects to an external service. With an eligible Microsoft Entra setup, an Azure Resource Manager service connection can use workload identity federation to let a pipeline authenticate as a configured identity, including a user-assigned managed identity, without keeping a long-lived secret in the pipeline. [Workload identity service connections](https://learn.microsoft.com/en-us/azure/devops/pipelines/release/configure-workload-identity?tabs=managed-identity&view=azure-devops).

There are separate questions to ask. Which pipeline can use the connection? Which identity does the connection use? What can that identity access at the destination? Can the agent reach the destination over the network? A connection can authenticate successfully and still get a permission error when it tries to change a resource.

Azure DevOps also lets resource owners configure **approvals and checks** outside the pipeline YAML. For example, a stage that uses a protected production resource can wait until an authorized approver has reviewed the release. A PR review is a decision about integrating the source change. A production approval is a decision about releasing a specific version to a specific target. [Service connections](https://learn.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops) · [Approvals and checks](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/approvals?view=azure-devops).

[Back to the pre-read guide](README.md)
