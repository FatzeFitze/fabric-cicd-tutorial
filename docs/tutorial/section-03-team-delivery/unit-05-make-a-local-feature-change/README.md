# Unit 5 — Make a local feature change

**Time:** approximately 35–45 minutes, with local tools already installed.  
**You will create:** a local feature branch and draft Azure Repos pull request changing how Tiny Sales handles returned orders. Dev stays on the previous source/runtime baseline.

## What you will learn

- Clone your existing Fabric source into an ordinary local Git working folder.
- Edit an exported notebook in an IDE while preserving its metadata and identity.
- Review, commit and push a small feature without changing shared Dev.
- Describe what is checked locally and what still needs CI and Fabric execution.

## Before you begin

Complete [Unit 4](../unit-04-connect-orchestration-configuration-and-reporting/README.md). Restore its original fixture prices, expected totals and configuration, run successfully and capture the final Code/Reporting definitions in Git. Data Dev and the report should show **342.20** revenue. Keep your Unit 4 solution record.

You need **Git**, **Visual Studio Code** and access to clone, create a branch and open a PR in your assigned **Azure DevOps Code repository**. Install/sign in using your organization's approved method before this exercise. Run `git --version` in PowerShell to confirm Git is available. No local Spark installation, Power BI Desktop or Fabric VS Code extension is required.

Continue the existing pilot's three role repositories and `dev` integration branch. Only the **Code repo** changes here; Data and Reporting retain their recorded source revisions. Do not clone the GitHub tutorial preparation repo as your participant solution or reorganize workspace/repo bindings. If your assigned layout differs, use its confirmed Code folder and integration branch with the facilitator.

Keep a private copy of the [feature record](resources/feature-record.md). Read the short [logical/physical ID reference](../../reference/fabric-item-identities.md); you will preserve the existing notebook's logical identity during the edit.

## Understand the source-to-runtime boundary

```mermaid
flowchart LR
    D["Azure Repos: dev baseline"] -->|clone / branch| L["Local feature files in VS Code"]
    L -->|commit + push| F["Azure Repos: feature branch"]
    F -->|propose change| P["Draft PR into dev\nheld for Unit 6 checks"]
    D -. current connected branch .-> W["Shared Code Dev\nunchanged in this unit"]
```

A local branch isolates **source files**, not Fabric runtime data. Saving these files changes your local checkout; a commit records that local state; pushing shares the feature branch. None of those actions switches the workspace branch, deploys the notebook or runs it.

Open the **cloned folder** in VS Code. Fabric's **Open in VS Code / VFS** experience is a different route: its saves synchronize to the remote workspace. We use ordinary Git files here so saving an unfinished feature does not publish it into shared Dev. See [Fabric VFS behavior](https://learn.microsoft.com/en-us/fabric/data-engineering/author-notebook-with-vs-code-vfs-mode).

## 1. Confirm and retain the integration baseline

1. In **Code Dev → Source control**, confirm Unit 4's final items are synchronized with `dev`. Resolve any unexplained changes with the facilitator before continuing; do not discard them or overwrite incoming content.
2. Save and close open notebook editors. For this exercise, coordinate a pause in UI changes to `build_sales` while you develop locally. If you are a pair, follow one local checkout together.
3. In **Azure DevOps → Repos → Files**, select your **Code repo** and branch **`dev`**. Confirm it contains the actual exported `build_sales` notebook, Variable Library and pipeline.
4. Record the full Code `dev` commit ID and retain the Data/Reporting revisions from Unit 4. Check **Code Dev → Workspace settings → Git integration** still points to that Code repo and `dev` without changing the connection.

**Expected result:** You have a known starting revision and an unchanged shared Dev mapping. A Git branch name alone is not a fixed source snapshot.

## 2. Clone the Code repository and open it locally

1. In **Azure DevOps → Repos → Files → Clone**, copy the Code repository's **HTTPS clone URL**. Use the actual assigned project/repo URL.
2. Choose a local development parent folder outside cloud-synchronized folders. Open PowerShell there. Replace the example URL below before running these commands; `tiny-sales-code` must be a new folder:

   ```powershell
   git clone "YOUR_CODE_REPOSITORY_HTTPS_URL" tiny-sales-code
   Set-Location tiny-sales-code
   git remote -v
   git switch dev
   git pull --ff-only origin dev
   git status --short
   git rev-parse HEAD
   ```

3. Complete the approved organizational sign-in if requested. Do not embed tokens in the clone URL or commit credentials. Confirm `origin` is your participant Code repo, the status is clean and the commit matches your recorded baseline. If `dev` has advanced, inspect the new commits and reconcile your baseline before continuing; if pull fails, preserve the checkout and diagnose it instead of forcing an overwrite.
4. In **VS Code → File → Open Folder**, select this new **`tiny-sales-code`** folder. Open **Terminal → New Terminal** and confirm it is at the repository root with `git status`.
5. Check the author values using `git config user.name` and `git config user.email`. If missing or wrong, set your own approved author details for **this repo only**:

   ```powershell
   git config --local user.name "YOUR_NAME"
   git config --local user.email "YOUR_APPROVED_COMMIT_EMAIL"
   ```

**Expected result:** VS Code shows ordinary files from your participant Code repo. The local clone contains source/history; it is not a copy of the lakehouse's runtime data. See [Azure Repos cloning](https://learn.microsoft.com/en-us/azure/devops/repos/git/clone?view=azure-devops).

## 3. Create the feature branch and locate the exported notebook

1. In the VS Code PowerShell terminal, create the branch:

   ```powershell
   git switch -c feature/exclude-returned-orders
   git branch --show-current
   ```

2. In Explorer, locate the notebook item folder whose `.platform` identifies **Notebook / build_sales**. It is normally `build_sales.Notebook`. Open its existing **`notebook-content.py`** as a text file. If your actual export is different, retain its filenames and ask the facilitator to check the representation before converting anything.
3. Read the sections for parameters, target guard, parameter validation, fixtures, transformation and persistence. Fabric's exported file contains cell delimiters and metadata as well as Python. Retain those sections; do not replace the whole file with the tutorial's initial starter or convert it to `.ipynb`.
4. Set a terminal variable to the actual repository-relative file path, including any assigned parent folder. For the current root-mapped Code repo:

   ```powershell
   $notebookFile = 'build_sales.Notebook/notebook-content.py'
   ```

5. Read the adjacent `.platform`'s `config.logicalId` and record it. Leave `.platform`, resource references, notebook settings, parameter/cell markers, workspace map and lakehouse metadata unchanged. A missing physical ID in `.platform` is expected; see the [ID reference](../../reference/fabric-item-identities.md).

**Expected result:** The feature branch is local, and you can identify the existing notebook source and logical ID. Code Dev remains connected to `dev`; do not switch it to the feature branch. See [notebook Git representation](https://learn.microsoft.com/en-us/fabric/data-engineering/notebook-source-control-deployment#notebook-representation-in-git).

## 4. Implement the returned-order rule

The fictional business now wants **revenue to exclude returned orders**. Keep all six rows for traceability and preserve gross revenue. A returned order contributes **0.00** to `revenue`; it is not a negative sale in this sample. The existing report's **Total Revenue** measure can keep summing the same column.

1. In the transformation section, find the existing line `.withColumn("revenue", F.col("gross_revenue"))`. Replace **that one chained call** with:

   ```python
   .withColumn(
       "revenue",
       F.when(
           F.col("is_returned"), F.lit(0).cast("decimal(12,2)")
       ).otherwise(F.col("gross_revenue")),
   )
   ```

2. Update the adjacent business-rule comment to explain that returned orders remain in the table but contribute zero revenue. Leave fixtures and the table schema unchanged.
3. In `EXPECTED_METRICS`, change **only** the `revenue` value to **`Decimal("189.70")`**. Keep `gross_revenue = Decimal("342.20")` and all count/invalid-row checks. Keep `validate_sales` before and after the write.
4. Change the final success message's wording from **matches the baseline** to **matches the expected metrics**, retaining the `UNIT_01_PASS` marker. Save the local file.
5. Review the expected result independently. Returned orders O003 and O006 contribute gross amounts 12.50 and 140.00. Therefore **342.20 − 12.50 − 140.00 = 189.70**. The future runtime checks must show:

   | Result | Before | After feature execution |
   | --- | ---: | ---: |
   | Rows / distinct orders | 6 / 6 | 6 / 6 |
   | Quantity / returned orders | 13 / 2 | 13 / 2 |
   | Gross revenue | 342.20 | 342.20 |
   | Revenue / report Total Revenue | 342.20 | 189.70 |
   | Invalid rows | 0 | 0 |

**Expected result:** One existing notebook definition contains the new calculation and matching monetary expectation. **189.70 is an expected result, not an executed Fabric result yet.** Do not use Run Python File on the export: this notebook needs Fabric's Spark/session utilities. Useful automated checks follow in Unit 6; integration/runtime checks follow the selected deployment path.

## 5. Review and commit the local change

1. Open VS Code's **Source Control** view and select the changed notebook to inspect the side-by-side diff. Confirm the calculation, expected revenue, comment and success-message wording changed; generated metadata, guards, parameters and fixtures did not.
2. In the terminal, check the scope and whitespace:

   ```powershell
   git diff --stat
   git diff --check
   git diff -- $notebookFile
   ```

   No output from `git diff --check` means it found no whitespace/conflict-marker errors. It does **not** prove the calculation, notebook structure, Spark execution or bindings are correct. If a long diff opens in a pager, press `q` to return.
3. Stage **only this file**, then inspect what will be committed:

   ```powershell
   git add -- $notebookFile
   git diff --cached --stat
   git diff --cached -- $notebookFile
   ```

4. When the staged diff matches the intended scope, commit and record its full ID:

   ```powershell
   git commit -m "Exclude returned orders from Tiny Sales revenue"
   git rev-parse HEAD
   git status --short
   ```

**Expected result:** A local feature commit with a clean working folder and unchanged `.platform`. The commit exists on your computer; it has not yet been shared or deployed. See [VS Code source control](https://code.visualstudio.com/docs/sourcecontrol/overview) and [Git diff checks](https://git-scm.com/docs/git-diff).

## 6. Push the feature and open a draft PR

1. Share the feature branch:

   ```powershell
   git push --set-upstream origin feature/exclude-returned-orders
   ```

2. Open your **Code repo → Repos → Pull requests → New pull request** in Azure DevOps. Set **source = `feature/exclude-returned-orders`** and **target = `dev`** explicitly; do not accept `main` just because it is offered.
3. Use the title **Exclude returned orders from Tiny Sales revenue**. Explain that returned rows stay present, `revenue` becomes zero for them, gross revenue/schema are unchanged and expected revenue becomes 189.70. Under validation, state **diff reviewed; whitespace check passed; CI and Fabric runtime validation pending**. Do not claim a notebook run.
4. Select the arrow beside **Create → Create as draft**. Open the resulting PR's **Files** and **Commits** tabs. Confirm only the intended notebook file changed, its logical ID was preserved and the feature commit is present. Record the PR URL and source/target branches.
5. Leave it **Draft**. Do not Complete, enable auto-complete or merge. Drafts do not automatically run Azure Repos build-validation policies; Unit 6 will add the check, publish the PR and exercise validation before merge. See [draft PR behavior](https://learn.microsoft.com/en-us/azure/devops/repos/git/pull-requests?view=azure-devops#create-draft-prs).

**Expected result:** The feature is available for review without advancing `dev`. In a productive team, independent review follows the required control model; preparing a solo draft here does not demonstrate that boundary is enforced.

## 7. Confirm what has stayed unchanged

1. Read **Code Dev → Git integration / Source control** without editing or updating items. Its branch should still be **`dev`** and its notebook should retain the original calculation. A feature-branch push alone should not appear as an incoming update to `dev`.
2. Compare the persisted Data Dev/report baseline with Unit 4's final **342.20**. No feature execution has occurred. If it differs, investigate another writer/run or an unrestored fixture rather than treating it as evidence that pushing deployed your feature.
3. Record the local folder, integration base commit, feature commit, notebook path/logical ID, retained Data/Reporting revisions and draft PR in the [feature record](resources/feature-record.md).

**Expected result:** You can explain four distinct states: local feature source, pushed feature source, unchanged Dev definition/configuration and unchanged runtime data. No workspace branch switch, feature workspace, deployment or report edit was needed.

## If something does not work

| Symptom | What to check |
| --- | --- |
| Clone/push fails authentication | Use the assigned organization/project and approved sign-in; confirm repo contribution/branch permissions with the facilitator. Never paste credentials into source. |
| Git asks for an author | Set repository-local `user.name` and `user.email`; author metadata is separate from authentication. |
| Branch already exists | Check whether you are resuming this exercise before creating another branch; retain existing work instead of deleting it. |
| Export file is missing or different | Confirm the Code repo/branch, Unit 4 Git capture and `.platform` item type/name. Do not invent a replacement export or copy the starter over the item. |
| The diff changes every line | Check editor encoding/line endings/formatting settings. Preserve the file format and narrow the edit before committing. |
| `.platform` or bindings changed | Stop and inspect the cause; this feature requires business-source edits only. Preserve unrelated work before correcting the scope. |
| Local Run fails on Spark or notebookutils | This is exported Fabric notebook source, not a standalone local program. No local notebook execution is required here. |
| Workspace shows a conflict or unexpected update | Stop competing edits, preserve both versions and identify the connected branch/revisions. Use the [conflict reference](../../auxiliary/aux-01-recover-from-source-conflicts/README.md); do not discard workspace changes to finish this unit. |
| PR targets `main` or changes unrelated items | Correct the target to the confirmed integration branch and inspect the branch base/file list before proceeding. |
| Draft PR has no automatic validation | Expected for a draft. Unit 6 adds and exercises the check; a missing result is not a passed test. |

## Completion checkpoint

- [ ] Your local clone points to the assigned Azure DevOps Code repo.
- [ ] `feature/exclude-returned-orders` contains one reviewed notebook-source feature; its logical ID, metadata, fixtures and schema are preserved.
- [ ] The expected new revenue is 189.70; gross revenue stays 342.20, with unchanged row/quantity/return counts.
- [ ] The feature commit is pushed and a **draft PR into `dev`** remains open, without auto-complete.
- [ ] Code Dev stays on `dev`, with its previous definition and 342.20 runtime baseline.
- [ ] The feature record distinguishes source inspection from unperformed CI/runtime validation.

Keep the local checkout, feature branch and draft PR for Unit 6. Retain approximate time and any sign-in, export-format or UI differences. Next we will introduce reusable validation components and PR checks before integration; their purpose is to test this change, not merely produce a green pipeline.

## References

- [Clone an Azure Repos repository](https://learn.microsoft.com/en-us/azure/devops/repos/git/clone?view=azure-devops).
- [Notebook source control and deployment](https://learn.microsoft.com/en-us/fabric/data-engineering/notebook-source-control-deployment).
- [VS Code source control](https://code.visualstudio.com/docs/sourcecontrol/overview).
- [Azure Repos draft PRs](https://learn.microsoft.com/en-us/azure/devops/repos/git/pull-requests?view=azure-devops#create-draft-prs).
- [Logical versus physical IDs](../../reference/fabric-item-identities.md).

[Previous: Unit 4](../unit-04-connect-orchestration-configuration-and-reporting/README.md) · [Tutorial index](../../README.md)
