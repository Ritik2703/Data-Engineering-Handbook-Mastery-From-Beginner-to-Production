# 9. Cloud SDK — GCP Deep Dive

## Setup & Authentication
```python
# pip install google-cloud-bigquery google-cloud-storage google-cloud-secret-manager
# Auth: set GOOGLE_APPLICATION_CREDENTIALS env var to a service account JSON key path,
# or rely on Application Default Credentials when running inside GCP (Cloud Functions, Compute Engine, etc.)

from google.cloud import bigquery, storage
from google.api_core.exceptions import NotFound, Forbidden, GoogleAPIError

bq_client = bigquery.Client(project="my-gcp-project")
storage_client = storage.Client(project="my-gcp-project")
```

## BigQuery — Querying and Loading
```python
def run_bigquery_query(sql):
    try:
        query_job = bq_client.query(sql)
        return query_job.result().to_dataframe()   # returns a pandas DataFrame directly
    except GoogleAPIError as e:
        logger.error(f"BigQuery query failed: {e}")
        raise

df = run_bigquery_query("""
    SELECT region, SUM(amount) AS total_sales
    FROM `my-gcp-project.analytics.fct_orders`
    WHERE order_date >= '2026-01-01'
    GROUP BY region
""")

def load_parquet_to_bigquery(gcs_uri, table_id):
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        write_disposition="WRITE_APPEND",
    )
    try:
        load_job = bq_client.load_table_from_uri(gcs_uri, table_id, job_config=job_config)
        load_job.result()  # blocks until job completes, raises on failure
        logger.info(f"Loaded {load_job.output_rows} rows into {table_id}")
    except GoogleAPIError as e:
        logger.error(f"BigQuery load job failed: {e}")
        raise

# Loading directly from a pandas DataFrame (no GCS staging needed for smaller datasets)
def load_dataframe_to_bigquery(df, table_id):
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    load_job = bq_client.load_table_from_dataframe(df, table_id, job_config=job_config)
    load_job.result()
```

## Cloud Storage (GCS) — Object Storage Operations
```python
def upload_to_gcs(bucket_name, blob_name, local_path):
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(local_path)
        logger.info(f"Uploaded {local_path} to gs://{bucket_name}/{blob_name}")
    except NotFound:
        logger.error(f"Bucket not found: {bucket_name}")
        raise
    except Forbidden:
        logger.critical("Insufficient permissions for this GCS operation")
        raise

def download_from_gcs(bucket_name, blob_name, local_path):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.download_to_filename(local_path)

def list_gcs_files(bucket_name, prefix=""):
    return [blob.name for blob in storage_client.list_blobs(bucket_name, prefix=prefix)]

# Reading directly into pandas without a local temp file
import pandas as pd
import io
bucket = storage_client.bucket("my-bucket")
blob = bucket.blob("raw/orders/2026-07-25.parquet")
data = io.BytesIO(blob.download_as_bytes())
df = pd.read_parquet(data)
```

## Secret Manager — Secure Credential Retrieval
```python
from google.cloud import secretmanager

def get_secret(project_id, secret_id, version="latest"):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version}"
    try:
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except GoogleAPIError as e:
        logger.error(f"Failed to retrieve secret {secret_id}: {e}")
        raise

db_password = get_secret("my-gcp-project", "prod-db-password")
```

## Cloud SQL Connection (managed Postgres/MySQL)
```python
# pip install cloud-sql-python-connector
from google.cloud.sql.connector import Connector
import sqlalchemy

connector = Connector()

def get_conn():
    return connector.connect(
        "my-project:region:instance-name",
        "pg8000",
        user="my_user",
        password=os.getenv("DB_PASSWORD"),
        db="mydb",
    )

engine = sqlalchemy.create_engine("postgresql+pg8000://", creator=get_conn, pool_size=5)
df = pd.read_sql("SELECT * FROM orders LIMIT 10", engine)
```

## Pub/Sub — Streaming Ingestion (Kafka-equivalent)
```python
from google.cloud import pubsub_v1
import json

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path("my-gcp-project", "orders-topic")

def publish_event(event_dict):
    future = publisher.publish(topic_path, json.dumps(event_dict).encode("utf-8"))
    return future.result()  # blocks until publish confirmed, raises on failure

publish_event({"order_id": 1001, "amount": 599})

# Subscriber (worker pulling messages)
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path("my-gcp-project", "orders-sub")

def callback(message):
    try:
        data = json.loads(message.data.decode("utf-8"))
        process_order(data)
        message.ack()   # only ack after successful processing
    except Exception as e:
        logger.error(f"Failed to process message: {e}")
        message.nack()  # message will be redelivered

streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
```

## Triggering a Dataflow (Apache Beam) Job Programmatically
```python
from googleapiclient.discovery import build

dataflow = build("dataflow", "v1b3", credentials=credential)

def launch_dataflow_template(project_id, template_path, parameters):
    request = dataflow.projects().templates().launch(
        projectId=project_id,
        gcsPath=template_path,
        body={"parameters": parameters, "environment": {"tempLocation": "gs://my-bucket/temp"}},
    )
    response = request.execute()
    logger.info(f"Launched Dataflow job: {response['job']['id']}")
    return response["job"]["id"]
```

## Error Handling Pattern Specific to GCP SDK
```python
from google.api_core.exceptions import NotFound, Forbidden, DeadlineExceeded, GoogleAPIError

try:
    run_bigquery_query(sql)
except NotFound:
    logger.error("Referenced table/dataset does not exist")
except Forbidden:
    logger.critical("Insufficient IAM permissions for this BigQuery operation")
    raise
except DeadlineExceeded:
    logger.warning("Query timed out — consider optimizing or increasing timeout")
except GoogleAPIError as e:
    logger.error(f"GCP API error: {e}")
    raise
```

## Try It Yourself
1. Write a function that queries BigQuery and returns results directly as a pandas DataFrame.
2. Load a local Parquet file into GCS, then load it from GCS into a BigQuery table.
3. Retrieve a secret from Secret Manager and use it to authenticate a Cloud SQL connection.
