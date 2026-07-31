# Case Study 5: End-to-End E-commerce Data Platform (Amazon/Flipkart-style)

## Step 1: Requirements
```
Functional: unify data from the OLTP order/inventory system, a payment
            gateway, marketing tools (Google Ads, email), and customer
            support tickets into ONE warehouse for company-wide analytics
            (revenue reporting, marketing attribution, customer support
            quality, inventory planning)

Non-functional:
  - Latency: MOST reporting can be next-day (nightly batch is fine);
    but inventory/stock-level data needs to be near-real-time (within
    ~15 minutes) to avoid overselling out-of-stock items
  - Scale: 10 million orders/month, dozens of external data sources
    (each with DIFFERENT extraction methods — APIs, DB CDC, file drops)
  - Data quality: financial reporting numbers must be provably accurate
    (reconciliation with the payment gateway is a hard requirement)
  - Governance: PII (customer addresses, payment details) needs strict
    access control and must be excluded from general-analyst-accessible tables
```

## Step 2: High-Level Data Flow
```
OLTP order DB --CDC (Debezium)--> Kafka --> near-real-time inventory
  aggregation (Spark Streaming) --> fast-serving inventory API
        |
        └──(also)──> S3 raw zone (Bronze, Iceberg)

Payment gateway API --nightly extraction (Python, per `03-python/06`)--> S3 raw zone
Marketing tools APIs --nightly extraction--> S3 raw zone
Support ticket system --nightly extraction--> S3 raw zone
        |
        v (ALL sources)
dbt: staging models (clean/rename, 1:1 per source, `04-etl-elt/08`)
        |
dbt: intermediate models (join order + payment + marketing touch data)
        |
dbt: mart models (fct_orders, dim_customer [PII-restricted], 
     fct_marketing_attribution, fct_support_quality)
        |
        v
Snowflake warehouse -> Power BI (company-wide dashboards, with RLS
  restricting PII-containing tables to authorized roles only)
```
**Key architectural insight**: this system has ONE latency-sensitive path (inventory, near-real-time via CDC+streaming) and MANY latency-tolerant paths (nightly batch for most sources) — correctly identifying WHICH specific data need NOT be batch, rather than defaulting either everything-to-streaming or everything-to-batch, is the central design decision.

## Step 3: Capacity Estimation
```
10,000,000 orders/month ≈ 330,000 orders/day ≈ ~4 orders/second average
  -> Genuinely MODEST transactional volume — the CDC/streaming inventory
     path doesn't need extreme throughput engineering, just correct
     low-latency design.

Total data volume across all sources (orders + line items + marketing +
  support), estimated generously at ~5 GB/day combined ≈ ~1.8 TB/year
  raw -> a genuinely SMALL-TO-MODERATE warehouse scale, meaning the
  PRIMARY engineering challenge here is INTEGRATION COMPLEXITY (many
  different source systems/formats) and DATA QUALITY/GOVERNANCE, not
  raw processing scale.
```

## Step 4: Technology Choices, Justified

**CDC (Debezium) + streaming ONLY for inventory, batch for everything else**
> Justification: directly matches the STATED requirement (inventory needs ~15 min freshness to prevent overselling; everything else is next-day-acceptable) — avoiding the temptation to stream EVERYTHING "for consistency," which would add unjustified operational complexity (recap file 3's Lambda/Kappa tradeoff analysis) for data that doesn't need it.

**dbt for transformation, with an explicit staging/intermediate/mart layering**
> Justification: with DOZENS of source systems, a disciplined, version-controlled, TESTED transformation layer (recap `04-etl-elt/08`) is essential to avoid the "spreadsheet spaghetti" chaos of ad-hoc SQL scripts — the staging layer specifically isolates each source's quirks (recap the staging-model pattern) so downstream marts stay clean.

**Separate, access-restricted PII tables (e.g., `dim_customer_pii` vs `dim_customer_public`)**
> Justification: directly satisfies the governance requirement — most analysts querying `fct_orders` for revenue trends never need to see raw customer addresses/payment details; separating PII into its own restricted table (with RLS/column-level security, recap `09-visualization/04` and `07-cloud-platforms/09`) lets the BROAD analyst population work freely while protecting sensitive data specifically.

**A dedicated reconciliation dbt model comparing order totals against payment gateway totals**
> Justification: directly satisfies the "provably accurate financial reporting" requirement — implementing the FULL OUTER JOIN reconciliation pattern (recap `02-sql/06-advanced-sql-patterns.md`) as an AUTOMATED, regularly-run dbt test/model, not a manual, occasional audit.

## Step 5: Failure Modes & Scale
```
"What happens if the CDC stream for inventory falls behind?"
  -> Inventory numbers become STALE, risking overselling — this is
     the ONE place in this design where a delay has genuine, direct
     business cost (unlike the batch paths' more tolerant delay budget),
     justifying dedicated monitoring/alerting SPECIFICALLY on this
     stream's lag (recap `08-orchestration/08`'s SLA discussion).

"A marketing API changes its schema without notice — what happens?"
  -> This is exactly why the staging layer + dbt tests (recap
     `04-etl-elt/08` and `03-python/12`'s schema drift detection) exist:
     the staging model's expected-schema check fails LOUDLY and
     specifically for THAT source, rather than silently corrupting
     downstream marts that join across multiple sources.

"Where does this break first if order volume grows 20x?"
  -> At only ~4 orders/second currently, 20x (≈80/second) is still
     genuinely modest — unlikely to be the bottleneck; the more likely
     future bottleneck is INTEGRATION COMPLEXITY continuing to grow
     (more source systems added over time) rather than raw volume,
     reinforcing that the primary engineering investment here should be
     in disciplined, testable INTEGRATION patterns, not premature
     scale-focused over-engineering.
```

## Step 6: Summary
> "Given that inventory is the ONLY genuinely latency-sensitive data source here, I'm proposing a hybrid architecture: CDC + streaming specifically for inventory, and a disciplined dbt-based nightly batch pipeline for everything else, unified in a Snowflake warehouse with explicit PII isolation for governance. The main tradeoff is maintaining one streaming path alongside many batch paths (some added complexity) versus a uniform approach — justified because only inventory has a genuine business cost tied to freshness. I'd prioritize the reconciliation model and schema-drift detection early, since with dozens of source systems, data quality/integration robustness is a bigger real risk here than raw scale."


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Patience in design saves the panic of a system built in haste."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
