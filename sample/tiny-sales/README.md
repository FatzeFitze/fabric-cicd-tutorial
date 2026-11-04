# Tiny Sales starter

[Unit 1](../../docs/tutorial/section-01-foundation/unit-01-create-a-tiny-sales-solution/README.md) explains how to create the lakehouse and notebook manually.

Open [the notebook starter](unit-01-notebook.py) and copy its four numbered cell sections into your Fabric notebook. Replace the two workspace-name placeholders in Cell 1 before execution. The file is ordinary PySpark starter source, not an exported Fabric notebook definition or a local command-line program. It uses the Fabric-provided `spark`, `notebookutils` and `display` objects.

The introductory **Markdown cell is separate**: add it manually using Unit 1, Section 3. The Python starter supplies the four code cells only. Your completed notebook has the rendered heading **Tiny Sales — initial build** above those cells.

The fixtures are embedded once in the starter: three customers, three products and six orders. Prices start as integer cents and are converted to decimal amounts. Customer names and transactions are fictional. All monetary amounts use one illustrative currency.

| Baseline check | Expected |
| --- | ---: |
| Sales rows / distinct orders | 6 / 6 |
| Total quantity | 13 |
| Returned orders | 2 |
| Gross revenue | 342.20 |
| Revenue under the initial rule | 342.20 |
| Invalid rows | 0 |

The initial rule includes returned orders in revenue. A later feature exercise will exclude them while preserving the table schema; with these fixtures that produces revenue of **189.70**, while gross revenue remains **342.20**. Unit 1 uses the baseline rule only.

Each run overwrites the disposable training `sales` table in the checked default lakehouse. It does not append rows, ingest an external source, or persist the three input collections as separate tables. This deliberate full-rebuild sample is not a productive incremental-load or data-recovery strategy.

Maintain this file as the canonical starter source; unit instructions link here rather than keeping another copy of its code. Participant-created Fabric definitions will be captured from their own workspaces in Unit 2.

## Native promotion

[environment-aware-target-cell.py](environment-aware-target-cell.py) replaces Cell 1 only in [Unit 3](../../docs/tutorial/section-02-model-a/unit-03-native-promotion/README.md). It keeps `check_target()` and declares the three allowed Code/Data pairs, so the guard can reject Test/Prod references to Dev while using one common source definition. Configure all six workspace names in Dev; do not remove the guard or customize source separately in target stages.

Local positive/negative context checks passed, and on 4 November the organizer accepted the full Unit 3 native chain as its first working version. Keep using the original starter for Unit 1; introduce this replacement in Unit 3.

## Unit 4 configuration and reporting

[unit-04-parameter-cells.py](unit-04-parameter-cells.py) supplies two **additional** cells for the existing notebook: a marked parameter cell before its target guard, and validation after the guard/before fixtures. Preserve the original guard/business/write cells. A pipeline passes `runtime_environment` and `run_label` from the same-workspace Variable Library; interactive defaults are Dev only.

[sales-model-measures.dax](sales-model-measures.dax) contains five separate New measure definitions for the one-table report model. Copy one definition at a time; it is not one executable DAX query. Unit 4's cloud path and DAX evaluation remain to be piloted.
