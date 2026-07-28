# 3. Airflow DAG Authoring — Operators, Sensors, XComs, Task Groups

## A Complete Modern DAG (TaskFlow API style)
```python
from airflow.decorators import dag, task
from datetime import datetime, timedelta

default_args = {
    "owner": "data-engineering",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

@dag(
    dag_id="orders_pipeline_daily",
    schedule="0 2 * * *",           # cron expression — 2 AM daily
    start_date=datetime(2026, 1, 1),
    catchup=False,                    # don't automatically backfill every missed
                                       # run since start_date — see file 4
    default_args=default_args,
    tags=["orders", "daily"],
)
def orders_pipeline():

    @task
    def extract_orders():
        # ... extraction logic ...
        return {"row_count": 5000}

    @task
    def extract_customers():
        return {"row_count": 1200}

    @task
    def transform(orders_result: dict, customers_result: dict):
        # receives the RETURN VALUES of upstream tasks automatically (XComs, see below)
        total = orders_result["row_count"] + customers_result["row_count"]
        return {"combined_rows": total}

    @task
    def load(transform_result: dict):
        print(f"Loading {transform_result['combined_rows']} rows")

    # Dependencies are inferred automatically from how you pass data between tasks
    orders = extract_orders()
    customers = extract_customers()
    transformed = transform(orders, customers)
    load(transformed)

orders_pipeline()
```

## Operators — Pre-Built Task Types (the older, still-common style)
```python
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator

extract_task = PythonOperator(task_id="extract", python_callable=extract_orders_function)
transform_task = BashOperator(task_id="transform", bash_command="python transform_script.py")
glue_task = GlueJobOperator(task_id="run_glue_etl", job_name="orders-etl-job")
sql_task = SnowflakeOperator(task_id="load_warehouse", sql="CALL load_orders_procedure();")

# Setting dependencies explicitly with >> (the traditional syntax, still very common)
extract_task >> transform_task >> [glue_task, sql_task]  # transform must finish before EITHER runs
```
**Provider packages**: Airflow's real power comes from its huge ecosystem of provider packages (`apache-airflow-providers-amazon`, `-google`, `-snowflake`, `-databricks`, etc.) — pre-built Operators/Hooks for virtually every cloud service and data tool, meaning you rarely need to write raw API-calling code yourself for common integrations.

## Sensors — Waiting for a Condition Before Proceeding
```python
from airflow.sensors.filesystem import FileSensor
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor

wait_for_file = FileSensor(
    task_id="wait_for_source_file",
    filepath="/data/incoming/orders.csv",
    poke_interval=60,     # check every 60 seconds
    timeout=3600,         # give up after 1 hour, mark as failed
    mode="reschedule",    # IMPORTANT — see below
)

wait_for_s3_file = S3KeySensor(
    task_id="wait_for_s3_upload",
    bucket_name="my-bucket",
    bucket_key="raw/orders/{{ ds }}/data.parquet",  # Jinja templating — see below
)
```
**`mode="poke"` vs `mode="reschedule"`**: `poke` mode holds a worker slot occupied for the ENTIRE waiting period (wasteful if waiting hours); `reschedule` mode releases the worker slot between checks, freeing it up for other tasks — always prefer `reschedule` for anything that might wait longer than a few minutes, a real, commonly-missed production optimization.

## Jinja Templating — Airflow's Dynamic Value Injection
```python
# {{ ds }} = the DAG run's logical date, formatted as YYYY-MM-DD
# {{ ds_nodash }} = same, without dashes (YYYYMMDD)
# {{ prev_ds }}, {{ next_ds }} = previous/next run's date

extract_task = BashOperator(
    task_id="extract",
    bash_command="python extract.py --date {{ ds }} --output s3://bucket/raw/{{ ds_nodash }}/",
)
```
This is how Airflow tasks know WHICH date/interval of data to process — critical for backfills (file 4) to work correctly, since the same task code runs correctly for ANY historical date automatically via this templating.

## XComs (Cross-Communications) — Passing Small Data Between Tasks
```python
# Older explicit style (TaskFlow API, shown earlier, does this automatically under the hood)
def extract(**context):
    result = {"row_count": 5000}
    context["ti"].xcom_push(key="extract_result", value=result)

def transform(**context):
    extract_result = context["ti"].xcom_pull(task_ids="extract", key="extract_result")
    print(extract_result["row_count"])
```
**Critical limitation to know**: XComs are stored in the Metadata Database and meant for SMALL values (counts, file paths, status flags) — NEVER pass large datasets (a whole DataFrame, millions of rows) through XComs; that data should be written to S3/a database/a file by one task, with only the LOCATION/reference passed via XCom to the next task.

## Task Groups — Organizing Complex DAGs Visually
```python
from airflow.decorators import task_group

@task_group(group_id="extraction_tasks")
def extract_all_sources():
    orders = extract_orders()
    customers = extract_customers()
    products = extract_products()
    return orders, customers, products
```
Purely a VISUAL/organizational tool in the Airflow UI — groups related tasks into a collapsible node in the graph view, making large DAGs (50+ tasks) much easier to read and navigate, with no functional/execution difference from ungrouped tasks.

## Branching — Conditional Logic in a DAG
```python
from airflow.operators.python import BranchPythonOperator

def choose_branch(**context):
    row_count = context["ti"].xcom_pull(task_ids="extract")["row_count"]
    return "load_data" if row_count > 0 else "send_empty_data_alert"

branch_task = BranchPythonOperator(task_id="check_data", python_callable=choose_branch)
branch_task >> [load_data_task, send_empty_data_alert_task]
```

## Trigger Rules — Controlling WHEN a Task Runs Based on Upstream Outcomes
```python
from airflow.utils.trigger_rule import TriggerRule

# Default: all_success — only runs if ALL upstream tasks succeeded
# Useful alternatives:
cleanup_task = PythonOperator(
    task_id="cleanup",
    trigger_rule=TriggerRule.ALL_DONE,   # runs regardless of upstream success/failure —
                                            # useful for cleanup steps that must always run
    python_callable=cleanup_function,
)
alert_task = PythonOperator(
    task_id="send_failure_alert",
    trigger_rule=TriggerRule.ONE_FAILED,  # runs if ANY upstream task failed
    python_callable=send_alert,
)
```

## Interview Traps
- "What's the difference between `poke` and `reschedule` mode for a Sensor?" — poke holds a worker slot for the entire wait; reschedule releases it between checks — a real, important production efficiency distinction.
- "Why shouldn't you pass a large DataFrame through XCom?" — XComs live in the Metadata Database, meant for small values; large data should be written to external storage with only a reference/path passed via XCom.
- "How do you make part of a DAG run only when upstream tasks failed (e.g., an alert)?" — trigger rules (`ONE_FAILED`, `ALL_DONE`, etc.) instead of the default `all_success`.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Real understanding is measured by how simply you can explain it to a beginner."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
