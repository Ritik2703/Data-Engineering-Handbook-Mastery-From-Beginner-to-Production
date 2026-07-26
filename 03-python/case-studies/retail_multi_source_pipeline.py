"""
Case Study: Multi-Source Enterprise Pipeline (Real Company Scenario)

Business context: A retail company needs a nightly pipeline that:
  1. Pulls order data from an internal REST API
  2. Pulls a SharePoint-hosted "Store Master" list (business team maintains this manually)
  3. Pulls product catalog from a Postgres OLTP database
  4. Validates data quality on all three sources
  5. Combines and loads the result into Snowflake
  6. Uploads a backup copy to S3
  7. Alerts on Slack if anything fails

This demonstrates EVERY concept from this module working together in one realistic script.
"""

import os
import logging
import io
from datetime import datetime, timedelta

import pandas as pd
import requests
import boto3
from botocore.exceptions import ClientError
from sqlalchemy import create_engine
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("retail_nightly_pipeline")


class DataQualityError(Exception):
    """Raised when extracted data fails validation — halts the pipeline."""
    pass


class SourceUnavailableError(Exception):
    """Raised when a source system can't be reached after retries."""
    pass


# ---------------------------------------------------------------------------
# EXTRACT: Internal Orders API
# ---------------------------------------------------------------------------
@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=2, min=2, max=30))
def _fetch_orders_page(url, headers, params):
    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def extract_orders_from_api(api_base_url, api_key, since_date):
    logger.info("Extracting orders from internal API")
    headers = {"Authorization": f"Bearer {api_key}"}
    all_orders, cursor = [], None

    try:
        while True:
            params = {"updated_since": since_date, "limit": 500}
            if cursor:
                params["cursor"] = cursor
            page = _fetch_orders_page(api_base_url, headers, params)
            all_orders.extend(page.get("data", []))
            cursor = page.get("next_cursor")
            if not cursor:
                break
    except requests.exceptions.HTTPError as e:
        logger.error(f"Orders API returned an error: {e}")
        raise SourceUnavailableError("orders_api") from e
    except Exception as e:
        logger.error(f"Orders extraction failed after retries: {e}")
        raise SourceUnavailableError("orders_api") from e

    logger.info(f"Extracted {len(all_orders)} orders")
    return pd.DataFrame(all_orders)


# ---------------------------------------------------------------------------
# EXTRACT: SharePoint Store Master List (via Microsoft Graph API)
# ---------------------------------------------------------------------------
def get_graph_token():
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


def extract_store_master_from_sharepoint():
    logger.info("Extracting Store Master list from SharePoint")
    try:
        token = get_graph_token()
        headers = {"Authorization": f"Bearer {token}"}
        base = "https://graph.microsoft.com/v1.0"

        site_resp = requests.get(f"{base}/sites/contoso.sharepoint.com:/sites/RetailOps", headers=headers, timeout=30)
        site_resp.raise_for_status()
        site_id = site_resp.json()["id"]

        lists_resp = requests.get(f"{base}/sites/{site_id}/lists", headers=headers, timeout=30)
        lists_resp.raise_for_status()
        list_id = next(l["id"] for l in lists_resp.json()["value"] if l["displayName"] == "Store Master")

        items, url = [], f"{base}/sites/{site_id}/lists/{list_id}/items?expand=fields"
        while url:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            payload = resp.json()
            items.extend(payload["value"])
            url = payload.get("@odata.nextLink")

        rows = [item["fields"] for item in items]
        logger.info(f"Extracted {len(rows)} store records from SharePoint")
        return pd.DataFrame(rows)

    except requests.exceptions.HTTPError as e:
        logger.error(f"SharePoint extraction failed: {e}")
        raise SourceUnavailableError("sharepoint_store_master") from e


# ---------------------------------------------------------------------------
# EXTRACT: Product Catalog from Postgres
# ---------------------------------------------------------------------------
def extract_products_from_postgres(conn_string):
    logger.info("Extracting product catalog from Postgres")
    try:
        engine = create_engine(conn_string, pool_pre_ping=True)
        df = pd.read_sql("SELECT product_id, product_name, category, price FROM products", engine)
        logger.info(f"Extracted {len(df)} products")
        return df
    except Exception as e:
        logger.error(f"Postgres extraction failed: {e}")
        raise SourceUnavailableError("postgres_products") from e


# ---------------------------------------------------------------------------
# VALIDATE: Data Quality Checks
# ---------------------------------------------------------------------------
def validate_data(orders_df, stores_df, products_df):
    errors = []

    if orders_df.empty:
        errors.append("Orders extract returned zero rows")
    elif orders_df["order_id"].duplicated().any():
        errors.append(f"{orders_df['order_id'].duplicated().sum()} duplicate order_ids found")

    if stores_df.empty:
        errors.append("Store Master extract returned zero rows")

    if products_df.empty:
        errors.append("Product catalog extract returned zero rows")
    elif (products_df["price"] < 0).any():
        errors.append("Negative prices found in product catalog")

    if errors:
        raise DataQualityError("; ".join(errors))

    logger.info("All data quality checks passed")


# ---------------------------------------------------------------------------
# TRANSFORM & LOAD: Combine and load to Snowflake + backup to S3
# ---------------------------------------------------------------------------
def transform_and_load(orders_df, stores_df, products_df, snowflake_conn_string, s3_bucket):
    logger.info("Transforming and combining datasets")
    orders_df.columns = orders_df.columns.str.lower().str.strip()
    stores_df.columns = stores_df.columns.str.lower().str.strip()
    products_df.columns = products_df.columns.str.lower().str.strip()

    enriched = (
        orders_df
        .merge(products_df, on="product_id", how="left")
        .merge(stores_df, on="store_id", how="left")
    )
    enriched["loaded_at"] = datetime.utcnow()

    logger.info(f"Loading {len(enriched)} enriched rows to Snowflake")
    engine = create_engine(snowflake_conn_string)
    enriched.to_sql("stg_daily_orders_enriched", engine, if_exists="append", index=False, chunksize=1000)

    logger.info("Backing up enriched data to S3")
    s3 = boto3.client("s3")
    buffer = io.BytesIO()
    enriched.to_parquet(buffer, index=False)
    backup_key = f"backups/orders_enriched/{datetime.utcnow().strftime('%Y-%m-%d')}.parquet"
    try:
        s3.put_object(Bucket=s3_bucket, Key=backup_key, Body=buffer.getvalue())
        logger.info(f"Backup written to s3://{s3_bucket}/{backup_key}")
    except ClientError as e:
        logger.warning(f"S3 backup failed (non-critical, pipeline continues): {e}")


# ---------------------------------------------------------------------------
# ALERTING
# ---------------------------------------------------------------------------
def send_slack_alert(message):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return
    try:
        requests.post(webhook_url, json={"text": message}, timeout=10)
    except Exception as e:
        logger.warning(f"Failed to send Slack alert (non-critical): {e}")


# ---------------------------------------------------------------------------
# MAIN PIPELINE ORCHESTRATION
# ---------------------------------------------------------------------------
def run_pipeline():
    since_date = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        orders_df = extract_orders_from_api(
            api_base_url=os.getenv("ORDERS_API_URL"),
            api_key=os.getenv("ORDERS_API_KEY"),
            since_date=since_date,
        )
        stores_df = extract_store_master_from_sharepoint()
        products_df = extract_products_from_postgres(os.getenv("POSTGRES_CONN_STRING"))

        validate_data(orders_df, stores_df, products_df)

        transform_and_load(
            orders_df, stores_df, products_df,
            snowflake_conn_string=os.getenv("SNOWFLAKE_CONN_STRING"),
            s3_bucket=os.getenv("BACKUP_S3_BUCKET"),
        )

        logger.info("Pipeline completed successfully")

    except DataQualityError as e:
        logger.critical(f"Data quality failure — halting pipeline: {e}")
        send_slack_alert(f"🚨 DQ failure in retail_nightly_pipeline: {e}")
        raise SystemExit(1)

    except SourceUnavailableError as e:
        logger.critical(f"Source system unavailable — halting pipeline: {e}")
        send_slack_alert(f"🚨 Source unavailable in retail_nightly_pipeline: {e}")
        raise SystemExit(1)

    except Exception as e:
        logger.critical(f"Unexpected pipeline failure: {e}")
        send_slack_alert(f"🚨 Unexpected failure in retail_nightly_pipeline: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    run_pipeline()
