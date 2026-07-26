# 12. Data Quality & Validation in Python

## Why This Belongs in Every Pipeline
Bad data reaching a dashboard erodes trust in the entire data platform faster than almost anything else. Production pipelines validate data **before** it reaches downstream consumers, and fail loudly (not silently) when something's wrong.

## Manual Validation (understand this before reaching for a library)
```python
import logging
logger = logging.getLogger(__name__)

class DataQualityError(Exception):
    pass

def validate_orders_df(df):
    errors = []

    if df.empty:
        errors.append("DataFrame is empty")

    if df["order_id"].duplicated().any():
        errors.append(f"Found {df['order_id'].duplicated().sum()} duplicate order_ids")

    if df["amount"].isnull().any():
        errors.append(f"Found {df['amount'].isnull().sum()} null amounts")

    if (df["amount"] < 0).any():
        errors.append(f"Found {(df['amount'] < 0).sum()} negative amounts")

    invalid_status = ~df["status"].isin(["pending", "delivered", "cancelled", "returned"])
    if invalid_status.any():
        errors.append(f"Found {invalid_status.sum()} rows with unexpected status values")

    if errors:
        raise DataQualityError("; ".join(errors))

    logger.info(f"Data quality checks passed for {len(df)} rows")

try:
    validate_orders_df(orders_df)
except DataQualityError as e:
    logger.critical(f"DQ validation failed, halting pipeline: {e}")
    raise
```

## Great Expectations (industry-standard DQ framework)
```python
# pip install great_expectations
import great_expectations as gx

context = gx.get_context()
validator = context.sources.pandas_default.read_dataframe(orders_df)

validator.expect_column_values_to_not_be_null("order_id")
validator.expect_column_values_to_be_unique("order_id")
validator.expect_column_values_to_be_between("amount", min_value=0, max_value=1_000_000)
validator.expect_column_values_to_be_in_set("status", ["pending", "delivered", "cancelled", "returned"])
validator.expect_table_row_count_to_be_between(min_value=1, max_value=10_000_000)

results = validator.validate()
if not results["success"]:
    failed_expectations = [r for r in results["results"] if not r["success"]]
    logger.critical(f"Data quality validation failed: {len(failed_expectations)} checks failed")
    raise DataQualityError(f"{len(failed_expectations)} Great Expectations checks failed")
```
**Why use this over manual checks**: built-in reporting/documentation ("Data Docs"), reusable "expectation suites" versioned in git, and integrates directly with Airflow/dbt in production data platforms.

## Pandera (schema + data validation for pandas, lighter weight than Great Expectations)
```python
# pip install pandera
import pandera as pa
from pandera import Column, Check, DataFrameSchema

order_schema = DataFrameSchema({
    "order_id": Column(int, Check.greater_than(0), unique=True, nullable=False),
    "customer_id": Column(int, nullable=False),
    "amount": Column(float, Check.greater_than_or_equal_to(0), nullable=False),
    "status": Column(str, Check.isin(["pending", "delivered", "cancelled", "returned"])),
})

try:
    validated_df = order_schema.validate(orders_df, lazy=True)  # lazy=True collects ALL errors, not just the first
except pa.errors.SchemaErrors as e:
    logger.error(f"Schema validation failed:\n{e.failure_cases}")
    raise
```
**Real scenario**: Pandera schemas are often defined once and reused as both **documentation** (what does this DataFrame look like?) and **validation** — especially popular in dbt-adjacent Python transform layers and ML feature pipelines.

## Custom Data Quality Framework (what many companies build internally)
```python
from dataclasses import dataclass
from typing import Callable
import pandas as pd

@dataclass
class DQCheck:
    name: str
    check_fn: Callable[[pd.DataFrame], bool]
    severity: str = "error"  # "error" halts pipeline, "warning" just logs

def run_dq_checks(df, checks: list[DQCheck]):
    failures = []
    for check in checks:
        try:
            passed = check.check_fn(df)
            if not passed:
                failures.append(check)
                log_fn = logger.error if check.severity == "error" else logger.warning
                log_fn(f"DQ check failed: {check.name}")
        except Exception as e:
            logger.error(f"DQ check '{check.name}' raised an exception: {e}")
            failures.append(check)

    error_failures = [f for f in failures if f.severity == "error"]
    if error_failures:
        raise DataQualityError(f"{len(error_failures)} critical DQ checks failed")
    return failures

checks = [
    DQCheck("no_null_order_ids", lambda df: df["order_id"].notnull().all(), severity="error"),
    DQCheck("no_duplicate_order_ids", lambda df: not df["order_id"].duplicated().any(), severity="error"),
    DQCheck("reasonable_row_count", lambda df: len(df) > 100, severity="warning"),
]
run_dq_checks(orders_df, checks)
```

## Freshness/Timeliness Checks (very common production requirement)
```python
from datetime import datetime, timedelta

def check_data_freshness(df, timestamp_col, max_staleness_hours=25):
    latest_timestamp = df[timestamp_col].max()
    staleness = datetime.utcnow() - latest_timestamp
    if staleness > timedelta(hours=max_staleness_hours):
        raise DataQualityError(
            f"Data is stale: latest record is {staleness} old (max allowed: {max_staleness_hours}h)"
        )
```
**Real scenario**: a nightly pipeline expects fresh data every 24h — if the source stopped sending updates 3 days ago (upstream outage), this check catches it immediately instead of silently reprocessing old data forever.

## Schema Drift Detection (catching upstream changes)
```python
def check_schema_drift(df, expected_columns: set):
    actual_columns = set(df.columns)
    missing = expected_columns - actual_columns
    extra = actual_columns - expected_columns

    if missing:
        raise DataQualityError(f"Missing expected columns: {missing}")
    if extra:
        logger.warning(f"New unexpected columns found (not failing, but worth reviewing): {extra}")

expected = {"order_id", "customer_id", "amount", "status", "order_date"}
check_schema_drift(orders_df, expected)
```
**Real scenario**: an upstream API adds/removes/renames a field — this check surfaces it immediately as a warning or failure instead of a silent `KeyError` three transformation steps downstream.

## Alerting on DQ Failures (closing the loop)
```python
import requests

def send_slack_alert(webhook_url, message):
    try:
        requests.post(webhook_url, json={"text": message}, timeout=10)
    except Exception as e:
        logger.error(f"Failed to send Slack alert: {e}")  # don't let alerting itself crash the pipeline

try:
    validate_orders_df(orders_df)
except DataQualityError as e:
    send_slack_alert(os.getenv("SLACK_WEBHOOK_URL"), f"🚨 DQ check failed in orders_pipeline: {e}")
    raise
```

## Try It Yourself
1. Write a manual validation function checking for nulls, duplicates, and out-of-range values on a sample DataFrame.
2. Convert those manual checks into a Pandera schema.
3. Add a freshness check that raises an exception if the most recent record is older than 24 hours.
