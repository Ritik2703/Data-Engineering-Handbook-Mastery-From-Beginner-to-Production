# Project 5: Complete Azure Enterprise Pipeline — ADF + Databricks + Synapse + Power BI

## Business Scenario
An insurance company (Azure-native, heavy Microsoft 365 usage) needs a complete claims-analytics platform — reuses/extends the case study from `07-cloud-platforms/case-studies/bank-migration-full-design.md` into a fully worked, code-level project.

## Architecture
```
[On-prem SQL Server, claims system] --Self-Hosted Integration Runtime-->
        |
   Azure Data Factory Pipeline
        |
   ADLS Gen2 (raw zone)
        |
   Azure Databricks Notebook (PySpark transform, SCD2 on Dim_Customer)
        |
   ADLS Gen2 (curated zone, Delta)
        |
   Synapse Analytics (Serverless SQL Pool, queries curated Delta directly)
        |
   Power BI (Import mode for the main dashboard, RLS by region)

   [Microsoft Purview scans ADLS + Synapse for governance/lineage]
   [Everything orchestrated/triggered by ADF Pipeline triggers]
```

## Stage 1: ADF Pipeline — Extract On-Prem to ADLS
```json
{
  "name": "Extract_Claims_To_ADLS",
  "properties": {
    "activities": [
      {
        "name": "Lookup_Watermark",
        "type": "Lookup",
        "typeProperties": {
          "source": { "type": "AzureSqlSource", "sqlReaderQuery": "SELECT LastWatermark FROM ControlTable WHERE TableName='Claims'" }
        }
      },
      {
        "name": "Copy_Claims",
        "type": "Copy",
        "dependsOn": [{ "activity": "Lookup_Watermark", "dependencyConditions": ["Succeeded"] }],
        "typeProperties": {
          "source": {
            "type": "SqlServerSource",
            "sqlReaderQuery": "SELECT * FROM Claims WHERE ModifiedDate > '@{activity('Lookup_Watermark').output.firstRow.LastWatermark}'"
          },
          "sink": { "type": "ParquetSink", "storeSettings": { "type": "AzureBlobFSWriteSettings" } }
        },
        "inputs": [{ "referenceName": "OnPremClaimsSource", "type": "DatasetReference" }],
        "outputs": [{ "referenceName": "ADLSRawClaims", "type": "DatasetReference" }]
      },
      {
        "name": "Run_Databricks_Transform",
        "type": "DatabricksNotebook",
        "dependsOn": [{ "activity": "Copy_Claims", "dependencyConditions": ["Succeeded"] }],
        "typeProperties": { "notebookPath": "/Repos/etl/transform_claims" }
      }
    ]
  }
}
```
This directly implements the parameterized, watermark-driven pipeline pattern from `04-etl-elt/06-azure-data-factory-deep-dive.md`, using the Self-Hosted Integration Runtime specifically to reach the on-prem source.

## Stage 2: Databricks Notebook — Transform + SCD2
```python
# transform_claims.py
from pyspark.sql import functions as F
from delta.tables import DeltaTable

raw_df = spark.read.parquet("abfss://raw@mystorageaccount.dfs.core.windows.net/claims/")

cleaned_df = (
    raw_df.dropDuplicates(["claim_id"])
    .withColumn("claim_amount", F.col("claim_amount").cast("decimal(10,2)"))
    .filter(F.col("claim_amount") > 0)
)

# SCD2 on Dim_Customer (recap the exact pattern from Project 3)
dim_customer = DeltaTable.forPath(spark, "abfss://curated@mystorageaccount.dfs.core.windows.net/dim_customer/")
dim_customer.alias("target").merge(
    cleaned_df.select("customer_id", "address", "policy_type").distinct().alias("source"),
    "target.customer_id = source.customer_id AND target.is_current = true"
).whenMatchedUpdate(
    condition="target.address <> source.address",
    set={"end_date": "current_date()", "is_current": "false"}
).execute()

cleaned_df.write.format("delta").mode("append") \
    .save("abfss://curated@mystorageaccount.dfs.core.windows.net/fct_claims/")
```

## Stage 3: Synapse Serverless SQL — Querying Curated Delta Directly
```sql
-- No data movement into a separate warehouse needed -- Synapse Serverless
-- SQL queries the curated ADLS Delta files directly (recap 04-etl-elt/06)
SELECT
    region,
    DATE_TRUNC('month', claim_date) AS month,
    SUM(claim_amount) AS total_claims
FROM OPENROWSET(
    BULK 'https://mystorageaccount.dfs.core.windows.net/curated/fct_claims/',
    FORMAT = 'DELTA'
) AS claims
GROUP BY region, DATE_TRUNC('month', claim_date);
```

## Stage 4: Power BI — RLS by Region (recap 09-visualization/04)
```dax
[Region] = LOOKUPVALUE(dim_users[region], dim_users[email], USERPRINCIPALNAME())
```

## Stage 5: ADF Trigger — Tumbling Window
```json
{
  "name": "Nightly_Claims_Trigger",
  "type": "TumblingWindowTrigger",
  "typeProperties": { "frequency": "Day", "interval": 1, "startTime": "2026-01-01T02:00:00Z" }
}
```

## What This Project Demonstrates
```
A full, realistic Azure-native pipeline: Self-Hosted Integration Runtime
for hybrid connectivity, ADF pipeline JSON with Lookup + Copy + Databricks
Notebook activities, Delta-based SCD2 in Databricks, Synapse Serverless
SQL querying Delta directly (no separate warehouse load step needed),
and Power BI RLS -- exactly the kind of single-cloud enterprise pipeline
covered conceptually in 07-cloud-platforms/04 and 04-etl-elt/06, now
fully implemented end to end.
```


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The one who helps a stranger's learning plants a tree whose shade they may never sit under."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
