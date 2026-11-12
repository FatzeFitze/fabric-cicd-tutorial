# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   }
# META }

# CELL ********************

from decimal import Decimal

from pyspark.sql import functions as F

totals = spark.table("sales").agg(
    F.sum("gross_revenue").alias("gross"),
    F.sum("revenue").alias("revenue"),
).first()

if (totals.gross, totals.revenue) != (Decimal("357.20"), Decimal("204.70")):
    raise RuntimeError(f"Unexpected Tiny Sales totals: {totals.asDict()}")

print("SALES_SMOKE_PASSED", totals.asDict())

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
