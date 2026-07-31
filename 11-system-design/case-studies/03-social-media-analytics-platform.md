# Case Study 3: Social Media Engagement Analytics Platform

## Step 1: Requirements
```
Functional: content creators need to see engagement metrics (likes,
            comments, shares, views) on their posts; the platform needs
            company-wide trending-content detection; product team needs
            historical analytics for feature decisions

Non-functional:
  - Latency: creator-facing "your post's engagement" numbers should
    update within a few minutes (not sub-second — creators checking
    their stats aren't doing so in real-time trading-style urgency)
  - Latency (different requirement!): TRENDING detection needs to be
    much faster (within ~1 minute) since trending content should
    surface QUICKLY while still relevant/viral
  - Scale: 100 million posts/day, ~2 billion engagement events/day
    (likes, comments, views combined)
  - Consistency: engagement COUNTS shown to creators can be
    eventually consistent (a like count off by a few for a moment is
    fine); but must never DOUBLE-COUNT (a user's like should count once,
    even if their app retries the request)
```

## Step 2: High-Level Data Flow
```
Engagement events (likes/comments/views) -> Kafka (partitioned by post_id)
      |
      ├──> Spark Structured Streaming (near-real-time aggregation,
      |     ~1 min windows) -> Fast-serving store (Redis) -> Trending
      |     detection service -> Trending feed
      |
      └──> Batch pipeline (hourly) -> Data Lake (Iceberg) -> Warehouse
            (Snowflake) -> Creator-facing analytics dashboard
                         -> Product team's historical analytics (BI tool)
```
**Key architectural insight**: this system has TWO genuinely different latency requirements for the SAME underlying event stream — trending detection (fast, ~1 min) and creator dashboards (a few minutes, less urgent) — a well-designed system serves BOTH from the same Kafka source via TWO different downstream consumers, rather than forcing one single processing path to serve both needs identically (recap the fan-out pattern from file 4).

## Step 3: Capacity Estimation
```
2,000,000,000 engagement events/day / 86,400 sec ≈ ~23,000 events/second average
At peak (evening usage spike, ~4x average): ≈ ~92,000 events/second peak
  -> This is genuinely HIGH throughput — directly informs the need for
     a well-partitioned Kafka topic (many partitions, keyed by post_id
     for per-post ordering) and a horizontally-scaled Spark Streaming
     cluster, not a single-node solution.

Storage: 2B events/day x ~0.3 KB (small engagement event) = 600 GB/day raw
Annual (compressed ~6x for repetitive engagement event structure):
  ≈ 600 GB x 365 / 6 ≈ ~36 TB/year
```

## Step 4: Technology Choices, Justified

**Deduplication strategy — idempotency key per (user_id, post_id, engagement_type)**
> Justification: directly addresses the stated "never double-count" requirement — each engagement event includes a unique idempotency key; both the streaming aggregation and batch pipeline use this key to deduplicate (e.g., a Spark `dropDuplicates` on this key, recap `06-big-data/10`), ensuring retries/at-least-once delivery never inflate counts.

**Two separate consumers from the same Kafka source (fan-out)**
> Justification: trending detection and creator dashboards have GENUINELY DIFFERENT latency requirements (1 min vs a few minutes) and different query patterns (trending = cross-post ranking; dashboards = per-post lookup) — forcing both through ONE identical pipeline would either over-engineer the dashboard path (unnecessary complexity) or under-serve the trending path (too slow) — the fan-out design serves each need appropriately.

**Fast-serving store (Redis) for trending, warehouse (Snowflake) for historical/creator dashboards**
> Justification: trending needs FAST, frequently-updated rankings across many posts (Redis sorted sets are a natural fit); creator dashboards and product analytics need rich historical querying/joins (a warehouse's SQL capability fits better) — again, matching the tool to the SPECIFIC access pattern rather than one-size-fits-all.

## Step 5: Failure Modes & Scale
```
"What happens if the streaming trending-detection job falls behind?"
  -> Trending content becomes STALE (shows what was trending 10 minutes
     ago, not right now) — a real but bounded degradation, not a total
     outage; monitoring should alert if the streaming lag exceeds a
     defined SLA threshold (recap `08-orchestration/08`'s monitoring layers).

"Where does this break first at 10x scale (20 billion events/day)?"
  -> Kafka partition count/broker capacity is the first likely
     bottleneck, requiring a partition rebalancing strategy; the
     batch warehouse load may also need better incremental-processing
     design (recap `04-etl-elt/02`'s incremental load patterns) rather
     than reprocessing full daily volumes each time.

"How do you handle a 'viral' post spiking to millions of engagements
in minutes (data skew)?"
  -> A single post_id becoming a massive HOT PARTITION is a genuine,
     realistic skew scenario (recap `06-big-data/04`'s data skew
     discussion) — mitigated via salting the partition key for
     extremely hot posts, or a separate "viral post" handling path
     with additional capacity headroom.
```

## Step 6: Summary
> "Given the two distinct latency requirements (fast trending detection vs slower creator dashboards) from the same event stream, I'm proposing a Kafka-based fan-out architecture feeding both a Spark Streaming trending pipeline (Redis-served) and an hourly batch pipeline (warehouse-served). Deduplication via idempotency keys directly satisfies the 'never double-count' requirement. The main tradeoff is maintaining two separate downstream paths rather than one unified pipeline — justified because forcing one path to serve both genuinely different latency needs would compromise one or the other. I'd want to specifically stress-test the hot-partition/viral-post scenario before launch, since that's a realistic edge case this design needs to handle gracefully."


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Every great structure begins with someone willing to ask 'what problem are we truly solving?'"*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
