# 9. What Real Companies Use — Big Data Stacks

## Netflix
- **Apache Iceberg** — created by Netflix specifically to solve their own petabyte-scale data lake reliability problems (see file 6); now their (and increasingly the industry's) standard lakehouse table format.
- **Spark** — core batch processing engine across their massive S3-based data lake.
- **Kafka + Flink** — real-time data pipelines (viewing events, operational monitoring) at enormous scale across global regions.
- **Why**: Netflix's defining need is petabyte-scale reliable storage with a genuinely open, multi-engine-compatible format (since different internal teams use different query engines against the same underlying data) — driving their investment in and creation of Iceberg specifically.

## Uber
- **Apache Hudi** — created by Uber specifically for their high-frequency trip-record upsert problem (see file 6).
- **Spark** — core batch and streaming (via Structured Streaming) processing.
- **Kafka** — the backbone for virtually all of Uber's real-time event data (trip requests, location pings, driver status changes).
- **Presto** (also significantly contributed to/used by Uber) — interactive SQL querying across their massive data lake for analyst/ad-hoc use cases.
- **Why**: Uber's trip data is CONSTANTLY updated in near-real-time throughout a ride's lifecycle, driving their need for (and creation of) an incremental-upsert-optimized lake format that didn't exist adequately elsewhere at the time.

## LinkedIn
- **Kafka** — LinkedIn literally CREATED Kafka (2011) to solve their own internal need for a unified, high-throughput log/event pipeline connecting hundreds of internal systems (it was open-sourced and has since become the de facto industry standard streaming platform).
- **Samza** — a stream processing framework also created at LinkedIn, tightly integrated with Kafka.
- **Spark** — for large-scale batch analytics (recommendation systems, feed ranking data pipelines).
- **Why**: LinkedIn's professional network graph and activity feed generate enormous, continuous event volume across countless microservices — Kafka's creation was driven directly by needing ONE consistent way for all these systems to publish/subscribe to events reliably at scale.

## Airbnb
- **Spark + Airflow** — Airbnb also created **Airflow** (2014) specifically to orchestrate their own growing complexity of interdependent data pipelines — since open-sourced and now the industry-standard orchestrator.
- **Druid** — for real-time analytics dashboards requiring fast aggregation queries over recent data (a different tool than their core Spark batch pipelines, chosen specifically for its low-latency aggregation strength).
- **Why**: as Airbnb's number of scheduled data pipelines grew into the hundreds, manually tracking dependencies/schedules/failures became unmanageable — directly motivating Airflow's creation as an internal tool before its open-source release.

## Meta (Facebook)
- **Presto** — created by Facebook (2012) specifically for fast interactive SQL queries across their petabyte-scale Hadoop-based data warehouse, where Hive's MapReduce-based execution was too slow for analyst-facing ad-hoc queries.
- **Spark** — extensively used for large-scale batch ETL and ML feature pipelines.
- **RocksDB** (also Meta-created) — an embeddable key-value store used as a building block within many of Meta's own larger distributed systems (including MyRocks, mentioned in `05-databases/11-what-companies-actually-use.md`).
- **Why**: Meta's scale consistently outpaced what existing open-source tools could handle adequately, driving them to build (and typically open-source) new purpose-built tools rather than force-fit existing ones — a recurring theme across nearly every major tech company's big data journey.

## Spotify
- **Google Cloud Dataflow (Apache Beam)** and **BigQuery** — Spotify is notably GCP-native, using Dataflow for both batch and streaming processing (recommendation pipelines, listening history aggregation) with a single unified Beam programming model.
- **Scio** — a Scala API for Apache Beam, created by Spotify to make Beam more ergonomic for their engineering teams.
- **Why**: choosing Apache Beam's unified batch+streaming programming model let Spotify's engineers write pipeline logic once and run it in either batch or streaming mode, reducing the code-duplication burden of maintaining separate batch and streaming codebases for similar logic.

## The Recurring Pattern (again, worth internalizing deeply)
```
Nearly EVERY major big data technology in production use today (Kafka, Airflow,
Presto, Iceberg, Hudi, RocksDB) was originally built INTERNALLY at a specific
company to solve THEIR specific scaling pain point, and later open-sourced —
often becoming a broader industry standard used by companies with completely
different business models than the original creator.

This tells you something important: the "best" tool for YOUR company's specific
problem might not exist yet as an off-the-shelf product — recognizing a genuine
gap and building (or adapting) the right solution IS a core senior data
engineering skill, not just knowing existing tools.
```

## Interview Traps
- "Why did LinkedIn create Kafka instead of using an existing message queue?" — existing message queues at the time didn't handle LinkedIn's specific need for high-throughput, durable, replayable event logs that MULTIPLE independent internal systems could consume at their own pace — a genuinely new requirement pattern that motivated new tooling.
- Practice explaining the "why" behind at least 3-4 of these company/tool pairings in your own words — this consistently signals deeper understanding than simply naming which company uses which tool.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Right effort, sustained without anxiety about the fruit, is the truest form of skill."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
