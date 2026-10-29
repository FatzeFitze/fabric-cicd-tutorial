# Copy each numbered section into a separate PySpark cell in build_sales.
# This is starter source for manual authoring, not a Fabric item export.

# %% Cell 1 - Check the execution target
from decimal import Decimal
import json

from pyspark.sql import functions as F

EXPECTED_CODE_WORKSPACE = "REPLACE_WITH_YOUR_CODE_DEV_WORKSPACE_NAME"
EXPECTED_DATA_WORKSPACE = "REPLACE_WITH_YOUR_DATA_DEV_WORKSPACE_NAME"
EXPECTED_LAKEHOUSE = "sales"
TABLE_NAME = "sales"


def check_target():
    context = notebookutils.runtime.context
    expected = {
        "currentWorkspaceName": EXPECTED_CODE_WORKSPACE,
        "defaultLakehouseWorkspaceName": EXPECTED_DATA_WORKSPACE,
        "defaultLakehouseName": EXPECTED_LAKEHOUSE,
    }
    actual = {key: context.get(key) for key in expected}
    if actual != expected:
        raise RuntimeError(
            "Target check failed. Check the two workspace names and the pinned "
            "default lakehouse; restart the Spark session after changing it. "
            f"Expected: {expected}. Actual: {actual}"
        )
    print(json.dumps(actual, indent=2))


check_target()

# %% Cell 2 - Create the small synthetic inputs in memory
CUSTOMERS = [
    ("C01", "Ada"),
    ("C02", "Ben"),
    ("C03", "Chloe"),
]
PRODUCTS = [
    ("P01", "Travel mug", 1990),
    ("P02", "Backpack", 3500),
    ("P03", "Lunch box", 1250),
]
ORDERS = [
    ("O001", "2026-01-01", "C01", "P01", 2, False),
    ("O002", "2026-01-02", "C02", "P02", 3, False),
    ("O003", "2026-01-03", "C01", "P03", 1, True),
    ("O004", "2026-01-04", "C03", "P01", 1, False),
    ("O005", "2026-01-05", "C02", "P03", 2, False),
    ("O006", "2026-01-06", "C03", "P02", 4, True),
]

customers = spark.createDataFrame(
    CUSTOMERS, "customer_id string, customer_name string"
)
products = spark.createDataFrame(
    PRODUCTS, "product_id string, product_name string, unit_price_cents int"
).withColumn(
    "unit_price",
    (F.col("unit_price_cents").cast("decimal(12,2)") / F.lit(100)).cast(
        "decimal(10,2)"
    ),
)
orders = spark.createDataFrame(
    ORDERS,
    "order_id string, order_date string, customer_id string, "
    "product_id string, quantity int, is_returned boolean",
).withColumn("order_date", F.to_date("order_date", "yyyy-MM-dd"))

print("Created 3 customers, 3 products and 6 orders in memory.")

# %% Cell 3 - Build and validate the curated result before writing
sales = (
    orders.join(customers, "customer_id").join(products, "product_id")
    .withColumn(
        "gross_revenue", (F.col("quantity") * F.col("unit_price")).cast("decimal(12,2)")
    )
    .withColumn("revenue", F.col("gross_revenue"))
    .select(
        "order_id", "order_date", "customer_id", "customer_name",
        "product_id", "product_name", "quantity", "unit_price",
        "is_returned", "gross_revenue", "revenue",
    )
)

# Baseline business rule: revenue includes every order, including returned orders.
# The local feature exercise will change this rule and its expected result.
EXPECTED_METRICS = {
    "rows": 6,
    "orders": 6,
    "quantity": 13,
    "returned_orders": 2,
    "gross_revenue": Decimal("342.20"),
    "revenue": Decimal("342.20"),
    "invalid_rows": 0,
}


def validate_sales(frame):
    invalid = (
        F.col("order_id").isNull()
        | F.col("order_date").isNull()
        | F.col("customer_name").isNull()
        | F.col("product_name").isNull()
        | F.col("quantity").isNull()
        | (F.col("quantity") <= 0)
        | F.col("is_returned").isNull()
        | F.col("unit_price").isNull()
        | (F.col("unit_price") <= 0)
        | F.col("gross_revenue").isNull()
        | F.col("revenue").isNull()
    )
    actual = frame.agg(
        F.count("*").alias("rows"),
        F.countDistinct("order_id").alias("orders"),
        F.sum("quantity").alias("quantity"),
        F.sum(F.when(F.col("is_returned"), 1).otherwise(0)).alias("returned_orders"),
        F.sum("gross_revenue").alias("gross_revenue"),
        F.sum("revenue").alias("revenue"),
        F.sum(F.when(invalid, 1).otherwise(0)).alias("invalid_rows"),
    ).first().asDict()
    if actual != EXPECTED_METRICS:
        raise ValueError(f"Sales validation failed. Expected {EXPECTED_METRICS}; got {actual}")
    print("Sales checks passed:", json.dumps(actual, default=str, sort_keys=True))


validate_sales(sales)
display(sales.orderBy("order_id"))

# %% Cell 4 - Write the Delta table and check the persisted result
check_target()
sales.write.format("delta").mode("overwrite").saveAsTable(TABLE_NAME)
persisted_sales = spark.table(TABLE_NAME)
validate_sales(persisted_sales)
display(persisted_sales.orderBy("order_id"))
print("UNIT_01_PASS: persisted sales table matches the baseline.")
