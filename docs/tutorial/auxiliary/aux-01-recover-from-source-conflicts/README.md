# Auxiliary unit — Recover from source conflicts

**Optional companion to Unit 5.** Read this when a local branch or shared Dev workspace has overlapping changes. Use the scenario to practise choosing a recovery path before applying it to a live conflict.

## What you will learn

- Distinguish a Git merge conflict from a Fabric workspace synchronization conflict and an open-editor version warning.
- Preserve both versions before choosing or combining changes.
- Return to one reviewed source state and one controlled Dev publisher.

Two teammates worked on the same notebook. One saved a change in Fabric while the other merged an edit in Azure Repos. A third person still has the notebook open in their browser and sees a version warning. Before anyone refreshes, ask what each person stands to lose. An unsaved edit, a saved workspace item and a committed Git change need different ways of being preserved.

Start where the warning appeared. Check whether Git is merging two histories, Fabric Source control is comparing two saved definitions, or an editor has an older version open. Use that answer to pick the recovery path below.

## Understand which conflict you have

| Situation | Where it appears | What needs reconciling |
| --- | --- | --- |
| Two Git branches change overlapping source | Local Git/IDE or Azure Repos PR | The changes in the two branches |
| A Fabric item changes in both its workspace and connected Git branch since synchronization | Fabric Source control | The saved workspace item and incoming Git definition; the conflict can be at item level even when edits affect different lines |
| An open editor reports a newer version after another editor or synchronization changed the item | Notebook/browser editor | The editor's content and current saved version; the warning alone does not prove a Git merge conflict |

## Use a recovery sequence that preserves work

1. Pause edits, Git updates and automated publishing to the affected Dev items. Identify the workspace, connected repo/folder/branch, last synchronized revision and incoming revision.
2. Preserve each version and any unsaved editor content before a refresh, Undo or choice that replaces content. Record which changes you intend to retain. Close editors only after preserving that work.
3. Compare the versions. If only one is needed, Fabric's conflict UI can choose that version per item. **Accept incoming** replaces the workspace version; **Keep current content** retains workspace content as uncommitted changes. Neither automatically combines both sets of edits.
4. If both changes matter, preserve workspace changes on a recovery branch from the last synchronized state, following the linked Microsoft procedure. Combine and review the source changes in Git, retain generated item metadata/identities, validate and merge through the agreed PR process. Coordinate branch changes with the team: they affect the shared workspace.
5. Reconcile Dev to the agreed branch/revision using the selected publishing mechanism, then inspect source status and run the relevant checks. A completed merge does not itself update or validate Fabric runtime state.

Use the smallest action that addresses the conflict. A stale editor may only need a reopen after you preserve its content. A force push, workspace-wide Undo or disconnect and reconnect can affect unrelated work.

## Local IDE development and shared Dev

Your feature branch gives you a place to edit local source. The team still shares the Dev runtime and its data. Agree who will apply changes and run tests when an exercise uses shared Dev.

The Fabric VS Code extension also offers workspace-connected editing. In **VFS mode**, saving edits synchronizes them to the remote workspace; that is a different workflow from editing an isolated Git checkout. Know which files you opened before saving. The core local-feature exercise uses an ordinary cloned Git working folder.

## Check that the team recovered the right thing

Imagine the two edits changed different cells. Before choosing a version in Fabric, ask where the other change will be kept and who will review the combined result. After the merge, have the person coordinating the Dev update point to the agreed commit, confirm what Fabric synchronized, and show the relevant check or run. A completed PR and a synchronized workspace are two observations you can verify independently.

Use the same reasoning in Unit 8 if you find incoming Git changes alongside a teammate’s work in Dev. The immediate goal is to preserve both contributions so the team can decide together what should go live.

## References

- [Fabric conflict types and recovery options](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/conflict-resolution).
- [Fabric Git integration process](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-integration-process).
- [Fabric notebook VFS editing in VS Code](https://learn.microsoft.com/en-us/fabric/data-engineering/author-notebook-with-vs-code-vfs-mode).

[Unit 5 local feature workflow](../../section-03-team-delivery/unit-05-make-a-local-feature-change/README.md) · [Unit 8 shared Dev sync](../../section-04-release-automation/unit-08-publish-shared-dev/README.md#6-optionally-sync-and-test-in-shared-dev) · [Tutorial index](../../README.md)
