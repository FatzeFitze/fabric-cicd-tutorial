# Unit 6 — Turn review into a required check

Allow **35 minutes of working time** with an available Azure Pipelines agent. You will add a reusable source validator and a Tiny Sales check, then make a successful build a requirement for completing PRs into `dev`.

## What you will learn

- Run the same source check from the command line and Azure Pipelines.
- Connect a YAML pipeline to an Azure Repos build validation policy.
- Diagnose a failing check and follow the result from a revised commit to a completed PR.

## Before you begin

Use your participant **Code** repository and local checkout. Find the completed Unit 5 PR and the resulting `dev` commit. In the notebook export, the returned-order branch uses `F.lit(0)`, and `EXPECTED_METRICS` declares **357.20 gross** and **204.70 revenue**. Keep the incoming Fabric update pending for the later publishing exercise. [Unit 5](../unit-05-make-a-local-feature-change/README.md).

You need permission to create an Azure Pipeline and queue it on the supplied agent. You or the facilitator need **Edit policies** permission for `dev`. This lesson uses a Microsoft-hosted Ubuntu agent with Python 3.12. Local Python 3.12 is optional. [Python on Azure Pipelines](https://learn.microsoft.com/en-us/azure/devops/pipelines/ecosystems/customize-python) · [Azure Repos branch policies](https://learn.microsoft.com/en-us/azure/devops/repos/git/branch-policies?view=azure-devops#set-build-validation).

## How the pieces fit

```mermaid
flowchart LR
    PR["PR targeting dev"] --> POLICY["Required build validation policy"]
    POLICY --> YAML["Azure Pipelines job"]
    YAML --> CHECK["Tiny Sales source check"]
    CHECK --> LOADER["Reusable notebook source validator"]
    CHECK --> RESULT["Pass or fail in the PR"]
```

The reusable validator reads the notebook's `.platform` metadata and compiles its Python source without executing it. The Tiny Sales check is a teaching shortcut. It hardcodes the parsed shape of the `revenue` expression and the two totals from Unit 5 so you can see a clear failure in the PR. Even a rewrite that produces the same result can fail this check. For a team project, use configurable checks for requirements such as item metadata and allowed dependencies. Test business rules by running the transformation on representative data and asserting the results. The later Fabric exercise verifies table writes, cross-workspace bindings and the report.

The **branch policy** queues this Azure Pipeline against the PR's proposed merge with `dev` and uses the run result when deciding whether completion is allowed. In Azure Repos Git, you configure that trigger on the target branch. The supplied YAML sets `trigger: none` so ordinary pushes do not queue a separate CI run. [Azure Repos PR triggers](https://learn.microsoft.com/en-us/azure/devops/pipelines/repos/azure-repos-git?view=azure-devops#pr-triggers).

## 1. Add the validator and pipeline

1. In your Code repository checkout, confirm `git status --short` is clean. Update `dev`, then start a second branch.

   ```powershell
   git switch dev
   git pull --ff-only origin dev
   git switch -c feature/required-pr-validation
   ```

2. Copy the three supplied files into the paths below, relative to the participant Code repository root. On GitHub, open each file and use **Raw** to get the source text.

   | Supplied file | Destination in your Code repo | Responsibility |
   | --- | --- | --- |
   | [Notebook validator](../../../../toolkit/notebook_validation.py) | `toolkit/notebook_validation.py` | Read `.platform`, validate Notebook type and logical ID, compile the Python export and return its parsed syntax. |
   | [Tiny Sales check](../../../../sample/tiny-sales/validate_tiny_sales.py) | `checks/validate_tiny_sales.py` | Check this project's revenue expression and declared totals. |
   | [CI YAML](../../../../.azuredevops/pipelines/notebook-ci.yml) | `.azuredevops/pipelines/notebook-ci.yml` | Set up Python and call the check on the notebook item folder. |

   Microsoft examples often start with a root `azure-pipelines.yml`. Azure Pipelines also lets you select an existing YAML file by path. We use `.azuredevops/pipelines/` to give CI and the later deployment pipelines one recognizable home. Keep project-specific rules in `checks/` and reusable functions in `toolkit/` so you can run and reuse them independently of the Azure DevOps YAML. [Azure Pipelines YAML and settings](https://learn.microsoft.com/en-us/azure/devops/pipelines/customize-pipeline?view=azure-devops) · [Select an existing YAML file](https://learn.microsoft.com/en-us/azure/devops/pipelines/get-started/clone-import-pipeline?view=azure-devops#clone-or-copy-a-pipeline).

   When setting up a new Fabric project, point the workspace's **Git folder** at a dedicated item folder such as `/fabric/code`. Keep `.azuredevops/`, `checks/` and `toolkit/` alongside `fabric/` at the repo root. This keeps workflow files and Python helpers outside the directory Fabric synchronizes. For this exercise, use the item path you recorded in Unit 5. [Fabric Git folder guidance](https://learn.microsoft.com/en-us/fabric/fundamentals/understand-best-practices-fabric-cicd#git-folder-settings).

3. In the YAML, confirm `NOTEBOOK_ITEM_DIR` is the folder you recorded in Unit 5. The supplied value is `build_sales.Notebook`. If your folder differs, enter its repo-relative path using forward slashes. The value points to the item folder containing `.platform` and `notebook-content.py`.
4. If you have local Python 3.12, run the check from the Code repository root. Use the same path as in the YAML. A successful run prints `VALIDATION PASSED`. Azure Pipelines will run this command as part of the required exercise.

   ```powershell
   python -B -m checks.validate_tiny_sales --item-dir 'build_sales.Notebook'
   ```

   `-m` takes a Python module name. The dot separates the `checks` package from the `validate_tiny_sales` module in `checks/validate_tiny_sales.py`. From the repo root, this invocation lets Python find both `checks` and the sibling `toolkit` it imports. Running a `.py` file directly takes a filesystem path and starts the import search in the script's directory. `--item-dir` still takes a filesystem path, such as `fabric/code/build_sales.Notebook`. [Python command-line options](https://docs.python.org/3.12/using/cmdline.html#cmdoption-m).

5. Review the three new files, then stage and push them.

   ```powershell
   git add -- toolkit/notebook_validation.py checks/validate_tiny_sales.py .azuredevops/pipelines/notebook-ci.yml
   git diff --cached --check
   git diff --cached --stat
   git commit -m "Add Tiny Sales source validation pipeline"
   git push -u origin feature/required-pr-validation
   ```

**Expected result** Azure Repos shows the three files on your feature branch. The notebook still contains the reviewed Unit 5 rule.

## 2. Register the pipeline and require it on `dev`

1. In your Azure DevOps project, select **Pipelines → New pipeline → Azure Repos Git**, then select the participant Code repo.
2. Choose **Existing Azure Pipelines YAML file**. Select branch `feature/required-pr-validation` and path `/.azuredevops/pipelines/notebook-ci.yml`. Select **Continue**. On the review screen use the dropdown beside **Run** to select **Save**. If you use **Run** at this point, treat that run as a setup check and use the feature branch as its source. [Register an existing YAML pipeline](https://learn.microsoft.com/en-us/azure/devops/pipelines/get-started/clone-import-pipeline?view=azure-devops#clone-or-copy-a-pipeline).
3. Open the saved pipeline under **Pipelines**. On its details page, select **… → Rename/move** and set its name to **Tiny Sales - Notebook CI**. The initial name may match the repository. A descriptive name makes the pipeline easier to pick when the Code repo has both CI and deployment pipelines. [Pipeline settings](https://learn.microsoft.com/en-us/azure/devops/pipelines/customize-pipeline?view=azure-devops#pipeline-settings).
4. In **Repos → Branches**, select your participant **Code repository** in the repository picker. On that repository's **`dev`** branch, open **… → Branch policies**. Under **Build validation**, select **+** and set the following values. Ask the facilitator to apply them if branch-policy editing is delegated.

   | Field | Value |
   | --- | --- |
   | Build pipeline | **Tiny Sales - Notebook CI** |
   | Path filter | Blank, so the policy covers all changes to `dev` |
   | Trigger | **Automatic** |
   | Policy requirement | **Required** |
   | Build expiration | **Immediately when `dev` is updated** |
   | Display name | **Tiny Sales source validation** |

5. Save and check that the policy is enabled on the Code repository's `dev` branch. Keep the existing branch requirements in place. [Configure build validation](https://learn.microsoft.com/en-us/azure/devops/repos/git/branch-policies?view=azure-devops#set-build-validation).

**Expected result** The Code repository's `dev` branch lists **Tiny Sales source validation** as a required, automatic policy backed by **Tiny Sales - Notebook CI**.

## 3. Watch the policy block a faulty change

1. In the exported `notebook-content.py` on your feature branch, change `F.lit(0)` to `F.lit(1)` in the `withColumn("revenue", ...)` expression. This is valid Python and would give each returned order 1.00 revenue. Keep the declared expectations and check files as reviewed.
2. Review the one-line diff, commit the notebook file and push the feature branch. Open an **active** PR titled **Add required Tiny Sales source validation** from `feature/required-pr-validation` into `dev`. Note the intentional defect in the PR description so reviewers can follow the exercise. Use **Create** to open it for review.
3. On the PR's **Overview**, wait for the required build to finish. Open its run from the policy result and find **Validate Tiny Sales notebook source**. Confirm the failure says `Returned orders must contribute zero revenue` and reports the actual `F.lit(1)` expression. Check that Azure Repos reports the required check as failed and blocks normal completion. Record the source commit, run link and failure in the worksheet. [CI evidence worksheet](resources/ci-evidence.md).

**Expected result** The agent runs the checker and the checker returns a failure for the deliberate defect. If the job never starts, or the task cannot find the source file or Python, resolve that setup issue first. The exercise checkpoint is the specific business-rule diagnostic in the job log.

## 4. Fix the source and complete the PR

1. Restore `F.lit(0)` in the same expression. Review the one-line fix, commit it and push to the same feature branch. Keep the same PR open.
2. Wait for the **new** required run. Find `VALIDATION PASSED` in the job log and check that the PR policy is green for the updated revision. Record the new source commit and run link. The build can show a generated PR merge commit, which is distinct from both your feature commit and the final `dev` commit.
3. On the PR's **Files** tab, verify the final proposed changes are the three validation files. The temporary notebook edit should have disappeared from the final diff. Update the PR description with the failing and passing run links and ask for any required review.
4. Complete the PR using the merge type permitted by your repo. Prefer squash if available so `dev` receives one commit with the validation files. Record the resulting `dev` commit and check that the build validation policy remains enabled. [Complete an Azure Repos PR](https://learn.microsoft.com/en-us/azure/devops/repos/git/complete-pull-requests?view=azure-devops#complete-a-pull-request).

**Expected result** The completed PR links the failed and successful checks to the source revisions. Future PRs into `dev` use the required pipeline. Carry the merged revision and the worksheet into the configuration lesson.

## If something does not work

| Symptom | What to check |
| --- | --- |
| The YAML picker cannot find the file | Select the participant Code repository and the pushed feature branch, then check the exact `/.azuredevops/pipelines/notebook-ci.yml` path. |
| The job waits or reports no hosted parallelism | Ask the facilitator to verify that your project can queue on the designated agent and has available job capacity. [Parallel jobs](https://learn.microsoft.com/en-us/azure/devops/pipelines/licensing/concurrent-jobs?view=azure-devops). |
| No build appears on the PR | Confirm the PR is active, targets `dev`, and has the enabled **Automatic / Required** policy attached to the saved pipeline. |
| The check reports missing `.platform` or notebook source | Check `NOTEBOOK_ITEM_DIR` and the item folder in the PR revision. |
| The corrected run reports a totals mismatch | Inspect `EXPECTED_METRICS` in the checkout. Unit 5 expects gross `Decimal("357.20")` and revenue `Decimal("204.70")`. |
| Build passed but completion is still blocked | Inspect the other policies, required reviewers and conflicts on the PR. |

## Completion checkpoint

- [ ] The Code repo contains the reusable validator, project check and CI YAML under `.azuredevops/pipelines/`.
- [ ] The Code repo's `dev` branch has an automatic required build policy for **Tiny Sales - Notebook CI**.
- [ ] The deliberately faulty revision failed with the intended diagnostic and normal PR completion was blocked.
- [ ] The corrected revision passed and the PR was completed through the branch's requirements.
- [ ] The worksheet records both runs, the completed PR and the resulting `dev` commit.

For a deeper look at what a PR can check from Git and where live validation belongs, see [Static validation for Fabric items](../../reference/static-fabric-validation.md).

The build policy in this unit applies to `dev`. When `main` becomes the Prod release branch, you will add its own policy and reuse this CI pipeline. [Unit 10 branch policies](../../section-04-release-automation/unit-10-release-to-prod/README.md#2-protect-main-and-promote-the-tested-code-commit).

[Previous unit](../unit-05-make-a-local-feature-change/README.md) · [Tutorial index](../../README.md) · [Next unit](../../section-04-release-automation/unit-07-configure-and-preview-release/README.md)
