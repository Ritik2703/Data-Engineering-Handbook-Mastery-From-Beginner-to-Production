# Case Study: Metadata-Driven Orchestration for 200+ Source Tables

## Business Problem
A mid-size retail company needs to ingest data from 200+ source tables across 12 different systems (POS systems per store region, an e-commerce platform, a CRM, an ERP, several SaaS marketing tools) into their warehouse — hand-writing 200+ individual Airflow DAGs is unmanageable to build AND maintain (any common change, like adding a new retry policy, would require editing 200+ files).

## The Metadata-Driven Solution

### Step 1: A Control Table Defines Every Source (the single source of truth)
```sql
CREATE TABLE pipeline_control (
    source_system VARCHAR(50),
    source_table VARCHAR(100),
    target_table VARCHAR(100),
    load_type VARCHAR(20),        -- 'full' or 'incremental'
    watermark_column VARCHAR(50),
    last_watermark TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    schedule_priority INT          -- controls execution order/pooling if needed
);
-- Populated with 200+ rows, one per source table needing ingestion
```

### Step 2: ONE Generic DAG, Dynamically Generating Tasks From the Control Table
```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(
    dag_id="metadata_driven_ingestion",
    schedule="0 1 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_tasks=20,   # limit overall concurrency across ALL 200+ sources
)
def metadata_driven_ingestion():

    @task
    def get_active_sources() -> list[dict]:
        engine = get_warehouse_engine()
        result = engine.execute(
            "SELECT * FROM pipeline_control WHERE is_active = TRUE"
        )
        return [dict(row) for row in result]

    @task(retries=3, pool="source_system_pool")   # shared pool prevents overwhelming
                                                     # any single source system (file 4)
    def ingest_one_source(source_config: dict):
        source_system = source_config["source_system"]
        source_table = source_config["source_table"]
        watermark = source_config["last_watermark"]

        # Generic extraction logic, parameterized by the config — the SAME
        # function handles ANY of the 200+ tables, driven entirely by config
        extractor = get_extractor_for_system(source_system)  # factory pattern,
                                                                # returns the right
                                                                # extraction class
                                                                # for this source type
        data = extractor.extract_incremental(source_table, since=watermark)

        validate_data_quality(data, source_table)  # generic DQ checks
        load_to_warehouse(data, source_config["target_table"])
        update_watermark(source_config, new_watermark=data["max_timestamp"])

    sources = get_active_sources()
    ingest_one_source.expand(source_config=sources)   # Dynamic Task Mapping —
                                                          # creates one task instance
                                                          # PER active source row,
                                                          # each independently
                                                          # monitorable in the Airflow UI

metadata_driven_ingestion()
```

### Step 3: A Factory Pattern for Source-Specific Extraction Logic
```python
def get_extractor_for_system(source_system: str):
    """Returns the appropriate extractor class based on source system type —
    each implementing a common interface, so the DAG code above never needs
    to know the specific details of any individual source."""
    extractors = {
        "postgres_pos": PostgresExtractor,
        "salesforce_crm": SalesforceAPIExtractor,
        "sap_erp": SAPExtractor,
        "google_ads": GoogleAdsAPIExtractor,
        # ... one entry per distinct SOURCE TYPE, not per individual table
    }
    return extractors[source_system]()
```
This is a direct application of the `BaseExtractor`/subclass OOP pattern from `03-python/01-python-fundamentals-for-de.md` — each source TYPE (not each of the 200+ tables) needs its own extraction logic implementation, but the orchestration DAG itself remains completely generic.

## Why This Design Solves the Real Problem
```
- Adding source table #201 requires ONE new row in pipeline_control —
  zero new Airflow code, zero new DAG files to create/deploy/review
- Changing the global retry policy requires editing ONE task definition,
  automatically applying to all 200+ sources simultaneously
- Each source's execution is independently visible/monitorable in the
  Airflow UI (via Dynamic Task Mapping), despite being generated from
  one generic task definition — you can see EXACTLY which of the 200+
  sources succeeded/failed on any given night, not just an aggregate status
- The shared "source_system_pool" prevents any single source system
  (e.g., a fragile legacy on-prem POS database) from being overwhelmed
  by too many concurrent extraction attempts, even as the total source
  count grows over time
```

## Extending This Pattern for SLA/Alerting (tying file 4 and file 8 together)
```python
@task(trigger_rule="all_done")   # runs regardless of upstream success/failure
def check_ingestion_summary(sources: list[dict]):
    failed_sources = get_failed_task_instances()  # query Airflow's own metadata
    if len(failed_sources) > 5:
        page_oncall_engineer(f"CRITICAL: {len(failed_sources)} source ingestions failed")
    elif len(failed_sources) > 0:
        post_to_slack(f"⚠️ {len(failed_sources)} of 200+ sources failed tonight")
    else:
        log_success_metric()
```

## Try It Yourself
Using this same metadata-driven pattern, design an orchestration solution for:
1. A company needing to run the SAME data quality validation suite against 50 different warehouse tables nightly.
2. A company needing to trigger a different downstream Databricks notebook for each of 30 different business units, with unit-specific parameters stored in a config table.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Every teacher was once a struggling beginner — remember that with compassion."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
