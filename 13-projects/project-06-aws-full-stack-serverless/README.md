# Project 6: Complete AWS Serverless-First Pipeline — Lambda + Glue + Redshift + QuickSight

## Business Scenario
A media/publishing company wants an event-driven, fully serverless pipeline (no clusters to manage) processing article-view events into a Redshift warehouse, extending the AWS deep dive from `07-cloud-platforms/03` into a fully worked project.

## Architecture
```
[Web app] --view event--> API Gateway --> Lambda (validate + write to S3 raw)
                                                  |
                                     S3 raw zone (JSON, partitioned by date)
                                                  |
                            S3 Event Notification --triggers--> Lambda
                            (small, fast validation/enrichment)
                                                  |
                                     S3 curated zone (Parquet)
                                                  |
                                     Glue Crawler (schema discovery)
                                                  |
                                     Glue ETL Job (aggregation)
                                                  |
                                     Redshift (COPY from S3, Redshift Serverless)
                                                  |
                                     QuickSight (dashboards)

  [Step Functions orchestrates the Glue Job -> Redshift COPY -> QuickSight
   refresh chain; EventBridge schedules the nightly trigger]
```

## Stage 1: Lambda — Ingesting the Event
```python
# lambda_ingest_view_event.py -- reuses the boto3 pattern from
# 03-python/07-cloud-sdk-aws-boto3.md
import json, boto3, os
from datetime import datetime

s3 = boto3.client("s3")
BUCKET = os.environ["DATA_LAKE_BUCKET"]

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
        required_fields = {"article_id", "user_id", "view_duration_seconds"}
        if not required_fields.issubset(body.keys()):
            return {"statusCode": 400, "body": json.dumps({"error": "Missing required fields"})}

        body["ingested_at"] = datetime.utcnow().isoformat()
        key = f"raw/article_views/dt={datetime.utcnow().strftime('%Y-%m-%d')}/{body['article_id']}_{context.aws_request_id}.json"
        s3.put_object(Bucket=BUCKET, Key=key, Body=json.dumps(body))

        return {"statusCode": 200, "body": json.dumps({"status": "accepted"})}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
```

## Stage 2: Glue Job — Aggregation
```python
# glue_aggregate_views.py -- recap 04-etl-elt/07
import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import functions as F

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

views_dyf = glueContext.create_dynamic_frame.from_catalog(
    database="raw_zone", table_name="article_views", transformation_ctx="views_dyf"
)
views_df = views_dyf.toDF()

daily_summary = (
    views_df.groupBy("article_id", F.to_date("ingested_at").alias("view_date"))
    .agg(
        F.count("user_id").alias("total_views"),
        F.countDistinct("user_id").alias("unique_viewers"),
        F.avg("view_duration_seconds").alias("avg_duration"),
    )
)

daily_summary.write.mode("overwrite").parquet("s3://my-media-data-lake/curated/daily_article_summary/")
job.commit()
```

## Stage 3: Redshift — Loading via COPY
```sql
CREATE TABLE fct_daily_article_summary (
    article_id VARCHAR(50),
    view_date DATE,
    total_views INT,
    unique_viewers INT,
    avg_duration FLOAT
)
DISTKEY(article_id)
SORTKEY(view_date);

COPY fct_daily_article_summary
FROM 's3://my-media-data-lake/curated/daily_article_summary/'
IAM_ROLE 'arn:aws:iam::123456789:role/RedshiftLoadRole'
FORMAT AS PARQUET;
```

## Stage 4: Step Functions — Orchestrating the Chain
```json
{
  "StartAt": "RunGlueJob",
  "States": {
    "RunGlueJob": {
      "Type": "Task",
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Parameters": { "JobName": "glue_aggregate_views" },
      "Next": "LoadRedshift"
    },
    "LoadRedshift": {
      "Type": "Task",
      "Resource": "arn:aws:states:::aws-sdk:redshiftdata:executeStatement",
      "Parameters": {
        "ClusterIdentifier": "analytics-cluster",
        "Database": "analytics",
        "Sql": "COPY fct_daily_article_summary FROM 's3://my-media-data-lake/curated/daily_article_summary/' IAM_ROLE 'arn:aws:iam::123456789:role/RedshiftLoadRole' FORMAT AS PARQUET;"
      },
      "Next": "RefreshQuickSight"
    },
    "RefreshQuickSight": {
      "Type": "Task",
      "Resource": "arn:aws:states:::aws-sdk:quicksight:createIngestion",
      "End": true
    }
  }
}
```

## Stage 5: QuickSight — The Dashboard
```
SPICE (QuickSight's in-memory engine, conceptually similar to Power
BI's Import mode / Tableau's Extract) refreshed via the Step Functions
chain's final step, ensuring the dashboard NEVER shows data from before
the Redshift load finished -- the exact race-condition-avoidance pattern
covered in 09-visualization/04's Power BI REST API discussion, here
implemented natively within the AWS ecosystem.
```

## What This Project Demonstrates
```
A genuinely serverless-first AWS pipeline: API Gateway + Lambda for
event ingestion (no servers to manage at the edge), Glue for serverless
Spark transformation, Redshift Serverless/COPY for warehouse loading,
and Step Functions for native AWS-to-AWS orchestration -- directly
implementing the AWS deep dive from 07-cloud-platforms/03 and the
serverless/elasticity concepts from 07-cloud-platforms/02, fully coded.
```


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Real mastery is quiet, built brick by brick, project by project, without needing applause."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
