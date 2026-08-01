# 06 — Big Data: Beginner to MNC Production Engineer

The complete Big Data module — from "what even IS big data and why does Hadoop exist" all the way to tuning a production Spark job that's mysteriously slow, understanding streaming architectures, and knowing exactly what Netflix/Uber/LinkedIn run internally.

## 📖 Learning Path

| # | File | Level | Covers |
|---|---|---|---|
| 1 | [`01-what-is-big-data.md`](./01-what-is-big-data.md) | Beginner | The 3 V's, why single machines stopped being enough, history |
| 2 | [`02-hadoop-ecosystem-deep-dive.md`](./02-hadoop-ecosystem-deep-dive.md) | Beginner-Intermediate | HDFS, MapReduce, YARN, Hive internals |
| 3 | [`03-spark-architecture-deep-dive.md`](./03-spark-architecture-deep-dive.md) | Intermediate | Driver/Executor, RDD vs DataFrame, Catalyst, Tungsten, DAG |
| 4 | [`04-spark-performance-tuning.md`](./04-spark-performance-tuning.md) | Advanced | Partitioning, shuffle, skew, caching, broadcast joins — real production tuning |
| 5 | [`05-streaming-fundamentals.md`](./05-streaming-fundamentals.md) | Advanced | Kafka deep dive, Spark Structured Streaming, Flink, exactly-once semantics |
| 6 | [`06-lakehouse-table-formats.md`](./06-lakehouse-table-formats.md) | Advanced | Delta Lake, Apache Iceberg, Apache Hudi — deep internals |
| 7 | [`07-distributed-computing-concepts.md`](./07-distributed-computing-concepts.md) | Intermediate-Advanced | Cluster managers (YARN/Kubernetes/Mesos), the MapReduce paradigm |
| 8 | [`08-big-data-on-cloud.md`](./08-big-data-on-cloud.md) | Advanced | EMR, Databricks, Dataproc, Synapse Spark Pools compared |
| 9 | [`09-what-companies-use.md`](./09-what-companies-use.md) | Production | Netflix, Uber, LinkedIn, Airbnb, Meta big data stacks |
| 10 | [`10-pyspark-code-examples.md`](./10-pyspark-code-examples.md) | Practical | Extensive, runnable-style PySpark patterns for real scenarios |
| 11 | [`11-scala-for-spark.md`](./11-scala-for-spark.md) | Practical | Why Spark is written in Scala, reading Scala Spark code, when it genuinely matters vs PySpark |
| — | [`case-studies/`](./case-studies/) | Production | Full real-world big data pipeline architecture |
| — | [`interview-questions.md`](./interview-questions.md) | All levels | 40+ Q&A across the whole module |

## 🎯 What "MNC Production Level" Means Here
Every file goes beyond "here's the syntax" to cover:
- **Why** this technology exists (what specific pain point it solves)
- **How** it actually works internally (not just how to call the API)
- **When it breaks in production** and how to diagnose/fix it
- **What real companies** run at scale and why they chose it

## 🗺️ Suggested Path
```
Total beginner:      01 -> 02 -> 07 -> 03
Already know basics: 04 -> 05 -> 06
Cloud-focused:        08 -> 09
Interview prep:       09 + interview-questions.md + case-studies/
```


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The truest wealth is a mind that remains steady in both gain and loss."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
