# Project 3: The Lakehouse Pattern — Databricks + Delta Lake + Airflow

## Business Scenario
A healthcare analytics company needs a Medallion (Bronze/Silver/Gold) lakehouse for patient appointment data, with full SCD Type 2 history on the patient dimension (a genuine regulatory/audit requirement) and reliable ACID guarantees despite living on cheap object storage.

## Architecture
```
[Source: hospital scheduling system, CDC via Debezium -> Kafka]
                    |
                    v
      Bronze (Delta table, raw, append-only, full history retained)
                    |
        [Databricks Notebook: Bronze -> Silver]
        (dedupe, validate schema, cast types)
                    |
      Silver (Delta table, cleaned, one row per current appointment state)
                    |
        [Databricks Notebook: Silver -> Gold, SCD2 MERGE on Dim_Patient]
                    |
      Gold (Delta tables: fct_appointments, dim_patient [SCD2], dim_provider)
                    |
      Databricks SQL / Power BI (Direct Lake mode, recap 09-visualization/04)

  [Airflow orchestrates: wait for Kafka data -> trigger Bronze notebook
   -> trigger Silver notebook -> trigger Gold notebook -> run data
   quality checks -> refresh Power BI dataset]
```

## Stage 1: Bronze Ingestion Notebook
```python
# 01_bronze_ingest.py -- reuses the Delta Lake pattern from 06-big-data/06
from pyspark.sql import functions as F

raw_df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "broker1:9092")
    .option("subscribe", "appointments")
    .load()
)

parsed_df = raw_df.select(
    F.from_json(F.col("value").cast("string"), appointment_schema).alias("data"),
    F.current_timestamp().alias("ingested_at"),
).select("data.*", "ingested_at")

(
    parsed_df.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/mnt/checkpoints/bronze_appointments")
    .trigger(processingTime="5 minutes")
    .table("bronze.appointments")
)
```

## Stage 2: Silver Transformation Notebook
```python
# 02_silver_transform.py
from pyspark.sql import functions as F
from pyspark.sql.window import Window

bronze_df = spark.read.table("bronze.appointments")

window_spec = Window.partitionBy("appointment_id").orderBy(F.col("ingested_at").desc())
deduped_df = (
    bronze_df.withColumn("rn", F.row_number().over(window_spec))
    .filter(F.col("rn") == 1).drop("rn")
    .filter(F.col("patient_id").isNotNull())  # basic data quality gate
    .withColumn("appointment_date", F.to_date("appointment_time"))
)

deduped_df.write.format("delta").mode("overwrite").saveAsTable("silver.appointments")
```

## Stage 3: Gold Layer — SCD Type 2 on Dim_Patient via Delta MERGE
```python
# 03_gold_scd2_patient.py -- reuses the SCD2 MERGE pattern from
# 06-big-data/06-lakehouse-table-formats.md
from delta.tables import DeltaTable

patient_updates_df = spark.read.table("silver.patients_latest")

dim_patient = DeltaTable.forName(spark, "gold.dim_patient")

(
    dim_patient.alias("target")
    .merge(
        source=patient_updates_df.alias("source"),
        condition="target.patient_id = source.patient_id AND target.is_current = true"
    )
    .whenMatchedUpdate(
        condition="target.address <> source.address OR target.insurance_provider <> source.insurance_provider",
        set={"end_date": "current_date()", "is_current": "false"}
    )
    .execute()
)

# Insert new/changed rows as new current versions
new_versions_df = (
    patient_updates_df.alias("s")
    .join(
        spark.read.table("gold.dim_patient").filter("is_current = true").alias("d"),
        on="patient_id", how="left"
    )
    .filter("d.patient_id IS NULL OR d.address != s.address OR d.insurance_provider != s.insurance_provider")
    .select("s.*")
    .withColumn("start_date", F.current_date())
    .withColumn("end_date", F.lit(None).cast("date"))
    .withColumn("is_current", F.lit(True))
)
new_versions_df.write.format("delta").mode("append").saveAsTable("gold.dim_patient")
```

## Stage 4: Gold Fact Table
```python
# 04_gold_fact_appointments.py
fact_df = (
    spark.read.table("silver.appointments")
    .join(
        spark.read.table("gold.dim_patient").filter("is_current = true"),
        on="patient_id"
    )
    .select("appointment_id", "patient_key", "provider_id", "appointment_date", "status")
)
fact_df.write.format("delta").mode("overwrite").partitionBy("appointment_date").saveAsTable("gold.fct_appointments")
```

## Stage 5: Airflow Orchestration
```python
# dags/lakehouse_pipeline.py -- reuses the Databricks Notebook trigger
# pattern (recap 08-orchestration and 04-etl-elt/06's Databricks Notebook Activity concept)
from airflow.decorators import dag
from airflow.providers.databricks.operators.databricks import DatabricksNotebookOperator
from datetime import datetime

@dag(schedule="0 4 * * *", start_date=datetime(2026, 1, 1), catchup=False)
def lakehouse_pipeline():
    bronze = DatabricksNotebookOperator(task_id="bronze", notebook_path="/Repos/etl/01_bronze_ingest")
    silver = DatabricksNotebookOperator(task_id="silver", notebook_path="/Repos/etl/02_silver_transform")
    gold_dim = DatabricksNotebookOperator(task_id="gold_dim", notebook_path="/Repos/etl/03_gold_scd2_patient")
    gold_fact = DatabricksNotebookOperator(task_id="gold_fact", notebook_path="/Repos/etl/04_gold_fact_appointments")

    bronze >> silver >> gold_dim >> gold_fact

lakehouse_pipeline()
```

## Stage 6: Time Travel for Audit/Compliance
```sql
-- A genuinely important healthcare-compliance capability enabled directly
-- by Delta Lake (recap 06-big-data/06)
SELECT * FROM gold.dim_patient VERSION AS OF 42;
SELECT * FROM gold.dim_patient TIMESTAMP AS OF '2026-06-01';

DESCRIBE HISTORY gold.dim_patient;  -- full audit trail of every change, when, by what job
```

## What This Project Demonstrates
```
Structured Streaming Bronze ingestion, deduplication + data quality
gating at Silver, a full Delta MERGE-based SCD Type 2 implementation
at Gold, Medallion architecture layering end to end, Airflow-orchestrated
Databricks Notebook chaining, and Delta Lake's time-travel capability
used for a genuine compliance/audit requirement.
```


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Generosity in sharing knowledge is a debt repaid to every teacher who came before."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
