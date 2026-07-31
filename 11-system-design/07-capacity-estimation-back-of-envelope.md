# 7. Capacity Estimation — Back-of-the-Envelope Math

## Why Interviewers Ask You to Do This Live
Being able to quickly estimate "roughly how much storage/compute/bandwidth do we need" demonstrates genuine quantitative reasoning, not just pattern-name recall — and in real jobs, this exact skill prevents both wildly over-provisioning (wasting money) and under-provisioning (the system falling over under real load).

## The Core Numbers Worth Memorizing (rough, but genuinely useful)
```
1 day ≈ 86,400 seconds (often rounded to ~100,000 for quick mental math)
1 million requests/day ≈ ~12 requests/second average (86,400 sec/day)
Peak traffic is often 2-10x average (depending on how "spiky" the business is —
  e.g., an e-commerce site's Black Friday peak vs a B2B tool's steady weekday usage)

Storage:
  1 KB ≈ a short text record / small JSON event
  1 MB ≈ 1,000 KB ≈ a few hundred such records, or one small image
  1 GB ≈ 1,000 MB
  1 TB ≈ 1,000 GB
  1 PB ≈ 1,000 TB
```

## Worked Example 1: Sizing Storage for an Event Ingestion Pipeline
```
Scenario: 5 million users, each generating ~20 events/day, each event
          is ~1 KB (a typical clickstream event as JSON)

Daily event volume: 5,000,000 users x 20 events = 100,000,000 events/day
Daily data volume: 100,000,000 events x 1 KB = 100,000,000 KB ≈ 100 GB/day

Annual storage (raw, uncompressed): 100 GB/day x 365 days ≈ 36.5 TB/year
With typical Parquet compression (~5-10x for this kind of repetitive JSON
  data, recap `01-fundamentals/07-file-formats-and-storage.md`):
  ≈ 3.5-7 TB/year of actual stored data

This number tells you IMMEDIATELY: this is comfortably within normal S3/
ADLS/GCS storage costs (cheap, no special scaling concern), and the
REAL design challenge is likely the INGESTION THROUGHPUT and QUERY
performance, not raw storage capacity.
```

## Worked Example 2: Estimating Required Ingestion Throughput
```
Same scenario: 100,000,000 events/day
Average events/second: 100,000,000 / 86,400 ≈ ~1,160 events/second average

If peak traffic is 5x average (a reasonable assumption for a consumer app
with daily usage patterns, e.g., evening peak usage):
  Peak throughput ≈ 5,800 events/second

This number tells you: you need an ingestion layer (Kafka, Kinesis, Pub/Sub)
sized to comfortably handle ~6,000 events/second at peak — informing
BOTH the technology choice (all of these handle this scale easily) AND
the SPECIFIC CONFIGURATION (partition count, consumer parallelism) needed.
```

## Worked Example 3: Sizing a Data Warehouse Query Workload
```
Scenario: a BI dashboard queried by 200 internal analysts, each running
          ~10 queries/day, each query scanning ~5 GB of data (assume a
          reasonably well-partitioned table)

Daily data scanned: 200 analysts x 10 queries x 5 GB = 10,000 GB = 10 TB/day scanned

In a pay-per-TB-scanned warehouse (BigQuery/Athena style,
`07-cloud-platforms/03` and `05`):
  If cost is roughly $5/TB scanned: 10 TB/day x $5 = $50/day ≈ $1,500/month

This number IMMEDIATELY tells you whether this is a comfortable cost, or
whether you need to invest in BETTER partitioning/clustering (to reduce
data scanned per query) or consider reserved/flat-rate pricing
(`07-cloud-platforms/08`'s FinOps guidance) instead of pure pay-per-scan.
```

## The General Estimation Process (a repeatable method)
```
1. Identify the KEY QUANTITY driving load (users, events, requests, rows)
2. Estimate a REASONABLE per-unit number (events per user per day, bytes
   per event) — state your assumption explicitly, it's fine to be
   approximate, just be TRANSPARENT about the assumption
3. Multiply to get a DAILY total
4. Convert to PER-SECOND (divide by ~86,400) for throughput questions
5. Apply a PEAK MULTIPLIER (2-10x average, depending on the business's
   traffic pattern) for capacity/scaling decisions — average alone
   UNDER-provisions for real peak load
6. Convert to STORAGE totals by multiplying by time period (day -> year)
   and applying REALISTIC compression ratios for the format in use
7. Sanity-check the result against known reference points ("is 5 TB/year
   a lot? No, that's genuinely modest for a warehouse" vs "is 5 PB/year
   a lot? Yes, that's genuinely big-data-scale, needs different tooling")
```

## Interview Traps
- "Estimate the storage needed for [scenario]." — always show your WORK explicitly (state assumptions, show the multiplication steps) rather than just giving a final number — interviewers are evaluating your REASONING PROCESS, not just accuracy.
- "Why does PEAK vs AVERAGE matter so much in capacity planning?" — average-based sizing under-provisions for real traffic spikes (e.g., Black Friday, viral moments) — systems must be sized (or auto-scale, `07-cloud-platforms/02`) for realistic PEAK load, not average.
- Don't be afraid to round aggressively and state assumptions — a rough, clearly-reasoned estimate ("roughly 100 GB/day, so we're in comfortable territory for standard cloud storage") is far more valuable in an interview than getting stuck trying to be precisely accurate.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The one who serves many teams well first learns to listen to each of them."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
