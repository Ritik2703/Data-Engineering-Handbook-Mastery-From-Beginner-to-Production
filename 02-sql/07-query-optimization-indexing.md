# 7. Query Optimization & Indexing

## Reading an Execution Plan
```sql
EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 101;
```
This shows what the database **actually did** — not just your SQL text. Look for:
- **Seq Scan (Sequential/Full Table Scan)** — reads every row; fine for small tables, a red flag on large ones.
- **Index Scan / Index Only Scan** — uses an index to jump directly to relevant rows — what you want on large tables.
- **Nested Loop / Hash Join / Merge Join** — how the engine is joining tables; a Nested Loop on two huge tables without an index is a common slow-query cause.
- **Rows estimated vs actual** — a huge mismatch means the optimizer's statistics are stale (`ANALYZE` the table to refresh them).

## When Does an Index Actually Get Used?
```sql
-- Index on customer_id WILL be used:
SELECT * FROM orders WHERE customer_id = 101;

-- Index WON'T be used (function wraps the column):
SELECT * FROM orders WHERE YEAR(order_date) = 2026;

-- Fix: rewrite as a sargable (index-friendly) range condition
SELECT * FROM orders WHERE order_date >= '2026-01-01' AND order_date < '2027-01-01';
```
> **Sargable** = "Search ARGument ABLE" — a condition the engine can use an index for directly. Wrapping a column in a function almost always makes a condition non-sargable.

## Composite Index Column Order
```sql
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);
```
Put columns in this order: **1) equality filters, 2) range filters, 3) columns used in ORDER BY.** A composite index on `(customer_id, order_date)` helps `WHERE customer_id = 101 AND order_date > '2026-01-01'`, but does NOT help `WHERE order_date > '2026-01-01'` alone (leftmost column must be used).

## Covering Index (avoid touching the table at all)
```sql
CREATE INDEX idx_orders_covering ON orders(customer_id) INCLUDE (order_date, amount);
```
If a query only needs `customer_id`, `order_date`, `amount`, the engine can answer entirely from the index (**Index Only Scan**) — never touching the actual table rows. Big win for read-heavy reporting queries.

## Real Production Scenario: Optimizing a Slow Dashboard Query
**Before** (Swiggy-style order dashboard, taking 8 seconds):
```sql
SELECT * FROM orders WHERE UPPER(status) = 'DELIVERED' AND YEAR(order_date) = 2026;
```
**Problems**: `UPPER()` and `YEAR()` both wrap indexed columns — neither can use an index.

**After** (down to 200ms):
```sql
SELECT * FROM orders 
WHERE status = 'delivered'   -- normalize data at write time instead of wrapping at read time
  AND order_date >= '2026-01-01' AND order_date < '2027-01-01';
```
Plus an index: `CREATE INDEX idx_orders_status_date ON orders(status, order_date);`

## Avoid SELECT * in Production
```sql
-- Bad: pulls every column, even ones you don't need, prevents covering-index optimization
SELECT * FROM orders WHERE customer_id = 101;

-- Good: only what's needed
SELECT order_id, amount, order_date FROM orders WHERE customer_id = 101;
```
In columnar warehouses (BigQuery/Snowflake), `SELECT *` also means scanning (and paying for) every column — a direct cost hit, not just a style preference.

## Partition Pruning (warehouse-scale optimization)
```sql
-- Table partitioned by sale_date
SELECT * FROM fact_sales WHERE sale_date = '2026-07-25';  -- scans ONE partition
SELECT * FROM fact_sales WHERE EXTRACT(YEAR FROM sale_date) = 2026; -- may scan ALL partitions!
```
Always filter directly on the partition column in its native form — wrapping it in a function can defeat pruning depending on the engine.

## JOIN Optimization
- Join on **indexed** columns (usually the primary/foreign keys already are).
- For a huge table joined to a tiny lookup table, a **broadcast join** (small table copied to every node) avoids an expensive shuffle — most modern optimizers (Spark, Snowflake) do this automatically for small tables, but you can hint it if needed.
- Filter **before** joining where possible (reduce row count early) — modern optimizers often do this automatically (predicate pushdown), but don't rely on it blindly for very complex queries.

## Common Anti-Patterns to Avoid
| Anti-pattern | Why it's slow | Fix |
|---|---|---|
| Function on indexed column in WHERE | Index can't be used | Rewrite as sargable range/equality |
| `SELECT *` | Extra I/O, blocks covering-index optimization, costs more in pay-per-scan warehouses | Select only needed columns |
| `NOT IN` with nullable subquery | Can silently return zero rows | Use `NOT EXISTS` |
| Implicit type casting (comparing INT column to a string literal) | Can silently disable index usage | Match types exactly |
| Correlated subquery in SELECT for every row | Re-executes per row, very slow at scale | Rewrite as a JOIN or window function |
| Huge unpartitioned/unfiltered scan on billions of rows | Scans everything | Add partitioning + always filter on partition column |

## Try It Yourself (in the playground)
1. Run `EXPLAIN` on a query filtering `orders` by `customer_id` — check if the sample schema's index gets used.
2. Rewrite a query using `YEAR(order_date) = 2026` into a sargable range condition.

## Interview Traps
- "Why isn't my index being used?" is one of the most common real debugging interview questions — always check for a function wrapping the column, a type mismatch, or low table statistics (needs `ANALYZE`).
- Be ready to explain **sargable** — it comes up a lot at senior/production-focused interviews.
