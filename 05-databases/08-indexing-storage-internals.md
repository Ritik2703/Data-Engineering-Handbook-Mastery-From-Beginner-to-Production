# 8. Indexing & Storage Internals — How a Query Actually Reads Disk

## Why This Matters Beyond Just "Add an Index"
Understanding what actually happens on disk/memory when a query runs is what separates someone who can write correct SQL from someone who can diagnose why a production query suddenly got 100x slower.

## B-Tree — The Default Structure for OLTP Databases (Postgres, MySQL, SQL Server, Oracle)
```
                    [50]
                 /        \
            [20, 35]      [70, 85]
           /   |   \      /   |   \
        [10] [25] [40]  [60] [75] [90]
```
A B-Tree keeps keys sorted in a balanced tree — finding any specific value takes O(log n) comparisons regardless of table size, which is why an indexed lookup on a billion-row table still returns almost instantly. Each node typically maps to one disk "page" (commonly 8KB in Postgres) — the tree height directly determines how many disk reads a lookup needs, which is why B-Trees are specifically optimized to stay very "flat" (wide, shallow) rather than tall.

**Why B-Trees are the default for OLTP**: they handle both **point lookups** (`WHERE id = 5`) AND **range queries** (`WHERE date BETWEEN x AND y`) efficiently, and they handle random inserts/updates reasonably well — exactly the mixed read/write workload a transactional application generates.

## LSM-Tree (Log-Structured Merge-Tree) — The Structure Behind Cassandra, RocksDB, LevelDB, HBase
**The problem it solves**: B-Trees require updating data IN PLACE on disk, which involves random disk I/O (seek to the right page, read it, modify it, write it back) — this is fine on fast SSDs but was a major bottleneck on the spinning disks common when many NoSQL databases were designed, AND it fundamentally limits pure write throughput even on modern hardware at extreme write volumes.
```
LSM-Tree write path:
1. New writes go to an in-memory structure called a MEMTABLE (very fast, sequential in RAM)
2. When the memtable fills up, it's flushed to disk as an immutable, sorted file (SSTable)
3. Background process periodically MERGES/COMPACTS multiple SSTables into fewer, larger ones,
   discarding overwritten/deleted values along the way
4. Reads may need to check the memtable AND multiple SSTables (mitigated by Bloom filters —
   a probabilistic structure that quickly tells you "this key is DEFINITELY NOT here" without
   an actual disk read, skipping SSTables that can't contain the key)
```
**Why this wins for write-heavy workloads**: writes are always fast, sequential appends (no random-access disk seeks needed at write time) — exactly why Cassandra can sustain enormous write throughput across a cluster, which is the whole point of a wide-column store (see file 3).
**The tradeoff**: reads can be slower/more complex (may need to check several SSTables), and background compaction consumes CPU/I/O resources — a real, tunable operational concern in production Cassandra clusters.

## Columnar Storage Internals (Parquet, ORC, and columnar warehouses like Redshift/BigQuery/Snowflake)
```
Row-based storage on disk:                 Columnar storage on disk:
[1, Rahul, 500][2, Priya, 750]...          [1, 2, 3, ...]        <- all IDs stored together
                                            [Rahul, Priya, ...]   <- all names stored together
                                            [500, 750, ...]       <- all amounts stored together
```
**Why analytics loves this**: a query like `SELECT SUM(amount) FROM orders` only needs to read the `amount` column's data block — completely skipping `name`, `id`, and every other column, dramatically reducing disk I/O for aggregation-heavy analytical queries. Combined with **compression** (similar values stored adjacent to each other compress far better — a column of repeated "delivered"/"cancelled" status values compresses extremely well) and **predicate pushdown** (skipping entire blocks based on stored min/max metadata per block, aka zone maps), this is why Parquet/columnar warehouses can scan billions of rows in seconds.

## Why You'd NEVER Use a Columnar Store for OLTP
A single-row insert/update in a purely columnar system requires touching MANY separate column files (one write operation split across every column's storage) — brutally inefficient for the "insert one order" pattern OLTP systems do constantly. This is exactly why OLTP databases use row-based B-Tree storage, and analytical warehouses use columnar storage — **it's a fundamental tradeoff based on query pattern, not one being objectively "better."**

## Bloom Filters — The Clever Trick Behind Fast NoSQL Reads
A Bloom filter is a compact, probabilistic data structure that can definitively say "this key is NOT in this file" (100% certain) or "this key MIGHT be in this file" (needs an actual check) — used heavily by Cassandra/HBase/RocksDB to avoid unnecessary disk reads across many SSTables when checking if a key exists.
```
Conceptually: a Bloom filter is a bit array + several hash functions.
Checking membership: hash the key several ways, check if all corresponding bits are set.
  - If ANY bit is 0: the key is DEFINITELY not present (skip this file entirely, no disk read needed)
  - If ALL bits are 1: the key MIGHT be present (false positives possible — must actually check)
```

## Write-Ahead Log (WAL) — How Every Serious Database Guarantees Durability
Before a database modifies its actual data files, it first writes the intended change to an append-only **Write-Ahead Log** on disk. If the system crashes mid-operation, on restart the database replays the WAL to redo any committed-but-not-yet-applied changes — this is the actual mechanism providing the "D" (Durability) in ACID.
```
Client: "UPDATE orders SET status = 'shipped' WHERE order_id = 1001"
       |
Database: 1. Write the intended change to the WAL (fast, sequential append) — COMMIT can
             return success to the client as soon as THIS is durably on disk
          2. Actually apply the change to the data files (can happen slightly later,
             asynchronously, since the WAL guarantees it won't be lost even if this step
             hasn't happened yet when a crash occurs)
```
This is also the exact mechanism Change Data Capture (CDC) tools like Debezium read from — they tail the database's WAL/binlog to capture every row-level change in real time, which is why CDC has minimal performance impact on the source database (it's reading a log that's already being written for durability reasons anyway, not adding new query load).

## Interview Traps
- "Why does Cassandra handle massive write throughput better than Postgres?" — LSM-Tree's sequential-append write path vs B-Tree's in-place random-access updates.
- "Why is Parquet so much faster for analytical queries than row-based CSV?" — columnar layout enables column pruning (skip unneeded columns entirely) and much better compression, plus predicate pushdown via stored min/max block metadata.
- "How does a database guarantee data isn't lost in a crash?" — Write-Ahead Logging; be ready to explain the commit-returns-after-WAL-write-not-after-full-data-file-write sequence.
- "How does CDC read database changes without slowing down the source database?" — it tails the WAL/binlog that the database is already writing for its own durability guarantees, rather than issuing new queries against the live tables.
