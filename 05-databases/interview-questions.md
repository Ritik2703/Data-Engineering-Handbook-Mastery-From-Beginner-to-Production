# Database Interview Questions — 50+ Spanning the Entire Module

## Fundamentals & History

**Q1. What is a database and why not just use files?**
> Files can't reliably guarantee concurrent-write safety, efficient querying without reading everything, or crash-durability. Databases solve these via transactions, indexing, and write-ahead logging.

**Q2. Why did NoSQL databases emerge in the mid-2000s?**
> Companies like Google/Amazon/Facebook hit internet-scale problems that traditional single-machine RDBMS couldn't cheaply solve — they needed horizontal scalability across commodity servers, trading strict consistency for availability/scale (see file 1 and file 3's CAP discussion).

**Q3. Why are vector databases suddenly a big deal in 2024-2026?**
> The explosion of AI applications (RAG/chatbots, semantic search) needs similarity-based search over embedding vectors — a fundamentally different query type traditional exact-match/range-based databases weren't built for. See file 6.

## Relational Databases

**Q4. Explain MVCC and why it matters.**
> Multi-Version Concurrency Control keeps multiple row versions internally so readers see a consistent snapshot without blocking writers, and vice versa — the mechanism behind Postgres/MySQL's ability to handle high concurrent read+write load without excessive locking.

**Q5. Why do we normalize OLTP databases but denormalize warehouses?**
> OLTP does frequent small targeted transactions where normalization prevents update anomalies cheaply; warehouses do infrequent large analytical scans where denormalization avoids expensive joins, since writes there are batched rather than per-transaction.

**Q6. What's the difference between a PRIMARY KEY and a UNIQUE constraint?**
> A table can have only ONE primary key (implicitly NOT NULL), but MULTIPLE unique constraints; a primary key is typically what foreign keys reference.

## NoSQL

**Q7. Name the four types of NoSQL databases and one company example using each.**
> Document (MongoDB — product catalogs), Key-Value (Redis/DynamoDB — caching/sessions), Wide-Column (Cassandra — Netflix viewing history), Graph (Neo4j — LinkedIn connections). See file 3.

**Q8. Explain CAP theorem with a real example.**
> Amazon's Dynamo/shopping cart deliberately chose AP (Availability + Partition tolerance) over strict consistency — better to show a customer a slightly stale cart than an error page during a network partition. See file 3.

**Q9. Why can't you easily do JOINs in Cassandra?**
> Data is physically partitioned by the partition key specifically to make partition-key queries fast across a distributed cluster; joining would require scanning across many nodes, defeating the design's purpose. Denormalization (designing tables per query pattern) is the standard Cassandra approach instead.

## NewSQL & Distributed Systems

**Q10. What problem does NewSQL solve that neither traditional RDBMS nor NoSQL solve alone?**
> Horizontal, NoSQL-style scaling WHILE retaining full ACID transactions and standard SQL — achieved via consensus algorithms (Raft/Paxos) rather than the harder tradeoffs either pure approach required.

**Q11. What is Google Spanner's TrueTime and why is it significant?**
> Synchronized atomic clocks/GPS across data centers, bounding clock uncertainty tightly enough to assign globally meaningful transaction timestamps — enabling strict serializability across continents, previously considered nearly impossible at that scale.

**Q12. Explain Raft consensus in your own words.**
> Nodes elect a leader; all writes go through the leader, which replicates to followers and considers a write committed once a MAJORITY acknowledge — tolerating up to floor((N-1)/2) node failures while continuing to operate with no manual failover.

## Cloud-Native & Modern

**Q13. What's architecturally different about Amazon Aurora vs traditional RDS MySQL?**
> Aurora separates compute from a distributed, self-healing storage layer replicated 6x across 3 AZs — replicas share the same storage (no replication lag from data copying), and failover just repoints to the same storage layer.

**Q14. Why would you choose Cosmos DB's "Session" consistency over "Strong"?**
> Lower latency/higher availability while still guaranteeing a user sees their own writes immediately — the right tradeoff for most user-facing features not needing global strong consistency.

## Vector Databases

**Q15. Why can't a normal `WHERE` clause do semantic search?**
> Exact-match/range filtering can't capture meaning-based similarity; you need distance calculations in high-dimensional vector space (cosine/euclidean distance), requiring specialized ANN indexing (HNSW/IVF) for performance at scale.

**Q16. When would you choose pgvector over a dedicated vector database like Pinecone?**
> Moderate scale, already running Postgres, want to combine vector similarity with normal relational filters/joins in one query, and prefer architectural simplicity over the absolute highest performance ceiling at extreme scale (100M+ vectors).

**Q17. Explain the RAG pattern end-to-end.**
> Embed the user's query -> vector search finds semantically similar document chunks -> feed those chunks + the query to an LLM as context -> LLM generates an answer grounded in real company data instead of hallucinating.

## Design & Modeling

**Q18. Walk through how you'd design a database for [any system] — what's your FIRST step?**
> List the actual key business questions/queries the system must answer BEFORE drawing any tables — jumping straight to schema design without this is a common weak-answer signal.

**Q19. When would you deliberately denormalize a relational schema?**
> When a specific, justified business reason requires it — e.g., storing `unit_price` on an order line item rather than always looking up the current menu price, to preserve historical accuracy even as menu prices change over time.

**Q20. UUID or auto-increment integer for a primary key — which would you choose?**
> Depends: auto-increment for single-database systems valuing storage/index performance; UUID (ideally time-ordered like UUIDv7) for distributed systems needing collision-free IDs generated client-side, or where ID predictability is a security concern.

**Q21. How do you handle a many-to-many relationship in a relational schema?**
> A junction/bridge table with foreign keys to both related tables, often with a composite primary key across both foreign keys to prevent duplicate relationships.

## Indexing & Internals

**Q22. Why is a B-Tree the default index structure for OLTP databases?**
> Handles both point lookups and range queries efficiently in O(log n), and manages random inserts/updates reasonably well — matching OLTP's mixed read/write workload.

**Q23. Why does Cassandra use LSM-Trees instead of B-Trees?**
> LSM-Trees write via fast sequential in-memory appends (memtable) flushed to immutable sorted files (SSTables), avoiding the random-access disk I/O that B-Trees require for in-place updates — critical for sustaining Cassandra's massive write throughput design goal.

**Q24. Why is Parquet so much faster than CSV for analytical queries?**
> Columnar storage lets queries read only needed columns (column pruning), compresses far better (similar values adjacent), and supports predicate pushdown via stored min/max block metadata.

**Q25. What is a Write-Ahead Log and why does every serious database have one?**
> An append-only log of intended changes written BEFORE modifying actual data files — guarantees durability (a crash mid-operation can be recovered by replaying the WAL) and is exactly what CDC tools like Debezium read from.

**Q26. What's a Bloom filter and why does Cassandra/HBase use them?**
> A compact, probabilistic structure that can definitively say a key is NOT in a file (skip a disk read entirely) or might be present (needs an actual check) — avoids unnecessary disk reads across many SSTables.

## Scaling

**Q27. Walk through how you'd scale a database from 10K to 10M users.**
> Staged approach: vertical scaling/query optimization first -> add read replicas + caching -> functional/vertical sharding (split services onto separate databases) -> horizontal sharding of the largest tables or migration to a purpose-built system for that specific access pattern. See file 9.

**Q28. What's replication lag and how do you handle it?**
> The delay between a write hitting the primary and appearing on read replicas; handled by routing "read-your-own-write" scenarios to the primary specifically, or using session-consistency patterns.

**Q29. Range-based vs hash-based sharding — tradeoffs?**
> Range-based is simple but risks hot shards from uneven data distribution; hash-based distributes evenly but makes range queries need to hit every shard.

**Q30. What does PgBouncer solve?**
> Connection pooling — multiplexes many application-level connections onto fewer actual database connections, preventing connection-limit exhaustion in microservices architectures with many services each opening their own pools.

## Transactions & Consistency

**Q31. Explain the difference between Read Committed and Repeatable Read isolation levels with an example.**
> Read Committed allows non-repeatable reads (the same query in one transaction can return different results if another transaction commits in between); Repeatable Read prevents this by keeping a consistent snapshot for the whole transaction. See file 10 for full worked examples.

**Q32. What's Two-Phase Commit and why is it considered fragile?**
> A distributed transaction protocol (Prepare phase, then Commit phase across all participants) — fragile because if the coordinator crashes between phases, participants can be left holding locks indefinitely in an uncertain state.

**Q33. Why would eventual consistency ever be an acceptable choice?**
> For features where brief staleness genuinely doesn't harm the business (like counts, view counts) — versus features needing strong consistency (account balances, inventory counts) — a nuanced, example-backed answer beats blanket statements either way.

## Real-World / Company Choices

**Q34. Why did Netflix create Apache Iceberg instead of using an existing table format?**
> To solve their own petabyte-scale data lake reliability problems (ACID transactions, schema evolution, time travel on top of cheap object storage) that no existing open format solved adequately at their scale at the time.

**Q35. Why does a large company like Spotify run multiple different databases instead of standardizing on one?**
> Different microservices have genuinely different access patterns (user library data, play history, real-time recommendations) — matching each to a purpose-built database beats forcing one database to serve every pattern adequately.

**Q36. Design a multi-database architecture for a ride-hailing app and justify each choice.**
> See the full worked case study in `case-studies/ride-hailing-architecture.md` — relational for trip/payment transactional data, Redis for real-time location, Cassandra for location history, warehouse for analytics.

## Rapid-Fire
37. What does ACID stand for? *(Atomicity, Consistency, Isolation, Durability.)*
38. What's a foreign key constraint prevent? *(Orphaned records pointing to non-existent parent rows.)*
39. What's the difference between a clustered and non-clustered index? *(Clustered physically orders table rows on disk, only one per table; non-clustered is separate, can have many.)*
40. What's a covering index? *(An index containing all columns a query needs, enabling an index-only scan without touching the base table.)*
41. What's a soft delete and why use one? *(Marking a row as deleted via a flag/timestamp instead of removing it, preserving referential integrity and audit history.)*
42. What's the difference between horizontal and vertical scaling? *(Horizontal = more servers; vertical = a bigger single server.)*
43. Why is `SELECT *` discouraged in production? *(Extra I/O/cost, breaks on schema changes, prevents covering-index optimization.)*
44. What's a materialized view? *(A physically stored, precomputed query result needing manual/scheduled refresh, vs a normal view which is just a saved query re-run each time.)*
45. What's the purpose of a junction/bridge table? *(Resolving many-to-many relationships between two tables.)*
46. Why might you choose a graph database over a relational database with self-joins? *(Deep relationship traversal — friends-of-friends, fraud rings — is far more efficient natively in a graph model than via repeated, increasingly expensive SQL self-joins.)*
47. What's the CAP theorem tradeoff in practice? *(In any real distributed system, partition tolerance is mandatory, so the real choice is Consistency vs Availability during a network partition.)*
48. Name one reason a company might choose NOT to migrate a legacy database system. *(Migration risk on audited/critical processes, regulatory recertification burden, ROI not justifying the effort for a stable system.)*
49. What's the difference between a document database and a wide-column store? *(Document DBs store flexible, nested JSON-like records queried by any field; wide-column stores are designed around querying primarily by a partition key, with denormalized tables per query pattern.)*
50. Why do vector databases use Approximate Nearest Neighbor instead of exact search? *(Exact nearest-neighbor search over billions of high-dimensional vectors is too slow for real-time use; ANN algorithms like HNSW trade a small accuracy loss for massive speed gains.)*

---

**Practice tip**: For system-design-style questions (Q18, Q27, Q36), always narrate your REASONING out loud, not just the final answer — interviewers are evaluating your decision-making process (why THIS tradeoff, not that one) far more than whether you land on the exact "textbook" answer.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"A mind anchored in purpose does not get shaken by every passing distraction."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
