# Unit 7 preparation and pilot checks

10 November 2026. The organizer reported a smooth Unit 6 walkthrough and requested optional readings for complex topics. Unit 7 starts from the completed validation PR. [Unit 7 lesson](../tutorial/section-04-release-automation/unit-07-configure-and-preview-release/README.md) · [Release preview worksheet](../tutorial/section-04-release-automation/unit-07-configure-and-preview-release/resources/release-preview-record.md).

## Design and scope

- The mask uses the three role repos from the observed pilot. Code comes from the current checkout. Data and Reporting come from two declared full commit pins. A one-repo source selector can be considered when validating the final participant topology.
- The preview works from the YAML and local Variable Library files. It checks the intended workspace assignments, declared graph and environment value supplied by each selected set. It reports target workspace GUIDs and a definition order. It does not resolve deployed item IDs, fetch external repositories, validate real workspace ownership or execute checks selected by the mask. Unit 6's existing CI step executes the Tiny Sales source check.
- Workspace IDs are distinct per role and environment in this lab. A real project sharing a workspace between roles would need a deliberate change to that validation rule.
- Use the vendor-documented Git layout for value sets and retain `.platform` and the Default values. Selection is desired state in the mask and active state in the workspace. No selection or import occurs in this unit. [Variable Library Git behavior](https://learn.microsoft.com/en-us/fabric/cicd/variable-library/variable-library-cicd) · [Value-set definition](https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/definitions/variable-library-definition).

## Evidence and walkthrough

- **Locally exercised.** The module command accepted a synthetic export assembled with the exact lesson value-set JSON and resolved the three target mappings and dependency order. It rejected repeated workspace IDs, missing roles, cycles, unknown bindings, stale value sets, duplicate YAML keys and unfilled fields. Parsed the Unit 7 YAML excerpt appended to the actual Unit 6 pipeline using the pinned PyYAML release.
- **Pilot pending.** Inspect the actual Variable Library paths, confirm PyYAML installation on the approved agent, and record both required build links and the merged commit. The expected negative checkpoint is the duplicate workspace diagnostic. The positive checkpoint is the corrected plan with all three environments and pinned source revisions. No Fabric API call, value-set activation, target deployment or runtime verification is part of this checkpoint.
- **MS coverage.** MS-03 for a reviewed configuration change, MS-04/06 for source and target separation, MS-08 for a rejected invalid configuration, and MS-12/14 for approved identity boundaries and reproducible source selection.

## Unit 8 handoff

Take the merged Code revision and the Data and Reporting pins from the worksheet. Before authoring the first publish path, prove the actual item exports, scoped repo checkout, workspace IDs and authorization, binding strategy and active value-set setting on the chosen tooling. In particular, verify the notebook's target lakehouse, pipeline notebook and library references, the Direct Lake on SQL source and report-to-model link. Rehearse seeding the table before the reporting items need it. The declared order is an input to this work and provides no cloud feasibility evidence on its own.
