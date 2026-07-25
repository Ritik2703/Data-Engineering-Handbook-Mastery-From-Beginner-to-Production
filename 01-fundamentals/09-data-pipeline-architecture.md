# 9. Data Pipeline Architecture Patterns

## ETL vs ELT (recap with architecture lens)
```
ETL (legacy-standard):
Source → Extract → Transform (on separate ETL server compute) → Load into Warehouse
         Used when warehouse compute was expensive/limited (on-prem era)

ELT (modern cloud-standard):
Source → Extract → Load raw into Warehouse/Lake → Transform IN warehouse (SQL, dbt)
         Used because cloud warehouse compute is now cheap, scalable, and elastic
```

## Lambda Architecture
Separate batch and speed layers, merged at serving time.
```
                ┌──────────────┐
Source Data ──▶ │  Batch Layer  │──▶ Batch Views (accurate, complete, but hours old)
     │          └──────────────┘                              │
     │                                                          ▼
     │          ┌──────────────┐                        Serving Layer
     └────────▶ │  Speed Layer  │──▶ Real-time Views ───▶ (merges both)
                └──────────────┘  (fast, approximate, recent-only)
```
- **Pros**: handles both historical accuracy and real-time freshness.
- **Cons**: maintaining two separate codebases (batch + streaming logic) for the same business logic — expensive to build and keep in sync.

## Kappa Architecture
Simplification of Lambda — everything flows through a single streaming pipeline; reprocessing is done by **replaying** the event log from the beginning instead of maintaining a separate batch layer.
```
Source Data ──▶ Kafka (durable event log, long retention) ──▶ Stream Processor (Flink/Spark Streaming)
                                                                      │
                                                                      ▼
                                                              Serving Layer (single source of truth)
```
- **Pros**: one codebase, simpler mental model.
- **Cons**: requires the streaming system to handle reprocessing/backfills well, and needs long log retention (storage cost).

## Medallion Architecture (Bronze/Silver/Gold — Databricks-popularized, now industry-common)
```
Bronze (raw)                Silver (cleaned/conformed)         Gold (business-level aggregates)
─────────────                ──────────────────────             ──────────────────────────────
Raw data, as-is from        Deduplicated, validated,           Aggregated, joined, ready for
source (no transforms)      typed, conformed schema             BI dashboards / ML features
Append-only, full history   Still fairly granular               Highly curated, few wide tables
     │                              │                                    │
     └──────────────────────────────┴────────────────────────────────────┘
                        Each layer typically a separate set of tables/folders,
                        transformations move data bronze -> silver -> gold
```
This maps cleanly onto S3/ADLS/GCS folder structure (`raw/`, `curated/`, `marts/`) and is the most common pattern taught/used today because it's simple to reason about and debug (you can always trace back to raw data).

## Batch Pipeline Pattern (most common in practice)
```
Airflow (scheduled trigger, e.g., 2 AM daily)
    → Extract task (API/DB pull → raw zone)
    → Transform task (Spark or dbt → curated zone)
    → Load task (curated → warehouse tables)
    → Data quality check task (row counts, null checks, freshness)
    → Notify task (Slack/email on failure)
```

## Streaming Pipeline Pattern
```
Producer (app/service) → Kafka topic → Stream processor (Spark Structured Streaming / Flink)
    → Sink (warehouse table via micro-batch writes, or real-time serving DB like Redis/DynamoDB)
    → Dashboard reads from serving layer (near-real-time)
```

## Choosing an Architecture
```
Simple daily/hourly reporting, no real-time need           -> Plain batch ETL/ELT, Medallion layers
Need both historical accuracy AND real-time, willing to
  maintain two pipelines                                    -> Lambda
Need real-time + willing to invest in one streaming system
  robust enough for replay/reprocessing                     -> Kappa
Building a new lakehouse platform today, want simplicity
  and clear data lineage                                    -> Medallion (Bronze/Silver/Gold)
```

## Orchestration Design Principles
1. **Idempotent tasks** — safe to re-run without duplicating data (see `02-core-concepts.md`)
2. **Parametrize by execution date** — enables backfills as a config change, not a code rewrite
3. **Fail fast, alert clearly** — a task should fail loudly with a clear error rather than silently produce bad data
4. **Data quality gates between layers** — don't let bad Bronze data silently propagate to Gold/BI

## Interview Traps
- Be ready to explain WHY Kappa emerged (Lambda's dual-codebase maintenance burden) — this is a very common "explain the evolution" interview question.
- Medallion isn't a new invention over Kimball/star-schema — it's a **physical layering strategy** for lake/lakehouse storage; you still apply dimensional modeling concepts within the Gold layer.
