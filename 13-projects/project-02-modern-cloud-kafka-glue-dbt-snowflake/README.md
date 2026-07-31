# Project 2: The Modern Cloud Stack — Kafka + S3 + AWS Glue + dbt + Snowflake

## Business Scenario
A modern e-commerce startup needs to ingest real-time order events, land them reliably in a data lake, transform them with a serverless engine, and model them in Snowflake with full test coverage — the "modern data stack" pattern described in `04-etl-elt/09` and `06-big-data/09`.

## Architecture
```
[Order Service] --publishes--> [Kafka topic: orders] --consumed by--> [Kafka Connect S3 Sink]
                                                                              |
                                                                              v
                                                              S3 raw zone (Bronze, JSON,
                                                              partitioned by dt=YYYY-MM-DD)
                                                                              |
                                                              [Glue Crawler] -> Glue Data Catalog
                                                                              |
                                                              [Glue ETL Job (PySpark)] -- clean,
                                                              dedupe, cast types, write Parquet
                                                                              |
                                                              S3 curated zone (Silver, Parquet)
                                                                              |
                                                              [Snowpipe] -- auto-ingest into Snowflake
                                                                              |
                                                              Snowflake RAW schema
                                                                              |
                                                              [dbt] -- staging -> intermediate -> marts
                                                                              |
                                                              Snowflake ANALYTICS schema (Gold)
                                                                              |
                                                              [Airflow] orchestrates the whole chain
                                                              nightly + dbt Cloud/Airflow triggers dbt runs
```

## Stage 1: Kafka Producer — Order Events
```python
# producer.py -- reuses the Kafka pattern from 06-big-data/05-streaming-fundamentals.md
from kafka import KafkaProducer
import json, time, random
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers=["broker1:9092"],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    key_serializer=lambda k: k.encode("utf-8"),
    acks="all",
)

def emit_order_event():
    event = {
        "order_id": f"ORD-{random.randint(100000, 999999)}",
        "customer_id": f"CUST-{random.randint(1, 5000)}",
        "amount": round(random.uniform(10, 500), 2),
        "status": random.choice(["placed", "confirmed", "shipped"]),
        "event_time": datetime.utcnow().isoformat(),
    }
    producer.send("orders", key=event["customer_id"], value=event)

if __name__ == "__main__":
    while True:
        emit_order_event()
        time.sleep(0.1)
```

## Stage 2: Kafka Connect S3 Sink — Landing Raw Events
```json
{
  "name": "s3-sink-orders",
  "config": {
    "connector.class": "io.confluent.connect.s3.S3SinkConnector",
    "topics": "orders",
    "s3.bucket.name": "my-company-data-lake",
    "topics.dir": "raw/orders",
    "flush.size": "1000",
    "partitioner.class": "io.confluent.connect.storage.partitioner.TimeBasedPartitioner",
    "path.format": "'dt'=YYYY-MM-dd",
    "format.class": "io.confluent.connect.s3.format.json.JsonFormat"
  }
}
```
This is the managed-connector alternative to hand-writing a consumer script — Kafka Connect handles batching, partitioning by date, and reliable delivery to S3 declaratively.

## Stage 3: AWS Glue Crawler + ETL Job
```python
# glue_transform_orders.py -- reuses the DynamicFrame pattern from
# 04-etl-elt/07-aws-glue-deep-dive.md
import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

orders_dyf = glueContext.create_dynamic_frame.from_catalog(
    database="raw_zone", table_name="orders", transformation_ctx="orders_dyf"  # Job Bookmark enabled
)
orders_df = orders_dyf.toDF()

# Deduplication -- keep latest event per order_id (recap 06-big-data/10)
window_spec = Window.partitionBy("order_id").orderBy(F.col("event_time").desc())
cleaned_df = (
    orders_df.withColumn("rn", F.row_number().over(window_spec))
    .filter(F.col("rn") == 1).drop("rn")
    .withColumn("amount", F.col("amount").cast("double"))
    .withColumn("event_date", F.to_date("event_time"))
)

cleaned_dyf = DynamicFrame.fromDF(cleaned_df, glueContext, "cleaned_dyf")
glueContext.write_dynamic_frame.from_options(
    frame=cleaned_dyf,
    connection_type="s3",
    connection_options={"path": "s3://my-company-data-lake/curated/orders/", "partitionKeys": ["event_date"]},
    format="parquet",
)
job.commit()
```

## Stage 4: Snowpipe — Continuous Ingestion Into Snowflake
```sql
-- Auto-ingests new Parquet files as they land in S3, no manual COPY needed
CREATE OR REPLACE STAGE orders_stage
    URL = 's3://my-company-data-lake/curated/orders/'
    STORAGE_INTEGRATION = my_s3_integration
    FILE_FORMAT = (TYPE = PARQUET);

CREATE OR REPLACE PIPE orders_pipe
    AUTO_INGEST = TRUE
    AS
    COPY INTO raw.orders
    FROM @orders_stage
    MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;
```

## Stage 5: dbt — Staging, Intermediate, Marts
```sql
-- models/staging/stg_orders.sql (recap 04-etl-elt/08)
{{ config(materialized='view') }}
SELECT
    order_id,
    customer_id,
    CAST(amount AS NUMERIC(10,2)) AS amount,
    LOWER(TRIM(status)) AS status,
    CAST(event_time AS TIMESTAMP) AS order_time
FROM {{ source('raw', 'orders') }}
WHERE order_id IS NOT NULL
```
```sql
-- models/marts/fct_orders.sql
{{ config(materialized='incremental', unique_key='order_id') }}
SELECT order_id, customer_id, amount, status, order_time
FROM {{ ref('stg_orders') }}
{% if is_incremental() %}
  WHERE order_time > (SELECT MAX(order_time) FROM {{ this }})
{% endif %}
```
```yaml
# models/marts/schema.yml -- tests give this pipeline real production confidence
models:
  - name: fct_orders
    columns:
      - name: order_id
        tests: [unique, not_null]
      - name: status
        tests:
          - accepted_values:
              values: ['placed', 'confirmed', 'shipped', 'delivered', 'cancelled']
      - name: amount
        tests:
          - dbt_utils.accepted_range:
              min_value: 0
```

## Stage 6: Airflow — Orchestrating the Chain
```python
# dags/orders_pipeline.py -- reuses the pattern from 08-orchestration/03
from airflow.decorators import dag, task
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.operators.bash import BashOperator
from datetime import datetime

@dag(schedule="0 3 * * *", start_date=datetime(2026, 1, 1), catchup=False, tags=["orders"])
def orders_pipeline():
    run_glue = GlueJobOperator(task_id="transform_orders", job_name="glue_transform_orders")
    run_dbt = BashOperator(task_id="run_dbt", bash_command="cd /dbt_project && dbt build --target prod")
    run_glue >> run_dbt

orders_pipeline()
```

## Stage 7: Snowflake — Serving Layer
```sql
-- Analytics-ready mart, tagged with a warehouse sized for the actual
-- workload (recap 07-cloud-platforms/08's FinOps guidance)
CREATE WAREHOUSE analytics_wh WITH WAREHOUSE_SIZE = 'SMALL' AUTO_SUSPEND = 60 AUTO_RESUME = TRUE;

SELECT customer_id, COUNT(*) AS order_count, SUM(amount) AS total_spend
FROM analytics.fct_orders
GROUP BY customer_id
ORDER BY total_spend DESC
LIMIT 100;
```

## What This Project Demonstrates
```
Kafka producer/consumer patterns, Kafka Connect managed sinks, AWS Glue
DynamicFrames with Job Bookmarks, Snowpipe continuous ingestion, dbt's
full staging->mart layering WITH tests, incremental models, and Airflow
orchestration tying a genuinely modern, production-grade ELT pipeline
together end to end.
```


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Every finished project is a small victory of patience over doubt."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
