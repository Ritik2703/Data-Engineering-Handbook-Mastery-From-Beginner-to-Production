# 2. Core Concepts

## Types of Data

| Type | Description | Examples | Typical Storage |
|---|---|---|---|
| **Structured** | Fixed schema, rows & columns | SQL tables, CSV with fixed columns | RDBMS, Warehouses |
| **Semi-structured** | Flexible schema, self-describing | JSON, XML, Avro | Document DBs, Data Lakes |
| **Unstructured** | No predefined schema | Images, video, PDFs, free text, logs | Object storage (S3/Blob/GCS) |

## Data Lifecycle (the full journey)
```
Generate → Ingest → Store (raw) → Process/Transform → Store (curated) → Serve → Consume → Archive/Delete
   │           │           │              │                  │            │         │            │
 App/IoT     ETL/ELT    Data Lake      Spark/dbt         Warehouse    BI Tool   Analyst/ML   Cold storage/
 Events      tools      (S3/ADLS)      (Silver layer)    (Gold layer) query    /App           lifecycle policy
```

## Batch vs Streaming vs Micro-batch

| | Batch | Micro-batch | Streaming |
|---|---|---|---|
| **Latency** | Hours (e.g., nightly) | Seconds-minutes | Milliseconds-seconds |
| **Example tool** | Airflow + Spark batch job | Spark Structured Streaming | Kafka Streams, Flink |
| **Use case** | Daily sales reports | Near-real-time dashboards | Fraud detection, alerting |
| **Complexity** | Low | Medium | High |
| **Cost** | Lower (scheduled bursts) | Medium | Higher (always-on compute) |

**Rule of thumb**: Don't default to streaming just because it's trendy — most business reporting doesn't need sub-second latency, and streaming systems are significantly harder to build, test, and debug. Use streaming when the business use case genuinely requires it (fraud detection, live inventory, real-time personalization).

## Anatomy of a Data Pipeline
```
┌─────────────┐   ┌───────────────┐   ┌──────────────┐   ┌────────────┐   ┌──────────────┐
│   Source    │──▶│   Extraction   │──▶│    Storage    │──▶│Transform   │──▶│   Serving    │
│ (API/DB/    │   │ (pull/push,    │   │  (raw zone -  │   │(clean,join,│   │ (warehouse   │
│  files/     │   │  CDC, webhook) │   │  S3/ADLS/GCS) │   │ aggregate) │   │  tables, BI) │
│  events)    │   └───────────────┘   └──────────────┘   └────────────┘   └──────────────┘
└─────────────┘
        Orchestration (Airflow/Dagster) coordinates every arrow above
        Monitoring/Alerting wraps the entire flow
```

## Push vs Pull Data Ingestion
- **Pull**: your pipeline actively requests data (poll a REST API every N minutes, run a SQL query against a source DB).
- **Push**: the source sends data to you (webhooks, event streams to Kafka, source DB triggers CDC events).
- **CDC (Change Data Capture)**: captures row-level inserts/updates/deletes from a source DB's transaction log (e.g., Postgres WAL, MySQL binlog) without hammering the DB with polling queries — tools: Debezium, AWS DMS, Fivetran.

## Idempotency (critical production concept)
A pipeline is **idempotent** if running it multiple times with the same input produces the same result (no duplicated data).
- Bad: `INSERT INTO orders VALUES (...)` on every run → duplicates if re-run
- Good: `MERGE`/`UPSERT` keyed on a unique ID → safe to re-run after a failure

## Data Quality Dimensions (the 6 pillars)
1. **Accuracy** — does the data reflect reality?
2. **Completeness** — are required fields populated?
3. **Consistency** — same value represented the same way everywhere (e.g., "USA" vs "US" vs "United States")
4. **Timeliness** — is data available within the expected SLA?
5. **Uniqueness** — no unintended duplicates
6. **Validity** — conforms to expected format/type/range (e.g., email looks like an email, age isn't negative)

## Schema-on-Write vs Schema-on-Read
- **Schema-on-write**: schema enforced before data is stored (traditional RDBMS/warehouse) — stricter, catches bad data early.
- **Schema-on-read**: schema applied only when data is queried (data lakes storing raw JSON/Parquet) — flexible, but bad data can sit undetected until query time.

## Interview Traps
- "Real-time" is often misused — clarify if the business actually needs sub-second latency or just "fresher than daily."
- Idempotency is one of the most commonly skipped concepts by juniors and one of the most commonly asked in senior interviews.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"A calm mind learns faster than an anxious one; steady your breath before you steady your code."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
