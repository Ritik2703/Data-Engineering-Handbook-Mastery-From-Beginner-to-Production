# 7. AWS Glue — Deep Dive

## What Glue Is
AWS Glue is AWS's **serverless** ETL service — built on Apache Spark under the hood, but you don't manage clusters directly (Glue provisions and tears them down automatically per job run). It's the AWS-native answer to "how do we run Spark-based ETL without managing EMR clusters ourselves."

## Core Components

### Glue Data Catalog — the central metadata store
A persistent metastore (Hive-metastore-compatible) that stores table definitions — schema, location, format — for data sitting in S3. This is the single most important Glue concept: **once a table is in the Data Catalog, Athena, Redshift Spectrum, EMR, and Glue jobs can all query it consistently**, without each tool needing its own separate schema definition.

### Glue Crawlers — automatic schema discovery
A Crawler scans data in S3 (or a JDBC source), infers the schema (column names, types, partitions), and automatically registers/updates a table in the Data Catalog.
```python
# Conceptually, what a Crawler does (you configure this via console/API, not by writing this code):
# 1. Scan s3://my-bucket/raw/orders/
# 2. Detect: it's Parquet, columns are (order_id: int, customer_id: int, amount: double, ...)
# 3. Detect partitioning: s3://my-bucket/raw/orders/year=2026/month=07/day=25/
# 4. Register/update table "orders" in the Glue Data Catalog with this schema + partition scheme
```
**Real scenario**: new files land in S3 daily with a slightly evolving schema (a new column added) — a scheduled Crawler keeps the Data Catalog in sync automatically, so downstream Athena queries and Glue jobs always see the current schema without manual intervention.

### Glue Jobs — the actual ETL/transformation logic
Written in **PySpark** (or Scala), either hand-coded or generated via **Glue Studio's** visual, drag-and-drop interface (Glue's answer to SSIS Data Flow / ADF Mapping Data Flows).
```python
# A typical Glue job script (auto-generated skeleton + your custom logic)
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ["JOB_NAME", "source_path", "target_path"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Read from the Data Catalog (not directly from S3 — this is the Glue-specific pattern)
orders_dyf = glueContext.create_dynamic_frame.from_catalog(
    database="raw_zone", table_name="orders"
)

# DynamicFrame -> Spark DataFrame for familiar PySpark transformation logic
orders_df = orders_dyf.toDF()
cleaned_df = (
    orders_df.dropDuplicates(["order_id"])
    .filter(orders_df["amount"] > 0)
)

# Back to DynamicFrame to write out (Glue's native write path, handles schema evolution gracefully)
from awsglue.dynamicframe import DynamicFrame
cleaned_dyf = DynamicFrame.fromDF(cleaned_df, glueContext, "cleaned_dyf")

glueContext.write_dynamic_frame.from_options(
    frame=cleaned_dyf,
    connection_type="s3",
    connection_options={"path": args["target_path"], "partitionKeys": ["order_date"]},
    format="parquet",
)

job.commit()
```

### DynamicFrame vs DataFrame — Glue's key extra abstraction
A **DynamicFrame** is Glue's own data structure, similar to a Spark DataFrame but designed to handle **semi-structured, schema-inconsistent data gracefully** — e.g., a column that's sometimes an integer and sometimes a string across different files won't crash a DynamicFrame-based job the way it might a strict DataFrame read. Real production jobs typically convert `DynamicFrame -> DataFrame` for the actual transformation logic (familiar PySpark), then back to `DynamicFrame` for the write step, to get Glue's more forgiving schema handling on read/write while keeping full PySpark flexibility for transforms.

## Glue Studio — Visual ETL Builder
A no-code/low-code canvas (similar in spirit to SSIS Data Flow / ADF Mapping Data Flows) for building simple-to-moderate transformation jobs by connecting Source -> Transform -> Target nodes visually, which then **generates the underlying PySpark script automatically** — useful for less code-heavy teams or quick prototyping, though most production-grade complex logic is still hand-written PySpark for full control.

## Orchestration: Glue Workflows & Triggers
```
Glue Workflow: "nightly_orders_pipeline"
  Trigger (scheduled, cron-based)
        |
        v
  Crawler: scan raw zone for new files
        |
        v
  Job: "transform_orders" (the PySpark script above)
        |
        v
  Crawler: register the newly-written curated table in the Data Catalog
        |
        v
  Job: "load_to_redshift" (COPY curated Parquet into Redshift)
```
For more complex cross-service orchestration (e.g., "wait for a Lambda function, then run this Glue job, then trigger a Step Function"), companies typically use **AWS Step Functions** or **Managed Airflow (MWAA)** on top of/alongside Glue Workflows, rather than Glue Workflows alone.

## Glue Job Bookmarks — Built-in Incremental Processing
```python
# Enabling bookmarks (set at job creation) automatically tracks which files/partitions
# have already been processed, so re-running the job only picks up NEW data since last run —
# without you needing to hand-build a watermark-tracking mechanism yourself.
orders_dyf = glueContext.create_dynamic_frame.from_catalog(
    database="raw_zone", table_name="orders",
    transformation_ctx="orders_dyf"  # this ctx name is what bookmarks key off of
)
```
This is a meaningful convenience over the manual watermark-table pattern needed in SSIS/Informatica/hand-rolled Python — though many teams still prefer explicit watermark control tables for more predictable, auditable incremental logic in complex enterprise scenarios.

## Real Enterprise Example: E-commerce Company's AWS-Native Pipeline
```
S3 (raw zone, JSON from order-service API dumps hourly)
        |
Glue Crawler (runs after each hourly dump, updates Data Catalog schema)
        |
Glue Job "clean_and_dedupe_orders" (PySpark: dedupe, type-cast, filter test orders)
        |
S3 (curated zone, partitioned Parquet by order_date)
        |
Glue Crawler (registers curated table)
        |
Athena (ad-hoc analyst queries directly on curated S3 data, no warehouse load needed for exploration)
        |
Glue Job "load_to_redshift" (COPY curated data into Redshift for BI/Power BI/Tableau consumption)
        |
Step Functions orchestrates the whole chain above, with SNS alerts on any step failure
```

## Interview Traps
- "Why use a DynamicFrame instead of a plain Spark DataFrame?" — more forgiving schema handling for messy/evolving semi-structured data, plus native integration with the Glue Data Catalog and Job Bookmarks.
- "How does Glue know the schema of data in S3?" — the Glue Data Catalog, populated either by a Crawler (automatic) or manually defined.
- "How do you handle incremental loads in Glue?" — Job Bookmarks (built-in) vs a hand-managed watermark/control table (more control, common in complex enterprise scenarios) — know both approaches and their tradeoffs.
