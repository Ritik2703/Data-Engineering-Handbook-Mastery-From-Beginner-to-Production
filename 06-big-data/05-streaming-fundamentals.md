# 5. Streaming Fundamentals — Kafka, Spark Structured Streaming, Flink

## Why Streaming Exists (the business problem)
Some decisions can't wait for a nightly batch job — fraud must be flagged within seconds of a suspicious transaction, a ride-hailing app must match a driver to a rider in real time, a live dashboard needs current numbers, not yesterday's. Streaming systems process data continuously, as events arrive, rather than in scheduled batches.

## Kafka — The Streaming Backbone

### Core Concepts
```
Producer -----writes events-----> Kafka Topic -----reads events-----> Consumer

A Topic is split into PARTITIONS for parallelism:
Topic: "orders"
  Partition 0: [event1, event4, event7, ...]
  Partition 1: [event2, event5, event8, ...]
  Partition 2: [event3, event6, event9, ...]

Each partition is an ordered, append-only log. Order is guaranteed WITHIN a partition,
NOT across partitions of the same topic.
```
- **Offset**: a message's position within its partition — consumers track which offset they've processed up to, enabling them to resume exactly where they left off after a restart/failure.
- **Consumer Group**: multiple consumer instances sharing the work of reading a topic — Kafka automatically assigns different partitions to different consumers in the same group, enabling parallel processing.
- **Replication Factor**: each partition is replicated across multiple brokers (Kafka servers) for durability — losing one broker doesn't lose data.
- **Retention**: Kafka can retain messages for a configured period (or indefinitely) — unlike traditional message queues that delete messages once consumed, Kafka's log-based design allows MULTIPLE independent consumer groups to read the same data at their own pace, and allows REPLAYING historical events (crucial for Kappa architecture, `01-fundamentals/09-data-pipeline-architecture.md`).

### Producing and Consuming (Python example)
```python
from kafka import KafkaProducer, KafkaConsumer
import json

producer = KafkaProducer(
    bootstrap_servers=["broker1:9092"],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    key_serializer=lambda k: k.encode("utf-8"),
    acks="all",  # wait for ALL in-sync replicas to acknowledge — strongest durability guarantee
)
# Keying by customer_id ensures all of one customer's events land in the SAME partition,
# preserving per-customer ordering even though the topic overall isn't globally ordered
producer.send("orders", key="customer_101", value={"order_id": 5001, "amount": 599})

consumer = KafkaConsumer(
    "orders",
    bootstrap_servers=["broker1:9092"],
    group_id="fraud-detection-service",
    enable_auto_commit=False,   # manual commit for at-least-once processing guarantees
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
)
for message in consumer:
    process_order(message.value)
    consumer.commit()   # only commit AFTER successful processing
```

## Delivery/Processing Semantics — The Critical Distinction
| Guarantee | Meaning | Risk |
|---|---|---|
| **At-most-once** | Message processed 0 or 1 times | Can silently LOSE messages on failure |
| **At-least-once** | Message processed 1 or MORE times | Can process DUPLICATES on failure/retry |
| **Exactly-once** | Message processed exactly 1 time | Hardest to achieve, requires idempotent processing + transactional guarantees |
```python
# Achieving effectively-exactly-once with at-least-once delivery + idempotent processing
# (the MOST common practical real-world approach)
def process_order_idempotent(order_event):
    # Using a MERGE/UPSERT keyed on order_id makes reprocessing the SAME event harmless
    db.execute("""
        INSERT INTO orders (order_id, amount) VALUES (%s, %s)
        ON CONFLICT (order_id) DO UPDATE SET amount = EXCLUDED.amount
    """, (order_event["order_id"], order_event["amount"]))
```
**Real production wisdom**: true exactly-once is genuinely hard to guarantee end-to-end across an entire pipeline; the pragmatic, widely-used approach is at-least-once delivery combined with IDEMPOTENT processing logic (see `01-fundamentals/02-core-concepts.md`) — the net effect behaves like exactly-once without needing the full complexity of distributed transactional guarantees everywhere.

## Spark Structured Streaming — Micro-Batch Processing
```python
from pyspark.sql import functions as F

stream_df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "broker1:9092")
    .option("subscribe", "orders")
    .load()
)

parsed_df = stream_df.select(
    F.from_json(F.col("value").cast("string"), order_schema).alias("data")
).select("data.*")

# Windowed aggregation — e.g., total sales per 5-minute window
windowed = (
    parsed_df
    .withWatermark("event_time", "10 minutes")   # tolerate up to 10 min of late-arriving data
    .groupBy(F.window("event_time", "5 minutes"))
    .agg(F.sum("amount").alias("total_sales"))
)

query = (
    windowed.writeStream
    .outputMode("append")
    .format("console")   # or "parquet", "delta", a database sink, etc.
    .trigger(processingTime="1 minute")   # micro-batch interval
    .start()
)
query.awaitTermination()
```
**Watermarking** — the critical concept: real-world events can arrive late (network delays, offline mobile devices syncing later) and out of order. A watermark tells Spark "how late can an event be and still get counted in its correct time window" — events arriving later than the watermark threshold are dropped, trading some completeness for the ability to eventually finalize and emit window results (you can't wait FOREVER for possibly-late data).

## Apache Flink — True Event-at-a-Time Streaming
Unlike Spark Structured Streaming's micro-batch model (processing small batches at short intervals), Flink processes each event individually as it arrives, achieving lower latency — important for use cases needing millisecond-level responsiveness (real-time fraud scoring, high-frequency trading signals).
```java
// Conceptual Flink pseudocode structure (Java/Scala, not Python-first like Spark)
DataStream<Order> orders = env.addSource(new FlinkKafkaConsumer<>("orders", schema, props));
orders
    .keyBy(order -> order.getCustomerId())
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .aggregate(new SumAggregator())
    .addSink(new FlinkKafkaProducer<>("alerts", schema, props));
```
**Real production choice**: Spark Structured Streaming is often preferred when a team ALREADY uses Spark for batch processing (unified codebase/skills, "good enough" latency of seconds); Flink is chosen specifically when sub-second/millisecond latency is a hard business requirement, or for very complex stateful event processing patterns.

## Windowing Types
```
Tumbling window:  Fixed, non-overlapping windows.  [0-5min][5-10min][10-15min]
Sliding window:    Fixed size, but OVERLAPPING, sliding forward by a smaller step.
                   [0-5min][1-6min][2-7min]... (e.g., a 5-min window sliding every 1 min)
Session window:    Dynamic size based on activity gaps — a "session" ends after
                   a period of inactivity (exactly the sessionization pattern from
                   `02-sql/06-advanced-sql-patterns.md`, but computed in a streaming context)
```

## Interview Traps
- "Why can't Kafka guarantee global ordering across an entire topic?" — ordering is only guaranteed WITHIN a single partition; a topic with multiple partitions has no cross-partition ordering guarantee, which is why keying by a meaningful field (customer_id) matters when per-entity order needs preserving.
- "How do you handle late-arriving data in a streaming aggregation?" — watermarking, explicitly trading some completeness for the ability to finalize window results in bounded time.
- "Exactly-once processing — how do you actually achieve it in practice?" — at-least-once delivery + idempotent processing logic (MERGE/UPSERT keyed on a unique ID) is the standard pragmatic approach, rather than relying purely on end-to-end exactly-once infrastructure guarantees.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The one who shares knowledge without fear of being surpassed becomes the true guide."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
