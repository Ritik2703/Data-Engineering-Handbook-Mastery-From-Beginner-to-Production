# 8. Cloud SDK — Azure Deep Dive

## Setup & Authentication
```python
# pip install azure-identity azure-storage-blob azure-keyvault-secrets

from azure.identity import ClientSecretCredential, DefaultAzureCredential

# Option A: Service Principal (explicit, common for scheduled pipelines/automation)
credential = ClientSecretCredential(
    tenant_id=os.getenv("AZURE_TENANT_ID"),
    client_id=os.getenv("AZURE_CLIENT_ID"),
    client_secret=os.getenv("AZURE_CLIENT_SECRET"),
)

# Option B: DefaultAzureCredential — tries multiple auth methods automatically
# (managed identity on Azure compute, environment variables, Azure CLI login, etc.)
# Preferred inside Azure (Functions, VMs, Databricks) — no secrets to manage at all
credential = DefaultAzureCredential()
```

## Blob Storage / ADLS Gen2 — Object Storage Operations
```python
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError

account_url = "https://mystorageaccount.blob.core.windows.net"
blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)

def upload_to_blob(container_name, blob_name, local_path):
    try:
        container_client = blob_service_client.get_container_client(container_name)
        with open(local_path, "rb") as f:
            container_client.upload_blob(name=blob_name, data=f, overwrite=True)
        logger.info(f"Uploaded {local_path} to {container_name}/{blob_name}")
    except ClientAuthenticationError:
        logger.critical("Azure authentication failed — check credentials/permissions")
        raise
    except Exception as e:
        logger.error(f"Blob upload failed: {e}")
        raise

def download_from_blob(container_name, blob_name, local_path):
    try:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        with open(local_path, "wb") as f:
            f.write(blob_client.download_blob().readall())
    except ResourceNotFoundError:
        logger.error(f"Blob not found: {container_name}/{blob_name}")
        raise

def list_blobs(container_name, name_prefix=""):
    container_client = blob_service_client.get_container_client(container_name)
    return [blob.name for blob in container_client.list_blobs(name_starts_with=name_prefix)]

# Reading a Parquet/CSV directly into pandas without a local temp file
import pandas as pd
import io
blob_client = blob_service_client.get_blob_client(container="raw", blob="orders/2026-07-25.parquet")
stream = io.BytesIO(blob_client.download_blob().readall())
df = pd.read_parquet(stream)
```

## Key Vault — Secure Credential Retrieval
```python
from azure.keyvault.secrets import SecretClient

def get_secret(vault_url, secret_name):
    client = SecretClient(vault_url=vault_url, credential=credential)
    try:
        secret = client.get_secret(secret_name)
        return secret.value
    except Exception as e:
        logger.error(f"Failed to retrieve secret {secret_name} from Key Vault: {e}")
        raise

db_password = get_secret("https://my-vault.vault.azure.net", "prod-sql-password")
```

## Azure SQL Database / Synapse Connection
```python
import pyodbc

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=myserver.database.windows.net;DATABASE=mydb;"
    f"UID={os.getenv('AZURE_SQL_USER')};PWD={os.getenv('AZURE_SQL_PASSWORD')};"
    "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
)
```

## Triggering an ADF (Azure Data Factory) Pipeline Programmatically
```python
from azure.mgmt.datafactory import DataFactoryManagementClient

adf_client = DataFactoryManagementClient(credential, subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID"))

def trigger_adf_pipeline(resource_group, factory_name, pipeline_name, parameters=None):
    run_response = adf_client.pipelines.create_run(
        resource_group_name=resource_group,
        factory_name=factory_name,
        pipeline_name=pipeline_name,
        parameters=parameters or {},
    )
    logger.info(f"Triggered ADF pipeline {pipeline_name}, run ID: {run_response.run_id}")
    return run_response.run_id

def check_adf_run_status(resource_group, factory_name, run_id):
    run = adf_client.pipeline_runs.get(resource_group, factory_name, run_id)
    return run.status  # "InProgress", "Succeeded", "Failed"
```
**Real scenario**: a Python script (e.g., part of a broader orchestration layer or a custom trigger service) kicks off an ADF pipeline after validating an upstream file has landed, then polls for completion before proceeding to the next step.

## Event Hubs — Streaming Ingestion (Kafka-compatible)
```python
from azure.eventhub import EventHubProducerClient, EventData

producer = EventHubProducerClient.from_connection_string(
    conn_str=os.getenv("EVENTHUB_CONNECTION_STRING"),
    eventhub_name="orders-events"
)

def send_event(event_dict):
    event_data_batch = producer.create_batch()
    event_data_batch.add(EventData(json.dumps(event_dict)))
    producer.send_batch(event_data_batch)

with producer:
    send_event({"order_id": 1001, "amount": 599, "event_time": "2026-07-25T10:00:00Z"})
```

## Error Handling Pattern Specific to Azure SDK
```python
from azure.core.exceptions import (
    ResourceNotFoundError, ClientAuthenticationError, HttpResponseError
)

try:
    download_from_blob("raw", "orders/missing_file.csv", "local.csv")
except ResourceNotFoundError:
    logger.error("File does not exist in Blob Storage")
except ClientAuthenticationError:
    logger.critical("Azure auth failed — check Service Principal / Managed Identity configuration")
    raise
except HttpResponseError as e:
    logger.error(f"Azure API returned an error: {e.status_code} — {e.message}")
    raise
```

## Try It Yourself
1. Write a function that reads a CSV directly from Azure Blob Storage into a pandas DataFrame without a local file.
2. Retrieve a database password from Key Vault and use it to connect to Azure SQL Database.
3. Write a function that triggers an ADF pipeline and polls its status until completion or failure.
