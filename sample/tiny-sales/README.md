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
