# Static validation for Fabric items

Static validation reads the definitions and configuration in Git. It can give a quick answer during a pull request, before an agent needs Fabric access. Choose checks that catch a specific failure your team cares about.

| What to check | A useful starting point | What still needs evidence |
| --- | --- | --- |
| Item structure and identity | Check expected definition files, JSON syntax, `.platform` type and logical IDs. Look for duplicate logical IDs within a workspace's item set and unexpected changes to IDs in the PR diff. | The corresponding deployed items and their physical IDs. |
| Format rules | Use a published schema or parser for the item's actual format when one is available. For instance, a report may use PBIR or PBIR-Legacy, which have different required parts. | Whether Fabric accepts the full definition and whether related items can load. |
| Source and project conventions | Parse or lint Python exports. Add focused checks for project requirements such as required parameters or forbidden literal target IDs in fields you understand. | Whether the notebook executes in Spark and produces the intended data. |
| Dependencies and release inputs | Check declared item references, workspace assignments and prerequisites. Unit 7 can reject a Test mapping that reuses a Dev workspace ID. | Whether the supplied workspace IDs identify the intended workspaces and whether the deployed bindings and permissions work. |

Start with the actual exported formats. A parser can catch syntax problems. A schema can catch invalid structure, and a project rule can catch a valid definition that violates a team convention. Check only fields you can interpret confidently. Some exporters have optional parts and versioned schemas, so base required-file and schema checks on the format you observed. [Fabric Git source format](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/source-code-format) · [Report definition formats](https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/definitions/report-definition).

In Unit 6, the generic loader checks metadata and Python syntax. The Tiny Sales teaching check also compares the exact shape of the parsed revenue expression. It catches the intended change from `0` to `1`, and it could also reject an equivalent refactor. A team can keep reusable structural checks in its toolkit and put the revenue rule in a project test that runs the transformation on representative data and checks the results.

Before making a check mandatory, try it on one known-good definition and one deliberately broken example. Give the failure a file, field or item name so the author knows where to look. Use a Fabric preflight for actual IDs, bindings and access. Use runtime verification for table writes, refreshes and business results. [Logical and physical Fabric IDs](fabric-item-identities.md).

The required PR check in Unit 6 demonstrates the automated validation before integration expected by Model B’s **MS-03 Change control & traceability**. The deployed solution still needs the automated technical and runtime checks described in **MS-08 Release validation**. [Fabric Minimum Standard](../../source-guidelines/fabric-minimum-standard.md#minimum-standard-by-operating-model).

**Discuss with your team.** If a report points to a model with the right name in the wrong workspace, what could a Git-only check detect? What would you need to inspect after deployment? Which three fast checks would earn a required place in your own PR pipeline?

[Unit 6](../section-03-team-delivery/unit-06-required-pr-validation/README.md) · [Tutorial index](../README.md)
