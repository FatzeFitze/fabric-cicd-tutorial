# Tiny Sales — native release record

Record actual source, targets and results from Unit 3. Keep this with your training notes. Do not include tokens/passwords. This is lightweight Model A evidence, not the later generic release-manifest format.

## Source and ownership

- Solution owner / technical contact:
- Release purpose / date:
- Data repo and full baseline commit ID/link:
- Code repo and full baseline commit ID/link after the target-cell replacement:
- Source items saved/committed and held unchanged during promotion:
- Reporting: not part of this release.

Native promotion uses source-stage workspace items. These commits record the intended baseline; they do not automatically pin deployment to a Git revision.

## Target and rule mappings

| Environment | Code workspace | Data workspace | Lakehouse item link | Physical lakehouse ID | Data workspace ID |
| --- | --- | --- | --- | --- | --- |
| Dev | | | | | |
| Test | | | | | |
| Prod | | | | | |

| Code pipeline target | Rule location | To option | Configured lakehouse name / ID / workspace ID | Deployment applying the rule |
| --- | --- | --- | --- | --- |
| Test | Code pipeline → Test → Deployment rules → build_sales | Other | | |
| Prod | Code pipeline → Prod → Deployment rules → build_sales | Other | | |

## Validation and authorization

| Check | Actual result | Deployment/execution link or identifier, if available |
| --- | --- | --- |
| Dev runtime after common-source change | | |
| Fresh Test lakehouse/schema | | |
| Test target context | | |
| Test data: 6 rows / revenue 342.20 | | |
| Repeat Test deployment/runtime | | |
| Fresh Prod lakehouse/schema | | |
| Prod target context | | |
| Prod data: 6 rows / revenue 342.20 | | |

- Prod promotion authorized by / date:
- Test evidence reviewed before authorization:
- Common source unchanged after Test validation:
- Intended environment-specific differences:
- Learner time / UI differences / exact errors:

## Bootstrap and recovery

- Environment prerequisites outside item definitions:
- Order for deploying, binding, executing and validating a fresh target:
- Correcting a wrong stage rule without target Python changes:
- Recovering wrong source logic through Dev/Test/authorized Prod:
- Runtime/data state this procedure does not recover:
