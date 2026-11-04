# Optional source-conflict exercise preparation

4 November 2026. Organizer requested local IDE/Git development and a deliberate conflict to prepare learners for combined workspace/Git authoring. Unit 5 already introduces the local feature workflow. The [auxiliary unit entry point](../tutorial/auxiliary/aux-01-recover-from-source-conflicts/README.md) now records concepts and recovery guidance; its intentional-conflict steps are not authored or tenant-rehearsed. No additional required workshop hours are allocated.

## Rehearsal design

After Unit 5's clone/branch/diff workflow is proven, prepare a 15–20 minute optional exercise. Use one developer sequentially, a harmless Markdown-only edit to a disposable Dev notebook, and a recorded clean source baseline. Avoid modifying business logic, generated logical IDs or environment bindings. Do not use Test/Prod or create feature workspaces.

1. First show a small local Git merge conflict with two branches editing the same text. Preserve and combine both intended contributions, inspect the result and complete the merge. This isolates Git recovery from cloud state.
2. For the Fabric case, begin with a synchronized disposable notebook. Save one text change in the workspace without committing; commit another to the same notebook's connected source from a local checkout. Capture the exact Source control state and diff/compare UI. Distinguish an item conflict from a line-level merge conflict and from Unit 2's stale-editor warning.
3. Rehearse preserving the workspace version on a branch from the last synchronized revision, merging both changes locally through a reviewed PR, returning the workspace to the intended integration branch and updating it. Verify no unrelated item/source mapping changed. Follow the current Microsoft procedure; record exact menu labels and branch/permission requirements before writing participant clicks.
4. Verify both text changes survive in source and the reopened notebook. Rerun the unchanged business checks if the sample notebook is used. Record final branch/revision and clean Source control state.

Pause competing publishers for the experiment and restore the selected Dev mechanism afterward. Never switch a shared workspace branch while another participant is testing. If a recovery action would discard unrelated work, stop, preserve it and choose a narrower route.

## Evidence and readiness

- Primary documentation supports Fabric's per-item keep/replace choices and recovery via a new branch from the last synchronized state; no workshop recovery has been observed yet.
- The notebook VFS extension saves to remote workspace state; ordinary cloned-source feature editing is the selected core IDE route.
- Record tested client/UI versions, source revisions, exact conflict status, preservation steps, final source/workspace state, permissions, time and any recovery issue.
- Related controls: MS-02/03 (source/review), MS-06 (source versus workspace state), MS-11 (recovering definitions), MS-14 (evidence). This is not a data-recovery exercise.

References: [Fabric conflict resolution](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/conflict-resolution), [VFS notebook authoring](https://learn.microsoft.com/en-us/fabric/data-engineering/author-notebook-with-vs-code-vfs-mode).
