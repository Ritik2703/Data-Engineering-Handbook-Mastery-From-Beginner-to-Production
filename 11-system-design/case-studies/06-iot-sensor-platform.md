# Case Study 6: IoT Sensor Data Platform at Scale (Manufacturing/Logistics)

## Step 1: Requirements
```
Functional: ingest sensor readings (temperature, vibration, location)
            from 500,000 industrial devices across factories/vehicles;
            detect anomalies (potential equipment failure) for
            proactive maintenance alerts; provide historical analytics
            for engineering teams

Non-functional:
  - Latency: anomaly detection alerts should fire within ~1-2 minutes
    of an abnormal reading (fast enough to prevent equipment damage,
    not requiring sub-second)
  - Throughput: 500,000 devices x 1 reading every 10 seconds = a
    genuinely HIGH, CONSTANT event rate (calculated in Step 3)
  - Reliability: devices are often on UNRELIABLE networks (factory
    floors, moving vehicles) — must tolerate late-arriving, out-of-order,
    and occasionally duplicate readings gracefully
  - Cost: at this device count, storage/processing cost efficiency is
    a genuine, ongoing concern, not an afterthought
```

## Step 2: High-Level Data Flow
```
IoT devices --(often via an edge gateway aggregating multiple
  devices)--> Kafka / IoT-specific ingestion (AWS IoT Core / Azure IoT
  Hub / GCP IoT Core, per `07-cloud-platforms/03-05`)
        |
        v
Spark Structured Streaming (with WATERMARKING for late/out-of-order data,
  recap `06-big-data/05`) -> Anomaly detection logic (statistical
  thresholds or a trained ML model) -> Alert service (pages
  maintenance team)
        |
        └──(also)──> Data Lake (Iceberg, partitioned by device/date)
                      -> Batch aggregation (hourly/daily summaries)
                      -> Warehouse -> Engineering analytics dashboards
```

## Step 3: Capacity Estimation
```
500,000 devices x 1 reading / 10 seconds = 50,000 readings/second average
  -> This is GENUINELY HIGH sustained throughput (much higher than the
     e-commerce case study's ~4 orders/second) — directly justifying
     serious streaming infrastructure investment here, unlike case study 5.

50,000 readings/sec x 86,400 sec/day ≈ 4.3 billion readings/day
At ~0.2 KB per reading (small sensor payload): 4.3B x 0.2 KB ≈ 860 GB/day raw
Annual (compressed ~8x, sensor data compresses very well due to
  repetitive/similar values): ≈ 860 GB x 365 / 8 ≈ ~39 TB/year
  -> Genuine big-data scale, reinforcing the need for a properly
     partitioned lakehouse (Iceberg) and NOT a traditional row-based
     database for historical storage.
```

## Step 4: Technology Choices, Justified

**Watermarking-based streaming (recap `06-big-data/05`) to explicitly handle late/out-of-order data**
> Justification: DIRECTLY addresses the stated "unreliable networks, late-arriving data" requirement — a naive streaming design assuming perfectly-ordered, on-time data would silently produce WRONG anomaly detection results (missing anomalies, or false alarms) once real-world network conditions (the stated constraint) are encountered. This is exactly the kind of requirement-driven technical choice this module emphasizes.

**Statistical threshold-based anomaly detection FIRST, ML-based detection as a later enhancement**
> Justification: a genuinely senior-level, pragmatic choice — simple statistical thresholds (e.g., "vibration reading > 3 standard deviations from this device's rolling average") can be implemented and VALIDATED quickly, delivering real business value (catching genuine equipment failures) faster than committing to a more sophisticated ML model upfront, which requires more data/time to train and validate properly. Sophistication should be added when justified by evidence the simpler approach is insufficient, not by default.

**Partitioning the lakehouse by device_id AND date**
> Justification: engineering teams' most common query pattern is "show me THIS device's history over THIS time range" — partitioning by both dimensions directly optimizes for this actual access pattern (recap the partition design reasoning from `01-fundamentals/07` and `05-databases/07`), avoiding full-table scans for routine engineering investigation queries.

**Edge aggregation (batching readings at a gateway before sending to the cloud) where devices support it**
> Justification: reduces network traffic/cost and Kafka ingestion load at the SOURCE, directly addressing the stated cost-efficiency concern at this device scale — an example of a system design choice that happens PARTIALLY outside the core "data platform" itself but is still a genuinely important architectural decision to raise.

## Step 5: Failure Modes & Scale
```
"What happens if a factory loses network connectivity for an hour?"
  -> Readings should BUFFER locally at the edge gateway/device and
     REPLAY once connectivity restores — this needs to be designed
     into the DEVICE/EDGE layer, not just the cloud ingestion layer,
     directly connecting to the "unreliable networks" requirement.
     Watermarking on the cloud side then correctly handles this
     resulting batch of "late" data once it arrives.

"Where does this break first if device count grows to 5 million (10x)?"
  -> At 500,000/second sustained throughput (10x the current 50,000/sec),
     Kafka partition count and Spark Streaming cluster size are the
     first likely constraints, requiring careful partition-key design
     (device_id-based, recap `06-big-data/05`'s Kafka partitioning
     discussion) to scale cleanly without hot-partition issues.

"How do you avoid alert fatigue from false-positive anomalies?"
  -> Directly connects to `08-orchestration/08`'s alert fatigue
     discussion — anomaly thresholds need tuning based on REAL
     historical false-positive rates, and alerts should be
     SEVERITY-CLASSIFIED (a clearly critical reading vs a borderline
     one) rather than treating every threshold-crossing identically.
```

## Step 6: Summary
> "Given the genuinely high sustained throughput (50,000 readings/second) and unreliable network conditions, I'm proposing a Kafka + Spark Structured Streaming architecture with explicit watermarking for late/out-of-order data, starting with statistical threshold-based anomaly detection rather than a more complex ML model upfront. The lakehouse is partitioned by device_id and date to match engineers' actual query patterns. The key tradeoff is starting with simpler anomaly detection logic, accepting it may miss more subtle failure patterns a trained model could catch — justified because it delivers real value faster and can be validated/upgraded incrementally once we have evidence of where the simple approach falls short."


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"To trust a team with real responsibility is to help them grow into it."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
