# Provisioning feedback review — 29 October 2026

Source: organizer-supplied `fabric_workspace_factory_transfer.zip`, SHA-256 `FF5CD80E509893CD178936C2FAEFE35B66C70E43A01BF6940ECBCB98366C77F3`. The seven files include two Python sources, a README, the actual manifest and three create-run evidence files. Originals are retained in ignored `work/imports/workspace-factory-2026-10-29/`, not copied into public starter configuration. This review does not execute the factory or query live infrastructure.

## Evidence received

Each role's supplied create record reports `success: true`, three environments, capacity-assigned workspaces and an Admin assignment for the configured participant principal. Across the records this gives nine distinct workspaces, three role-specific repositories in one project, and Dev as both default and workspace branch. The Git directory is `/` in each separate repository. Private Link is disabled; the configuration requests public access rather than deny rules.

All three Dev connections report `ConnectedAndInitialized`, initialization `requiredAction: None`, and `lastSyncTime: null`. That is evidence of connection/bootstrap, not evidence of a later Fabric item commit or update-from-Git session. The source initializes repositories with README commits and does not perform a subsequent `commitToGit` or `updateFromGit` action.

The factory's project-access reconciliation is disabled in this manifest. Fabric workspace Admin grants therefore do not establish participant Azure Repos contribution rights. Verify actual participant access separately.

## Git identity finding

`authenticate` acquires Fabric and Azure DevOps tokens through the active Azure CLI credential. These provisioning calls use that signed-in identity. `connect_fabric_dev_to_git` sends `gitProviderDetails` without `myGitCredentials`; the current Connect API specifies automatic credentials as the default for Azure DevOps and describes them as user-specific, not shared with other workspace contributors.

Thus prebinding the workspace does not by itself make every participant's future sync run as the organizer. Participants still need their own usable Git credentials/repository access. A configured cloud connection, if introduced later, has separate access and credential semantics. The supplied evidence does not inspect each participant's `myGitCredentials` configuration.

Check this with a genuinely different participant identity. Using the organizer account for both provisioning and the pilot cannot demonstrate another user's authentication behavior. The decisive later check is a Fabric item commit/update under the participant identity; editing README in Azure Repos only tests repository contribution access.

Official sources checked 29 October 2026:

- [Git Connect API](https://learn.microsoft.com/en-us/rest/api/fabric/core/git/connect): connection coordinates, credential default, and synchronization boundary.
- [Get My Git Credentials](https://learn.microsoft.com/en-us/rest/api/fabric/core/git/get-my-git-credentials): caller-specific credential configuration.
- [Configured/service-principal Git integration](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/automate-git-integration-with-service-principal): configured connections and automation identity setup.

## Teaching recommendation

Keep the already-created Dev bindings for this pilot. Participants should inspect and explain repository, branch and directory, authenticate as themselves if prompted, and perform the first real Fabric-to-Git action in the asset/source-control unit. Provide a short optional connect-it-yourself path for the final tutorial instead of requiring everyone to disconnect/reconnect a working environment.

Later Model B item-API publishing need not reuse the organizer's Git connection: the job checks out source through Azure DevOps and authenticates to Fabric through its deployment identity. If a later design invokes Fabric Git APIs, configure that caller's Git credential and repository permissions explicitly. Reconcile pending workspace changes and select one publisher before changing the Dev update mechanism.

## Layout differences to resolve

- The pilot has three repositories, not the currently recommended single solution repo with role folders. This is a valid topology but requires explicit cross-repository source selection/version correlation. Matching `dev` branch names do not identify one atomic solution revision.
- Do not recreate the current workspaces to resolve repository layout. Decide before the Model B release design whether to retain separate repos with a release manifest pinning all source revisions, or adjust bindings to one repository/nonoverlapping folders while source content is still minimal. The latter needs a factory enhancement: tiered loading currently derives three repo names and rejects explicit project/repository overrides.
- `dev` as integration/default branch is acceptable. A second long-lived `main` is not required merely to match the old tutorial.
- The source calls `initializeConnection` but leaves any returned follow-up sync action to the caller. These supplied runs have `None`; a generic provisioning readiness report should surface pending actions without calling them completed synchronization.
- The Git-coordinate validator compares `branchName` case-insensitively. Treat branch refs as exact identifiers when adapting it; avoid accepting a differently cased branch as the intended source.
- The README's earlier statement that project creation is outside the factory is qualified later by the tiered feature. Make the single-layout versus tiered behavior explicit in final facilitator documentation.

These are a targeted readiness review, not a complete audit of create/destroy/networking or effective authorization. No factory or cloud operation was run.

Local checks: both Python sources parsed as syntax without importing/executing them; all three JSON run records parsed and covered nine distinct workspace names. The actual YAML manifest was read as text, not validated by running its parser or provisioning commands.

## Remaining participant feedback

1. Can the actual participant identity open all nine workspaces and contribute to the intended repository/repositories? Record whether this is different from the provisioning account.
2. Do the three Dev Source control panes open without authentication/access errors, and do their repo/branch/directory values match the intended mapping?
3. Are the workspaces still empty of solution items, and is the native Deployment pipelines feature available? The create records do not prove those checks.
4. How long did provisioning and learner verification take, and which Unit 1 instructions required improvisation?

Do not ask the organizer to retype the nine names or branch configuration already present in the evidence. Mark Unit 1 partially evidenced until the user-side checks are reported. First real Fabric Git commit remains a checkpoint for a later unit.
