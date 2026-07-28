# 1. Database Fundamentals & History (1970s → 2026)

## What Is a Database, Really?
A database is organized, persistent storage that lets you **reliably** store, retrieve, and query data — "reliably" is the key word. A text file can "store data" too, but it can't guarantee two people editing it simultaneously won't corrupt it, can't efficiently find one record among a billion without reading everything, and can't guarantee your data survives a power outage mid-write. Every database, from the oldest to the newest, exists to solve some combination of these reliability problems.

## The Full Timeline — Why Each Era's Database Was Invented

### 1970s — The Relational Model is Born
**Problem it solved**: Before relational databases, data was stored in rigid hierarchical or network structures tightly coupled to how an application accessed it — changing the application meant restructuring the whole data storage. Edgar Codd (IBM) proposed the **relational model** in 1970: store data in simple tables (relations), let a declarative query language (which became SQL) ask questions without caring how data is physically stored.
**What emerged**: IBM System R, Oracle (1979, first commercial SQL RDBMS), later Sybase, Informix.

### 1980s-1990s — RDBMS Becomes the Default Enterprise Standard
**Problem it solved**: Businesses needed reliable transactional systems — banking, inventory, order processing — where correctness (ACID) mattered more than raw speed. This era gave us **Oracle Database, Microsoft SQL Server, IBM Db2, and MySQL (1995)** and **PostgreSQL (1996, from the academic POSTGRES project)** — nearly all still dominant today. ETL tools (Informatica 1993, SSIS-predecessor DTS with SQL Server 7 in 1998) emerged alongside to move data between these systems into early data warehouses (Teradata, 1983 — one of the first purpose-built MPP analytical database).

### Early-Mid 2000s — The Internet Scale Problem (Birth of NoSQL)
**Problem it solved**: Companies like Google, Amazon, and Facebook hit a wall — relational databases, built for single-machine reliability and strict consistency, couldn't cheaply scale to **billions of users across thousands of commodity servers**. Google published the **Bigtable** paper (2006) and **GFS** (2003); Amazon published the **Dynamo** paper (2007) describing a highly-available key-value store built for their shopping cart service. These papers directly inspired the **NoSQL movement**: HBase (Bigtable-inspired), Cassandra (2008, Dynamo+Bigtable hybrid, born at Facebook), MongoDB (2009, document model for developer flexibility), Redis (2009, in-memory key-value).
**Why "NoSQL" specifically**: these systems traded strict consistency and rigid schemas for **horizontal scalability and availability** — a direct, deliberate tradeoff (see CAP theorem in file 3) that made sense for social media feeds and shopping carts, where showing slightly stale data momentarily is a fine tradeoff for never going down.

### 2006-2014 — Big Data & Hadoop Ecosystem
**Problem it solved**: Storing and processing petabytes of semi-structured/unstructured web data far beyond what any single relational database could handle. Hadoop (2006, open-source implementation of Google's papers) brought HDFS + MapReduce; Hive (2010) let analysts query it with SQL-like syntax. This isn't a "database" in the traditional sense but fundamentally shaped how the next generation of databases thought about distributed storage.

### 2010s — Cloud-Native Databases Emerge
**Problem it solved**: Running your own database servers (provisioning, patching, scaling, backups) was operationally expensive and slow to scale. Amazon Aurora (2014) reimagined MySQL/Postgres-compatible databases with storage/compute separated and cloud-native replication; Google Spanner (2012, published paper; later offered as a cloud service) solved **globally distributed, strongly-consistent transactions** — previously thought nearly impossible at planet-scale — using synchronized atomic clocks (TrueTime). Snowflake (2014) reimagined the data warehouse with fully separated storage/compute billing.

### Mid-2010s — NewSQL: "We Want NoSQL's Scale AND SQL's Consistency"
**Problem it solved**: Companies loved NoSQL's horizontal scalability but missed SQL's ACID guarantees and familiar query language. **NewSQL** databases (CockroachDB 2015, TiDB 2016, YugabyteDB 2016) deliver distributed horizontal scaling like NoSQL, while still supporting full SQL and ACID transactions — a genuine "best of both worlds" architectural achievement using consensus algorithms (Raft/Paxos) under the hood.

### Late 2010s-2020s — Lakehouse & Table Formats
**Problem it solved**: Data lakes (cheap, flexible S3/ADLS storage) lacked the ACID guarantees and reliability of a database. Delta Lake (2019, Databricks), Apache Iceberg (2018, Netflix), Apache Hudi (2016, Uber) added transactional guarantees, schema enforcement, and time travel directly on top of cheap object storage — blurring the line between "data lake" and "database."

### 2020s-2026 — The AI/Vector Era
**Problem it solved**: Modern AI applications (semantic search, RAG — Retrieval-Augmented Generation, recommendation engines) need to search by **meaning/similarity** (via embedding vectors), not exact matches. This need birthed dedicated **vector databases** (Pinecone 2019, Weaviate 2019, Milvus 2019) and vector **extensions** to existing databases (`pgvector` for Postgres, 2021) — the newest major category, seeing explosive adoption 2023-2026 as every company adds AI-powered search/chat features. See file 6 for full depth.

## The Big Picture Pattern (helps you understand ANY new database that emerges)
```
Every new database category was invented because:
  Existing tools + a NEW real-world scale/consistency/data-shape problem = gap
  Someone built a new tool specifically to close that gap
  That tool became mainstream once enough companies hit the same problem

This pattern will repeat again — expect new database categories to keep emerging
as new classes of applications (AI agents, IoT at planetary scale, quantum-adjacent
workloads) hit new limits of today's tools.
```

## Try It Yourself (conceptual)
1. Explain in your own words why Amazon needed Dynamo instead of just using a bigger Oracle server for their shopping cart in 2007.
2. Why would Google need Spanner's synchronized atomic clocks specifically — what problem does that solve that a normal distributed database can't?
3. Why did vector databases only become mainstream in 2023+ rather than, say, 2015?


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Duty done well, without craving credit, is its own quiet reward."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
