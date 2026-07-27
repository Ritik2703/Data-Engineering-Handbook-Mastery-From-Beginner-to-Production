# 05 — Databases: The Complete A-to-Z (Beginner to Pro, World-Class Level)

The most comprehensive database module in this repo — history and evolution, every database type, internals (how they actually work under the hood), design methodology, real production company choices, and interview-ready depth. Someone with zero database knowledge should finish this able to design a database, explain WHY a company picked a specific database, and reason about scaling/consistency tradeoffs like a senior engineer.

## 📖 Learning Path

| # | File | Level | Covers |
|---|---|---|---|
| 1 | [`01-database-fundamentals-and-history.md`](./01-database-fundamentals-and-history.md) | Beginner | What a database is, decade-by-decade evolution 1970s-2026 |
| 2 | [`02-relational-databases-deep-dive.md`](./02-relational-databases-deep-dive.md) | Beginner-Intermediate | RDBMS internals, ACID, normalization, storage engines |
| 3 | [`03-nosql-databases-deep-dive.md`](./03-nosql-databases-deep-dive.md) | Intermediate | Document/Key-Value/Wide-Column/Graph, CAP theorem in practice |
| 4 | [`04-newsql-distributed-sql.md`](./04-newsql-distributed-sql.md) | Advanced | CockroachDB, Google Spanner, TiDB, YugabyteDB — the "best of both" era |
| 5 | [`05-cloud-native-databases.md`](./05-cloud-native-databases.md) | Advanced | Aurora, Cosmos DB, Spanner, serverless databases |
| 6 | [`06-vector-databases-ai-era.md`](./06-vector-databases-ai-era.md) | Advanced, Cutting-Edge | pgvector, Pinecone, Weaviate — the newest category (RAG/AI era) |
| 7 | [`07-database-design-and-modeling.md`](./07-database-design-and-modeling.md) | Intermediate-Advanced | Full schema design walkthrough, normalization vs denormalization decisions |
| 8 | [`08-indexing-storage-internals.md`](./08-indexing-storage-internals.md) | Advanced | B-Tree vs LSM-Tree, columnar internals, how a query actually reads disk |
| 9 | [`09-replication-sharding-scaling.md`](./09-replication-sharding-scaling.md) | Advanced | Every real scaling pattern, with real-world numbers |
| 10 | [`10-transactions-consistency-deep-dive.md`](./10-transactions-consistency-deep-dive.md) | Advanced | Isolation levels, distributed transactions, Raft/Paxos consensus |
| 11 | [`11-what-companies-actually-use.md`](./11-what-companies-actually-use.md) | Production | Real database choices at Amazon, Netflix, Uber, Instagram, Discord, and more |
| 12 | [`12-ddl-schema-design-queries.md`](./12-ddl-schema-design-queries.md) | Practical | DDL, constraints, indexes, partitioning — hands-on queries |
| 13 | [`case-studies/`](./case-studies/) | Production | Full real-world database architecture designs |
| 14 | [`interview-questions.md`](./interview-questions.md) | All levels | 50+ questions spanning every topic in this module |

## 🧠 How This Module Is Different
Most tutorials teach "here's MongoDB syntax" without ever explaining **why** MongoDB exists, what problem it solves that Postgres doesn't, or why a company would pick one over the other. This module is built backwards from that gap — every database type is introduced by first explaining **the exact production pain point that caused it to be invented**, then how it works, then who actually uses it and why.

## 🗺️ Suggested Path
```
Total beginner:        01 -> 02 -> 07 -> 08 (get the RDBMS foundation rock solid first)
NoSQL / modern:         03 -> 04 -> 05 -> 06
Scaling & production:   09 -> 10 -> 11
Design practice:        07 + 12 + case-studies/
Interview prep:         11 + interview-questions.md
```
