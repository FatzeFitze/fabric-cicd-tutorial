# Publish this preparation repository to GitHub

Published on 28 October 2026 to [the destination repository](https://github.com/FatzeFitze/fabric-cicd-tutorial). `origin` and repository-local author settings are configured, Git authentication succeeded, and `main` was pushed with upstream tracking. The instructions below are retained as a reference for initial setup; do not repeat initialization against the existing remote.

## Guided route

1. Sign in to the intended account and open [GitHub's new repository form](https://github.com/new).
2. Select the intended owner and a repository name such as `dna-fabric-days`.
3. Choose **Private** for this preparation repository.
4. Leave creation of a README, `.gitignore`, and license disabled; the local repository already has content.
5. Create the repository and copy its HTTPS URL from the setup page.
6. Provide that URL and the commit author name/email to the assistant. A GitHub no-reply email from your account's email settings is suitable if preferred.

The assistant can then configure author details locally for this repository, create the first commit, add the remote, and push. If Git asks for authentication, complete the supported sign-in flow; do not paste passwords or tokens into chat. Installing a GitHub plugin is optional for this browser-and-Git route.

## Equivalent local actions

These commands are a reference; placeholders must be replaced before execution. Run them in this exact repository folder:

```powershell
Set-Location -LiteralPath 'C:\Users\matth\Documents\Codex\2026-10-28\ok-now-it-is-time-to-2\outputs\dna-fabric-days'
git config --local user.name 'YOUR COMMIT AUTHOR NAME'
git config --local user.email 'YOUR COMMIT AUTHOR EMAIL'
git add README.md AGENTS.md .gitignore docs
git commit -m 'docs: establish Fabric Days workshop scope and DataOps baseline'
git remote add origin 'https://github.com/YOUR-ACCOUNT/YOUR-REPOSITORY.git'
git push -u origin main
```

Do not run `git init` again or clone an empty remote over this folder. Before adding `origin`, check whether it already exists. After publication, verify the expected files and commit on GitHub and keep this folder as the working copy. Later edits can be committed and pushed from it.

Source: [GitHub's guide to adding locally hosted code](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github?platform=windows) [S15].
