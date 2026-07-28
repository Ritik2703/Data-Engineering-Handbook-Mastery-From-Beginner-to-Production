# Case Study: Full Big Data Pipeline — Video Streaming Platform (Netflix-style)

## Business Requirements
```
- Ingest billions of viewing events daily (play, pause, stop, buffer, quality change)
- Real-time monitoring dashboard (are streams failing right now, anywhere in the world?)
- Daily/weekly recommendation model training needs cleaned, aggregated viewing history
- Content team needs "what's trending in India this week" style analytical queries
- Data must be reliable enough that a bad job doesn't corrupt weeks of history
```

## Architecture
```
Client apps (TV, mobile, web) generate viewing events
        |
        v
Kafka (ingests billions of events/day across many topics: play_events, quality_events, error_events)
        |
        ├──────────────────────────────┐
        v                                v
Spark Structured Streaming          Real-time monitoring service
(near-real-time aggregation,        (Flink — sub-second alerting on
 windowed counts, written to        stream error-rate spikes, paging
 a fast-serving store)               on-call engineers automatically)
        |
        v
Fast-serving store (e.g., Cassandra/Redis) — powers live dashboards
        |
        (separately, in parallel)
        v
Kafka --batch export--> S3 raw zone (Bronze layer, Iceberg table format)
        |
        v
Spark batch job (nightly): dedupe, validate schema, clean malformed events
        |
        v
S3 curated zone (Silver layer, Iceberg) — one clean row per viewing event
        |
        v
Spark batch job: aggregate into daily/weekly summaries, join with content metadata
        |
        v
S3 Gold layer (Iceberg) — "trending by region", "completion rate by title", etc.
        |
        ├───────────────────────────┐
        v                             v
Presto/Trino (ad-hoc analyst      ML feature pipeline (feeds the
queries directly on Iceberg)       recommendation model training job)
```

## Why Each Design Decision Was Made
1. **Kafka as the single ingestion point**: every downstream consumer (real-time monitoring, batch aggregation, ML features) reads from the SAME event stream independently, at its own pace — avoiding building separate custom ingestion pipelines for each consumer.
2. **Two parallel processing paths (streaming + batch) from the same Kafka topics**: real-time monitoring genuinely needs sub-second latency (Flink); daily aggregation for recommendations/analytics doesn't need that latency and benefits from Spark's more mature batch ecosystem and cost efficiency for large-scale reprocessing — this is a real Lambda-architecture-style tradeoff (`01-fundamentals/09-data-pipeline-architecture.md`).
3. **Iceberg as the table format**: at this event volume (billions of rows daily), reliable ACID guarantees and efficient file-level metadata tracking (not Hive-style partition-directory tracking) are essential — this is precisely the scale problem that motivated Netflix's real-world creation of Iceberg.
4. **Bronze/Silver/Gold layering**: keeps a full audit trail (Bronze = exactly what arrived, unmodified) while providing increasingly refined, business-ready data (Gold) — if a Silver/Gold transformation bug is found, you can reprocess from Bronze without needing to re-ingest from Kafka (which may have already aged out of retention).
5. **Presto/Trino for ad-hoc analyst queries, separate from the Spark batch jobs**: analysts need fast, interactive SQL response times; Presto/Trino's architecture (in-memory, no MapReduce-style overhead) is specifically optimized for this INTERACTIVE query pattern, distinct from Spark's strength in large-scale scheduled batch ETL.

## Data Quality Gates (where they'd sit in this pipeline)
```
Bronze -> Silver transition: schema validation (reject/quarantine malformed events),
                              basic null checks on critical fields (user_id, content_id)
Silver -> Gold transition: business logic validation (completion rates between 0-100%,
                            no negative watch durations), row count sanity checks
                            against historical daily averages (catch upstream outages)
```

## Failure Scenarios & How This Architecture Handles Them
```
Kafka broker fails: replication factor ensures no data loss; consumers simply
                     reconnect to a surviving broker holding replica partitions

A Spark batch job crashes mid-run: Iceberg's transactional guarantees mean the
                                    table simply reflects its last successfully
                                    committed state — no partial/corrupt data
                                    visible to downstream consumers

A bad code deploy corrupts the Silver layer: time travel (Iceberg) lets engineers
                                              query/restore the table to its state
                                              before the bad deploy, and Bronze
                                              retains the original raw data for
                                              full reprocessing if needed

Flink real-time monitoring lags/fails: does NOT affect the batch/analytics path at
                                        all (fully decoupled) — on-call is paged
                                        for the monitoring issue specifically,
                                        while recommendation/analytics pipelines
                                        continue unaffected
```

## Try It Yourself
Using this same reasoning, sketch a big data architecture for:
1. A ride-hailing app's location-ping ingestion and driver-matching pipeline (consider: what needs sub-second latency vs what can be batch?).
2. An e-commerce platform's clickstream-to-recommendation pipeline (consider: where would you put data quality gates, and why?).


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Every act of teaching is also an act of learning, if done with an open heart."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
