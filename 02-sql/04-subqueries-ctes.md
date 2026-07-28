# 4. Subqueries & CTEs

## Subquery — a query inside a query

### Scalar Subquery (returns one value)
**Real scenario (Amazon-style)**: "Find products priced above the average product price."
```sql
SELECT product_name, price
FROM products
WHERE price > (SELECT AVG(price) FROM products);
```

### Subquery in WHERE with IN
**Real scenario**: "Find all customers who have placed at least one order over ₹5000."
```sql
SELECT * FROM customers
WHERE customer_id IN (
    SELECT customer_id FROM orders WHERE amount > 5000
);
```

### Correlated Subquery (references the outer query — runs once per outer row)
**Real scenario**: "Find each customer's most recent order."
```sql
SELECT o.*
FROM orders o
WHERE o.order_date = (
    SELECT MAX(o2.order_date)
    FROM orders o2
    WHERE o2.customer_id = o.customer_id
);
```
> ⚠️ Correlated subqueries can be slow — they conceptually re-run for every outer row. A window function (`05-window-functions.md`) often solves the same problem faster and more readably.

### Subquery in FROM (derived table)
```sql
SELECT city, AVG(total_spent) AS avg_customer_value
FROM (
    SELECT c.customer_id, c.city, SUM(o.amount) AS total_spent
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.city
) customer_totals
GROUP BY city;
```

## CTE (Common Table Expression) — `WITH` clause
Same idea as a subquery-in-FROM, but far more **readable** — especially with multiple steps. This is the standard in modern production SQL (dbt models are built almost entirely from CTEs).

```sql
WITH customer_totals AS (
    SELECT c.customer_id, c.city, SUM(o.amount) AS total_spent
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.city
)
SELECT city, AVG(total_spent) AS avg_customer_value
FROM customer_totals
GROUP BY city;
```

## Chaining Multiple CTEs (how real production SQL/dbt models are structured)
**Real scenario (Spotify-style)**: "Find the top 3 most-streamed songs per genre this month."
```sql
WITH monthly_streams AS (
    SELECT song_id, genre, COUNT(*) AS stream_count
    FROM streams
    WHERE stream_date >= '2026-07-01'
    GROUP BY song_id, genre
),
ranked_songs AS (
    SELECT
        song_id, genre, stream_count,
        ROW_NUMBER() OVER (PARTITION BY genre ORDER BY stream_count DESC) AS rnk
    FROM monthly_streams
)
SELECT genre, song_id, stream_count
FROM ranked_songs
WHERE rnk <= 3;
```
This CTE-chaining pattern (`raw -> filtered -> aggregated -> ranked -> final`) mirrors exactly how dbt staging → intermediate → mart models are structured (see `04-etl-elt/dbt_example/` and `09-sql-in-production.md`).

## Recursive CTE — for hierarchical/graph-like data
**Real scenario**: Employee org chart, or a product category tree (Category > Subcategory > Sub-subcategory).
```sql
WITH RECURSIVE org_chart AS (
    -- Anchor: top-level (no manager)
    SELECT employee_id, manager_id, name, 1 AS level
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive: find employees whose manager is already in our result
    SELECT e.employee_id, e.manager_id, e.name, oc.level + 1
    FROM employees e
    JOIN org_chart oc ON e.manager_id = oc.employee_id
)
SELECT * FROM org_chart ORDER BY level;
```

## Subquery vs CTE vs Temp Table — When to Use What
| | Best For | Notes |
|---|---|---|
| **Subquery** | One-off, simple filters | Gets unreadable if nested 3+ levels deep |
| **CTE** | Multi-step logic, readability | Most engines don't materialize it (re-evaluated each reference) — check your engine |
| **Temp Table** | Reusing a large intermediate result multiple times, or when the CTE would be recomputed expensively | Materializes to disk/memory once, indexable |
| **Materialized CTE** (Postgres `WITH ... AS MATERIALIZED`) | Force materialization when you know the CTE is expensive and reused | Explicit control over the CTE-vs-subquery tradeoff |

## EXISTS vs IN — a subtle but important difference
```sql
-- IN: compares against a list of values
SELECT * FROM customers WHERE customer_id IN (SELECT customer_id FROM orders);

-- EXISTS: checks if ANY row matches — often faster on large datasets, handles NULLs safely
SELECT * FROM customers c
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id);
```
> ⚠️ `NOT IN` with a subquery that can return `NULL` is a classic bug — if even one row in the subquery result is `NULL`, `NOT IN` returns **no rows at all** (unexpected empty result). `NOT EXISTS` doesn't have this problem — prefer it for "not in" logic in production.

## Try It Yourself (in the playground)
1. Find customers whose total order value is above the overall average customer's total.
2. Write a CTE that computes each customer's order count, then filter to customers with more than 2 orders.
3. Find the most recent order for each customer using a correlated subquery, then rewrite it using a window function (preview of next file) and compare.

## Interview Traps
- Explain the `NOT IN` + NULL trap above — this is a very common "found a bug in production" interview story prompt.
- "When would you use EXISTS over IN?" — mention performance on large subqueries and NULL-safety.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"A steady, humble learner outlasts a proud one who stopped asking questions."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
