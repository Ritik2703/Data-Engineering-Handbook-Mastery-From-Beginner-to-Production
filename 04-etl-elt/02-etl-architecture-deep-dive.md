# 2. ETL/ELT Architecture Deep Dive

## The Staging Area Concept
Almost every ETL/ELT system has a **staging area** — a temporary holding zone where raw extracted data lands before any cleaning happens.
```
Source Systems --> STAGING (raw, untouched copy) --> Transform --> Final Tables (curated/business-ready)
```
**Why not transform directly during extraction?**
1. **Speed** — extraction should be fast and simple; if it fails partway through, you don't want half-transformed data floating around.
2. **Re-runnability** — if a transformation bug is found, you can fix the transform logic and re-run it against the staged raw data, WITHOUT re-extracting from the (possibly slow/rate-limited) source again.
3. **Auditability** — you always have an untouched copy of exactly what the source sent, useful for debugging "why does this number look wrong."

This maps directly to the **Bronze/Silver/Gold** medallion pattern from `01-fundamentals/09-data-pipeline-architecture.md` — Bronze = staging, Silver/Gold = transformed layers.

## Types of Transformations (know these — used to describe any ETL job)
| Type | Description | Example |
|---|---|---|
| **Cleansing** | Fix bad/inconsistent data | Trim whitespace, standardize date formats, fix casing |
| **Filtering** | Remove unwanted rows | Exclude test accounts, exclude cancelled orders from revenue calc |
| **Deduplication** | Remove duplicate records | Same customer submitted twice due to a form bug |
| **Joining/Lookup** | Combine data from multiple sources | Attach product category to every order line |
| **Aggregation** | Summarize granular data | Turn transaction-level rows into daily totals |
| **Derivation** | Calculate new fields | `total = quantity * unit_price` |
| **Pivoting/Unpivoting** | Reshape rows to columns or vice versa | Monthly columns -> one row per month |
| **Type Conversion** | Fix data types | String "1,234.50" -> numeric 1234.50 |
| **Surrogate Key Generation** | Create warehouse-internal IDs | Auto-incrementing keys independent of source system IDs |
| **Slowly Changing Dimension (SCD) Handling** | Track historical changes | See `01-fundamentals/03-data-modeling.md` |

## Full/Incremental Load Strategies
```
FULL LOAD:
  Every run, wipe the destination table and reload EVERYTHING from the source.
  Simple, but slow and wasteful for large tables — used for small reference/lookup tables.

INCREMENTAL LOAD:
  Only pull records that are NEW or CHANGED since the last run.
  Requires either:
    a) A reliable "last modified" timestamp column in the source
    b) Change Data Capture (CDC) reading the source database's transaction log
    c) An incrementing ID/sequence you can track a "high water mark" against
```
```sql
-- Incremental extraction example — pull only what changed since last run
SELECT * FROM orders WHERE updated_at > '2026-07-24 02:00:00';  -- last successful run's watermark
```
**Real production concern**: incremental loads are much cheaper/faster, but need careful handling of **late-arriving data** (a row updated in the source AFTER your incremental window already ran) — many pipelines re-process a small overlapping window (e.g., "last 3 days" instead of "since exact last run") as a safety margin.

## Orchestration — Tying It All Together
Every ETL tool needs something to answer: "in what order do these steps run, and what happens if one fails?"
```
Extract Orders --> Extract Customers --> [both must finish] --> Transform (join them) --> Load --> Validate --> Notify
                                                                                              |
                                                                                     (if fails: alert + stop)
```
This dependency graph is what SSIS's "Control Flow", Informatica's "Workflow Manager", ADF's "Pipeline", and Airflow's "DAG" all represent — just with different visual/code interfaces for the same underlying concept.

## Error Handling & Restartability (production-critical, often skipped by beginners)
A real production ETL job needs to answer:
- What happens if the source API times out on step 2 of 5? (Retry? Skip and alert? Stop everything?)
- If the job fails at step 4, can you restart from step 4, or must you redo 1-4 from scratch?
- Is re-running the whole job safe (idempotent), or will it create duplicate data?

Enterprise tools (SSIS, Informatica, ADF) all have built-in **checkpoint/restart** features precisely because this is such a common real need — a failed nightly load shouldn't force a 3-hour full reprocess if only the last 10 minutes actually failed.

## Metadata-Driven ETL (how large enterprises scale to hundreds of pipelines)
Instead of hand-writing 200 nearly-identical pipelines (one per source table), large enterprises build **one generic, parameterized pipeline** driven by a metadata/config table:
```
control_table:
  source_table | source_system | target_table | load_type   | last_watermark
  orders       | postgres_prod | fct_orders   | incremental | 2026-07-24 02:00
  customers    | postgres_prod | dim_customer | full        | NULL
  products     | api_catalog   | dim_product  | incremental | 2026-07-23 18:00
```
A single pipeline reads this control table and dynamically extracts/loads each row's source/target — this is exactly how ADF's "ForEach" activities and Informatica's "parameter files" are used at real enterprise scale, and it's a very common senior-level system design interview topic ("how would you design a pipeline framework for 200+ tables without writing 200 pipelines?").

## Interview Traps
- "Why have a staging area instead of transforming directly?" — re-runnability, auditability, decoupling extraction failures from transformation bugs.
- "How would you design an incremental load without a reliable timestamp column?" — mention CDC (reading the transaction log) as the robust answer, or a monotonically increasing ID as a simpler fallback.
- Metadata-driven / parameterized pipeline design is a strong signal of senior-level thinking in interviews — bring it up when asked about scaling ETL to many tables.
