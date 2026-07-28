# 4. Databases Fundamentals

## RDBMS Internals — How a query actually executes
```
SQL query text
     │
Parser (syntax check) → Query Optimizer (picks best execution plan using statistics)
     │
Execution Engine (reads data via storage engine, applies filters/joins/aggregations)
     │
Storage Engine (B-Tree indexes, heap/pages on disk, buffer cache in memory)
     │
Result set returned
```
This is why `EXPLAIN ANALYZE` matters — it shows you the *actual plan* the optimizer chose, so you can tell if it's doing a full table scan vs using an index.

## ACID Properties (transactional guarantees)
| Property | Meaning | Example |
|---|---|---|
| **Atomicity** | Transaction is all-or-nothing | Bank transfer: debit + credit both happen, or neither |
| **Consistency** | DB moves from one valid state to another (constraints hold) | Foreign key can't point to a non-existent row |
| **Isolation** | Concurrent transactions don't interfere | Two people booking the last seat — only one succeeds |
| **Durability** | Once committed, survives a crash | Power failure right after commit doesn't lose the data |

### Isolation Levels (from weakest to strongest)
```
Read Uncommitted → Read Committed → Repeatable Read → Serializable
(dirty reads possible)                                (fully isolated, slowest)
```
Most databases default to **Read Committed** (Postgres, SQL Server) or **Repeatable Read** (MySQL/InnoDB) as a practical tradeoff between consistency and performance.

## CAP Theorem (distributed systems fundamental)
A distributed data store can only fully guarantee **2 of 3**:
- **Consistency** — every read gets the most recent write
- **Availability** — every request gets a (non-error) response
- **Partition Tolerance** — system keeps working despite network splits between nodes

Since partition tolerance is non-negotiable in any real distributed system, the actual choice is **CP vs AP**:
- **CP systems** (e.g., HBase, MongoDB in strong-consistency mode) — sacrifice availability during a partition to guarantee consistency.
- **AP systems** (e.g., Cassandra, DynamoDB by default) — sacrifice strict consistency (offer "eventual consistency") to stay available.

## Indexing — Deep Dive
- **B-Tree index** (default in most RDBMS) — balanced tree, great for equality (`=`) and range (`<`, `>`, `BETWEEN`) queries, and sorting.
- **Hash index** — O(1) equality lookups, but no range query support.
- **Bitmap index** — efficient for low-cardinality columns (e.g., `status IN ('active','inactive')`), common in data warehouses (Oracle, Redshift).
- **Composite index** — index on multiple columns; **column order matters** — put equality-filter columns first, then range-filter columns, then sort columns.
- **Covering index** — includes all columns needed by a query so the engine never touches the base table (index-only scan).
- **Clustered vs Non-clustered**: Clustered index physically orders the table's rows on disk by the indexed column (only one per table); non-clustered is a separate structure pointing back to rows (can have many).

## NoSQL Database Types

| Type | Data Model | Example DBs | Best For |
|---|---|---|---|
| **Document** | JSON-like nested documents | MongoDB, CouchDB | Flexible/evolving schemas, nested data |
| **Key-Value** | Simple key → value | Redis, DynamoDB | Caching, session store, ultra-low-latency lookups |
| **Wide-Column** | Rows with dynamic columns, grouped by column families | Cassandra, HBase | High write throughput, time-series, multi-datacenter |
| **Graph** | Nodes + edges | Neo4j, Amazon Neptune | Relationship-heavy data (social networks, fraud rings, recommendations) |

## SQL vs NoSQL — Decision Framework
```
Need strong transactional guarantees + relationships?      -> SQL/RDBMS
Need flexible/evolving schema, nested JSON-like data?       -> Document (MongoDB)
Need sub-millisecond key lookups at massive scale?           -> Key-Value (Redis/DynamoDB)
Need to write huge volumes fast, query by key/time range?    -> Wide-Column (Cassandra)
Need to traverse deep relationships (friends-of-friends)?    -> Graph (Neo4j)
```

## Replication & Sharding (scaling databases)
- **Replication**: copy data across multiple nodes for fault tolerance and read scaling.
  - *Primary-Replica (Master-Slave)*: writes go to primary, reads can be served from replicas.
  - *Multi-primary*: multiple nodes accept writes (more complex conflict resolution).
- **Sharding**: split data horizontally across servers by a shard key (e.g., `customer_id % 4`) — scales writes, but cross-shard joins/queries become harder.

## Connection Pooling
Opening a new DB connection is expensive. Production systems use a **connection pool** (e.g., PgBouncer for Postgres, HikariCP for Java) to reuse a fixed set of open connections across many requests/pipeline tasks — critical when hundreds of parallel Airflow tasks hit the same DB.

## Interview Traps
- CAP theorem: don't say "you can only ever have 2" without the partition-tolerance caveat — interviewers want to hear that partition tolerance is mandatory in practice, so it's really a CP vs AP tradeoff.
- Isolation levels: know that higher isolation = more locking = lower concurrency/throughput.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Knowledge shared freely returns multiplied — teach what you learn, and you will learn it twice as deeply."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
