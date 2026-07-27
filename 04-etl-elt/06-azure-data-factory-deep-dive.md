# 6. Azure Data Factory (ADF) — Deep Dive

## What ADF Is and Why It Replaced SSIS for New Builds
ADF is Microsoft's **cloud-native** orchestration and data movement service — the modern successor to SSIS for organizations moving to Azure. Key shift: ADF is fundamentally **serverless and elastic** (no ETL server to provision/patch/maintain) and natively designed for **ELT** (move data into cloud storage/warehouse first, transform using scalable compute like Databricks/Synapse Spark after), whereas SSIS was built for **ETL** (transform on a dedicated server before loading).

## Core Building Blocks

### Linked Services — connection definitions
Exactly like SSIS's Connection Managers — reusable definitions of HOW to connect to a system (a database, an API, a storage account), storing connection strings/credentials (ideally referencing Azure Key Vault, never hardcoded).

### Datasets — pointers to specific data
A Dataset references a specific table, file, or API endpoint WITHIN a Linked Service — e.g., "the `Orders` table inside the `PROD_SQL` Linked Service" or "the `orders/*.csv` files inside the `DataLakeStorage` Linked Service."

### Pipelines — the orchestration layer (ADF's equivalent of SSIS Control Flow)
A Pipeline is a sequence of **Activities** with dependency logic between them.
```
Pipeline: "Load_Orders_Daily"

[Lookup Activity: get last watermark from control table]
              |
              v
[Copy Activity: extract orders from SQL source WHERE modified > @watermark, 
                land as Parquet in ADLS raw zone]
              |
   (On Success)                                    (On Failure)
              v                                              v
[Databricks Notebook Activity:                    [Web Activity: 
 transform raw -> curated]                          send Teams/Slack alert]
              |
              v
[Stored Procedure Activity: 
 update watermark in control table]
```

### Key Activity Types
| Activity | Purpose |
|---|---|
| **Copy Activity** | Move data from a source to a sink (the workhorse — handles most simple extract/load) |
| **Data Flow Activity** | Visual, no-code transformation (Mapping Data Flows — runs on managed Spark under the hood) |
| **Databricks Notebook Activity** | Trigger a PySpark notebook for heavy custom transformation |
| **Stored Procedure Activity** | Run a SQL stored procedure (e.g., update a watermark, run post-load validation) |
| **Lookup Activity** | Read a small amount of data (e.g., a config/control table) into the pipeline for use elsewhere |
| **ForEach Activity** | Loop over a collection (e.g., a list of tables from a control table) — key to metadata-driven pipelines |
| **Web Activity** | Call any REST API (e.g., trigger a Slack/Teams alert, or call an external system) |
| **If Condition / Switch Activity** | Branching logic based on pipeline variables |
| **Execute Pipeline Activity** | Call another pipeline (like SSIS's Execute Package Task) — enables modular, reusable pipeline design |

## Mapping Data Flows — ADF's No-Code Transformation Engine
Built on top of managed Spark clusters (spun up/down automatically — you never manage the cluster directly), using a visual designer similar in spirit to SSIS Data Flow, but scales to big-data volumes.
```
[Source: raw Orders from ADLS]
        |
        v
[Derived Column: total_amount = quantity * unit_price]
        |
        v
[Lookup: join against Dim_Customer for customer_key]
        |
        v
[Aggregate: SUM(total_amount) GROUP BY customer_key, order_date]
        |
        v
[Sink: write to curated zone as partitioned Parquet]
```
Many modern Azure shops actually **prefer Databricks notebooks (PySpark) over Mapping Data Flows** for complex transformation logic — Mapping Data Flows are great for simpler, visual-friendly transforms, while Databricks gives full code control, better testability, and more flexibility for complex business logic.

## Parameterization & Metadata-Driven Pipelines (ADF's version of the pattern from file 2)
```json
// Pipeline parameters — passed in at trigger time
{
  "sourceTableName": "orders",
  "watermarkColumn": "modified_date",
  "targetPath": "curated/orders/"
}
```
A single generic "Copy_Table_Generic" pipeline combined with a **ForEach Activity** iterating over rows from a control/metadata table (stored in Azure SQL or a config file) lets one pipeline definition handle 100+ source tables — the direct ADF implementation of the metadata-driven pattern from `02-etl-architecture-deep-dive.md`.

## Triggers (ADF's scheduling layer)
- **Schedule Trigger**: run at fixed times/intervals (like a cron schedule).
- **Tumbling Window Trigger**: runs on fixed, non-overlapping time windows, with built-in support for dependency chaining between windows and automatic retry/backfill of missed windows — particularly suited to sequential incremental loads.
- **Event-Based Trigger**: fires when a file lands in Blob/ADLS storage — enables event-driven pipelines instead of purely time-based ones.

## Real Enterprise Example: Retail Company Migrating from SSIS to ADF
```
OLD (SSIS, on-prem SQL Server):
  SQL Server Agent job -> runs LoadOrders.dtsx nightly at 2 AM
  -> extracts from on-prem OLTP, transforms on the SSIS server itself, loads into on-prem DW

NEW (ADF, cloud):
  ADF Tumbling Window Trigger (daily) -> Pipeline: "Load_Orders_Daily"
    -> Copy Activity: on-prem SQL Server (via Self-Hosted Integration Runtime) -> ADLS raw zone
    -> Databricks Notebook Activity: PySpark transform, raw -> curated (replaces SSIS Data Flow logic)
    -> Copy Activity: curated Parquet -> Synapse Analytics warehouse table
    -> Stored Procedure Activity: refresh watermark control table
    -> Web Activity: notify Teams channel on completion/failure
```
Note the **Self-Hosted Integration Runtime** — a lightweight agent installed on-premises that lets cloud-native ADF securely reach on-prem data sources still living behind a corporate firewall — critical for real migrations where not everything moves to the cloud at once.

## Interview Traps
- "Difference between a Linked Service and a Dataset?" — Linked Service = the connection itself (how to connect); Dataset = a specific pointer to data within that connection (what to connect to).
- "How do you handle 100+ tables without building 100+ pipelines?" — parameterized pipeline + ForEach Activity + metadata/control table, exactly as described above.
- "How does ADF reach an on-premises SQL Server?" — Self-Hosted Integration Runtime, a critical concept for any hybrid cloud/on-prem migration conversation.
