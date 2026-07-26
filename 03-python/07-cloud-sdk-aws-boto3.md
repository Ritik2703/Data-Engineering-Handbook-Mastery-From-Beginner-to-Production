# 7. Cloud SDK — AWS (boto3) Deep Dive

## Setup & Credentials
```python
import boto3

# Best practice: let boto3 find credentials automatically via IAM role (on EC2/Lambda/Glue)
# or ~/.aws/credentials locally — NEVER hardcode access keys in code
session = boto3.Session(region_name="ap-south-1")
s3 = session.client("s3")
```

## S3 — Object Storage Operations
```python
import boto3
from botocore.exceptions import ClientError

s3 = boto3.client("s3", region_name="ap-south-1")

def upload_file_to_s3(local_path, bucket, s3_key):
    try:
        s3.upload_file(local_path, bucket, s3_key)
        logger.info(f"Uploaded {local_path} to s3://{bucket}/{s3_key}")
    except ClientError as e:
        logger.error(f"S3 upload failed: {e}")
        raise
    except FileNotFoundError:
        logger.error(f"Local file not found: {local_path}")
        raise

def download_file_from_s3(bucket, s3_key, local_path):
    try:
        s3.download_file(bucket, s3_key, local_path)
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            logger.error(f"File not found: s3://{bucket}/{s3_key}")
        else:
            logger.error(f"S3 download failed: {e}")
        raise

def list_s3_files(bucket, prefix):
    """Handles pagination automatically — critical for buckets with 1000+ objects."""
    paginator = s3.get_paginator("list_objects_v2")
    all_keys = []
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            all_keys.append(obj["Key"])
    return all_keys

# Reading a file directly into memory (e.g., into pandas) without downloading to disk first
import pandas as pd
obj = s3.get_object(Bucket="my-bucket", Key="raw/orders/2026-07-25.parquet")
df = pd.read_parquet(obj["Body"])

# Writing a DataFrame directly to S3 without a local temp file
import io
buffer = io.BytesIO()
df.to_parquet(buffer, index=False)
s3.put_object(Bucket="my-bucket", Key="curated/orders/2026-07-25.parquet", Body=buffer.getvalue())
```

## Glue — Triggering and Monitoring ETL Jobs
```python
glue = boto3.client("glue", region_name="ap-south-1")

def run_glue_job_and_wait(job_name, arguments, poll_interval=30):
    response = glue.start_job_run(JobName=job_name, Arguments=arguments)
    run_id = response["JobRunId"]
    logger.info(f"Started Glue job {job_name}, run ID: {run_id}")

    import time
    while True:
        status = glue.get_job_run(JobName=job_name, RunId=run_id)["JobRun"]["JobRunState"]
        if status in ("SUCCEEDED",):
            logger.info(f"Glue job {job_name} succeeded")
            return True
        elif status in ("FAILED", "TIMEOUT", "STOPPED"):
            logger.error(f"Glue job {job_name} ended with status: {status}")
            return False
        time.sleep(poll_interval)
```

## Redshift Data API (query without managing a persistent connection)
```python
redshift_data = boto3.client("redshift-data", region_name="ap-south-1")

def run_redshift_query(cluster_id, database, db_user, sql):
    response = redshift_data.execute_statement(
        ClusterIdentifier=cluster_id, Database=database, DbUser=db_user, Sql=sql
    )
    statement_id = response["Id"]

    import time
    while True:
        desc = redshift_data.describe_statement(Id=statement_id)
        if desc["Status"] == "FINISHED":
            break
        elif desc["Status"] in ("FAILED", "ABORTED"):
            raise RuntimeError(f"Query failed: {desc.get('Error')}")
        time.sleep(1)

    result = redshift_data.get_statement_result(Id=statement_id)
    return result["Records"]
```

## Lambda — Invoking Serverless Functions
```python
lambda_client = boto3.client("lambda", region_name="ap-south-1")

import json
response = lambda_client.invoke(
    FunctionName="process-new-file",
    InvocationType="RequestResponse",  # synchronous; use "Event" for fire-and-forget async
    Payload=json.dumps({"bucket": "my-bucket", "key": "raw/orders/new.json"}),
)
result = json.loads(response["Payload"].read())
```

## Secrets Manager — Secure Credential Retrieval (production standard)
```python
import json
import boto3
from botocore.exceptions import ClientError

def get_secret(secret_name, region_name="ap-south-1"):
    client = boto3.client("secretsmanager", region_name=region_name)
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response["SecretString"])
    except ClientError as e:
        logger.error(f"Failed to retrieve secret {secret_name}: {e}")
        raise

db_creds = get_secret("prod/redshift/creds")
db_password = db_creds["password"]  # never hardcoded, never logged
```

## SQS — Message Queues (decoupling pipeline stages)
```python
sqs = boto3.client("sqs", region_name="ap-south-1")

# Sending a message (e.g., "new file arrived, process it")
sqs.send_message(
    QueueUrl="https://sqs.ap-south-1.amazonaws.com/123456789/file-processing-queue",
    MessageBody=json.dumps({"bucket": "my-bucket", "key": "raw/orders/new.json"})
)

# Receiving and processing messages (typical worker loop)
def poll_queue(queue_url):
    while True:
        response = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10, WaitTimeSeconds=20)
        messages = response.get("Messages", [])
        for msg in messages:
            try:
                body = json.loads(msg["Body"])
                process_file(body["bucket"], body["key"])
                # Delete only after successful processing (at-least-once delivery pattern)
                sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=msg["ReceiptHandle"])
            except Exception as e:
                logger.error(f"Failed to process message: {e}")
                # Don't delete — message will reappear after visibility timeout for retry
```

## Athena — Serverless SQL Queries on S3
```python
athena = boto3.client("athena", region_name="ap-south-1")

def run_athena_query(query, database, output_location):
    response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={"Database": database},
        ResultConfiguration={"OutputLocation": output_location},
    )
    query_id = response["QueryExecutionId"]

    import time
    while True:
        status = athena.get_query_execution(QueryExecutionId=query_id)["QueryExecution"]["Status"]["State"]
        if status == "SUCCEEDED":
            break
        elif status in ("FAILED", "CANCELLED"):
            raise RuntimeError(f"Athena query failed: {status}")
        time.sleep(2)

    results = athena.get_query_results(QueryExecutionId=query_id)
    return results["ResultSet"]["Rows"]
```

## Error Handling Pattern Specific to boto3
```python
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError

try:
    s3.upload_file(local_path, bucket, key)
except NoCredentialsError:
    logger.critical("AWS credentials not found — check IAM role/environment configuration")
    raise
except EndpointConnectionError:
    logger.error("Could not reach AWS endpoint — check network/VPC configuration")
    raise
except ClientError as e:
    error_code = e.response["Error"]["Code"]
    if error_code == "NoSuchBucket":
        logger.error(f"Bucket does not exist: {bucket}")
    elif error_code == "AccessDenied":
        logger.error(f"IAM permissions insufficient for this operation on {bucket}")
    else:
        logger.error(f"AWS ClientError [{error_code}]: {e}")
    raise
```

## Try It Yourself
1. Write a function that uploads a pandas DataFrame directly to S3 as Parquet, without a local temp file.
2. Write a Glue job trigger function that polls until completion and logs the final status.
3. Retrieve database credentials from Secrets Manager and use them to connect to Redshift.
