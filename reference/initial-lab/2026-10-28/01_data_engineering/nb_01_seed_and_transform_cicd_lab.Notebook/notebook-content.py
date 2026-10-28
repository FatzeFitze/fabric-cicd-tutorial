# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "404fe2f2-9f32-8433-4d7a-40799ab95163",
# META       "default_lakehouse_name": "lh_cicd_lab",
# META       "default_lakehouse_workspace_id": "00000000-0000-0000-0000-000000000000",
# META       "known_lakehouses": [
# META         {
# META           "id": "404fe2f2-9f32-8433-4d7a-40799ab95163",
# META           "workspace_id": "00000000-0000-0000-0000-000000000000"
# META         }
# META       ]
# META     }
# META   }
# META }

# MARKDOWN ********************

# # fabric-cicd-lab — Seed and Transform
# 
# This notebook is the first executable item in the Fabric CI/CD learning project.
# 
# It demonstrates:
# 
# - deterministic data generation
# - writing raw Delta tables to a Lakehouse
# - creating curated Delta tables
# - creating a simple aggregate table
# - separating code state, deployment state, environment state, and runtime state
# 
# Deployment automation tutorial marker:
# 
# - API_DEV_TO_TEST_V1
# - PYTHON_DEPLOY_CLI_V1
# - U05_NONPROD_RELEASE_V1
# - U06_PROD_RELEASE_V1
# - U06_FORWARD_RECOVERY_V1
# - S3_U02_FABRIC_CICD_TEST_V1
# - S3_U03_TEST_RUNTIME_CANDIDATE_V1
# - S3_U06_PROD_RUNTIME_VALIDATION_V1
# 
# Target Lakehouse:
# 
# - lh_cicd_lab
# 
# Tables created:
# 
# - raw_sales_orders
# - curated_sales_orders
# - agg_sales_by_date
# - cicd_run_audit


# CELL ********************

from pyspark.sql import functions as F
from pyspark.sql import types as T
from datetime import date, timedelta

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# PARAMETERS CELL ********************

environment_name = "DEV"
release_candidate_label = "INTERACTIVE"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# ---------------------------------------------------------------------------
# fabric-cicd-lab
# Deterministic demo data generation
#
# Design principle:
# - No random values.
# - Same code should produce same business results every time.
# - This makes CI/CD verification possible.
# ---------------------------------------------------------------------------

base_date = date(2026, 1, 1)

rows = []

customers = [
    ("C001", "Contoso Steel"),
    ("C002", "Fabrikam Components"),
    ("C003", "Northwind Metals"),
]

products = [
    ("P001", "Forged Bar", "Steel", 120.00),
    ("P002", "Powder Metal", "Powder", 85.00),
    ("P003", "Tool Plate", "Plate", 210.00),
]

order_id = 1000

for day_offset in range(10):
    order_date = base_date + timedelta(days=day_offset)

    for customer_index, (customer_id, customer_name) in enumerate(customers):
        product_id, product_name, product_category, unit_price = products[
            (day_offset + customer_index) % len(products)
        ]

        quantity = (day_offset + 1) * (customer_index + 1)

        rows.append(
            (
                order_id,
                order_date.isoformat(),
                customer_id,
                customer_name,
                product_id,
                product_name,
                product_category,
                quantity,
                unit_price,
            )
        )

        order_id += 1

schema = T.StructType(
    [
        T.StructField("order_id", T.IntegerType(), False),
        T.StructField("order_date", T.StringType(), False),
        T.StructField("customer_id", T.StringType(), False),
        T.StructField("customer_name", T.StringType(), False),
        T.StructField("product_id", T.StringType(), False),
        T.StructField("product_name", T.StringType(), False),
        T.StructField("product_category", T.StringType(), False),
        T.StructField("quantity", T.IntegerType(), False),
        T.StructField("unit_price", T.DoubleType(), False),
    ]
)

raw_df = spark.createDataFrame(rows, schema)

display(raw_df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# ---------------------------------------------------------------------------
# Runtime state:
# This writes data into the attached Lakehouse.
#
# Important ALM point:
# The table data is NOT the same thing as Git-tracked notebook code.
# ---------------------------------------------------------------------------

(
    raw_df
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("raw_sales_orders")
)

print("Created/overwritten table: raw_sales_orders")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# ---------------------------------------------------------------------------
# Curated transformation:
# - cast order_date to date
# - calculate sales_amount
# - add simple business classification
# - add technical load metadata
# ---------------------------------------------------------------------------

curated_df = (
    raw_df
    .withColumn("order_date", F.to_date("order_date"))
    .withColumn("sales_amount", F.col("quantity") * F.col("unit_price"))
    .withColumn(
        "order_size_band",
        F.when(F.col("quantity") < 10, F.lit("Small"))
         .when(F.col("quantity") < 20, F.lit("Medium"))
         .otherwise(F.lit("Large"))
    )
    .withColumn("lab_solution_name", F.lit("fabric-cicd-lab"))
    .withColumn("lab_notebook_name", F.lit("nb_01_seed_and_transform_cicd_lab"))
    .withColumn("lab_environment_name", F.lit(environment_name))
    .withColumn("lab_load_timestamp_utc", F.current_timestamp())
)

(
    curated_df
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("curated_sales_orders")
)

display(curated_df)

print("Created/overwritten table: curated_sales_orders")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# ---------------------------------------------------------------------------
# Simple reporting-friendly aggregate.
#
# This later becomes the input candidate for a semantic model/report.
# ---------------------------------------------------------------------------

agg_df = (
    curated_df
    .groupBy("order_date", "product_category")
    .agg(
        F.countDistinct("order_id").alias("order_count"),
        F.sum("quantity").alias("total_quantity"),
        F.round(F.sum("sales_amount"), 2).alias("total_sales_amount"),
    )
    .withColumn(
        "average_order_value",
        F.round(
            F.col("total_sales_amount") / F.col("order_count"),
            2,
        ),
    )
    .orderBy("order_date", "product_category")
)

(
    agg_df
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("agg_sales_by_date")
)

display(agg_df)

print("Created/overwritten table: agg_sales_by_date")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

tables_to_check = [
    "raw_sales_orders",
    "curated_sales_orders",
    "agg_sales_by_date",
]

for table_name in tables_to_check:
    count_value = spark.table(table_name).count()
    print(f"{table_name}: {count_value} rows")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

required_aggregate_columns = {
    "order_date",
    "product_category",
    "order_count",
    "total_quantity",
    "total_sales_amount",
    "average_order_value",
}

actual_aggregate_columns = set(
    spark.table("agg_sales_by_date").columns
)

missing_columns = required_aggregate_columns - actual_aggregate_columns

assert not missing_columns, (
    f"Missing aggregate columns: {sorted(missing_columns)}"
)

print("Aggregate schema verification succeeded.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# ---------------------------------------------------------------------------
# Lightweight deterministic verification.
#
# This is not a full test framework yet.
# It is a first sanity check that lets us detect accidental logic changes.
# ---------------------------------------------------------------------------

import uuid
from datetime import datetime, timezone

expected_result = {
    "raw_row_count": 30,
    "curated_row_count": 30,
    "aggregate_row_count": 30,
    "total_quantity": 330,
    "total_sales_amount": 45905.0,
    "min_order_date": date(2026, 1, 1),
    "max_order_date": date(2026, 1, 10),
}

assert environment_name in {"DEV", "TEST", "PROD"}, (
    f"Unexpected environment_name: {environment_name!r}"
)

assert isinstance(release_candidate_label, str) and release_candidate_label.strip(), (
    "release_candidate_label must be a non-empty string."
)

if environment_name in {"TEST", "PROD"}:
    try:
        uuid.UUID(release_candidate_label)
    except ValueError as exc:
        raise AssertionError(
            "TEST/PROD release_candidate_label must be the Fabric "
            "Data Factory pipeline RunId."
        ) from exc

raw_row_count = spark.table("raw_sales_orders").count()
curated_row_count = spark.table("curated_sales_orders").count()
aggregate_row_count = spark.table("agg_sales_by_date").count()

curated_result = (
    spark.table("curated_sales_orders")
    .agg(
        F.sum("quantity").alias("total_quantity"),
        F.round(F.sum("sales_amount"), 2).alias("total_sales_amount"),
        F.min("order_date").alias("min_order_date"),
        F.max("order_date").alias("max_order_date"),
    )
    .collect()[0]
)

aggregate_result = (
    spark.table("agg_sales_by_date")
    .agg(
        F.round(F.sum("total_sales_amount"), 2).alias(
            "aggregate_total_sales_amount"
        )
    )
    .collect()[0]
)

environment_values = {
    row["lab_environment_name"]
    for row in (
        spark.table("curated_sales_orders")
        .select("lab_environment_name")
        .distinct()
        .collect()
    )
}

actual_result = {
    "raw_row_count": raw_row_count,
    "curated_row_count": curated_row_count,
    "aggregate_row_count": aggregate_row_count,
    "total_quantity": int(curated_result["total_quantity"]),
    "total_sales_amount": round(
        float(curated_result["total_sales_amount"]), 2
    ),
    "min_order_date": curated_result["min_order_date"],
    "max_order_date": curated_result["max_order_date"],
}

assert actual_result == expected_result, (
    "Deterministic runtime validation failed. "
    f"Expected {expected_result}, got {actual_result}."
)

assert environment_values == {environment_name}, (
    "Runtime environment isolation failed. "
    f"Expected only {environment_name!r}, got {sorted(environment_values)}."
)

aggregate_total_sales_amount = round(
    float(aggregate_result["aggregate_total_sales_amount"]), 2
)

assert aggregate_total_sales_amount == expected_result["total_sales_amount"], (
    "Aggregate and curated totals differ. "
    f"Aggregate={aggregate_total_sales_amount}, "
    f"curated={expected_result['total_sales_amount']}."
)

validation_run_id = str(uuid.uuid4())
validated_at_utc = datetime.now(timezone.utc).replace(tzinfo=None)

validation_schema = T.StructType(
    [
        T.StructField("validation_run_id", T.StringType(), False),
        T.StructField("release_candidate_label", T.StringType(), False),
        T.StructField("environment_name", T.StringType(), False),
        T.StructField("validation_status", T.StringType(), False),
        T.StructField("raw_row_count", T.LongType(), False),
        T.StructField("curated_row_count", T.LongType(), False),
        T.StructField("aggregate_row_count", T.LongType(), False),
        T.StructField("total_quantity", T.LongType(), False),
        T.StructField("total_sales_amount", T.DoubleType(), False),
        T.StructField("min_order_date", T.DateType(), False),
        T.StructField("max_order_date", T.DateType(), False),
        T.StructField("validated_at_utc", T.TimestampType(), False),
    ]
)

validation_row = [
    (
        validation_run_id,
        release_candidate_label,
        environment_name,
        "SUCCEEDED",
        actual_result["raw_row_count"],
        actual_result["curated_row_count"],
        actual_result["aggregate_row_count"],
        actual_result["total_quantity"],
        actual_result["total_sales_amount"],
        actual_result["min_order_date"],
        actual_result["max_order_date"],
        validated_at_utc,
    )
]

(
    spark.createDataFrame(validation_row, validation_schema)
    .write
    .format("delta")
    .mode("append")
    .saveAsTable("cicd_run_audit")
)

print("Runtime validation succeeded.")
print(f"validation_run_id:       {validation_run_id}")
print(f"release_candidate_label: {release_candidate_label}")
print(f"environment_name:        {environment_name}")
print(f"raw_row_count:           {actual_result['raw_row_count']}")
print(f"curated_row_count:       {actual_result['curated_row_count']}")
print(f"aggregate_row_count:     {actual_result['aggregate_row_count']}")
print(f"total_quantity:          {actual_result['total_quantity']}")
print(f"total_sales_amount:      {actual_result['total_sales_amount']}")
print(f"min_order_date:          {actual_result['min_order_date']}")
print(f"max_order_date:          {actual_result['max_order_date']}")
print("Audit row appended to:  cicd_run_audit")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# ---------------------------------------------------------------------------
# Pipeline return contract.
#
# A Fabric Notebook activity can return one string value to its parent
# pipeline. We use JSON so Azure DevOps can correlate the Fabric pipeline run
# with the deterministic Notebook validation that just completed.
# ---------------------------------------------------------------------------

import json

runtime_validation_result = {
    "validation_run_id": validation_run_id,
    "release_candidate_label": release_candidate_label,
    "environment_name": environment_name,
    "validation_status": "SUCCEEDED",
    "raw_row_count": actual_result["raw_row_count"],
    "curated_row_count": actual_result["curated_row_count"],
    "aggregate_row_count": actual_result["aggregate_row_count"],
    "total_quantity": actual_result["total_quantity"],
    "total_sales_amount": actual_result["total_sales_amount"],
    "min_order_date": actual_result["min_order_date"].isoformat(),
    "max_order_date": actual_result["max_order_date"].isoformat(),
    "validated_at_utc": validated_at_utc.isoformat() + "Z",
}

notebookutils.notebook.exit(
    json.dumps(
        runtime_validation_result,
        sort_keys=True,
        separators=(",", ":"),
    )
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

