# Sources and evidence limits

Consulted 28 October 2026. These references support technical scoping; no tenant behavior has been verified. Recheck documentation and pin actual tool versions during implementation and before the event.

| ID | Source | Relevance |
| --- | --- | --- |
| S1 | [Import a Git repository into Azure Repos](https://learn.microsoft.com/en-us/azure/devops/repos/git/import-git-repository?view=azure-devops) | GitHub-to-Azure-Repos transfer is supported; destination setup remains necessary |
| S2 | [Build GitHub repositories with Azure Pipelines](https://learn.microsoft.com/en-us/azure/devops/pipelines/repos/github?view=azure-devops) | Repository hosting and pipeline execution can use different services |
| S3 | [Dependency binding in cross-workspace deployment](https://learn.microsoft.com/en-us/fabric/cicd/cross-workspace-dependency-binding) | Logical/object IDs, item-specific behavior, and lack of automatic binding for references to other workspaces |
| S4 | [Understand the Deployment pipelines process](https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/understand-the-deployment-process) | Promotion, data lifecycle, and item-specific deployment limitations |
| S5 | [Fabric item management API overview](https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/item-management-overview) | Item definitions and operation/identity support require item-specific checking |
| S6 | [fabric-cicd overview](https://microsoft.github.io/fabric-cicd/latest/) | Existing deployment library to evaluate before expanding custom code |
| S7 | [fabric-cicd parameterization](https://microsoft.github.io/fabric-cicd/latest/how_to/parameterization/) | Existing environment replacement and binding features may reduce custom configuration requirements |
| S8 | [Fabric CI/CD overview](https://learn.microsoft.com/en-us/fabric/cicd/cicd-overview) | Native features and API-based tooling can be combined |
| S9 | [Official OpenAI guidance: projects and chats](https://learn.chatgpt.com/docs/projects) | Local project folders, focused chats, and durable guidance in repository files |
| S10 | [Assign Workspace to Stage API](https://learn.microsoft.com/en-us/rest/api/fabric/core/deployment-pipelines/assign-workspace-to-stage) | Assignment requires both deployment-pipeline admin and workspace admin roles |
| S11 | [Azure Pipelines approvals and checks](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/approvals?view=azure-devops) | Resource-owner checks are configured outside pipeline YAML; include their setup separately |
| S12 | [Development process in Fabric](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/manage-branches?tabs=azure-devops) | A workspace is a shared runtime connected to one branch; client-tool development and workspace isolation serve different needs |
| S13 | [Fabric CI/CD workflow options](https://learn.microsoft.com/en-us/fabric/cicd/manage-deployment) | Source-of-truth, branching, and publishing choices must be consistent for a selected path |
| S14 | [Fabric CI/CD concepts and best practices](https://learn.microsoft.com/en-us/fabric/fundamentals/understand-best-practices-fabric-cicd) | Distinct Git folder settings for workspaces in one solution; keep item definitions separate from workflow files |
| S15 | [Adding locally hosted code to GitHub](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github?platform=windows) | Create an empty remote for existing local content, add its URL and push after authentication |
| S16 | [OpenAI: custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) | Concise global and repository guidance with directory-based scope |
| S17 | [OpenAI: configuration basics](https://learn.chatgpt.com/docs/config-file/config-basic) | User defaults and trusted project configuration are distinct layers |
| S18 | [OpenAI: local environments](https://learn.chatgpt.com/docs/environments/local-environment) | Portable app actions/setup can be shared through selected project configuration |
| S19 | [OpenAI: customization](https://learn.chatgpt.com/docs/customization/overview) | Repository-specific skills and personal workflows have different locations/scopes |
| S20 | [Microsoft: resolve OneDrive sync issues](https://learn.microsoft.com/en-us/troubleshoot/sharepoint/sync/troubleshoot-sync-issues) | Describes non-Office conflict copies; recommendation to avoid active Git checkouts in sync folders is an engineering inference |

The organizer-supplied guideline documents are maintained in [source-guidelines](../source-guidelines/README.md) and are the workshop's policy-design baseline. They are not Microsoft platform documentation.

## Interpretation limits

- S3 describes definition-based dependency behavior and explicitly warns that cross-workspace references do not automatically bind. Specialized native features can differ; validate the precise mechanism and item pair selected for the workshop.
- S4 currently lists limitations affecting PBIR reports and Direct Lake target bindings. Do not infer that a particular exported report/model combination works in both Git-based and native promotion paths without testing it.
- S6/S7 establish an existing deployment/configuration starting point. They do not prove the sample's cross-workspace orchestration, recovery, or post-deployment validation requirements are fully covered.
- Identity support is specific to an operation, item type, runtime, and tenant settings. A general support table cannot establish the complete authentication chain.
- Some documentation pages and their linked source revisions can differ. Save the exact relevant behavior and observed test results when selecting a workshop release.
- OpenAI project guidance supports file-based project context, not a guarantee that every chat automatically knows the full transcript of other chats. Durable decisions belong in the repository.
