# 2. Relational Databases — Deep Dive

## The Relational Model in One Picture
```
TABLE = a relation (a set of rows, each with the same columns)
customers
+-------------+---------------+------------+
| customer_id | name          | city       |
+-------------+---------------+------------+
| 1           | Rahul Sharma  | Bangalore  |
| 2           | Priya Nair    | Mumbai     |
+-------------+---------------+------------+
```
Relationships between tables are expressed via **foreign keys**, not by physically nesting data — this separation is what lets SQL flexibly query data in ways the original schema designer never explicitly anticipated.

## Storage Engines (the layer beneath SQL you rarely see, but that shapes everything)
A **storage engine** is the component responsible for actually reading/writing data to disk, managing indexes, locking, and transactions. Different engines make different tradeoffs:
| Engine | Database | Tradeoff |
|---|---|---|
| **InnoDB** | MySQL (default since 5.5) | Row-level locking, full ACID/transactions, foreign keys — the modern MySQL default |
| **MyISAM** | MySQL (legacy) | Faster for read-heavy, no transactions/foreign keys — largely legacy now |
| **Heap/MVCC storage** | PostgreSQL | MVCC-native from the ground up (see below), no engine-swapping concept like MySQL |
| **InnoDB-compatible (Aurora)** | AWS Aurora MySQL | Cloud-native rewrite separating compute/storage, same InnoDB API |

## MVCC — Multi-Version Concurrency Control (the real reason Postgres/MySQL "feel fast")
Instead of locking a row every time it's read (which would block writers), MVCC keeps **multiple versions** of a row internally — each transaction sees a consistent snapshot as of when it started, without blocking concurrent writers, and vice versa.
```
Transaction A starts at 10:00:00, reads customer row (version as of 10:00:00)
Transaction B updates the same row at 10:00:02, creating a NEW internal version
Transaction A, still running, continues seeing the 10:00:00 version until it commits/re-reads
                — no blocking occurred for either transaction
```
This is why Postgres/MySQL InnoDB handle concurrent read-heavy + write-heavy workloads far better than a naive lock-everything approach would.

## How a Query Actually Executes (tie-in to `02-sql/07-query-optimization-indexing.md`)
```
SQL text
   |
Parser (syntax validity check)
   |
Query Rewriter (view expansion, rule application)
   |
Planner/Optimizer (uses table statistics to choose: table scan? index scan? which join algorithm?)
   |
Executor (actually reads pages from disk/cache, applies filters, returns rows)
```
The **planner/optimizer** is the most "magical" part — it uses statistics about data distribution (collected via `ANALYZE`) to estimate the cheapest way to answer your query, which is why stale statistics cause "why is my index suddenly not being used" production incidents.

## B-Tree Indexes — The Default Structure (see file 8 for the full internals comparison)
A B-Tree keeps data sorted and allows searches, insertions, and deletions in logarithmic time — this is why an indexed lookup on a billion-row table is nearly instant, while an unindexed lookup scans the whole table.

## Normalization — Full Recap with Real Business Reasoning
| Form | Rule | Real business reason to care |
|---|---|---|
| 1NF | Atomic values, no repeating groups | Prevents "phone1, phone2, phone3" column sprawl that breaks when a customer has a 4th phone |
| 2NF | No partial dependency on a composite key | Prevents redundant storage of data that only depends on PART of a multi-column key |
| 3NF | No transitive dependency | Prevents update anomalies — e.g., changing a city's state requires updating it in exactly ONE place, not thousands of scattered rows |

**Why OLTP systems normalize heavily**: a normalized schema guarantees you can never have inconsistent data (customer's city says "Mumbai" in one row and "Bombay" in another) because each fact is stored exactly once. The cost is more JOINs at query time — an acceptable tradeoff for OLTP systems doing small, targeted transactional queries.

## Constraints — The Database Enforcing Data Integrity For You
```sql
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES customers(customer_id),
    amount NUMERIC(10,2) CHECK (amount >= 0),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending','delivered','cancelled')),
    order_date DATE NOT NULL,
    UNIQUE (customer_id, order_date, amount)  -- example composite uniqueness rule
);
```
- **PRIMARY KEY**: uniquely identifies each row, implicitly NOT NULL + UNIQUE.
- **FOREIGN KEY**: enforces that a value must exist in a referenced table — prevents orphaned records (an order pointing to a customer_id that doesn't exist).
- **CHECK**: enforces a business rule directly at the database level (amount can never be negative) — a powerful, often underused safety net independent of application code correctness.
- **UNIQUE**: prevents duplicate combinations of values.

**Real production value**: constraints catch data integrity bugs at the database level even if application code has a bug — a critical last line of defense that many teams underuse in favor of "we'll validate in the application layer," which is necessary but not sufficient on its own.

## The Modern RDBMS Landscape (2026)
| Database | Best Known For | Real Companies Using It |
|---|---|---|
| **PostgreSQL** | Extensibility (JSON, geospatial via PostGIS, `pgvector`), open-source, huge community | Instagram, Spotify (partially), Robinhood |
| **MySQL** | Simplicity, web-app default, huge hosting ecosystem | Facebook (historically, heavily modified), YouTube (early years), Booking.com |
| **Oracle Database** | Enterprise reliability, advanced features, legacy enterprise lock-in | Banks, telecoms, large ERP-heavy enterprises |
| **SQL Server** | Microsoft-stack integration | Enterprises on Azure/Windows Server stacks |
| **Amazon Aurora** | Cloud-native MySQL/Postgres-compatible, storage/compute separation | AWS-native companies wanting managed Postgres/MySQL at scale |

## Interview Traps
- "Why does Postgres 'not block readers with writers'?" — MVCC, explained above; be ready to describe it in your own words.
- "Why do OLTP systems normalize while warehouses denormalize?" — different query patterns: OLTP does frequent small targeted writes/reads (normalization prevents anomalies cheaply); warehouses do infrequent large analytical reads (denormalization avoids expensive joins at query time, since writes are batched, not per-transaction).


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Stillness before action prevents most of the mistakes that haste creates."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
