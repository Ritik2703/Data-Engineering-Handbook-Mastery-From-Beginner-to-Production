# 8. Transactions & Concurrency

## Why This Matters for Data Engineers
Even though DE work is heavy on analytical (OLAP) queries, understanding OLTP transactional behavior is essential — you're often extracting FROM transactional systems (Postgres/MySQL app databases) that are being written to concurrently, and you need to understand consistency guarantees to avoid pulling corrupted/partial data.

## Transactions — BEGIN / COMMIT / ROLLBACK
**Real scenario**: Transferring money between two accounts must be atomic — either both the debit and credit happen, or neither does.
```sql
BEGIN;

UPDATE accounts SET balance = balance - 500 WHERE account_id = 1;
UPDATE accounts SET balance = balance + 500 WHERE account_id = 2;

COMMIT;   -- if anything failed above, ROLLBACK instead to undo both changes
```
If the server crashes between the two UPDATEs (before COMMIT), the transaction is automatically rolled back on restart — you'll never see money vanish from one account without appearing in the other.

## Isolation Levels (recap + practical impact)
| Level | Dirty Read? | Non-repeatable Read? | Phantom Read? | Practical Impact |
|---|---|---|---|---|
| Read Uncommitted | ✅ Possible | ✅ Possible | ✅ Possible | Rarely used — can read uncommitted/rolled-back data |
| Read Committed (Postgres/SQL Server default) | ❌ No | ✅ Possible | ✅ Possible | Good balance for most OLTP apps |
| Repeatable Read (MySQL/InnoDB default) | ❌ No | ❌ No | ✅ Possible (varies) | Same query run twice in one transaction gives same result |
| Serializable | ❌ No | ❌ No | ❌ No | Full isolation, most locking, lowest concurrency |

- **Dirty Read**: reading another transaction's uncommitted changes (which might get rolled back).
- **Non-repeatable Read**: re-reading the same row within a transaction gives a different value (another transaction committed a change in between).
- **Phantom Read**: re-running the same query within a transaction returns a different SET of rows (another transaction inserted/deleted matching rows).

## Locking
- **Row-level lock**: locks only the specific row being modified — allows high concurrency.
- **Table-level lock**: locks the entire table — simpler but blocks all other writers, used rarely except for specific bulk operations (e.g., `TRUNCATE`).
- **Shared lock (read lock)**: multiple transactions can hold it simultaneously (for reading).
- **Exclusive lock (write lock)**: only one transaction can hold it — blocks others from reading/writing that row until released.

## Deadlocks
**Real scenario**: Transaction A locks row 1 then wants row 2; Transaction B locks row 2 then wants row 1 — both wait forever for each other.
```
Transaction A:                    Transaction B:
UPDATE accounts                   UPDATE accounts
  WHERE account_id = 1;             WHERE account_id = 2;
-- waiting for row 2...           -- waiting for row 1...
UPDATE accounts                   UPDATE accounts
  WHERE account_id = 2;             WHERE account_id = 1;
```
Databases detect this automatically and kill one transaction (rolling it back) to break the deadlock. **Fix**: always acquire locks/update rows in a **consistent order** across your application code (e.g., always update lower account_id first) to prevent circular waits.

## Why This Matters for ETL Extraction
When extracting data from a live OLTP source:
- Pulling data mid-transaction (without snapshot isolation) can give you **inconsistent** results (e.g., you see the debit but not yet the credit from a bank transfer).
- Most modern databases use **MVCC (Multi-Version Concurrency Control)** — readers see a consistent snapshot as of when their query/transaction started, without blocking writers. This is why Postgres/MySQL InnoDB readers generally don't block writers by default.
- For very large extracts from a busy production DB, consider reading from a **replica** instead of the primary, to avoid adding read load to the system serving live user traffic.

## Optimistic vs Pessimistic Concurrency Control
- **Pessimistic**: lock the row before reading/updating (assume conflicts will happen) — safer under high contention, but reduces concurrency.
- **Optimistic**: read without locking, check a version number/timestamp before committing the update; retry if it changed — better for low-contention scenarios (common pattern: a `version` or `updated_at` column checked in the `WHERE` clause of an `UPDATE`).
```sql
UPDATE orders SET status = 'shipped', version = version + 1
WHERE order_id = 500 AND version = 3;  -- fails/no-op if another process already updated it
```

## Interview Traps
- Explain MVCC in plain language: "readers don't block writers, writers don't block readers, everyone sees a consistent snapshot" — this is why Postgres feels fast under concurrent read/write load.
- Be ready to describe a real deadlock scenario and the standard fix (consistent lock ordering).


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The one who masters their reactions masters far more than the one who only masters their tools."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
