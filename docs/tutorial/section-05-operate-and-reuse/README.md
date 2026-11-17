# Section 5 — Operate, recover and reuse

Publish a tested Tiny Sales baseline once, then use it as the starting point for an advanced lab. Use your team's dedicated Code, Data and Reporting repos and assigned Fabric workspaces. Use the Test and Prod connections already authorized for your pipelines. If your team has already published the baseline, go to [Start an advanced lab from the baseline](#start-an-advanced-lab-from-the-baseline).

## Publish the Tiny Sales baseline

### 1. Reconcile the release tooling into Code dev

Start from the completed [Unit 10 release](../section-04-release-automation/unit-10-release-to-prod/README.md). Open your Prod tooling PR and the Test manifest used for promotion. The PR identifies which tooling changes to bring back. The manifest records the Code, Data and Reporting revisions used for that release.

1. In a clean **Code** checkout, start a feature branch from the current `dev` in your team's Code repo.

   ```powershell
   git status --short
   git fetch origin
   git switch -c feature/reconcile-release-tooling origin/dev
   ```

   Start when `git status --short` prints nothing. Fetch refreshes the remote branch tips used here. [Git basics](../pre-reads/git-basics.md#get-updates-and-handle-overlaps).

2. Compare the Unit 10 tooling PR with this branch. Bring over its Prod wrapper and environment settings, the Prod Python entry point, and any shared publishing changes from that PR. If those are the only changes on `main` that belong on `dev`, use `git merge origin/main`. Otherwise, bring over the specific reviewed tooling changes and resolve differences with your reviewer. Check that the Tiny Sales definitions and the Data and Reporting pins still match the intended Unit 10 baseline. If you already reconciled the tooling, open that PR and confirm its result. [Unit 10 tooling files](../section-04-release-automation/unit-10-release-to-prod/README.md#3-prepare-the-prod-release-pipeline) · [Conflict recovery](../auxiliary/aux-01-recover-from-source-conflicts/README.md).
3. Review the diff, push the feature branch with `git push -u origin feature/reconcile-release-tooling`, and open a Code PR into `dev`. Complete it after required CI and review. You can use this description:

   ```markdown
   ## Change
   Reconcile the Unit 10 release tooling into Code dev for the advanced labs.

   ## Validation
   - Reviewed the Unit 10 tooling PR: <link>
   - Compared the workload definitions and Data and Reporting pins with the Unit 10 baseline: <result>
   - Required Notebook CI: <run link>
   ```

**Expected result** The shared publisher and both release entry points are on Code `dev`. The reconciled commit is ready to validate in Test.

### 2. Validate the reconciled commit in Test

1. In the existing **Tiny Sales - Test Release** pipeline, queue from Code **dev** with **Publish to Test after preflight** selected. Use your assigned Test targets and the authorized Test connection. Wait for the publish to finish and open **test-release-evidence → test-release.json**.
2. Confirm `status: published`, the Test workspace IDs and the selected **Test** value set. Keep the full Code hash from `verified_source_revisions.code` and compare the Data and Reporting hashes against the pins in that Code revision's release mask. Compare the physical IDs of the existing items with your earlier Test release.
3. Run `run_sales` in Code Test, run `validate_release`, and open the Test report. Confirm **357.20** gross revenue, **204.70** recognized revenue and the intended Test model binding. Retain the run and smoke evidence together. [Verify the Test release and runtime](../section-04-release-automation/unit-09-release-to-test/README.md#4-review-what-changed).

**Expected result** You have Test deployment and runtime evidence for the exact reconciled Code commit. The Unit 10 Prod run is separate provenance. Record its link and the original source revision it deployed.

### 3. Create and push an annotated Git tag

A tag gives an exact commit a name you can retrieve after the `dev` branch advances. An **annotated tag** also holds a message. Use that message as the release note. The Code commit includes the release mask, which pins the Data and Reporting commits for the same source snapshot. [Git tags in Azure Repos](https://learn.microsoft.com/en-us/azure/devops/repos/git/git-tags?view=azure-devops).

1. Save a plain Markdown note on your computer outside the Code checkout. Fill in this example with your team's evidence:

   ```markdown
   # Tiny Sales v1.0.0

   - Purpose: starting version for the advanced labs
   - Code: <validated full SHA>
   - Data and Reporting: <repo names and full pins in the tagged release mask>
   - Reconciliation PR and required CI: <links>
   - Test publish and smoke result for this Code revision: <links and outcome>
   - Unit 10 Prod publish and its original Code revision: <link and full SHA>
   - Live prerequisites: <assigned workspaces, registered Test pipeline, authorized Test connection and seeded Tiny Sales data>
   ```

2. Confirm the Code hash from the new Test manifest is a commit on your fetched `dev` history.

   ```powershell
   git fetch origin
   $baselineCommit = Read-Host 'Paste the full Code SHA from the new Test manifest'
   git show --no-patch --oneline $baselineCommit
   git merge-base --is-ancestor $baselineCommit origin/dev
   $LASTEXITCODE
   ```

   Compare the commit with your reviewed reconciliation and runtime evidence. An exit code of `0` means the exact hash is in `origin/dev` history. Investigate a different result before tagging. [Check which commit is being released](../pre-reads/git-basics.md#check-which-commit-is-being-released).
3. Create `tiny-sales-v1.0.0` on that commit in the **Code** repo and push that tag. If your team has already published the tag for this baseline, verify its hash and note in **Repos → Tags** and use the existing tag.

   ```powershell
   $releaseNotePath = Read-Host 'Enter the full path to your release note file'
   git tag -a tiny-sales-v1.0.0 $baselineCommit -F $releaseNotePath --cleanup=verbatim
   git show --no-patch refs/tags/tiny-sales-v1.0.0
   git push origin refs/tags/tiny-sales-v1.0.0
   ```

   `-a` creates an annotated tag, `-F` reads the message from your note file, and `--cleanup=verbatim` keeps its Markdown intact. Review the displayed commit and note before running the push. In Azure DevOps, open **Repos → Tags** and select the Code repo. Open the tag and check its Code hash and note. If you are retrying a push and already have the local tag, inspect it with the same `git show` command before you retry. If Azure Repos denies tag creation, ask your repo administrator to publish the reviewed tag. [Git tag commands](../pre-reads/git-basics.md#publish-and-use-a-git-tag).

Keep the run evidence for as long as the labs need it. Azure Pipelines run retention also controls its artifacts. Keep the recorded source hashes and smoke result in the note. [Run and artifact retention](https://learn.microsoft.com/en-us/azure/devops/pipelines/policies/retention?view=azure-devops).

**Expected result** The team can find the baseline tag in Azure Repos, recover the three source revisions, and open the evidence that explains what was verified.

## Start an advanced lab from the baseline

1. In a clean **Code** checkout, fetch the tag and compare its source tree with the current team `dev` tree.

   ```powershell
   git fetch origin
   git fetch origin tag tiny-sales-v1.0.0
   git rev-parse 'refs/tags/tiny-sales-v1.0.0^{commit}'
   git diff --name-status refs/tags/tiny-sales-v1.0.0 origin/dev
   ```

   The third command prints the tagged **commit** hash for comparison with the release note. The last lists files whose contents differ. If it prints no paths, the current `dev` files match the baseline.
2. If your team has already changed its Code `dev` in an advanced lab, review the listed differences together before doing the next lab. Restore the relevant baseline files through a PR into `dev`. [Restore Code files for another lab](#restore-code-files-for-another-lab).
3. In your assigned Test workspaces, confirm the expected Tiny Sales items, data and pipeline permissions. Use the baseline note and its Test manifest to compare the live setup. The tag selects Git revisions. The manifest and the Fabric runtime checks tell you what the pipeline deployed and what is in use. If needed, re-establish the Test baseline using the publish and smoke steps above.

Choose either lab. Each has its own feature branch starting at the tag.

- [Unit 11 · Diagnose and recover a failed Test release](unit-11-recover-a-test-release/README.md)
- [Unit 12 · Use a shared deployment starter](unit-12-shared-deployment-starter/README.md)

### Restore Code files for another lab

Work in a new feature branch from current `origin/dev`, starting with a clean checkout. For each path you agreed to restore, substitute its actual repo-relative path in the second line. A tracked file introduced by a lab is staged for removal if that path is absent from the tag.

```powershell
git switch -c feature/restore-tiny-sales-baseline origin/dev
git restore --source=refs/tags/tiny-sales-v1.0.0 --staged --worktree -- 'path/from-the-diff'
git diff --cached --name-status
```

Review the staged changes, commit them and complete a PR into `dev` after CI. Fetch again and compare `origin/dev` to the tag. Check any remaining differences that could affect the lab. Inspect Fabric separately, especially if the earlier lab created an extra item or changed data.

## Completion checkpoint

- [ ] The Code tag resolves to the reconciled commit verified by the new Test run.
- [ ] The release note identifies the Data and Reporting pins, Test evidence, Unit 10 Prod evidence and live prerequisites.
- [ ] You can explain which state you get from Git and what you check in Fabric before a live lab.

[Closing recap](../closing-recap.md) · [Tutorial index](../README.md)
