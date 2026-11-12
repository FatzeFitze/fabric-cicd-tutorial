# Git basics

**Allow 10–15 minutes, including the optional local practice.**

Git is a version control system. It records changes to files so you can see what changed, compare versions, work on a change in isolation and combine work with teammates. Teams use it for code, configuration and documentation. A service such as Azure Repos, GitHub or GitLab can host a shared copy and provide a place to review changes.

## Where your work lives

| Term | What it means |
| --- | --- |
| **Repository (repo)** | The project files and the Git history that describes how they evolved. |
| **Working copy** | The files you see and edit on your computer. Saving a file edits this copy. |
| **Staging area** | The changes you've selected for your next commit. This lets you record one coherent change even if you have several edits in progress. |
| **Commit** | A recorded snapshot of the project's tracked files, with a message and a commit ID. Use the ID to refer to one exact revision. |
| **Branch** | A named pointer to a commit. New commits advance the current branch. Names such as `main` or `dev` usually identify shared branches by team convention. |
| **Remote** | A repository you exchange commits with. When you clone a shared repo, Git normally calls that remote `origin`. |

Suppose you're adding a column to a data export. You can create a branch from the current shared version, make the change, and record it on that branch. Meanwhile, a teammate can update the documentation on a different branch. Later, Git can combine the two changes. [Pro Git on recording changes](https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository) · [Pro Git on branches and merges](https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging).

## Follow a change from laptop to review

1. **Clone** the shared repository with `git clone` to get a local copy and history. Before branching, check that you're on the intended base branch and that it is up to date. For a team using `dev`, run `git switch dev` followed by `git pull --ff-only`.
2. **Create a feature branch** with `git switch -c feature/add-export-column`. It starts at your current commit. Choose a name that describes the change.
3. **Edit and inspect.** Run `git status` to see changed and untracked files. Use `git diff` to see unstaged changes to tracked files. An IDE's Git view can show the same information.
4. **Stage and commit.** Use `git add <file>` to select the changes, then `git diff --staged` to review what you'll commit. Record it with `git commit -m "Add warehouse column to export"`. If you edit a file after staging it, run `git add` again to include the new edit.
5. **Push** with `git push -u origin feature/add-export-column` to share your branch. The `-u` option establishes which remote branch your local branch tracks for future operations.
6. **Open a pull request (PR)** in your team's repository host. Choose your feature branch as the source and the team's shared branch as the target. Explain the change and how you checked it. The host displays the diff, review comments and any configured automated checks.
7. **Complete the PR** after review and checks. The host integrates the change using the team's chosen strategy. A merge commit can retain both lines of history, while a squash merge records the feature as one new commit on the target branch.

Your new branch and commits live locally until you push them. The pull request is part of the hosting service. Completing it updates the target branch. Deployment happens through whatever separate release process the team uses. [Azure Repos pull requests](https://learn.microsoft.com/en-us/azure/devops/repos/git/pull-requests?view=azure-devops).

## Get updates and handle overlaps

**Fetch** downloads new commits and refreshes your view of remote branches. **Pull** fetches and integrates changes into your current branch. Before pulling, check which branch you're on and inspect any local edits. On a local copy of a shared branch, `git pull --ff-only` updates it when it can move straight to the remote revision. If it reports divergent histories, review what's on each side and follow your team's integration workflow.

A **merge conflict** means Git needs a person to decide how two changes fit together. If two branches edited the same line of a calculation, inspect both versions and decide what the final behavior should be. Edit the affected file, check the result, stage the resolution and finish the merge. When an already shared commit needs to be undone, `git revert` records an inverse change as a new commit and keeps the history visible. [Pro Git on remotes](https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes) · [Git revert](https://git-scm.com/docs/git-revert).

## Check which commit is being released

In Unit 10, the Test manifest gives you a full commit hash. `HEAD` identifies your current checkout. `origin/dev` and `origin/main` show the branch tips as of your last fetch. Run the commands in your local Code repository.

| Command | What it does |
| --- | --- |
| `git fetch origin` | Refreshes your view of the shared repo and downloads commits. Your current branch and working files stay as they are. |
| `git rev-parse origin/dev` or `git rev-parse origin/main` | Prints the full hash at that branch tip. Use `git rev-parse HEAD` for the commit checked out locally. |
| `git branch release/unit-10 $testedCodeCommit` | Creates a local branch at the commit hash stored in the PowerShell variable `$testedCodeCommit`. Your checkout stays on its current branch. |
| `git push origin release/unit-10` | Publishes that local branch so you can select it as a PR source in Azure Repos. |
| `git merge-base --is-ancestor $testedCodeCommit origin/main` | Checks whether the exact tested commit is already in `main` history, including when it is the tip. In PowerShell, read `$LASTEXITCODE` immediately after the command. `0` means yes, `1` means no, and a higher value indicates a Git error. |
| `git switch -c feature/prod-release origin/main` | Creates and switches to a local feature branch starting at the fetched `main` commit. |

A merge commit can retain the exact tested hash in the target branch's history. Squashing the same file changes can produce a different hash. Unit 10 uses the original hash to retrieve the exact tested snapshot even after additional commits land on `main`.

## Try it in a disposable local folder

In PowerShell, go to a folder where you can create `git-practice`, then run the following. If Git asks for an author name and email, configure those in this repo with `git config --local user.name "Your Name"` and `git config --local user.email "you@example.com"`, using your approved details. Then retry the commit.

```powershell
mkdir git-practice
cd git-practice
git init
Set-Content -Path notes.txt -Value "Inventory notes" -Encoding ascii
git add notes.txt
git commit -m "Add notes"
git switch -c feature/stock-note
Add-Content -Path notes.txt -Value "Stock counts are checked daily" -Encoding ascii
git diff
git add notes.txt
git diff --staged
git commit -m "Document stock checks"
git log --oneline -2
```

Look for the second line in the diff, then the two commits in the log. Try `git switch -` to return to your previous branch and open `notes.txt` again. The file should show the original one-line version. [VS Code source control](https://code.visualstudio.com/docs/sourcecontrol/overview).

[Back to the pre-read guide](README.md)
