# 12. DDL, Schema Design & Practical Queries (Hands-On)

## Creating Tables — Full Real Example with Every Constraint Type
```sql
CREATE TABLE restaurants (
    restaurant_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    cuisine_type VARCHAR(50),
    rating NUMERIC(2,1) CHECK (rating BETWEEN 0 AND 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE menu_items (
    item_id SERIAL PRIMARY KEY,
    restaurant_id INT NOT NULL REFERENCES restaurants(restaurant_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    price NUMERIC(8,2) NOT NULL CHECK (price >= 0),
    is_available BOOLEAN DEFAULT TRUE,
    UNIQUE (restaurant_id, name)   -- a restaurant can't have two menu items with the same name
);
```
- `ON DELETE CASCADE`: automatically deletes all menu items if their parent restaurant is deleted — a deliberate referential integrity choice (the alternative, `ON DELETE RESTRICT`, would BLOCK deleting a restaurant that still has menu items, forcing explicit cleanup first).
- `SERIAL`: Postgres shorthand for an auto-incrementing integer primary key.

## ALTER TABLE — Evolving a Schema Safely in Production
```sql
-- Adding a column (safe, non-blocking in most modern Postgres versions if no default/NOT NULL)
ALTER TABLE restaurants ADD COLUMN phone_number VARCHAR(20);

-- Adding a NOT NULL column to an EXISTING large table safely (avoiding a full table lock)
ALTER TABLE restaurants ADD COLUMN is_active BOOLEAN;             -- Step 1: add nullable
UPDATE restaurants SET is_active = TRUE WHERE is_active IS NULL;  -- Step 2: backfill in batches for huge tables
ALTER TABLE restaurants ALTER COLUMN is_active SET NOT NULL;      -- Step 3: enforce constraint after backfill
ALTER TABLE restaurants ALTER COLUMN is_active SET DEFAULT TRUE;  -- Step 4: set default for future rows

-- Renaming a column (coordinate with application code deploys!)
ALTER TABLE restaurants RENAME COLUMN cuisine_type TO cuisine;

-- Dropping a column (IRREVERSIBLE — always back up / confirm no code depends on it first)
ALTER TABLE restaurants DROP COLUMN phone_number;
```
**Real production concern**: adding a `NOT NULL` column with a default value directly can lock a huge table for the entire duration of rewriting every existing row in older database versions — the 4-step pattern above (add nullable → backfill in batches → enforce NOT NULL → set default) avoids a long production-impacting lock on large tables.

## Indexes — Creating, Choosing Type, and Verifying Usage
```sql
-- Standard B-Tree index (the default, right for most cases)
CREATE INDEX idx_orders_customer_id ON orders(customer_id);

-- Composite index — column order matters (see 02-sql/07-query-optimization-indexing.md)
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);

-- Unique index (enforces uniqueness AND speeds up lookups)
CREATE UNIQUE INDEX idx_customers_email ON customers(email);

-- Partial index — only indexes rows matching a condition, smaller and faster for that specific query pattern
CREATE INDEX idx_orders_pending ON orders(order_date) WHERE status = 'pending';

-- GIN index — for JSONB columns or full-text search (Postgres-specific)
CREATE INDEX idx_products_attributes ON products USING GIN (attributes_jsonb);

-- Verify an index is actually being used
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 101;
```

## Views — Saved, Reusable Queries
```sql
CREATE VIEW active_high_value_customers AS
SELECT c.customer_id, c.name, SUM(o.amount) AS total_spent
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.status = 'delivered'
GROUP BY c.customer_id, c.name
HAVING SUM(o.amount) > 10000;

SELECT * FROM active_high_value_customers WHERE total_spent > 20000;  -- query the view like a table
```
A view doesn't store data itself — it's a saved query, re-executed every time it's queried (unless it's a **materialized view**, which DOES store the result physically and needs manual/scheduled refresh):
```sql
CREATE MATERIALIZED VIEW mv_daily_sales AS
SELECT order_date, SUM(amount) AS total_sales FROM orders GROUP BY order_date;

REFRESH MATERIALIZED VIEW mv_daily_sales;  -- must be run periodically to update
```

## Partitioning a Large Table (critical for warehouse-scale fact tables)
```sql
-- Range partitioning by date — a very common production pattern for large fact tables
CREATE TABLE orders (
    order_id BIGINT,
    customer_id INT,
    order_date DATE NOT NULL,
    amount NUMERIC(10,2)
) PARTITION BY RANGE (order_date);

CREATE TABLE orders_2026_01 PARTITION OF orders
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
CREATE TABLE orders_2026_02 PARTITION OF orders
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- A query filtering on order_date automatically only scans the relevant partition(s)
SELECT * FROM orders WHERE order_date >= '2026-01-15' AND order_date < '2026-01-20';
```

## Transactions in Practice
```sql
BEGIN;

UPDATE inventory SET stock = stock - 1 WHERE product_id = 501;
INSERT INTO orders (customer_id, product_id, amount) VALUES (101, 501, 999);

-- Check a business rule before committing
DO $$
BEGIN
    IF (SELECT stock FROM inventory WHERE product_id = 501) < 0 THEN
        RAISE EXCEPTION 'Insufficient stock';
    END IF;
END $$;

COMMIT;  -- or ROLLBACK if the exception above fired
```

## Common Production DDL Scenarios

### Adding a Foreign Key to an Existing Table (safely)
```sql
ALTER TABLE orders ADD COLUMN restaurant_id INT;
-- Validate existing data first — check for orphaned values that would violate the constraint:
SELECT DISTINCT o.restaurant_id FROM orders o
LEFT JOIN restaurants r ON o.restaurant_id = r.restaurant_id
WHERE r.restaurant_id IS NULL AND o.restaurant_id IS NOT NULL;
-- Only after confirming no orphans:
ALTER TABLE orders ADD CONSTRAINT fk_orders_restaurant
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id);
```

### Soft Deletes (a very common real-world pattern instead of actual DELETE)
```sql
ALTER TABLE customers ADD COLUMN deleted_at TIMESTAMP DEFAULT NULL;

-- "Deleting" a customer without losing historical data (needed for order history integrity)
UPDATE customers SET deleted_at = CURRENT_TIMESTAMP WHERE customer_id = 101;

-- All normal queries must remember to filter these out
SELECT * FROM customers WHERE deleted_at IS NULL;
```
**Why soft deletes are so common in production**: hard-deleting a customer would orphan their historical order records (breaking foreign key integrity or losing audit trail), and many industries have legal/compliance requirements to retain historical records even after a user "deletes" their account.

## Try It Yourself
1. Design and create (with `CREATE TABLE`) a normalized schema for a simple library book-lending system (books, members, loans).
2. Add a `NOT NULL` column to a large existing table using the safe 4-step pattern above.
3. Create a partial index for "only pending orders" and verify with `EXPLAIN ANALYZE` that it's used for a query filtering on `status = 'pending'`.
4. Implement a soft-delete pattern for a `products` table and rewrite a `SELECT *` query to respect it.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Let effort be joyful, not anxious — the quality of your work reflects the quality of your mind."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
