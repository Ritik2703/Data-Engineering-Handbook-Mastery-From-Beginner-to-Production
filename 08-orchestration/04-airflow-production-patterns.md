# 4. Airflow Production Patterns — Real-World Gotchas & Best Practices

## Idempotency — The #1 Production Design Requirement (recap + Airflow-specific angle)
```python
# BAD — re-running this task (after a failure, or during a backfill) DUPLICATES data
def load_bad(**context):
    df.to_sql("orders", engine, if_exists="append")  # appends AGAIN if re-run!

# GOOD — safe to re-run any number of times with the same result
def load_good(**context):
    execution_date = context["ds"]
    engine.execute(f"DELETE FROM orders WHERE load_date = '{execution_date}'")  # clear first
    df.to_sql("orders", engine, if_exists="append")  # or better: use a proper MERGE/UPSERT
```
**Why this matters MORE in Airflow specifically**: Airflow WILL retry failed tasks automatically (per your `retries` config), and backfills explicitly re-run historical dates — a non-idempotent pipeline will silently corrupt data (duplicate rows) the very first time either of these completely normal Airflow behaviors occurs.

## Backfilling — Reprocessing Historical Data Correctly
```bash
# Airflow CLI backfill command — reruns the DAG for a historical date range
airflow dags backfill orders_pipeline_daily \
  --start-date 2026-06-01 --end-date 2026-06-30
```
```python
# catchup=True (or omitted, since it defaults to True) means Airflow will
# AUTOMATICALLY create and run a DAG run for EVERY missed interval between
# start_date and now, the first time a DAG is turned on — this can be a
# surprising, unwanted flood of runs if not handled deliberately
@dag(
    start_date=datetime(2020, 1, 1),  # if catchup=True (default), and today is 2026,
    catchup=False,                      # this would trigger THOUSANDS of backfill runs!
    schedule="@daily",
)
```
**Real production guidance**: `catchup=False` is usually the safer default for NEW DAGs unless you specifically intend a full historical backfill immediately — a very common beginner mistake is forgetting this and having Airflow attempt years of backfill runs the moment a DAG is enabled.

## SLAs — Setting and Alerting on Expected Completion Times
```python
from datetime import timedelta

@dag(
    dag_id="orders_pipeline",
    schedule="0 2 * * *",
    sla_miss_callback=notify_sla_miss,   # custom function called when an SLA is breached
)
def orders_pipeline():
    @task(sla=timedelta(hours=2))   # this task MUST finish within 2 hours of its scheduled start
    def transform_data():
        ...
```
**Real production use**: if the finance team needs the warehouse refreshed by 6 AM every day, an SLA set for 5:30 AM lets the team get PAGED automatically if the pipeline is running late — BEFORE a business user discovers stale data themselves and escalates, which is a dramatically better experience for everyone involved.

## Dynamic Task Generation — When the Number of Tasks Isn't Fixed
```python
# The metadata-driven pattern (recap from `04-etl-elt/02-etl-architecture-deep-dive.md`),
# implemented in Airflow — process a VARIABLE list of tables without hand-writing
# a task for each one
from airflow.decorators import dag, task

@dag(schedule="@daily", start_date=datetime(2026,1,1), catchup=False)
def dynamic_table_loader():
    tables = ["orders", "customers", "products", "inventory"]  # could come from a config/DB

    @task
    def load_table(table_name: str):
        print(f"Loading {table_name}")

    load_table.expand(table_name=tables)  # dynamic task mapping — creates ONE task
                                            # instance PER item in the list automatically,
                                            # each visible/monitorable separately in the UI
```
**Dynamic Task Mapping** (`.expand()`) is Airflow's modern, native way to handle "N tasks where N varies" — replacing older, clunkier patterns of dynamically generating DAG code by looping over a config at parse time.

## Real Production Gotcha: Timezone Handling
```python
# A VERY common real bug: a DAG scheduled with "0 2 * * *" runs at 2 AM in
# whatever timezone the Airflow instance's scheduler is configured for —
# NOT necessarily the timezone the business stakeholders are thinking in.

# Always be EXPLICIT about timezone when it matters for business-correctness
import pendulum
local_tz = pendulum.timezone("Asia/Kolkata")
start_date = pendulum.datetime(2026, 1, 1, tz=local_tz)
```

## Real Production Gotcha: Resource Contention / Pool Management
```python
# Without limits, 50 simultaneously-triggered tasks might all try to hit the
# SAME source database at once, overwhelming it — Airflow Pools solve this
extract_task = PythonOperator(
    task_id="extract_from_shared_db",
    pool="shared_database_pool",   # limits how many tasks using this pool run concurrently,
                                     # regardless of overall Airflow worker capacity
    python_callable=extract_function,
)
```
**Real scenario**: 30 different DAGs all extracting from the SAME legacy on-prem database — without a shared Pool limiting concurrent connections, a scheduling coincidence (many DAGs happening to run at once) could accidentally overwhelm that database exactly as if it were a DDoS attack from your OWN pipelines.

## Testing Airflow DAGs (recap + Airflow-specific tooling)
```python
# Basic DAG integrity test — catches syntax errors, cyclic dependencies, import errors
def test_dag_loads_without_errors():
    from airflow.models import DagBag
    dagbag = DagBag(dag_folder="dags/", include_examples=False)
    assert len(dagbag.import_errors) == 0, f"DAG import errors: {dagbag.import_errors}"

# Testing individual task logic (mock external calls, per `03-python/13-production-best-practices.md`)
def test_extract_function_handles_empty_response():
    with patch("dags.orders_pipeline.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"data": []}
        result = extract_orders_function()
        assert result["row_count"] == 0
```

## Monitoring Checklist for a Production Airflow Deployment
```
1. Scheduler heartbeat/health — is the Scheduler itself alive and processing?
2. DAG parse time — slow-parsing DAG files (see file 2's warning) degrade
   the ENTIRE Airflow instance's responsiveness, not just that one DAG
3. Task queue depth — are tasks piling up waiting for available workers
   (undersized worker capacity for your actual DAG volume)?
4. Failed task rate over time — a rising trend often signals a systemic
   issue (a source system degrading) rather than isolated random failures
5. SLA miss frequency — repeated SLA misses on the same DAG signal it's
   either genuinely under-resourced or the SLA threshold needs realistic adjustment
```

## Interview Traps
- "What's `catchup` and why is it dangerous if misunderstood?" — controls whether Airflow automatically runs a DAG for every missed historical interval since `start_date`; forgetting `catchup=False` on a new DAG with an old `start_date` can trigger an unwanted flood of backfill runs.
- "How do you handle a variable, config-driven number of tasks in a DAG?" — Dynamic Task Mapping (`.expand()`), the modern native Airflow pattern.
- "How would you prevent 30 different DAGs from overwhelming one shared source database?" — Airflow Pools, limiting concurrent task execution against that specific shared resource regardless of overall worker capacity.
- Be ready to explain WHY idempotency matters MORE in an orchestrated context specifically — because retries and backfills are normal, expected, frequent Airflow behaviors, not rare edge cases.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Every act of patience today compounds into wisdom tomorrow."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
