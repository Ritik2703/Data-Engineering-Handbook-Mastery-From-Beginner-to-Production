# 11. What Real Companies Actually Use (Production Database Choices)

> Note: large companies use MANY databases internally for different services — the entries below highlight well-documented, notable choices (from public engineering blogs/talks), not an exhaustive or exclusive list. Company architectures also evolve over time.

## Amazon
- **DynamoDB** — born directly from Amazon's own 2007 Dynamo paper; powers the shopping cart and many high-scale internal services needing always-available, low-latency key-value access.
- **Aurora** — used extensively for relational workloads across Amazon's own retail systems, being AWS's own flagship managed relational database.
- **Redshift** — internal analytics/BI workloads at large scale.
- **Why**: Amazon's scale (hundreds of millions of customers, Black Friday-level traffic spikes) demands databases that prioritize availability above all — a shopping cart being briefly "eventually consistent" is far preferable to it being unavailable.

## Netflix
- **Cassandra** (and its EVCache/Cassandra-based systems) — extensively used for viewing history, user preferences, and operational metadata across global regions, prized for its multi-datacenter replication and no-single-point-of-failure design.
- **MySQL** — for certain more traditional relational needs.
- **Delta Lake / Iceberg-style lakehouse formats** — Netflix actually CREATED Apache Iceberg (2018) specifically to solve their own petabyte-scale data lake reliability problems.
- **Why**: Netflix's defining requirement is global availability and massive read/write scale for a service that must never appear "down" to a user browsing content, making AP-style systems (Cassandra) a natural fit for much of their data.

## Uber
- **MySQL** (heavily customized, via their own "Schemaless" storage layer built on top of MySQL) — historically core to trip/user data.
- **Apache Hudi** — Uber CREATED this project specifically to solve their own need for efficient incremental upserts into their massive data lake (constantly updating trip records as they progress through states).
- **Cassandra/Docstore** (their own document store) — for various high-throughput operational services.
- **Why**: Uber's trip data is constantly being updated in near-real-time (a trip's status changes many times per ride) at enormous scale, driving their investment in incremental-upsert-optimized lake technology (Hudi) that didn't exist elsewhere yet.

## Instagram / Meta (Facebook)
- **PostgreSQL** — Instagram famously runs (and has publicly discussed) a heavily sharded PostgreSQL architecture for core data, valuing Postgres's reliability, extensibility (JSON support), and rich feature set.
- **MyRocks** (Meta's own RocksDB-based MySQL storage engine) — Meta built this specifically to get LSM-tree-style write efficiency (see file 8) with MySQL's familiar interface, at their enormous internal scale.
- **TAO** (Meta's own distributed graph-data-caching layer, sitting on top of MySQL) — purpose-built for the social graph's specific read patterns (friends, likes, comments).
- **Why**: Meta's social graph has extremely specific, extremely high-volume read patterns that no off-the-shelf database perfectly served, driving them to build custom layers (TAO, MyRocks) on top of proven relational foundations rather than adopting NoSQL wholesale.

## Discord
- **Cassandra**, later migrated significant workloads to **ScyllaDB** (a Cassandra-compatible, C++-rewritten database) after hitting performance/operational limits at their message-storage scale (they've published detailed, widely-read engineering blog posts about this exact migration).
- **Why**: storing trillions of chat messages with high write throughput and horizontal scalability requirements matches wide-column store strengths precisely; their migration to ScyllaDB was driven by wanting the same data model with better raw performance and lower operational overhead at their specific scale.

## Airbnb
- **MySQL** — core transactional data (bookings, listings, payments).
- **Druid** — for real-time analytics dashboards needing fast aggregation over recent data.
- **Why**: a hybrid approach — reliable relational storage for the transactional core, with a purpose-built OLAP-style system for the specific real-time analytics use case that a general warehouse wouldn't serve fast enough.

## Spotify
- **PostgreSQL, Cassandra, and Bigtable** (being GCP-hosted) — a genuinely mixed environment reflecting different microservices' different needs (user library data, play history, real-time recommendation features each favor different data models).
- **Why**: a large microservices architecture naturally leads to "the right database for each specific service's access pattern" rather than one single company-wide database choice — a realistic pattern at most large tech companies.

## Modern AI-Era Companies (2024-2026 pattern)
- Companies building RAG/AI-search products increasingly adopt **pgvector** (if already Postgres-based) or **Pinecone/Weaviate** (if building a dedicated AI search product) alongside their existing operational databases — see file 6.
- **Snowflake/BigQuery/Databricks** remain the dominant analytics warehouse choices at most product companies doing traditional BI, now increasingly ALSO hosting vector search capabilities natively (Snowflake Cortex, BigQuery vector search) as warehouses race to absorb the AI-era vector workload rather than cede it entirely to dedicated vector databases.

## The Real Pattern Across All These Companies
```
1. Start with a reliable, well-understood relational database (usually MySQL or Postgres)
2. As specific access patterns hit real scale limits, adopt a PURPOSE-BUILT system for
   THAT specific pattern (Cassandra for write-heavy logs, Redis for caching, a graph DB
   for relationship traversal) — rather than trying to force one database to do everything
3. At the very largest scale, some companies build/heavily customize their OWN systems
   (Meta's TAO/MyRocks, Uber's Hudi, Amazon's Dynamo) because no existing off-the-shelf
   tool perfectly fit their exact scale/access pattern — and often OPEN-SOURCE these
   innovations afterward, which is why so many modern database technologies trace
   directly back to a specific company's specific scaling pain point (see file 1's history)
```
This is precisely why this module teaches concepts and tradeoffs first, tool-by-tool — because the real skill senior engineers and interviewers value is the judgment to pick (or build) the RIGHT tool for a SPECIFIC access pattern, not loyalty to any single database technology.

## Interview Traps
- "Which database is the best?" has no correct single answer — the strong answer is always "it depends on the access pattern, consistency needs, and scale," backed by a specific real example like the ones above.
- Being able to name WHY a specific company chose/built a specific technology (not just that they use it) signals genuine understanding rather than name-dropping — practice explaining the "why" for at least 2-3 of the examples above in your own words.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The disciplined mind finds opportunity exactly where the restless mind finds only obstacles."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
