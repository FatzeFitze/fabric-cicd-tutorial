# Item creation, ownership and execution identities

Requested by the organizer on 4 November 2026. Required learning outcome: create at least one new target item through the managed-identity-only Test/Prod delivery path and examine its ownership and operational implications. This is planned coverage, not a completed tenant experiment.

## Place it in the existing journey

| Unit | Role in the story |
| --- | --- |
| 4 | Record the human-created Dev baseline and actual pipeline/model connection choices. Do not change ownership to manufacture an expected observation. |
| 8 | Establish the approved managed deployment identity/runner and distinguish deployment from runtime/data access. Validate required item/API operations before expanding this exercise. |
| 9 | Introduce a small new read-only validation notebook, provisionally `validate_release`, after the managed path exists. Demonstrate its **first creation in Test by the managed deployment identity**, alongside an update to an existing human-created item. Inspect both before/after. |
| 10 | Release the same selected source to Prod. Verify the new item did not already exist, create it through the Prod managed identity, inspect ownership/identity and run its validation through the chosen supported runtime path. |
| 11 / reference | Explain recovery/support implications: access changes, account lifecycle, connections and any supported takeover/identity reassignment. Do not make human takeover the routine fix for a broken deployment identity. |

Adding this one notebook uses an item type and workspace role already taught. Choose its exact definition/checks after the managed runner/runtime path is proven. Unit 4's new library/pipeline/model/report also remain absent from Test/Prod until managed release, so their first target creation can supply additional observations. No new type, workspace, public data source or beta API is required merely for this topic.

## Questions that must stay distinct

| Concern | Observation to record |
| --- | --- |
| Creator | Which identity performed the first create operation? Record the actual caller's Entra principal/object ID and deployment evidence. |
| Displayed item owner | Which principal does the selected item's UI/API call the owner? Preserve the exact label and observation method; do not infer it solely from the caller. |
| Associated/default item identity | Does the item type expose a separate identity used for connections/data access? Record it separately where supported. |
| Deployment identity | Which managed identity actually called Fabric during this release? A connection name alone does not prove the caller. |
| Runtime identity | Which principal executes the validation/notebook activity and has access to its target? It need not equal the deployment identity or visible owner. |
| Connection owner / authentication | Who can manage the connection, and whose credentials/principal authenticate to the source? These are different properties. |
| Report/model consumer | Does the query use SSO or fixed identity, and which source permissions are needed? |

The organizer's expectation that a non-human creator becomes the owner is a hypothesis to verify for the selected item type and operation. A deployment that updates an existing item need not behave like first creation. Do not teach one universal owner rule for notebooks, lakehouses, semantic models and reports without evidence.

## Minimal preparation and exercise contract

1. Select the managed-identity-only Test/Prod deployment route and validate operation-specific support, tenant settings and least-privilege workspace access. Do not substitute a human connection and claim the managed path passed.
2. Before introducing the new definition, inventory target item names, physical/logical identities and available ownership fields. Confirm the new item is absent; preserve existing human-created items for comparison.
3. Author the new definition on a feature branch through the validated new-item template or coordinated export route established for Model B. Give this genuinely new item its own stable logical identity; preserve existing items' identities. Pass CI/shared-Dev integration before selecting the snapshot for Test, then use that same snapshot through Test and Prod. Do not introduce an uncoordinated second Dev publisher or require feature workspaces. The new notebook performs a small read-only check without recreating/deleting the main lakehouse or altering unrelated permissions.
4. Deploy Test under the managed identity. Record the new physical item ID, caller, owner/associated identity fields actually exposed, deployment result and supported runtime/access result. Compare with an existing item's ownership before/after an update in that same release.
5. Redeploy the same source and determine whether it updates the same physical item and whether the observed identities change. Do not delete/recreate merely to force an ownership outcome.
6. Promote that same selected source to Prod through its governed managed connection, repeat the absence/creation/ownership/runtime checks and retain the evidence with the release record.
7. Discuss consequences: support without the original developer, connection/data access continuity, editing/takeover constraints, owner-dependent model framing, and what changes when the owner and executor differ. A successful create or an owner display alone is not proof that operations work.

The core exercise observes ownership; it does not require changing it. Human UI inspection is compatible with managed deployment, but editing, autosave or Take over can change the evidence. Prefer read-only UI or bounded supported item GET APIs for the initial observation. Tenant-admin APIs are an optional facilitator route, not a reason to grant participants tenant-admin access.

## Documentation and evidence limits

- [Fabric item takeover](https://learn.microsoft.com/en-us/fabric/fundamentals/item-ownership-take-over) describes user takeover and item-specific exceptions; its generic UI flow does not establish service-principal takeover for every item.
- [Associated item identities (beta)](https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/associate-item-identity) currently documents Lakehouse and Eventstream, including default-identity assignment at creation. This is a distinct, limited feature; do not generalize it to our proposed validation notebook or make its beta assignment API a core prerequisite.
- [Direct Lake data access](https://learn.microsoft.com/en-us/fabric/fundamentals/direct-lake-security-integration) distinguishes the effective query identity, connection configuration and owner read requirements for framing. This supplies a concrete operational reason to inspect more than a displayed owner.
- If an API uses a field named `creatorPrincipal` but describes it as owner, retain that exact field/version and compare it with the item's actual ownership/identity surfaces. Do not silently merge creator/current owner/default identity into one property.

Checked 4 November 2026. No managed creation/ownership result has been observed for this sample. Record date, tenant/tool/API versions, selected source, operation, caller, target item IDs, ownership inspection method, permissions and actual runtime result during V20. Future capability changes should update implementation guidance without silently rewriting the organizer's Working Version 1 baseline.

## Completion and control mapping

Done when a fresh Test item and its fresh Prod counterpart are demonstrably created by the intended managed identities, their ownership/identity observations and rerun behavior are recorded, runtime/access works, and learners can explain the implications. Map coverage to MS-01, MS-05, MS-07, MS-08, MS-10, MS-11, MS-12 and MS-14. If an item surface is unavailable, state the remaining observation gap rather than invent an owner.
