# 6. Big Data Fundamentals

## Why "Big Data" needed new tools
Traditional single-machine databases hit limits when data volume exceeds what one machine's disk/RAM/CPU can handle. The solution: **distribute** data and computation across many cheap commodity machines instead of buying one giant expensive machine (scale-out vs scale-up).

## The 3 V's (and beyond) of Big Data
- **Volume** — terabytes/petabytes of data
- **Velocity** — speed of data arrival (streaming events per second)
- **Variety** — structured, semi-structured, unstructured mixed together
- *(later added)* **Veracity** — data quality/trustworthiness, **Value** — actual business usefulness

## Distributed Computing Core Concepts

### Partitioning
Splitting data into chunks distributed across nodes/workers so each processes a subset in parallel.
```
1 TB dataset → split into 100 partitions of 10GB each → 100 workers each process 1 partition in parallel
```

### Replication
Copying data across multiple nodes so a node failure doesn't lose data (HDFS default: 3x replication).

### Shuffle
The expensive step where data must move between nodes to complete an operation (e.g., a `GROUP BY` or `JOIN` needs all rows with the same key on the same node) — shuffles are usually the biggest performance bottleneck in Spark/Hadoop jobs.

### Data Skew
When one partition/key has disproportionately more data than others, causing one worker to become a bottleneck while others sit idle. Fixed via salting keys, repartitioning, or broadcast joins for small tables.

## Hadoop Ecosystem History (know this for legacy-system interviews)
```
2003-04: Google publishes GFS + MapReduce papers
2006: Hadoop born at Yahoo (HDFS + MapReduce, open-source implementation)
2008-2012: Hive (SQL-on-Hadoop), HBase (NoSQL on HDFS), Pig added
2014: Spark overtakes MapReduce — in-memory processing, much faster for iterative workloads
2015+: Cloud object storage (S3/ADLS/GCS) starts replacing HDFS as the storage layer
Today: Spark (via Databricks/EMR/Dataproc/Synapse) is the processing standard;
       raw Hadoop/MapReduce mostly seen in legacy on-prem enterprise systems
```

### MapReduce (the original model, still worth understanding conceptually)
```
Map phase: transform each record independently (e.g., emit (word, 1) for each word in a document)
     ↓
Shuffle phase: group all values by key across the cluster (all "1"s for word "the" go to same reducer)
     ↓
Reduce phase: aggregate values per key (sum counts -> word frequency)
```
Slow because every phase writes intermediate results to disk. Spark's key innovation: keep intermediate data **in memory** across stages when possible.

## Spark Internals

### Core Architecture
```
Driver Program (your code, builds the execution plan)
     │
Cluster Manager (YARN / Kubernetes / Spark Standalone) — allocates resources
     │
Executors (worker processes on cluster nodes — actually run the tasks)
```

### Key Concepts
- **RDD (Resilient Distributed Dataset)**: low-level distributed collection abstraction — rarely used directly today, but everything else is built on it.
- **DataFrame/Dataset API**: higher-level, optimized via **Catalyst Optimizer** (query planning) and **Tungsten** (memory/CPU efficiency) — this is what you use in practice.
- **Lazy evaluation**: transformations (`filter`, `select`, `groupBy`) build a plan but don't execute until an **action** (`show`, `count`, `write`) triggers it — lets Spark optimize the whole chain before running.
- **Partitions**: a Spark DataFrame is internally split into partitions distributed across executors — the unit of parallelism.
- **Wide vs Narrow transformations**: narrow (e.g., `filter`, `map`) = no shuffle needed, data stays on the same partition; wide (e.g., `groupBy`, `join`) = requires a shuffle across the network.

### Common Spark Performance Levers
- Avoid unnecessary shuffles — use `broadcast()` for joining a small table against a huge one (avoids shuffling the huge table).
- Repartition wisely — too few partitions underutilizes cluster, too many creates overhead from task scheduling.
- Cache/persist a DataFrame only if reused multiple times downstream — otherwise it wastes memory.
- Use columnar file formats (Parquet) — enables predicate/column pruning (skip reading irrelevant data entirely).

## Streaming Fundamentals

### Micro-batch (Spark Structured Streaming)
Processes small batches of data at short, fixed intervals — simpler programming model (same DataFrame API as batch), slight latency (seconds).

### True Streaming (Flink, Kafka Streams)
Processes each event as it arrives — lowest latency, but more complex (state management, watermarks for late/out-of-order events).

### Key Streaming Concepts
- **Watermark**: a threshold telling the system "how late can an event be and still get counted" — handles out-of-order event arrival.
- **Windowing**: grouping streaming events into time buckets (tumbling, sliding, session windows) for aggregation.
- **Exactly-once vs At-least-once vs At-most-once**: delivery/processing guarantees — exactly-once is hardest to guarantee and usually needs idempotent writes + checkpointing.

## Interview Traps
- "Why is Spark faster than MapReduce?" → in-memory computation across stages + Catalyst/Tungsten optimizations + lazy evaluation building a globally optimized plan, not just "it uses RAM."
- Data skew is one of the most common real-world Spark performance issues asked about in senior interviews — know at least one mitigation (salting, broadcast join, repartition).
