# 1. SQL Basics (Absolute Beginner Start)

## What is SQL?
SQL (Structured Query Language) is how you talk to a database — ask it questions ("show me all orders from last month") and it answers with rows of data. Every product company — Amazon, Swiggy, Netflix — stores its core business data (orders, users, payments) in databases queried with SQL every single day.

## The Sample Database We'll Use Throughout This Module
Imagine we work at an e-commerce company like Amazon/Flipkart. We have these tables:

```sql
customers (customer_id, name, city, signup_date)
products  (product_id, product_name, category, price)
orders    (order_id, customer_id, order_date, status)
order_items (order_item_id, order_id, product_id, quantity, unit_price)
```

> 💡 Open [`sql-playground.html`](./sql-playground.html) in your browser — this exact schema is pre-loaded with sample data so you can run every query below yourself.

## SELECT — Your First Query
```sql
-- "Show me everything in the customers table"
SELECT * FROM customers;

-- "Show me only name and city"
SELECT name, city FROM customers;
```
**Real scenario**: A support agent at Swiggy needs to look up a customer's city to check delivery zone issues — this is the exact query they'd (indirectly, via an internal tool) trigger.

## WHERE — Filtering Rows
```sql
-- Customers from Bangalore
SELECT * FROM customers WHERE city = 'Bangalore';

-- Orders placed after a certain date
SELECT * FROM orders WHERE order_date >= '2026-01-01';

-- Multiple conditions
SELECT * FROM orders WHERE status = 'delivered' AND order_date >= '2026-01-01';

-- OR condition
SELECT * FROM customers WHERE city = 'Bangalore' OR city = 'Mumbai';

-- IN (cleaner than multiple ORs)
SELECT * FROM customers WHERE city IN ('Bangalore', 'Mumbai', 'Delhi');

-- Pattern matching
SELECT * FROM customers WHERE name LIKE 'A%';   -- starts with A
SELECT * FROM customers WHERE name LIKE '%sh%'; -- contains 'sh' anywhere

-- NULL checks (never use = NULL, always IS NULL)
SELECT * FROM orders WHERE status IS NULL;
```
**Real scenario**: A product manager at Zomato wants "all orders from Bangalore placed this month that are still pending" — that's a `WHERE` clause with 3 conditions combined with `AND`.

## ORDER BY — Sorting
```sql
SELECT * FROM products ORDER BY price DESC;      -- most expensive first
SELECT * FROM products ORDER BY category, price; -- sort by category, then price within each
```

## LIMIT — Restrict Row Count
```sql
SELECT * FROM products ORDER BY price DESC LIMIT 5;  -- top 5 priciest products
```
**Real scenario**: "Show top 10 best-selling products this week" for a homepage banner — `ORDER BY ... LIMIT 10`.

## Data Types (know these cold)
| Type | Examples | Notes |
|---|---|---|
| `INT` / `BIGINT` | 1, 42, 1000000 | Whole numbers; BIGINT for IDs that could exceed ~2 billion |
| `DECIMAL(p,s)` / `NUMERIC` | 199.99 | Exact precision — **always use for money**, never FLOAT |
| `FLOAT` / `DOUBLE` | 3.14159 | Approximate — fine for scientific data, risky for currency |
| `VARCHAR(n)` / `TEXT` | 'Rahul Sharma' | Variable-length text |
| `DATE` | '2026-07-25' | Date only |
| `TIMESTAMP` / `DATETIME` | '2026-07-25 14:30:00' | Date + time |
| `BOOLEAN` | TRUE/FALSE | Flags (is_active, is_deleted) |

> ⚠️ Common beginner mistake: storing money as `FLOAT`. `0.1 + 0.2` in floating point doesn't always equal exactly `0.3` — this causes real accounting bugs. Always use `DECIMAL`/`NUMERIC` for prices, amounts, balances.

## Comparison & Logical Operators
```
=, !=, <>, <, >, <=, >=      -- comparison
AND, OR, NOT                  -- logical
BETWEEN 10 AND 20             -- range (inclusive both ends)
IS NULL, IS NOT NULL          -- null checks
IN (...), NOT IN (...)        -- membership
LIKE, NOT LIKE                -- pattern match (% = any chars, _ = single char)
```

## DISTINCT — Unique Values
```sql
-- How many unique cities do our customers come from?
SELECT DISTINCT city FROM customers;
```
**Real scenario**: "Which cities do we currently operate in?" — a very common first query when exploring a new dataset.

## Basic Calculations in SELECT
```sql
SELECT product_name, price, price * 0.18 AS gst_amount, price * 1.18 AS price_with_gst
FROM products;
```
`AS` renames (aliases) a column — critical for readable output, especially in reports going to business stakeholders.

## Try It Yourself (in the playground)
1. Find all customers who signed up in 2026.
2. Find all products priced above ₹500, sorted cheapest to most expensive.
3. Find the top 3 most expensive products.
4. Find all orders that are NOT delivered yet.

## Common Beginner Mistakes
- Forgetting `WHERE` clause order doesn't matter for logic but does for readability — put the most selective filter first for your own clarity (engine usually reorders anyway).
- Using `=` instead of `LIKE` for partial text matches (it will error or return nothing).
- Comparing `NULL` with `=` instead of `IS NULL` (always returns unknown/false, never true).
