# Unit 6 preparation and pilot checks

10 November 2026. The organizer reports completing all Unit 5 steps and confirms `build_sales.Notebook/notebook-content.py` in the completed PR. Unit 5 is parked at the lesson body in `348d885`. The participant supplied the path and format. The full export, Azure Repos commit IDs and Fabric execution logs have yet to be collected.

[Unit 6 lesson](../tutorial/section-03-team-delivery/unit-06-required-pr-validation/README.md) · [CI evidence worksheet](../tutorial/section-03-team-delivery/unit-06-required-pr-validation/resources/ci-evidence.md).

## Exercise design

- Continue in the Code repository from the completed Unit 5 merge. The new PR introduces CI as a separate step and records its resulting `dev` commit for Unit 7. Workspace publishing remains scheduled for Unit 8.
- The reusable Python function reads and compiles Fabric notebook source and checks `.platform` metadata. The project-specific function compares the actual parsed `revenue` expression and declared 357.20/204.70 totals with the Unit 5 source contract. Formatting and comments do not change that comparison. An intentional refactor to an equivalent expression may require updating the project contract through review.
- The learner changes `F.lit(0)` to `F.lit(1)` and restores it on the same PR after observing the failed build. The check reads the notebook under review and exits with a nonzero status for that source defect. The exercise uses standard Python. The later runtime exercise evaluates the Spark computation and checks persisted data and reporting.
- The lesson starts with a Microsoft-hosted Ubuntu 24.04 job, Python 3.12, and the learner's Code repo checkout. Verify that project pipeline creation, agent authorization, hosted parallel capacity and `dev` policy editing are available before the session. Measure both working time and queue time. Use a facilitator for delegated branch-policy setup.

## 10 November revision after organizer feedback

- Use `.azuredevops/pipelines/notebook-ci.yml` and keep `validate_tiny_sales.py` as the checker filename in both repositories. The revision explains module invocation from the repo root and distinguishes the hardcoded teaching check from configurable project validation. [Generic validation candidates](../planning/backlog.md#configurable-validation-candidates).
- Rename the registered pipeline to **Tiny Sales - Notebook CI** and select it in the policy on the Code repo's `dev` branch. The policy display name is **Tiny Sales source validation**. Observe the live rename, selected YAML path and policy run during the walkthrough. [Pipeline settings](https://learn.microsoft.com/en-us/azure/devops/pipelines/customize-pipeline?view=azure-devops#pipeline-settings).
- The organizer requested that draft migration guidance stay in chat. The lesson now explains the selected pipeline folder, the split between project checks and shared functions, and the dedicated Fabric item directory recommended for new projects. [Repository layout rationale](../planning/repositories-and-bootstrap.md#recommended-participant-layout).

## Evidence and limits

- **Organizer-reported** Unit 5 clone, edit, push, review and first merge completed without issue. The recorded export path confirms the default CI input.
- **Locally exercised** The same module command used by the YAML passed on a notebook assembled from the canonical starter plus the documented Unit 4 and 5 edits. It rejected the zero-to-one defect, stale revenue expectation, invalid Python, invalid logical ID and missing item folder. It accepted a folder with spaces and UTF-8 BOMs. The generic loader also accepted the retained historical Fabric Python export.
- **Documented** Azure Repos can attach an automatic required build validation policy to `dev`. It queues the pipeline against the PR merge revision. The participant setup selects the YAML on the feature branch before installing the policy. [Azure Repos Git pipeline triggers](https://learn.microsoft.com/en-us/azure/devops/pipelines/repos/azure-repos-git?view=azure-devops#pr-triggers) · [Build validation policy](https://learn.microsoft.com/en-us/azure/devops/repos/git/branch-policies?view=azure-devops#set-build-validation).
- **Organizer-reported** Unit 6 went through smoothly and the organizer requested moving to Unit 7. Exact run IDs, policy screenshots, revisions and duration were not supplied. Preserve the exercise at `583b9bf` with the optional reading and next-unit navigation added.

The workshop branch policy demonstrates an automatic requirement and its enforcement in the participant repo. Before treating it as a production control, evaluate who can change the pipeline/check files, edit the policy, bypass it or administer the agent. Trace MS-02/03 for review and integration, MS-08 for the observed validation failure, and MS-14 for commit and run evidence.

## Unit 7 handoff

Use the `dev` revision with the validation pipeline. Unit 7 adds the versioned YAML mask and read-only preview as a second step in that required build. [Unit 7 pilot notes](unit-07-pilot-notes.md).
