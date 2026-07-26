# 2. JOINs — Where Most Beginners Get Stuck (Go Slow Here)

## Why JOINs exist
Real databases split data across multiple tables to avoid duplication (normalization — see `01-fundamentals/03-data-modeling.md`). A `customers` table and an `orders` table are related by `customer_id` — a JOIN combines rows from both based on that relationship.

## Visual: All Join Types
```
INNER JOIN                LEFT JOIN                 RIGHT JOIN               FULL OUTER JOIN
   A ∩ B                  All of A + matching B     Matching A + all of B    Everything, matched where possible

  ┌───┐┌───┐               ┌───┐┌───┐                ┌───┐┌───┐               ┌───┐┌───┐
  │ A ││ B │                │ A ││ B │                │ A ││ B │               │ A ││ B │
  │  ╲╱   │                │███╲╱   │                │   ╲╱███│               │███╲╱███│
  │  ╱╲   │                │███╱╲   │                │   ╱╲███│               │███╱╲███│
  └───┘└───┘               └───┘└───┘                └───┘└───┘               └───┘└───┘
  (only overlap)         (all A, overlap+A-only)   (all B, overlap+B-only)   (all A + all B)
```

## Sample tables
```sql
customers (customer_id, name, city)
orders    (order_id, customer_id, amount, order_date)
```

## INNER JOIN — only rows that match in both tables
```sql
SELECT c.name, o.order_id, o.amount
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id;
```
**Real scenario**: "Show me customer names alongside their orders" — customers with **zero orders** won't appear (that's the key thing to understand about INNER JOIN).

## LEFT JOIN — all rows from the left table, matched where possible
```sql
-- All customers, and their orders if they have any (NULL if not)
SELECT c.name, o.order_id, o.amount
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id;
```
**Real scenario (Amazon-style)**: Marketing wants "all customers, and flag which ones have NEVER placed an order" (for a win-back email campaign):
```sql
SELECT c.customer_id, c.name
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;   -- customers with no matching order = never ordered
```
> ⚠️ **The #1 JOIN mistake**: putting a filter on the right table's column in `WHERE` instead of the `ON` clause silently turns a LEFT JOIN back into an INNER JOIN. Example:
```sql
-- WRONG: this accidentally excludes customers with no orders!
SELECT c.name, o.amount FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.amount > 100;   -- customers with NULL amount get filtered out here

-- RIGHT: move the condition into the ON clause
SELECT c.name, o.amount FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.amount > 100;
```

## RIGHT JOIN — all rows from the right table (rarely used — just flip table order and use LEFT JOIN instead, more readable)
```sql
SELECT c.name, o.order_id
FROM customers c
RIGHT JOIN orders o ON c.customer_id = o.customer_id;
-- equivalent, more common style:
SELECT c.name, o.order_id
FROM orders o
LEFT JOIN customers c ON c.customer_id = o.customer_id;
```

## FULL OUTER JOIN — everything from both sides
```sql
SELECT c.name, o.order_id
FROM customers c
FULL OUTER JOIN orders o ON c.customer_id = o.customer_id;
```
**Real scenario**: Reconciling two systems — e.g., comparing orders in your app DB vs orders recorded in a payment gateway, to find mismatches on either side (orders with no payment, payments with no order record).

## SELF JOIN — a table joined to itself
**Real scenario (org chart / Uber driver referral)**: find employees who earn more than their manager.
```sql
SELECT e.name AS employee, e.salary, m.name AS manager, m.salary AS manager_salary
FROM employees e
JOIN employees m ON e.manager_id = m.employee_id
WHERE e.salary > m.salary;
```

## CROSS JOIN — every combination of both tables (cartesian product)
**Real scenario**: Generate all possible (product, warehouse) combinations to check stock coverage.
```sql
SELECT p.product_name, w.warehouse_name
FROM products p
CROSS JOIN warehouses w;
```
> ⚠️ Accidental cross joins (forgetting the `ON` condition) is one of the most common production bugs — a 10K x 10K table "join" without a condition silently produces 100 million rows and can crash a query or blow up a bill on pay-per-scan warehouses (BigQuery).

## Multi-table JOINs (very common in real reporting)
**Real scenario (Swiggy-style order report)**: "Show customer name, restaurant name, and item names for every order."
```sql
SELECT c.name AS customer, r.restaurant_name, p.product_name, oi.quantity
FROM orders o
JOIN customers c   ON o.customer_id = c.customer_id
JOIN restaurants r ON o.restaurant_id = r.restaurant_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p    ON oi.product_id = p.product_id;
```

## JOIN Performance Notes
- Always JOIN on **indexed** columns (usually primary/foreign keys) — see `07-query-optimization-indexing.md`.
- JOIN order in the SQL text usually doesn't matter — the query optimizer reorders based on statistics — but readability still matters for humans.
- In distributed warehouses (Spark/Snowflake/BigQuery), joining a **huge table to a small table** benefits from a broadcast join (small table copied to every node) — the optimizer usually detects this automatically but you can hint it.

## Try It Yourself (in the playground)
1. List every order along with the customer's name and city.
2. Find customers who have never placed an order (LEFT JOIN + IS NULL pattern).
3. Find the total amount spent by each customer, including customers with $0 (no orders).
4. Write a self-join to find products in the same category as "Wireless Mouse".

## Interview Traps
- "Difference between WHERE and ON in a LEFT JOIN" is one of the most common SQL interview questions — know the silent-INNER-JOIN gotcha above cold.
- Be ready to explain why a JOIN without an `ON`/`USING` clause (accidental cross join) is dangerous in production.
