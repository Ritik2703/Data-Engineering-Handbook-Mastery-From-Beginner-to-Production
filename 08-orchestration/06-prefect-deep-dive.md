# 6. Prefect — Dynamic, Pythonic Flows

## The Core Problem Prefect Identified in Airflow's Model
Airflow requires defining your ENTIRE DAG structure UPFRONT, statically, before it runs — every possible task and its dependencies must be known at DAG-parse time. Prefect's core pitch: let workflow structure be determined DYNAMICALLY, at runtime, using genuinely normal Python control flow (if statements, loops, function calls) — removing a real friction point Airflow users often hit when a pipeline's structure genuinely depends on runtime conditions.

## Flows and Tasks — Prefect's Basic Units
```python
from prefect import flow, task

@task(retries=3, retry_delay_seconds=30)
def extract_data(source: str):
    print(f"Extracting from {source}")
    return {"rows": 100}

@task
def transform_data(data: dict):
    data["rows"] *= 2
    return data

@task
def load_data(data: dict):
    print(f"Loaded {data['rows']} rows")

@flow(name="orders-pipeline")
def orders_pipeline(sources: list[str]):
    # GENUINELY NORMAL PYTHON — a real for-loop, not a special "dynamic task mapping" API
    for source in sources:
        raw = extract_data(source)
        transformed = transform_data(raw)
        load_data(transformed)

if __name__ == "__main__":
    orders_pipeline(sources=["api_a", "api_b", "api_c"])  # the number of sources
                                                              # can genuinely vary
                                                              # at runtime, no special
                                                              # handling needed
```
**Why this matters in practice**: if your pipeline's structure genuinely needs to branch/loop based on data discovered DURING execution (e.g., "process however many files actually showed up in this folder today, whatever that number is"), Prefect's model handles this with completely ordinary Python code — no special "dynamic task mapping" syntax needed, unlike Airflow's more constrained upfront-DAG-definition model.

## Prefect's Developer Experience Focus
```python
# Local development: just run your Python file directly, like any normal script —
# no need to spin up a Scheduler/Webserver/Metadata DB just to test a flow locally
python orders_pipeline.py

# Deployment: wrap the SAME code with scheduling/infrastructure config when
# ready for production, without rewriting the actual pipeline logic
```
This "write it, run it locally exactly like normal Python, THEN deploy it" workflow is a genuinely smoother initial developer experience than Airflow's requirement of a running Airflow instance (Scheduler + Webserver + Metadata DB) even just to test a simple DAG locally — a real, commonly-cited reason some teams prefer Prefect, especially smaller teams or those newer to orchestration concepts.

## Native Error Handling and Observability
```python
from prefect import flow, task
from prefect.states import Failed

@task
def validate_data(data: dict):
    if data["rows"] == 0:
        raise ValueError("No rows extracted — halting pipeline")
    return data

@flow
def pipeline_with_error_handling():
    try:
        data = extract_data("api_a")
        validated = validate_data(data)
        load_data(validated)
    except ValueError as e:
        # Prefect's UI automatically captures and displays this failure state,
        # with the full Python traceback, without extra configuration
        raise
```
Prefect's UI (Prefect Cloud, or self-hosted Prefect Server) automatically captures rich state/logging/error information from genuinely normal Python exception handling — you don't need Airflow-specific patterns (XComs, trigger rules) to get good visibility into what happened and why.

## Prefect Blocks — Reusable Configuration/Connections
```python
from prefect_aws import S3Bucket
from prefect_sqlalchemy import SqlAlchemyConnector

s3_block = S3Bucket.load("my-data-lake-block")   # securely stored, reusable config
db_block = SqlAlchemyConnector.load("warehouse-connection")

@task
def load_to_s3(data):
    s3_block.upload_from_dataframe(data, "orders/output.parquet")
```
Similar in spirit to Dagster's Resources — centrally-managed, reusable connection/configuration objects that can be swapped between environments without changing task code.

## When Prefect Is the Better Choice (real, honest positioning)
```
Strong fit:
- Teams wanting the smoothest possible LOCAL development experience
  (write and test Python, deploy later) without standing up infrastructure first
- Pipelines with genuinely DYNAMIC structure determined at runtime
  (variable numbers of files/sources/branches discovered during execution)
- Smaller teams or newer-to-orchestration teams wanting less operational
  overhead to get started compared to standing up a full Airflow deployment

Less clear fit:
- Teams wanting the LARGEST possible existing ecosystem of pre-built
  integrations (Airflow's provider package ecosystem remains larger/more mature)
- Very large enterprises with hundreds of existing Airflow DAGs already
  representing significant sunk investment and institutional knowledge
```

## Interview Traps
- "What's Prefect's core positioning difference from Airflow?" — dynamic, genuinely Pythonic workflow structure determined at runtime (normal loops/conditionals) vs Airflow's more rigid requirement to define the full DAG structure upfront/statically.
- "Why might a smaller team prefer Prefect over Airflow?" — smoother local development experience (run flows like normal Python scripts without needing infrastructure standing up first) and less operational overhead to get started.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"A mind at peace with uncertainty makes wiser choices than one demanding false certainty."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
