# Auxiliary unit — Recover from source conflicts

**Optional companion to local development in Unit 5.** This entry point introduces the recovery approach; the intentional-conflict exercise will be added after its rehearsal. It is outside the required workshop completion path.

## What you will learn

- Distinguish a Git merge conflict from a Fabric workspace synchronization conflict and an open-editor version warning.
- Preserve both versions before choosing or combining changes.
- Return to one reviewed source state and one controlled Dev publisher.

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

Do not use a force push, workspace-wide Undo or disconnect/reconnect as the default recovery shortcut. Those actions can replace unrelated work. A stale editor may only need a reopen after its content is preserved; first identify which situation applies.

## Local IDE development and shared Dev

Editing a cloned repository on a feature branch changes local source. It does not create an isolated Fabric runtime or automatically publish that branch into Dev. Coordinate any runtime test that uses shared Dev.

The Fabric VS Code extension also offers workspace-connected editing. In **VFS mode**, saving edits synchronizes them to the remote workspace; that is a different workflow from editing an isolated Git checkout. Know which files you opened before saving. The core local-feature exercise uses an ordinary cloned Git working folder.

## References

- [Fabric conflict types and recovery options](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/conflict-resolution).
- [Fabric Git integration process](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-integration-process).
- [Fabric notebook VFS editing in VS Code](https://learn.microsoft.com/en-us/fabric/data-engineering/author-notebook-with-vs-code-vfs-mode).

[Tutorial index](../../README.md)
