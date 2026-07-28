# 3. AWS — Deep Dive (Full Data Platform)

## AWS's Overall Philosophy
AWS (launched 2006, the pioneer of modern cloud computing) offers the BROADEST set of individual, composable services — giving maximum flexibility and control, at the cost of needing to understand and wire together more individual pieces yourself compared to some more opinionated/integrated competitors.

## The Complete AWS Data Pipeline (how the pieces fit together)
```
Sources (apps, APIs, on-prem DBs via DMS)
        |
        v
   S3 (raw zone) ←──────────────── the foundational storage layer EVERYTHING else builds on
        |
   Glue Crawler (schema discovery) → Glue Data Catalog (central metadata)
        |
   Glue ETL Job / EMR (Spark) — transform
        |
   S3 (curated zone) ── or ── Redshift (data warehouse)
        |
   Athena (serverless SQL on S3) / QuickSight / Power BI / Tableau
```

## Storage — S3 (the foundation of almost everything)
```python
import boto3
s3 = boto3.client("s3")

# Storage classes — a REAL cost lever, not just a technical detail
# S3 Standard: frequently accessed data
# S3 Infrequent Access (IA): cheaper storage, retrieval fee, for monthly-ish access patterns
# S3 Glacier / Glacier Deep Archive: very cheap, for long-term archival/compliance data,
#   retrieval takes minutes to hours — NOT for active pipeline data

# Lifecycle policies automate moving data through these tiers as it ages —
# a critical, often-overlooked cost optimization (see file 8)
s3.put_bucket_lifecycle_configuration(
    Bucket="my-data-lake",
    LifecycleConfiguration={
        "Rules": [{
            "ID": "archive-old-raw-data",
            "Status": "Enabled",
            "Filter": {"Prefix": "raw/"},
            "Transitions": [
                {"Days": 30, "StorageClass": "STANDARD_IA"},
                {"Days": 90, "StorageClass": "GLACIER"},
            ]
        }]
    }
)
```

## Glue — Serverless ETL + Metadata Catalog (recap + production depth)
Glue's Data Catalog is the SINGLE most important AWS data concept to understand deeply — it's the shared metadata layer that Athena, Redshift Spectrum, EMR, and Glue jobs ALL read from consistently, avoiding each tool needing its own separate schema definition (see `04-etl-elt/07-aws-glue-deep-dive.md` for full depth).

## Redshift — The AWS Data Warehouse
```sql
-- Redshift uses distribution keys and sort keys for MPP performance (see 05-databases/02)
CREATE TABLE fct_orders (
    order_id BIGINT, customer_id INT, order_date DATE, amount DECIMAL(10,2)
)
DISTKEY(customer_id)      -- co-locates same-customer rows on the same compute node for fast joins
SORTKEY(order_date);       -- enables zone-map pruning for date-range queries

-- Redshift Spectrum: query data directly in S3 WITHOUT loading it into Redshift first —
-- blurs the line between "warehouse" and "lake" for less-frequently-queried historical data
SELECT * FROM spectrum_schema.historical_orders WHERE order_date < '2023-01-01';
```
**Redshift Serverless** (newer offering): removes the need to manage cluster sizing entirely, scaling automatically and billing per-second of actual usage — AWS's answer to Snowflake/BigQuery's serverless-first model.

## Athena — Serverless SQL, Pay-Per-Query
```sql
-- Query data DIRECTLY in S3, no loading/warehouse needed — perfect for ad-hoc/exploratory analysis
SELECT region, SUM(amount) FROM orders_table WHERE year = 2026 GROUP BY region;
```
**Cost model**: billed per TB of data SCANNED — this makes partitioning and using columnar formats (Parquet) directly impact your bill, not just query speed (a `SELECT *` on a huge unpartitioned CSV table can be a genuinely expensive mistake here).

## EMR — Managed Hadoop/Spark Clusters
Closer to "managed infrastructure" than fully abstracted — you choose instance types/cluster size, giving fine control at the cost of more operational awareness (see `06-big-data/08-big-data-on-cloud.md` for full comparison against Databricks/Dataproc).

## Lambda — Serverless Event-Driven Compute
```python
# A common DE pattern: trigger a Lambda automatically when a new file lands in S3
def lambda_handler(event, context):
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]
    # e.g., trigger a Glue job, validate the file, or kick off a Step Functions workflow
    trigger_downstream_processing(bucket, key)
```
**Real production use**: event-driven, "as data arrives" pipeline triggers, avoiding the need for a constantly-running poller checking "has a new file arrived yet?"

## Step Functions — Orchestrating Multi-Service Workflows
```json
{
  "StartAt": "ExtractData",
  "States": {
    "ExtractData": {"Type": "Task", "Resource": "arn:aws:states:::lambda:invoke", "Next": "RunGlueJob"},
    "RunGlueJob": {"Type": "Task", "Resource": "arn:aws:states:::glue:startJobRun.sync", "Next": "NotifySuccess"},
    "NotifySuccess": {"Type": "Task", "Resource": "arn:aws:states:::sns:publish", "End": true}
  }
}
```
AWS's native visual/JSON-based orchestrator for coordinating Lambda, Glue, EMR, and other AWS services together — the AWS-native alternative to Airflow for AWS-centric workflows (many companies still prefer Airflow/MWAA for its portability and richer community ecosystem).

## Kinesis — Managed Streaming (Kafka-equivalent)
```python
import boto3
kinesis = boto3.client("kinesis")
kinesis.put_record(StreamName="orders-stream", Data=json.dumps(order_event).encode(), PartitionKey=str(order_id))
```
**Kinesis vs self-managed Kafka (MSK)**: Kinesis is more fully-managed/simpler to operate but less flexible/portable; MSK (Managed Streaming for Kafka) gives you genuine open-source Kafka compatibility (easier to migrate elsewhere later) with AWS handling the operational burden.

## DMS (Database Migration Service) — Moving Data INTO AWS
Specifically built for migrating databases (on-prem or other clouds) into AWS, supporting both one-time bulk migration AND ongoing CDC replication (keeping a source database and an AWS target continuously in sync during a gradual migration) — directly relevant to file 7's migration playbook.

## Secrets Manager & KMS — Security Foundations
```python
# Secrets Manager: store/retrieve credentials securely (see 03-python/07-cloud-sdk-aws-boto3.md)
# KMS (Key Management Service): manages encryption keys used to encrypt S3 buckets,
#   RDS databases, and virtually every other AWS data service — foundational to file 9
```

## Interview Traps
- "Why would you use Athena instead of loading data into Redshift?" — for ad-hoc/exploratory/infrequent queries where standing up and paying for a warehouse cluster isn't justified; Athena's pay-per-scan model fits sporadic access patterns better.
- "Kinesis vs MSK (managed Kafka) — how do you choose?" — Kinesis for simplicity/full AWS-native integration when portability isn't a concern; MSK when you need genuine Kafka API compatibility (existing Kafka-based tooling, or wanting to avoid AWS-specific lock-in).
- Be ready to explain why the Glue Data Catalog is the "glue" (pun intended) holding the whole AWS analytics ecosystem together, consistently queryable across Athena/Redshift Spectrum/EMR.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"To serve knowledge selflessly is to keep it alive for those who come after you."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
