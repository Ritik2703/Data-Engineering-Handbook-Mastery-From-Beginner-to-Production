# Project 4: Real-Time Streaming Analytics — Kafka + Spark Structured Streaming + Power BI

## Business Scenario
A logistics company wants a LIVE operations dashboard showing delivery performance by region, updating within ~1 minute, directly connecting the streaming concepts from module 06 to the visualization layer in module 09.

## Architecture
```
[Delivery tracking app] --GPS/status events--> Kafka topic: delivery_events
                                                        |
                                            Spark Structured Streaming
                                            (windowed aggregation, watermarking
                                             for late data -- recap 06-big-data/05)
                                                        |
                                            Write to a fast-serving sink:
                                            Azure SQL Database / a Delta table
                                            refreshed every minute
                                                        |
                                            Power BI (DirectQuery mode, recap
                                            09-visualization/04) -- dashboard
                                            auto-refreshes against the live sink
```

## Stage 1: Spark Structured Streaming Job
```python
# streaming_delivery_metrics.py -- reuses the pattern from
# 06-big-data/05-streaming-fundamentals.md
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType

event_schema = StructType([
    StructField("delivery_id", StringType()),
    StructField("region", StringType()),
    StructField("status", StringType()),
    StructField("event_time", TimestampType()),
    StructField("delay_minutes", DoubleType()),
])

stream_df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "broker1:9092")
    .option("subscribe", "delivery_events")
    .load()
)

parsed_df = stream_df.select(
    F.from_json(F.col("value").cast("string"), event_schema).alias("data")
).select("data.*")

# Windowed aggregation with watermarking for realistic, unreliable network
# conditions (recap 06-big-data/05 and the IoT case study in 11-system-design)
windowed_metrics = (
    parsed_df
    .withWatermark("event_time", "5 minutes")
    .groupBy(
        F.window("event_time", "1 minute"),
        F.col("region")
    )
    .agg(
        F.count("delivery_id").alias("total_deliveries"),
        F.avg("delay_minutes").alias("avg_delay"),
        F.sum(F.when(F.col("status") == "delayed", 1).otherwise(0)).alias("delayed_count"),
    )
)

def write_to_sql(batch_df, batch_id):
    """Foreach-batch sink writing to Azure SQL for Power BI DirectQuery."""
    (
        batch_df.write
        .format("jdbc")
        .option("url", "jdbc:sqlserver://myserver.database.windows.net:1433;database=OpsDB")
        .option("dbtable", "live_delivery_metrics")
        .mode("append")
        .save()
    )

query = (
    windowed_metrics.writeStream
    .foreachBatch(write_to_sql)
    .outputMode("update")
    .trigger(processingTime="1 minute")
    .option("checkpointLocation", "/mnt/checkpoints/delivery_metrics")
    .start()
)
query.awaitTermination()
```

## Stage 2: The Serving Table Design
```sql
CREATE TABLE live_delivery_metrics (
    window_start DATETIME2,
    window_end DATETIME2,
    region VARCHAR(50),
    total_deliveries INT,
    avg_delay FLOAT,
    delayed_count INT,
    INDEX idx_region_window (region, window_start)  -- supports the exact
                                                       -- query pattern Power
                                                       -- BI's DirectQuery will use
);
```

## Stage 3: Power BI — DirectQuery Live Dashboard
```dax
-- DAX measures against the live streaming sink (recap 09-visualization/05)
Total Deliveries (Last Hour) =
CALCULATE(
    SUM(live_delivery_metrics[total_deliveries]),
    live_delivery_metrics[window_start] >= NOW() - TIME(1,0,0)
)

Delay Rate % =
DIVIDE(SUM(live_delivery_metrics[delayed_count]), SUM(live_delivery_metrics[total_deliveries]))
```
```
Report configured with DirectQuery mode (not Import) specifically because
the requirement is genuine near-live data -- recap the explicit tradeoff
reasoning from 09-visualization/04: DirectQuery accepts a real performance
cost per interaction in exchange for always-current data, the right
choice for THIS specific dashboard's stated requirement.

Page auto-refresh set to 1 minute, matching the streaming job's own
micro-batch trigger interval -- deliberately aligned so the dashboard
never refreshes faster than genuinely new data could exist.
```

## What This Project Demonstrates
```
Kafka to Spark Structured Streaming with proper watermarking for
realistic late/out-of-order data, a foreachBatch sink pattern writing
to a relational serving table, and a Power BI DirectQuery dashboard
correctly matched to a genuine real-time requirement -- directly
applying the latency-requirement-driven design reasoning from
11-system-design throughout.
```


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"A journey mapped with honesty travels further than one rushed without direction."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
