# 4. Spark Performance Tuning — Real Production Scenarios

## Diagnosing a Slow Spark Job — The Spark UI (your #1 debugging tool)
Every Spark job exposes a web UI (accessible while running, or via history server after completion) showing: Stages (how long each took, how much data shuffled), Tasks within each stage (are they evenly sized, or is one task taking way longer — a skew signal), SQL query plan (the actual physical plan Catalyst chose), and Storage (what's cached and how much memory it's using). **Always start diagnosing a slow job here before guessing.**

## Data Skew — The #1 Real-World Spark Performance Problem
```
Symptom: 199 tasks in a stage finish in 2 seconds each, but 1 task takes 10 minutes.
Cause: one partition/key has FAR more data than others (e.g., a "region" column where
       90% of orders are from one mega-city, and a groupBy/join is keying on region).
```
**Fixes**:
```python
# Fix 1: Salting — add randomness to the skewed key to spread it across more partitions
from pyspark.sql import functions as F
df = df.withColumn("salted_key", F.concat(df.region, F.lit("_"), (F.rand() * 10).cast("int")))
# Aggregate on salted_key first, then combine the salted partial results afterward

# Fix 2: Broadcast join — if one side of a join is small, broadcast it to avoid shuffling the huge side
from pyspark.sql.functions import broadcast
result = huge_orders_df.join(broadcast(small_regions_df), on="region_id")

# Fix 3: Adaptive Query Execution (AQE) — let Spark detect and handle skew automatically (Spark 3.0+)
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
```
**Real scenario**: an e-commerce company's daily sales-by-city job routinely took 3x longer than expected — the Spark UI revealed one task (the capital city, with disproportionately more orders) taking 8x longer than every other task. Salting the join key cut the job's runtime by more than half.

## Shuffle Optimization — Reducing the Most Expensive Operation
```python
# BAD: repartitioning unnecessarily creates an expensive shuffle for no benefit
df = df.repartition(200)  # only do this if you have a SPECIFIC reason (e.g., before a big join)

# GOOD: coalesce reduces partitions WITHOUT a full shuffle (when reducing, not increasing)
df = df.coalesce(10)  # cheaper than repartition when going from many partitions to fewer

# Tune shuffle partition count based on data size (default 200 is often wrong for your data)
spark.conf.set("spark.sql.shuffle.partitions", "50")  # smaller for smaller datasets, avoiding
                                                          # excessive tiny-task overhead
```
**Real guidance**: the default `spark.sql.shuffle.partitions=200` is a one-size-fits-all guess that's frequently wrong — too many partitions for a small dataset creates excessive task-scheduling overhead; too few for a huge dataset creates memory pressure and long individual tasks. Tune this based on your actual data volume (a common rule of thumb: aim for partitions around 100-200MB each).

## Caching/Persisting — When It Helps and When It Hurts
```python
df_expensive = spark.read.parquet("s3a://bucket/huge_table/").filter(...)  # expensive to compute
df_expensive.cache()  # or .persist(StorageLevel.MEMORY_AND_DISK)

df_expensive.count()  # triggers the actual caching (cache() itself is lazy!)

result1 = df_expensive.groupBy("a").count()   # reuses the cached data
result2 = df_expensive.groupBy("b").count()   # reuses the cached data again — big win

df_expensive.unpersist()  # release memory when done reusing it
```
**When caching HURTS**: caching a DataFrame that's only used ONCE wastes memory and adds overhead for no benefit — only cache when you'll genuinely reuse the same DataFrame multiple times downstream.

## Broadcast Joins — Avoiding Unnecessary Shuffles
```python
# Without broadcast: joining a 1-billion-row table to a 100-row table still
# shuffles BOTH tables across the network by default (wasteful for the huge table)

# With broadcast: the small table is copied in full to EVERY executor,
# and the huge table never needs to be shuffled at all for this join
from pyspark.sql.functions import broadcast
result = huge_df.join(broadcast(tiny_lookup_df), on="key")

# Spark often auto-detects this via a size threshold, but you can force/tune it:
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", 10 * 1024 * 1024)  # 10MB threshold
```

## Avoiding Python UDFs When a Native Function Exists (recap + why it's so important)
```python
# SLOW — row-by-row serialization between JVM and Python process for every single row
from pyspark.sql.types import DoubleType
slow_udf = F.udf(lambda amt: amt * 1.18, DoubleType())
df = df.withColumn("total", slow_udf(df.amount))

# FAST — stays entirely within the JVM's optimized Tungsten execution
df = df.withColumn("total", df.amount * 1.18)

# If a UDF is truly unavoidable, use pandas_udf (vectorized) instead of a row-by-row UDF —
# processes data in batches via Arrow, dramatically reducing serialization overhead
from pyspark.sql.functions import pandas_udf
@pandas_udf(DoubleType())
def fast_udf(amount: pd.Series) -> pd.Series:
    return amount * 1.18
```

## Small Files Problem (recap from `01-fundamentals/07-file-formats-and-storage.md`, Spark-specific angle)
```python
# Symptom: a job reading thousands of tiny files spends most of its time on
# file-open/close overhead rather than actual data processing.

# Fix: periodic compaction — read the small files, write back as fewer, larger files
df = spark.read.parquet("s3a://bucket/many_small_files/")
df.coalesce(20).write.mode("overwrite").parquet("s3a://bucket/compacted/")
```

## Memory Management — Understanding OOM (Out of Memory) Errors
```
Common causes of executor OOM errors:
1. Data skew (one partition holds far more data than the executor's memory allows)
2. Caching too much data without enough memory allocated
3. A broadcast join where the "small" table turns out to be much bigger than expected
4. Collecting too much data back to the Driver (.collect() on a huge result)

Diagnosis: check the Spark UI's "Storage" tab and executor memory metrics;
           look for a specific stage/task where memory spikes right before the failure.
```

## Real Production Tuning Checklist
```
1. Check the Spark UI FIRST — don't guess, look at actual stage/task timing
2. Look for data skew (one task dramatically slower than others in the same stage)
3. Check if unnecessary shuffles are happening (unneeded repartition, or missing broadcast joins)
4. Verify shuffle partition count is reasonable for your actual data size
5. Check for Python UDFs that could be replaced with native functions
6. Check for small-files problems if reading from many tiny source files
7. Only cache DataFrames genuinely reused multiple times, and unpersist when done
8. Enable Adaptive Query Execution (AQE) — Spark 3.0+'s automatic runtime optimization,
   often the single highest-leverage "quick win" configuration change available
```

## Interview Traps
- "A Spark job is running slower than expected — how do you diagnose it?" — always start with the Spark UI, look for stage/task-level skew, unnecessary shuffles, and memory pressure signals — this systematic approach matters more than jumping to a specific fix.
- "How would you fix a skewed join?" — be ready to explain BOTH salting (manual) and AQE's automatic skew handling (Spark 3.0+), and know when each applies.
- "When should you avoid caching a DataFrame?" — when it's only used once — caching adds memory pressure and computation overhead (materializing the cache) for zero reuse benefit.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Every complex system, like every complex mind, rewards patience over force."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
