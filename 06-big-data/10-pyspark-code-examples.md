# 10. PySpark Code Examples — Practical Production Patterns

## Setup
```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType

spark = (
    SparkSession.builder
    .appName("orders-etl")
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.sql.adaptive.skewJoin.enabled", "true")
    .getOrCreate()
)
```

## Reading With an Explicit Schema (production best practice — avoid `inferSchema` on large files)
```python
order_schema = StructType([
    StructField("order_id", StringType(), nullable=False),
    StructField("customer_id", StringType(), nullable=False),
    StructField("amount", DoubleType(), nullable=True),
    StructField("order_date", TimestampType(), nullable=True),
])
df = spark.read.schema(order_schema).option("header", True).csv("s3a://bucket/raw/orders/")
```
**Why explicit schemas matter in production**: `inferSchema=True` requires Spark to read through the data once just to guess types (extra pass, extra time) and can guess WRONG on edge cases (e.g., a mostly-integer column with one bad string value) — explicit schemas are faster and safer.

## Deduplication — Keep Latest Record Per Key (the most common real ETL pattern)
```python
window_spec = Window.partitionBy("order_id").orderBy(F.col("updated_at").desc())
deduped_df = (
    df.withColumn("rn", F.row_number().over(window_spec))
      .filter(F.col("rn") == 1)
      .drop("rn")
)
```

## Incremental Processing Pattern
```python
def get_last_processed_date(control_table_path):
    control_df = spark.read.parquet(control_table_path)
    return control_df.agg(F.max("last_processed_date")).collect()[0][0]

last_date = get_last_processed_date("s3a://bucket/control/orders_watermark/")
new_orders_df = spark.read.parquet("s3a://bucket/raw/orders/").filter(F.col("order_date") > last_date)
```

## Data Quality Checks Before Writing (never let bad data flow downstream silently)
```python
def validate_before_write(df, min_rows=1):
    row_count = df.count()
    if row_count < min_rows:
        raise ValueError(f"Data quality check failed: only {row_count} rows, expected at least {min_rows}")

    null_order_ids = df.filter(F.col("order_id").isNull()).count()
    if null_order_ids > 0:
        raise ValueError(f"Data quality check failed: {null_order_ids} rows with null order_id")

    negative_amounts = df.filter(F.col("amount") < 0).count()
    if negative_amounts > 0:
        raise ValueError(f"Data quality check failed: {negative_amounts} rows with negative amount")

    print(f"Data quality checks passed: {row_count} rows validated")

validate_before_write(deduped_df)
```

## Slowly Changing Dimension (SCD Type 2) With PySpark + Delta Lake
```python
from delta.tables import DeltaTable

def scd2_merge(spark, updates_df, target_path):
    delta_table = DeltaTable.forPath(spark, target_path)

    # Step 1: identify changed records (compare incoming vs current)
    changed_df = (
        updates_df.alias("updates")
        .join(
            delta_table.toDF().filter("is_current = true").alias("current"),
            on="customer_id"
        )
        .filter("updates.city != current.city OR updates.name != current.name")
        .select("updates.*")
    )

    # Step 2: close old records for changed customers
    delta_table.update(
        condition="is_current = true AND customer_id IN (SELECT customer_id FROM changed_view)",
        set={"is_current": "false", "end_date": "current_date()"}
    )

    # Step 3: insert new versions
    changed_df.withColumn("start_date", F.current_date()) \
              .withColumn("end_date", F.lit(None)) \
              .withColumn("is_current", F.lit(True)) \
              .write.format("delta").mode("append").save(target_path)
```

## Sessionization in PySpark (grouping events into sessions with a time-gap rule)
```python
window_spec = Window.partitionBy("user_id").orderBy("event_time")

sessions_df = (
    df.withColumn("prev_event_time", F.lag("event_time").over(window_spec))
      .withColumn(
          "is_new_session",
          F.when(
              F.col("prev_event_time").isNull() |
              (F.col("event_time").cast("long") - F.col("prev_event_time").cast("long") > 1800),  # 30 min gap
              1
          ).otherwise(0)
      )
      .withColumn("session_id", F.sum("is_new_session").over(window_spec))
)
```

## Joining Skewed Data — Salting Example
```python
# The "region" column is heavily skewed (one region has 90% of the data)
salt_count = 10
salted_orders = orders_df.withColumn("salt", (F.rand() * salt_count).cast("int")) \
    .withColumn("salted_region", F.concat("region", F.lit("_"), "salt"))

# Explode the small lookup table to match every possible salt value
salted_regions = regions_df.crossJoin(
    spark.range(salt_count).withColumnRenamed("id", "salt")
).withColumn("salted_region", F.concat("region", F.lit("_"), "salt"))

result = salted_orders.join(salted_regions, on="salted_region")
```

## Writing Partitioned Output (production pattern)
```python
(
    enriched_df.write
    .mode("overwrite")
    .partitionBy("order_date")
    .format("delta")
    .option("mergeSchema", "true")   # allows safe schema evolution (new columns added over time)
    .save("s3a://bucket/curated/orders/")
)
```

## Full Production Job Skeleton (putting it together with proper error handling)
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_job():
    spark = SparkSession.builder.appName("orders-daily-etl").getOrCreate()
    try:
        logger.info("Reading raw orders")
        raw_df = spark.read.schema(order_schema).parquet("s3a://bucket/raw/orders/")

        logger.info("Deduplicating")
        deduped_df = deduplicate(raw_df)

        logger.info("Validating data quality")
        validate_before_write(deduped_df)

        logger.info("Writing curated output")
        deduped_df.write.mode("overwrite").partitionBy("order_date").parquet("s3a://bucket/curated/orders/")

        logger.info(f"Job completed successfully: {deduped_df.count()} rows written")

    except ValueError as e:
        logger.error(f"Data quality failure: {e}")
        raise
    except Exception as e:
        logger.critical(f"Unexpected job failure: {e}")
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    run_job()
```

## Try It Yourself
1. Write a PySpark job that reads CSV with an explicit schema, deduplicates, validates row count > 0, and writes partitioned Parquet.
2. Implement the salting pattern above on a synthetic skewed dataset and compare Spark UI timing before/after.
3. Extend the SCD2 merge function to also handle brand-new customers (not just changed ones).


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"A single sincere step taken today is worth more than a hundred planned for tomorrow."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
