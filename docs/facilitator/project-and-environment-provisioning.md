# Facilitator reference — Prepare projects and environments

Status: retained from the earlier Unit 1 setup draft. Participants now begin with [Unit 0](../tutorial/section-01-foundation/unit-00-observe-and-test-the-setup.md). The organizer reports successful access/feature checks and about one minute of provisioning without private endpoints. See the [review](provisioning-review-2026-10-29.md). This manual alternative is a facilitator reference, not an additional required participant unit.

Estimated learner time: 15–25 minutes once resources are provisioned. For this organizer pilot, allow additional provisioning time and record it separately. This unit uses browser interfaces; local Python, Git clients and pipeline agents are not prerequisites yet.

## Objective

Start a new solution with a traceable first source state and separate training environments. By the end you will have one Azure DevOps project/repository, a README commit, and nine empty Fabric workspaces assigned to a Fabric capacity: Dev/Test/Prod for each of code, data and reporting.

Our sample will grow into a small synthetic sales solution. The workspace roles are present from the start. We will introduce assets gradually, demonstrate a bounded native promotion path, then build coordinated Model B automation across the roles. Nine provisioned workspaces do not mean nine independent development tasks in this first unit.

## What the two repositories are for

- The preparation repository contains this tutorial, reference material and reusable starter files.
- Your new Azure DevOps repository will contain the solution you create. Build it incrementally through the units. Copy only the README template in this unit.

An Azure DevOps project contains repositories and delivery resources. A Fabric workspace contains deployed items and associated runtime resources. Creating a repository does not deploy a solution.

## Prerequisites and provisioning boundary

For the final workshop, the facilitator provides the project, workspaces and access. As the first pilot participant and organizer, you will provision those resources yourself where needed. Provisioning all nine is organizer setup time; learner time covers checking access and recording the environment map.

You need access to an Azure DevOps organization, permission to create/use the training project and Git repository, a Fabric user account, and a Fabric capacity available for the training workspaces. Your training user will be workspace Admin in all nine workspaces. Use public-endpoint training resources as agreed for this workshop.

If a required action is blocked, record the error and stop that step for facilitator support. This exercise does not require changing tenant-wide security/networking settings or running the old reference lab's networking helper.

## 1. Choose your training names

Use the following defaults for the first pilot, or keep your organization's naming convention and report the actual names at the checkpoint. `p01` identifies the participant/pair.

| Resource | Suggested name |
| --- | --- |
| Azure DevOps project | `fabric-days-p01` |
| Solution repository | Use the project's default Git repository; `fabric-days-p01` is fine |
| Initial branch | `main` |
| Dev code workspace | `ws_ffd_p01_code_dev` |
| Test code workspace | `ws_ffd_p01_code_test` |
| Simulated Prod code workspace | `ws_ffd_p01_code_prod` |
| Dev data workspace | `ws_ffd_p01_data_dev` |
| Test data workspace | `ws_ffd_p01_data_test` |
| Simulated Prod data workspace | `ws_ffd_p01_data_prod` |
| Dev reporting workspace | `ws_ffd_p01_reports_dev` |
| Test reporting workspace | `ws_ffd_p01_reports_test` |
| Simulated Prod reporting workspace | `ws_ffd_p01_reports_prod` |

These are the intended solution roles, provisioned from the outset. Data workspaces hold persistent data items; code workspaces hold executable/orchestration items; reporting workspaces hold consumption items. Detailed item placement and permissions will be verified as we introduce each asset. Feature workspaces remain outside the required path.

All environments, including simulated Prod, contain only workshop data. They are not company production environments.

## 2. Create or open the empty Azure DevOps project

**If pre-provisioned:** open the supplied project and repository/repositories. Keep an existing README, `dev` branch and Dev workspace bindings. Do not recreate them to match the example names or branch. For the first pilot, the factory supplied three role repositories; record that mapping. The final one-repository versus multi-repository release choice will be settled before Model B automation.

1. Sign in to your intended Azure DevOps organization.
2. If the training project has not already been provisioned, create a **private** project using **Git** version control. The work-item process is not material to this exercise; retain the normal organizational default.
3. Open the project and select **Repos → Files**.
4. Use the existing default repository if one is provided. Otherwise create one Git repository. We will use one solution repository throughout the core tutorial.
5. Verify that this is the new training solution, with no old Fabric definitions or deployment scripts imported.

**Expected result:** You can open the solution repository and create its initial content. Do not import the preparation or historical reference repository as the learner solution.

## 3. Make the first source-controlled change

**If the factory already initialized the repo:** update the existing README through your participant account, on its existing integration branch (`dev` in the first pilot). Use the starter as a guide; preserve useful existing content. Record this new participant-authored commit and the actual branch. Do not create `main` solely for this unit. With multiple repos, update one README for this checkpoint and verify access to the others. This tests Azure Repos contribution, not yet Fabric Git synchronization.

1. Initialize the repository with a root `README.md`. If the UI offers initialization with a README, use that; otherwise use its new-file action.
2. Use `main` as the initial branch where the UI permits it. If an existing organizational default creates a different branch, record the actual branch at the checkpoint so we can align before connecting Fabric.
3. Copy the content of the [participant README starter](../../examples/participant-bootstrap/README.md) into the root README.
4. Replace the owner and workspace-name placeholders with your actual training details.
5. Commit the change with the message `docs: initialize workshop solution`.
6. Open the commit history and record the resulting commit ID. If initialization created an earlier README commit, that is fine; record the commit containing your completed starter.

**Expected result:** The README is visible on the selected branch and the change has a commit ID. Leave integration-branch PR policies for the later unit that introduces controlled collaboration; this initial bootstrap commit is deliberate.

There is no need to create empty Fabric role folders yet. The initial Git folder will be selected explicitly in the unit that captures actual Fabric definitions.

## 4. Provision or verify the Fabric environment matrix

1. Open Fabric and create/open each of your nine training workspaces. Use workspace resources, rather than My workspace.
2. In each workspace's settings, verify that the workspace is assigned to your intended **Fabric capacity**. A capacity name or successful workspace creation alone does not confirm all required feature access.
3. Verify that your participant account has **Admin** access in each workspace. This is our lab permission choice; later units explain how productive permissions differ.
4. Verify that no solution items have been created yet. If a reused workspace contains existing items or is attached to another solution, use a fresh training workspace rather than deleting unknown content.
5. Record the workspace names and capacity assignment in your notes; correct the README if your actual names differ.

**Expected result:** Nine distinct, empty workspaces are available on the intended capacity, with your training account able to manage them. Existing pre-provisioned Dev Git bindings may remain. No new Git bindings or native Deployment pipelines are required in this unit.

## 5. Inspect feature entry points

In **Dev code**, inspect the workspace settings for **Git integration** and check whether Azure DevOps is offered. If Dev workspaces are already connected, inspect all three Dev mappings (repository, branch and Git directory) and open their Source control panes as the participant. Complete your own sign-in if prompted; record access errors without disconnecting/rebinding. Also check whether the Fabric Deployment pipelines entry point is available to your account. Do not assign pipeline stages or deploy anything yet.

Record these as **visible**, **not visible**, or **blocked with an error**. Visibility is a preliminary access check, not proof that authentication, workspace assignment or deployment succeeds. We will test those actions in their own units. Git integration requires capacity and tenant enablement; pipeline/workspace permissions are separate concerns.

## 6. Explain what changed

| State | Result of this unit |
| --- | --- |
| Code | README stored in Git with a recorded revision |
| Deployment | No Fabric solution definitions deployed |
| Environment | Workspaces, capacity assignment and access prepared |
| Runtime | No sample data or workloads executed |

The lab itself is training/sandbox. Model A/B describe the fictional productive solution we will learn to deliver; this setup does not certify productive compliance.

## Checkpoint — report back here

Stop after this checkpoint. The next unit will create the first Fabric assets manually in the relevant Dev roles. The native-promotion exercise must explicitly handle the dependencies of its selected items; provisioning nine workspaces does not establish cross-workspace auto-binding.

```text
Unit: 1 — project and environments
Result: passed / blocked / passed with deviations
Azure DevOps project:
Repository:
Initial branch:
Additional role repositories / branches / Git folders, if pre-provisioned:
Provisioning identity different from participant: yes / no
Participant can open/contribute to intended repos: yes / no / not checked
Prebound Dev Source control panes: accessible / authentication needed / blocked / not applicable
README commit ID:
Code workspaces (Dev / Test / simulated Prod):
Data workspaces (Dev / Test / simulated Prod):
Reporting workspaces (Dev / Test / simulated Prod):
All nine on intended Fabric capacity: yes / no
Participant Admin in all nine: yes / no
Workspaces empty: yes / no
Dev Git integration / Azure DevOps option: visible / not visible / blocked
Fabric Deployment pipelines entry point: visible / not visible / blocked
Learner time:
Additional organizer provisioning time:
Confusing steps, deviations, or exact errors:
```

Resource names and commit IDs are enough for this checkpoint. Do not include credentials or access tokens. A missing entry point can be reported as a blocker without guessing its cause.

## Troubleshooting

| Observation | Next action |
| --- | --- |
| Cannot create a project/repository | Record the operation and error; ask the organizer to provision it or grant the intended training access |
| Cannot commit the README | Check repository contribution access and whether a branch policy was already applied; report rather than disabling unrelated policies |
| Workspace shows trial/shared/another capacity | Confirm the actual capacity assignment with the organizer |
| Git integration/Azure DevOps is absent | Record workspace capacity and the visible UI; tenant/feature access needs checking |
| Deployment pipeline entry point is absent | Record the symptom; account licensing and feature permissions may need checking |
| Branch name differs from `main` | Report it; no history rewrite or workaround is needed in this unit |

## Control coverage and references

This unit introduces MS-01 (ownership), MS-02/MS-03 (first traceable source change), MS-04 (separated environments), MS-12 (explicit training access) and MS-13 (initial execution-access awareness). It does not fully establish source control of Fabric definitions, bootstrap reproducibility, deployment connectivity or runtime validation.

Official references checked on 28 October 2026:

- [Create an Azure DevOps project](https://learn.microsoft.com/en-us/azure/devops/organizations/projects/create-project?view=azure-devops).
- [Create a Git repository](https://learn.microsoft.com/en-us/azure/devops/repos/git/create-new-repo?view=azure-devops).
- [Fabric Git integration prerequisites](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-get-started).
- [Assign workspaces to native Deployment pipelines](https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/assign-pipeline).

UI wording can differ. Report the labels you actually encounter so the final instructions can reflect the pilot.
