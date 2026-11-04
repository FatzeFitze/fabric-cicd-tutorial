# Tiny Sales — Dev solution record

Record what you observe in Unit 4. Keep actual workspace/connection details in your training notes; exclude credentials and tokens.

| Item | Workspace | Logical ID from `.platform` | Fabric item link / physical ID if unambiguous | Visible owner/creator label and principal, if exposed |
| --- | --- | --- | --- | --- |
| `sales` Lakehouse | Data Dev | | | |
| `build_sales` Notebook | Code Dev | | | |
| `sales_config` Variable Library | Code Dev | | | |
| `run_sales` Pipeline | Code Dev | | | |
| `sales_model` Semantic model | Reporting Dev | | | |
| `sales_overview` Report | Reporting Dev | | | |

Logical IDs are source identities; physical IDs identify deployed instances and are not required to appear in `.platform`. Retain the item link when its URL does not expose an unambiguous item ID. See the [ID reference](../../../reference/fabric-item-identities.md).

## Configuration and runtime

- Active `sales_config` value set and correct final values:
- `EnvironmentName` / `RunLabel` reference expressions:
- Notebook activity Connection (unselected or selected name) / authentication details actually exposed:
- Pipeline last modifying user / notebook run Submitter (record their displayed labels separately):
- Authored defaults and generated runtime-cell values observed in the execution snapshot:
- Successful pipeline/activity run and received values:
- Controlled environment-mismatch failure and restored successful run:
- Persisted table rows / revenue:

## Reporting and source

- Semantic model mode (selected path: Direct Lake on SQL):
- Data Dev SQL analytics endpoint item link / server / displayed model database reference / metadata-readiness behavior:
- Direct Lake type evidence (creation selection and TMDL connector/source expression):
- Model connection authentication / SSO setting as actually exposed:
- Model owner versus data-access identity observations:
- Report-to-model reference / exported representation:
- Report values (Total Revenue 342.20, Order Count 6, Sample Check PASS):
- Product values (Backpack 245.00, Travel mug 59.70, Lunch box 37.50):
- Temporary price-change result (Total Revenue 357.20 / Travel mug 74.70), run and model/visual refresh observations:
- Restored price/expected checks and final report baseline (342.20 / 59.70) before Git capture:
- Code repo full commit ID/link:
- Reporting repo full commit ID/link:
- Retained Data repo baseline commit ID/link:
- Actual generated file lists / reference fields needed for later deployment:
- Approximate time / UI differences / exact errors:
