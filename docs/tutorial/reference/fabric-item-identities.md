# Logical and physical IDs in Fabric

A name such as `build_sales` helps people recognize an item. An ID lets Fabric or deployment tooling identify it precisely. Two identifiers matter here:

| Identifier | Meaning | Where to find it |
| --- | --- | --- |
| **Logical ID** | Identity of an item in its Git representation; corresponding items can share it across workspaces | The item's `.platform` file, under `config.logicalId` |
| **Physical item ID**, also called **object ID** in lifecycle documentation | Identity of one concrete deployed item in a workspace | Its Fabric item URL or an item API response's `id` field |
| **Workspace ID** | Identity of the workspace containing the deployed item | Workspace URL or item API response's `workspaceId` field |

The `.platform` file is not an inventory of every environment's physical IDs. Finding only a logical ID there is expected. Other definition files can contain physical dependency references, logical references, names or relative paths; inspect the actual format rather than interpreting every GUID as a physical item ID. See [Fabric source-control identities](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/source-code-format#platform-file).

## One definition, several deployed items

This is an illustration, not a manifest format or a claim about your actual IDs:

| Source item | Logical ID in Git | Environment | Physical item ID |
| --- | --- | --- | --- |
| `build_sales` | L-notebook | Dev | N-dev |
| `build_sales` | L-notebook | Test | N-test |
| `build_sales` | L-notebook | Prod | N-prod |

The same controlled definition can correspond to distinct deployed items. Updating an existing item is different from deleting and recreating it; recreation can give it a new physical ID. Names and previous run records are therefore insufficient to establish current identity.

Preserve the generated logical ID when editing an existing definition. Do not regenerate `.platform`, copy another item's logical ID or replace it with a Dev/Test/Prod physical ID. That changes how source control identifies the item; it does not configure its environment.

## Assign a logical ID to a new source item

Unit 9 starts `validate_release` as a new notebook definition in Git. A fresh, unique, nonzero GUID gives that definition its own identity. The value is a key used to correlate the source item and its references. It encodes no workspace, environment or permission. Generate the GUID once, store it in `config.logicalId` inside `.platform`, and keep it with the notebook through later revisions. Corresponding items can share this logical ID across Test and Prod while each deployed item has its own physical item ID. When starting from an existing Fabric export, keep the logical ID Fabric supplied. [Fabric Git source format](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/source-code-format#platform-file).

## Find a physical ID without changing the item

1. Open the item from its intended Fabric workspace. Retain its item link in your private solution record.
2. Read the workspace/item identifiers in the URL where they are explicit. URL shapes vary by item type; do not assume the last GUID always identifies the item. A run/job link can identify an execution instead.
3. When an unambiguous machine-readable result is needed, deployment tooling can use the supported item API. For example, `GET /v1/workspaces/{workspaceId}/items/{itemId}` returns `id`, `workspaceId`, type and display name; current responses can also expose a logical ID. The API route uses the **physical item ID**, not `.platform`'s logical ID. No API call is required for this reference exercise. See [Get Item](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/get-item).

A lakehouse and its SQL analytics endpoint have different identities. So do a semantic model and its report. Record the item **type** alongside an ID; a GUID's appearance does not reveal what it identifies.

## Why deployment needs both concepts

A release must connect the source item to its deployed target and bind consumers to the correct dependencies. A useful deployment record can correlate **source commit + logical identity → target workspace + physical item identity**, together with the validation result.

For example, a Test notebook must reach the intended Test lakehouse, not the Dev lakehouse merely because its display name is also `sales`. Supported Git binding can resolve some logical references, while remaining physical references need the appropriate supported binding/configuration mechanism. Behavior depends on item type and deployment mechanism; preserving logical IDs alone does not configure every cross-workspace link. See [dependency binding](https://learn.microsoft.com/en-us/fabric/cicd/cross-workspace-dependency-binding).

We introduced actual target binding in Unit 3. Unit 4 records the expanded Dev dependencies; Unit 5 preserves source identities during local edits. The later environment/deployment lessons will resolve and verify target mappings and show them in release evidence. An item ID is also distinct from the user, managed identity or connection used to deploy or execute it.

[Tutorial index](../README.md)
