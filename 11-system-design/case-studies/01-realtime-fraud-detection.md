# Case Study 1: Real-Time Fraud Detection System (Fintech)

*Worked using the 6-step framework from `10-interview-framework-how-to-answer.md`*

## Step 1: Requirements (as clarified with the "business")
```
Functional: flag potentially fraudulent transactions WITHIN SECONDS of
            occurring, so they can be held/blocked before completing;
            also need accurate historical data for compliance reporting
            and to retrain fraud models periodically

Non-functional:
  - Latency: fraud SCORING must complete in under 500ms per transaction
    (a hard business requirement — can't hold up checkout longer than that)
  - Throughput: ~2,000 transactions/second at peak (estimated in Step 3)
  - Consistency: the fraud score MUST use the most current account/
    device history available — cannot use stale data
  - Availability: this system CANNOT go down — a fraud-check outage
    either blocks ALL transactions (revenue loss) or must fail open
    (risk exposure) — a genuinely hard business tradeoff to surface explicitly
  - Durability: EVERY transaction record must be retained, zero data
    loss (regulatory requirement)
```

## Step 2: High-Level Data Flow
```
Transaction Event -> Kafka (durable, ordered per-account) -> Real-time
  Feature Computation (Flink) -> Fraud Model Scoring (low-latency
  serving) -> Decision (allow/hold/block) -> back to checkout flow
                                          |
                                    (in parallel)
                                          v
                              Data Lake (Iceberg) -> Batch feature
                              engineering + model retraining (Spark)
                              -> Compliance reporting (warehouse)
```

## Step 3: Capacity Estimation
```
2,000 transactions/second peak x 2 KB average event size (transaction +
  computed features) ≈ 4 MB/second ≈ ~340 GB/day raw event volume
Annual (with Parquet/Iceberg compression ~5x): ≈ 340 GB x 365 / 5 ≈ ~25 TB/year
-> Comfortably within normal cloud storage/Kafka retention costs; the
   REAL challenge is clearly the SUB-500ms LATENCY requirement, not raw volume.
```

## Step 4: Technology Choices, Justified

**Ingestion — Kafka, keyed by account_id**
> Justification: need ORDERING per account (so features reflect the correct sequence of that account's recent activity) and durable replay capability for reprocessing/model retraining. Tradeoff accepted: operational complexity of running/monitoring a Kafka cluster, justified by the strict latency and ordering requirements.

**Real-time processing — Flink, not Spark Structured Streaming**
> Justification: the hard 500ms end-to-end latency requirement favors Flink's true event-at-a-time processing over Spark's micro-batch model (recap `06-big-data/05`). Tradeoff accepted: Flink has a steeper operational learning curve and smaller talent pool than Spark — justified here because the latency requirement is a genuine hard business constraint, not a nice-to-have.

**Feature store — a low-latency key-value store (Redis) for "recent activity" features**
> Justification: fraud scoring needs FAST lookups of recent account/device history (e.g., "how many transactions from this device in the last hour") — Redis's sub-millisecond reads fit the 500ms budget; a data warehouse query would be far too slow for this specific access pattern. Tradeoff accepted: Redis data needs careful TTL/eviction management and is NOT the system of record (Kafka/Iceberg remain that).

**Storage — Apache Iceberg (recap `06-big-data/06`)**
> Justification: need reliable, ACID-compliant historical storage for compliance + ability to reprocess for model retraining; Iceberg's file-level metadata scales well at this volume. Tradeoff accepted: added complexity vs plain Parquet, justified by the genuine need for reliable updates/time-travel for compliance audit needs.

**Model serving — a dedicated low-latency inference service (not embedded directly in the Flink job)**
> Justification: decouples MODEL UPDATES (data science team iterates on the fraud model) from the STREAMING INFRASTRUCTURE (data engineering team maintains) — a genuinely important team/ownership boundary, not just a technical one.

## Step 5: Failure Modes & Scale
```
"What happens if the fraud model serving endpoint is down?"
  -> This is the CRITICAL fail-open vs fail-closed business decision
     that MUST be explicitly surfaced to stakeholders, not decided
     unilaterally by engineering: fail-closed (block ALL transactions)
     protects against fraud risk but causes total revenue loss during
     an outage; fail-open (allow all transactions) protects revenue
     but exposes fraud risk during the outage window. REAL systems
     often use a hybrid: fail-open for LOW-value transactions, fail-closed
     (hold for manual review) for HIGH-value transactions — a genuinely
     senior-level insight (explicit business-tradeoff surfacing, not
     a purely technical answer).

"Where does this break first at 10x load (20,000 tx/second)?"
  -> Likely the Redis feature store's throughput ceiling first, then
     Flink's processing capacity — mitigated by Redis Cluster (horizontal
     sharding) and Flink's own horizontal scaling via more task managers.

"How do you prevent duplicate transaction processing (idempotency)?"
  -> Each transaction has a unique ID; scoring/decision logic is
     idempotent (re-processing the same transaction ID produces the
     same result, doesn't double-charge or double-flag).
```

## Step 6: Summary
> "Given the hard 500ms latency requirement and strict ordering/durability needs, I'm proposing a Kafka + Flink + Redis feature store architecture, with Iceberg for durable historical storage feeding both compliance reporting and model retraining. The key tradeoff is added operational complexity (Flink, Redis, Kafka all require real operational maturity) versus a simpler batch-only approach — justified because sub-second fraud detection is a stated hard requirement, not optional. The biggest open question I'd want to validate with the business is the fail-open vs fail-closed policy during an outage — that's a business risk decision, not a purely technical one."


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The steady architect plans for the storm long before the clouds appear."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
