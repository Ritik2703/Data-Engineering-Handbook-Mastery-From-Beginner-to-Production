# 11. PySpark for Python Developers

## When to Reach for PySpark Instead of pandas
```
Data fits comfortably in memory (< a few GB)     -> pandas
Data is too large for one machine's RAM           -> PySpark (distributes across a cluster)
Need to scale processing across many machines     -> PySpark
Working inside Databricks/EMR/Dataproc/Synapse    -> PySpark is the native tool
```

## Starting a Spark Session
```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("orders-etl")
    .config("spark.sql.shuffle.partitions", "200")
    .getOrCreate()
)
```

## Reading Data
```python
df = spark.read.option("header", True).option("inferSchema", True).csv("s3a://bucket/raw/orders/")
df = spark.read.parquet("s3a://bucket/curated/orders/")
df = spark.read.json("s3a://bucket/raw/events/")

# Reading from a JDBC database source
df = spark.read.format("jdbc").options(
    url="jdbc:postgresql://host:5432/mydb",
    dbtable="orders",
    user="postgres",
    password=os.getenv("DB_PASSWORD"),
    driver="org.postgresql.Driver",
).load()
```

## DataFrame Operations (parallels pandas, but distributed)
```python
from pyspark.sql import functions as F

# Filtering
delivered = df.filter(F.col("status") == "delivered")

# Selecting / renaming
df2 = df.select("order_id", F.col("amount").alias("total_amount"))

# Adding a column
df = df.withColumn("amount_with_tax", F.col("amount") * 1.18)

# GroupBy / aggregation
summary = df.groupBy("region").agg(
    F.sum("amount").alias("total_sales"),
    F.count("order_id").alias("order_count")
)

# Joins
joined = orders_df.join(customers_df, on="customer_id", how="left")

# Deduplication (keep latest per key — the standard ETL pattern)
from pyspark.sql.window import Window
window_spec = Window.partitionBy("order_id").orderBy(F.col("updated_at").desc())
deduped = (
    df.withColumn("rn", F.row_number().over(window_spec))
      .filter(F.col("rn") == 1)
      .drop("rn")
)
```

## Handling Nulls and Type Casting
```python
df = df.na.fill({"status": "unknown", "amount": 0})
df = df.na.drop(subset=["customer_id"])
df = df.withColumn("amount", F.col("amount").cast("double"))
```

## Writing Output
```python
(
    df.write
    .mode("overwrite")            # or "append"
    .partitionBy("order_date")
    .parquet("s3a://bucket/curated/orders/")
)

# Writing to a JDBC database
df.write.format("jdbc").options(
    url="jdbc:postgresql://host:5432/mydb", dbtable="orders_summary",
    user="postgres", password=os.getenv("DB_PASSWORD"), driver="org.postgresql.Driver",
).mode("append").save()
```

## Error Handling in Spark Jobs
```python
import logging
logger = logging.getLogger(__name__)

def run_etl_job():
    try:
        df = spark.read.parquet("s3a://bucket/raw/orders/")
        row_count = df.count()
        if row_count == 0:
            raise ValueError("Source data is empty — halting job to avoid loading nothing downstream")

        cleaned = df.dropDuplicates(["order_id"]).filter(F.col("amount") > 0)

        (cleaned.write.mode("overwrite").parquet("s3a://bucket/curated/orders/"))
        logger.info(f"Job completed: {cleaned.count()} rows written")

    except ValueError as e:
        logger.error(f"Data quality issue: {e}")
        raise
    except Exception as e:
        logger.critical(f"Spark job failed unexpectedly: {e}")
        raise
    finally:
        spark.stop()   # always release cluster resources
```

## Performance Tips (Python-developer-relevant)
- **Avoid `.collect()` on large DataFrames** — pulls all data back to the driver's memory, defeating the purpose of distributed processing. Use it only for small, final results.
- **Avoid Python UDFs when a built-in Spark function exists** — Python UDFs serialize data between JVM and Python process-by-process, which is much slower than native Spark SQL functions. Use `pandas_udf` (vectorized) if a UDF is unavoidable.
```python
# SLOW — row-by-row Python UDF
from pyspark.sql.types import DoubleType
slow_tax_udf = F.udf(lambda amt: amt * 1.18, DoubleType())
df = df.withColumn("with_tax", slow_tax_udf(F.col("amount")))

# FAST — native Spark expression, no Python serialization overhead
df = df.withColumn("with_tax", F.col("amount") * 1.18)
```
- **Cache/persist** a DataFrame only if it's reused multiple times downstream: `df.cache()`.
- **Broadcast small tables** in joins to avoid expensive shuffles: `df.join(F.broadcast(small_df), on="id")`.

## Try It Yourself
1. Write a PySpark job that reads a CSV, deduplicates on a key keeping the latest record, and writes partitioned Parquet.
2. Rewrite a Python UDF-based transformation using native Spark functions and compare.
3. Add proper try/except/finally error handling (including `spark.stop()`) to a Spark ETL script.
