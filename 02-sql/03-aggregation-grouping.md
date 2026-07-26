# 3. Aggregation & GROUP BY

## Aggregate Functions
```sql
COUNT(*), COUNT(column)     -- count rows / non-null values
SUM(column)                 -- total
AVG(column)                 -- average
MIN(column), MAX(column)    -- smallest/largest
```

## GROUP BY — Aggregating Per Category
**Real scenario (Amazon-style)**: "Total sales per product category, this month."
```sql
SELECT category, SUM(price * quantity) AS total_sales
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY category;
```

**Real scenario (Uber-style)**: "Number of trips per city, per day."
```sql
SELECT city, DATE(trip_start_time) AS trip_date, COUNT(*) AS num_trips
FROM trips
GROUP BY city, DATE(trip_start_time)
ORDER BY trip_date, num_trips DESC;
```

## The Golden Rule of GROUP BY
Every column in `SELECT` that is **not** wrapped in an aggregate function **must** appear in `GROUP BY`. This is the #1 error beginners hit ("column must appear in GROUP BY clause or be used in an aggregate function").
```sql
-- WRONG — customer_name isn't aggregated or grouped
SELECT customer_name, COUNT(*) FROM orders GROUP BY customer_id;

-- RIGHT
SELECT customer_id, customer_name, COUNT(*) 
FROM orders 
GROUP BY customer_id, customer_name;
```

## HAVING — Filtering AFTER Aggregation
`WHERE` filters rows **before** grouping; `HAVING` filters groups **after** aggregation.

**Real scenario (Zomato-style)**: "Restaurants with more than 100 orders this month" (need the count first, then filter on it):
```sql
SELECT restaurant_id, COUNT(*) AS order_count
FROM orders
WHERE order_date >= '2026-07-01'
GROUP BY restaurant_id
HAVING COUNT(*) > 100;
```
> You can't write `WHERE COUNT(*) > 100` — `COUNT(*)` doesn't exist yet at the row-filtering stage; that's exactly why `HAVING` exists.

## Query Execution Order (know this — explains WHERE vs HAVING forever)
```
1. FROM (+ JOIN)
2. WHERE
3. GROUP BY
4. HAVING
5. SELECT
6. ORDER BY
7. LIMIT
```
This is the **logical** processing order — NOT the order you type the clauses in. This is why you can't reference a `SELECT` alias in `WHERE` (alias doesn't exist yet at that stage) in most databases, but you often can in `ORDER BY` (it runs after `SELECT`).

## Combining Multiple Aggregates
**Real scenario (Netflix-style)**: "For each content genre: total watch count, average watch duration, and number of unique viewers."
```sql
SELECT
    genre,
    COUNT(*) AS total_views,
    AVG(watch_duration_minutes) AS avg_watch_duration,
    COUNT(DISTINCT user_id) AS unique_viewers
FROM watch_history
GROUP BY genre
ORDER BY total_views DESC;
```

## CASE WHEN inside aggregates (conditional aggregation — very common in production)
**Real scenario (Swiggy-style)**: "Count of orders by status, all in one row instead of multiple rows."
```sql
SELECT
    restaurant_id,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) AS delivered_count,
    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_count
FROM orders
GROUP BY restaurant_id;
```

## GROUPING SETS / ROLLUP / CUBE (advanced multi-level aggregation)
**Real scenario**: A finance report needs subtotals by region AND an overall grand total, in one query instead of three.
```sql
SELECT region, category, SUM(amount) AS total
FROM sales
GROUP BY ROLLUP(region, category);
-- Produces: (region, category) subtotals, (region, NULL) region subtotals, (NULL, NULL) grand total
```

## Try It Yourself (in the playground)
1. Find total revenue per customer.
2. Find the average order value per city.
3. Find product categories with total sales over ₹10,000 (use HAVING).
4. Count orders by status in a single row using conditional aggregation.

## Interview Traps
- Explain why `WHERE` can't use an aggregate function but `HAVING` can — tie it to execution order.
- "Find categories where average price > 500 AND number of products > 10" — needs both `HAVING AVG(price) > 500 AND COUNT(*) > 10` in one clause.
