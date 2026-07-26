"""
================================================================================
MASTER LIBRARY REFERENCE — Python for Data Engineers (Enterprise Edition)
================================================================================
Every library a Data Engineer commonly touches in a real product-based company,
with what it's for, how to install it, and a working code snippet.

This file is a REFERENCE, not meant to run top-to-bottom (some sections need
real credentials/servers). Search for the section you need (Ctrl+F the heading).

INDEX
  1.  Core Python stdlib essentials for DE
  2.  Error handling / retries (tenacity)
  3.  Environment & secrets (python-dotenv)
  4.  File formats (csv, json, openpyxl, pyarrow/parquet, xmltodict, pyyaml)
  5.  Data manipulation (pandas, numpy)
  6.  Database connectivity (psycopg2, pymysql, pymongo, snowflake, sqlalchemy, pyodbc, cx_Oracle)
  7.  REST APIs (requests)
  8.  AWS (boto3)
  9.  Azure (azure-identity, azure-storage-blob, azure-keyvault-secrets)
  10. GCP (google-cloud-bigquery, google-cloud-storage, google-cloud-secret-manager)
  11. Microsoft Graph API / SharePoint (msal + requests)
  12. Big data processing (pyspark)
  13. Data quality (great_expectations, pandera)
  14. Orchestration (apache-airflow client-side usage)
  15. Visualization (matplotlib, seaborn, plotly)
  16. Testing (pytest, unittest.mock)
  17. Logging & config (logging, pyyaml, argparse)
================================================================================

INSTALL EVERYTHING (reference requirements.txt):
pip install requests pandas numpy psycopg2-binary pymysql pymongo \
    snowflake-connector-python sqlalchemy pyodbc boto3 msal \
    azure-identity azure-storage-blob azure-keyvault-secrets \
    google-cloud-bigquery google-cloud-storage google-cloud-secret-manager \
    pyspark tenacity python-dotenv pyyaml openpyxl pyarrow xmltodict \
    great_expectations pandera matplotlib seaborn plotly pytest mypy black flake8
"""

import os
import io
import json
import logging
import time
from datetime import datetime, timedelta
from contextlib import contextmanager

# ==============================================================================
# 1. CORE PYTHON STDLIB ESSENTIALS FOR DATA ENGINEERING
# ==============================================================================
"""
Used for: every script touches these. No install needed (built into Python).
"""

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# Custom exceptions — used throughout enterprise pipelines to distinguish failure types
class DataQualityError(Exception):
    """Raised when data fails validation checks. Should HALT the pipeline."""
    pass

class SourceUnavailableError(Exception):
    """Raised when an upstream source (API/DB/file) can't be reached after retries."""
    pass


def retry_decorator(max_attempts=3, delay_seconds=2):
    """Hand-rolled retry pattern — understand this before reaching for `tenacity` below."""
    import functools
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    logger.warning(f"Attempt {attempt}/{max_attempts} failed: {e}")
                    time.sleep(delay_seconds * attempt)  # linear backoff
            raise last_exc
        return wrapper
    return decorator


@contextmanager
def timed_block(label):
    """Context manager to time any block of code — useful for perf debugging."""
    start = time.time()
    try:
        yield
    finally:
        logger.info(f"{label} took {time.time() - start:.2f}s")


# ==============================================================================
# 2. ERROR HANDLING / RETRIES — tenacity (pip install tenacity)
# ==============================================================================
"""
Used for: production-grade retry logic on flaky network/API/DB calls.
Why: hand-rolled retry loops get repeated everywhere; tenacity is declarative,
tested, and the de-facto standard in production Python data pipelines.
"""
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
)
def flaky_network_call():
    """Example: any function that might transiently fail over network."""
    pass


# ==============================================================================
# 3. ENVIRONMENT & SECRETS — python-dotenv (pip install python-dotenv)
# ==============================================================================
"""
Used for: loading local .env files for development so credentials are NEVER
hardcoded in source code. In production, real environment variables or a
secrets manager (Secrets Manager / Key Vault / Secret Manager) replace this.
"""
from dotenv import load_dotenv
load_dotenv()  # reads a local .env file (must be in .gitignore, never committed)

DB_PASSWORD = os.getenv("DB_PASSWORD")
API_KEY = os.getenv("API_KEY")


# ==============================================================================
# 4. FILE FORMATS
# ==============================================================================
"""
csv (stdlib), json (stdlib): built-in, zero install
openpyxl (pip install openpyxl): Excel read/write engine used by pandas
pyarrow (pip install pyarrow): Parquet read/write engine used by pandas, also standalone
xmltodict (pip install xmltodict): converts XML into Python dicts, JSON-like ease
pyyaml (pip install pyyaml): YAML config file parsing (Airflow/dbt/k8s configs)
"""
import csv
import yaml
import xmltodict

def read_csv_stdlib(filepath):
    with open(filepath, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def read_yaml_config(filepath):
    with open(filepath) as f:
        return yaml.safe_load(f)  # ALWAYS safe_load, never load() (arbitrary code execution risk)

def read_xml_as_dict(filepath):
    with open(filepath) as f:
        return xmltodict.parse(f.read())

def read_json_lines(filepath):
    """JSONL — one JSON object per line, common for streaming/event exports."""
    records = []
    with open(filepath) as f:
        for line in f:
            records.append(json.loads(line))
    return records


# ==============================================================================
# 5. DATA MANIPULATION — pandas, numpy (pip install pandas numpy)
# ==============================================================================
"""
Used for: in-memory tabular data cleaning, joining, reshaping — the daily-driver
tool for anything that fits comfortably in RAM (up to a few GB).
"""
import pandas as pd
import numpy as np

def clean_dataframe_example(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(subset=["order_id"], keep="last")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["order_id", "amount"])
    df["status"] = df["status"].str.strip().str.lower()
    df["is_high_value"] = np.where(df["amount"] > 1000, True, False)
    return df

def read_excel_all_sheets(filepath):
    return pd.read_excel(filepath, sheet_name=None, engine="openpyxl")

def read_parquet_specific_columns(filepath, columns):
    return pd.read_parquet(filepath, columns=columns, engine="pyarrow")


# ==============================================================================
# 6. DATABASE CONNECTIVITY
# ==============================================================================
"""
psycopg2-binary: PostgreSQL          | pymysql: MySQL
pymongo: MongoDB (NoSQL)             | snowflake-connector-python: Snowflake
sqlalchemy: universal engine/ORM      | pyodbc: SQL Server (and other ODBC sources)
cx_Oracle: Oracle (legacy enterprise)
"""

@contextmanager
def get_postgres_connection(config: dict):
    """The standard production pattern: connect, commit-on-success, rollback-on-error, always close."""
    import psycopg2
    conn = None
    try:
        conn = psycopg2.connect(**config, connect_timeout=10)
        yield conn
        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def query_mongo_example(uri, db_name, collection_name, filter_dict):
    from pymongo import MongoClient
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
        return list(client[db_name][collection_name].find(filter_dict).limit(100))
    finally:
        client.close()

def query_snowflake_example(account, user, password, warehouse, database, schema, sql):
    import snowflake.connector
    conn = snowflake.connector.connect(
        account=account, user=user, password=password,
        warehouse=warehouse, database=database, schema=schema,
    )
    try:
        cur = conn.cursor()
        cur.execute(sql)
        return cur.fetchall()
    finally:
        conn.close()

def get_sqlalchemy_engine(conn_string):
    """Universal — works with pandas.read_sql / to_sql across Postgres/MySQL/etc."""
    from sqlalchemy import create_engine
    return create_engine(conn_string, pool_size=5, pool_pre_ping=True, pool_recycle=1800)


# ==============================================================================
# 7. REST APIs — requests (pip install requests)
# ==============================================================================
"""
Used for: pulling/pushing data to any HTTP API — SaaS tools, internal microservices,
webhooks. Foundation for every cloud/SharePoint integration below.
"""
import requests

def fetch_paginated_api(base_url, headers, cursor_param="cursor"):
    """Cursor-based pagination — the most common modern API pagination style."""
    all_records = []
    cursor = None
    while True:
        params = {cursor_param: cursor} if cursor else {}
        resp = requests.get(base_url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        page = resp.json()
        all_records.extend(page.get("data", []))
        cursor = page.get("next_cursor")
        if not cursor:
            break
    return all_records

def get_oauth2_token(token_url, client_id, client_secret, scope):
    """Client-credentials OAuth2 flow — used by Graph API, Salesforce, most B2B APIs."""
    resp = requests.post(token_url, data={
        "grant_type": "client_credentials", "client_id": client_id,
        "client_secret": client_secret, "scope": scope,
    })
    resp.raise_for_status()
    return resp.json()["access_token"]


# ==============================================================================
# 8. AWS — boto3 (pip install boto3)
# ==============================================================================
"""
Used for: S3 (storage), Glue (ETL), Redshift (warehouse), Lambda (serverless),
Secrets Manager (credentials), SQS (queues), Athena (serverless SQL).
"""
import boto3
from botocore.exceptions import ClientError

def s3_upload(local_path, bucket, key, region="ap-south-1"):
    s3 = boto3.client("s3", region_name=region)
    try:
        s3.upload_file(local_path, bucket, key)
    except ClientError as e:
        logger.error(f"S3 upload failed: {e}")
        raise

def s3_read_parquet_to_df(bucket, key, region="ap-south-1"):
    s3 = boto3.client("s3", region_name=region)
    obj = s3.get_object(Bucket=bucket, Key=key)
    return pd.read_parquet(io.BytesIO(obj["Body"].read()))

def get_aws_secret(secret_name, region="ap-south-1"):
    client = boto3.client("secretsmanager", region_name=region)
    resp = client.get_secret_value(SecretId=secret_name)
    return json.loads(resp["SecretString"])


# ==============================================================================
# 9. AZURE — azure-identity, azure-storage-blob, azure-keyvault-secrets
# ==============================================================================
"""
pip install azure-identity azure-storage-blob azure-keyvault-secrets
Used for: Blob/ADLS storage, Key Vault (secrets), Service Principal auth.
"""

def azure_get_credential():
    from azure.identity import ClientSecretCredential
    return ClientSecretCredential(
        tenant_id=os.getenv("AZURE_TENANT_ID"),
        client_id=os.getenv("AZURE_CLIENT_ID"),
        client_secret=os.getenv("AZURE_CLIENT_SECRET"),
    )

def azure_blob_download_to_df(account_url, container, blob_name):
    from azure.storage.blob import BlobServiceClient
    client = BlobServiceClient(account_url=account_url, credential=azure_get_credential())
    blob_client = client.get_blob_client(container=container, blob=blob_name)
    data = io.BytesIO(blob_client.download_blob().readall())
    return pd.read_parquet(data)

def azure_get_secret(vault_url, secret_name):
    from azure.keyvault.secrets import SecretClient
    client = SecretClient(vault_url=vault_url, credential=azure_get_credential())
    return client.get_secret(secret_name).value


# ==============================================================================
# 10. GCP — google-cloud-bigquery, google-cloud-storage, google-cloud-secret-manager
# ==============================================================================
"""
pip install google-cloud-bigquery google-cloud-storage google-cloud-secret-manager
Used for: BigQuery (warehouse), Cloud Storage (lake), Secret Manager (credentials).
"""

def bigquery_query_to_df(project_id, sql):
    from google.cloud import bigquery
    client = bigquery.Client(project=project_id)
    return client.query(sql).result().to_dataframe()

def gcs_download_to_df(bucket_name, blob_name):
    from google.cloud import storage
    client = storage.Client()
    blob = client.bucket(bucket_name).blob(blob_name)
    return pd.read_parquet(io.BytesIO(blob.download_as_bytes()))

def gcp_get_secret(project_id, secret_id, version="latest"):
    from google.cloud import secretmanager
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version}"
    return client.access_secret_version(request={"name": name}).payload.data.decode("UTF-8")


# ==============================================================================
# 11. MICROSOFT GRAPH API / SHAREPOINT — msal + requests
# ==============================================================================
"""
pip install msal requests
Used for: pulling SharePoint lists/files, Azure AD users, Teams, Outlook data —
essential in any enterprise running Microsoft 365.
"""

def graph_get_token():
    import msal
    app = msal.ConfidentialClientApplication(
        os.getenv("AZURE_CLIENT_ID"),
        authority=f"https://login.microsoftonline.com/{os.getenv('AZURE_TENANT_ID')}",
        client_credential=os.getenv("AZURE_CLIENT_SECRET"),
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" not in result:
        raise SourceUnavailableError(f"Graph auth failed: {result.get('error_description')}")
    return result["access_token"]

def graph_fetch_all_pages(url, headers):
    results = []
    while url:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        payload = resp.json()
        results.extend(payload.get("value", []))
        url = payload.get("@odata.nextLink")
    return results

def pull_sharepoint_list_to_df(site_hostname, site_path, list_name):
    token = graph_get_token()
    headers = {"Authorization": f"Bearer {token}"}
    base = "https://graph.microsoft.com/v1.0"

    site_id = requests.get(f"{base}/sites/{site_hostname}:{site_path}", headers=headers).json()["id"]
    lists = graph_fetch_all_pages(f"{base}/sites/{site_id}/lists", headers)
    list_id = next(l["id"] for l in lists if l["displayName"] == list_name)

    items = graph_fetch_all_pages(f"{base}/sites/{site_id}/lists/{list_id}/items?expand=fields", headers)
    return pd.DataFrame([item["fields"] for item in items])

def pull_aad_users_to_df():
    token = graph_get_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://graph.microsoft.com/v1.0/users?$select=id,displayName,mail,department"
    return pd.DataFrame(graph_fetch_all_pages(url, headers))


# ==============================================================================
# 12. BIG DATA PROCESSING — pyspark (pip install pyspark)
# ==============================================================================
"""
Used for: distributed processing when data doesn't fit on one machine.
"""

def get_spark_session(app_name="etl-job"):
    from pyspark.sql import SparkSession
    return SparkSession.builder.appName(app_name).getOrCreate()

def spark_dedup_keep_latest(spark_df, key_col, order_col):
    from pyspark.sql import functions as F
    from pyspark.sql.window import Window
    window_spec = Window.partitionBy(key_col).orderBy(F.col(order_col).desc())
    return (
        spark_df.withColumn("rn", F.row_number().over(window_spec))
        .filter(F.col("rn") == 1).drop("rn")
    )


# ==============================================================================
# 13. DATA QUALITY — great_expectations, pandera
# ==============================================================================
"""
pip install great_expectations pandera
Used for: declarative, testable data validation before data reaches downstream consumers.
"""

def pandera_validate_orders(df):
    import pandera as pa
    from pandera import Column, Check, DataFrameSchema
    schema = DataFrameSchema({
        "order_id": Column(int, unique=True, nullable=False),
        "amount": Column(float, Check.greater_than_or_equal_to(0)),
        "status": Column(str, Check.isin(["pending", "delivered", "cancelled", "returned"])),
    })
    return schema.validate(df, lazy=True)  # lazy=True collects ALL validation errors at once


# ==============================================================================
# 14. ORCHESTRATION — apache-airflow (client-side patterns)
# ==============================================================================
"""
pip install apache-airflow
Used for: scheduling and monitoring pipelines — see 04-etl-elt/airflow/ in this repo
for a full DAG example. Key idea: your extraction/transform/load functions above
get wrapped in PythonOperator tasks and chained with >>.
"""
# from airflow import DAG
# from airflow.operators.python import PythonOperator
# t1 = PythonOperator(task_id="extract", python_callable=extract_orders_from_api)
# t2 = PythonOperator(task_id="load", python_callable=transform_and_load)
# t1 >> t2


# ==============================================================================
# 15. VISUALIZATION — matplotlib, seaborn, plotly
# ==============================================================================
"""
pip install matplotlib seaborn plotly
Used for: pipeline QA charts, ad-hoc analysis, NOT a replacement for Power BI/Tableau.
"""

def plot_quick_trend(df, x_col, y_col, output_path="trend.png"):
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 5))
    plt.plot(df[x_col], df[y_col], marker="o")
    plt.savefig(output_path)


# ==============================================================================
# 16. TESTING — pytest, unittest.mock
# ==============================================================================
"""
pip install pytest
Used for: unit testing pipeline logic without hitting real APIs/databases.
"""
# Example test (would live in tests/test_pipeline.py):
#
# from unittest.mock import patch, MagicMock
# @patch("my_module.requests.get")
# def test_fetch_orders(mock_get):
#     mock_get.return_value = MagicMock(status_code=200, json=lambda: {"data": [{"id": 1}]})
#     result = fetch_orders()
#     assert len(result) == 1


# ==============================================================================
# 17. LOGGING & CONFIG — logging, pyyaml, argparse (all stdlib except pyyaml)
# ==============================================================================
"""
Used for: production observability and environment-specific configuration.
"""

def setup_production_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )

def parse_pipeline_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", default="prod", choices=["dev", "staging", "prod"])
    parser.add_argument("--start-date", required=True)
    return parser.parse_args()


# ==============================================================================
# QUICK DECISION GUIDE — "I need to do X, which library?"
# ==============================================================================
"""
Pull data from a REST API                          -> requests (+ tenacity for retries)
Pull data from SharePoint / Teams / Outlook / AAD    -> msal + requests (Microsoft Graph API)
Connect to Postgres/MySQL/SQL Server/Oracle          -> psycopg2 / pymysql / pyodbc / cx_Oracle
Connect to MongoDB                                    -> pymongo
Connect to Snowflake                                  -> snowflake-connector-python
Universal DB engine + pandas integration              -> sqlalchemy
Read/write S3                                         -> boto3
Read/write Azure Blob/ADLS                            -> azure-storage-blob + azure-identity
Read/write GCS                                        -> google-cloud-storage
Query BigQuery                                        -> google-cloud-bigquery
Retrieve secrets (AWS/Azure/GCP)                      -> boto3 Secrets Manager / azure-keyvault-secrets / google-cloud-secret-manager
Process data too big for one machine                  -> pyspark
Clean/transform data that fits in memory               -> pandas + numpy
Validate data quality                                 -> pandera (lightweight) or great_expectations (full framework)
Read CSV/JSON/Excel/Parquet/XML/YAML                  -> csv/json (stdlib), openpyxl, pyarrow, xmltodict, pyyaml
Retry flaky network calls                             -> tenacity
Manage secrets locally in dev                          -> python-dotenv
Test pipeline code                                    -> pytest + unittest.mock
Chart data for pipeline QA                            -> matplotlib / seaborn / plotly
"""

if __name__ == "__main__":
    logger.info("This file is a reference module — import functions from it, or read it top to bottom.")
