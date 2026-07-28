# Case Study: Amazon-style E-commerce Order Analytics

## Schema
```sql
customers   (customer_id, name, email, city, signup_date)
products    (product_id, product_name, category, price, seller_id)
orders      (order_id, customer_id, order_date, status)      -- status: placed, shipped, delivered, cancelled, returned
order_items (order_item_id, order_id, product_id, quantity, unit_price)
reviews     (review_id, product_id, customer_id, rating, review_date)
```

## Business Question 1: "What's our monthly revenue trend, and how does it compare to last month?"
```sql
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', o.order_date) AS month,
        SUM(oi.quantity * oi.unit_price) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status NOT IN ('cancelled', 'returned')
    GROUP BY DATE_TRUNC('month', o.order_date)
)
SELECT
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY month) AS prev_month_revenue,
    ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month)) 
          / LAG(revenue) OVER (ORDER BY month), 1) AS mom_growth_pct
FROM monthly_revenue
ORDER BY month;
```
**Concept used**: `LAG()` window function for month-over-month comparison. **Why not GROUP BY alone?** Because we need to compare each row to the previous one — GROUP BY alone can't "look back" a row.

## Business Question 2: "Which product categories are most returned — a quality/listing accuracy signal?"
```sql
SELECT
    p.category,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN o.status = 'returned' THEN 1 ELSE 0 END) AS returned_orders,
    ROUND(100.0 * SUM(CASE WHEN o.status = 'returned' THEN 1 ELSE 0 END) / COUNT(*), 2) AS return_rate_pct
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category
HAVING COUNT(*) > 50   -- exclude categories with too few orders to be statistically meaningful
ORDER BY return_rate_pct DESC;
```
**Concept used**: Conditional aggregation (`CASE WHEN` inside `SUM`) + `HAVING` to filter on the aggregated count.

## Business Question 3: "Find each customer's first and most recent order (for a 'welcome back' + 'loyal customer' email campaign)"
```sql
WITH ranked_orders AS (
    SELECT
        customer_id, order_id, order_date,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date ASC)  AS rn_first,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS rn_last
    FROM orders
)
SELECT customer_id,
       MAX(CASE WHEN rn_first = 1 THEN order_date END) AS first_order_date,
       MAX(CASE WHEN rn_last = 1 THEN order_date END) AS last_order_date
FROM ranked_orders
GROUP BY customer_id;
```
**Concept used**: Two separate `ROW_NUMBER()` windows (ascending and descending) combined with conditional aggregation to pull both extremes in one pass.

## Business Question 4: "Identify customers at risk of churn — no orders in the last 60 days, but were active before"
```sql
WITH last_order AS (
    SELECT customer_id, MAX(order_date) AS last_order_date
    FROM orders
    GROUP BY customer_id
)
SELECT customer_id, last_order_date
FROM last_order
WHERE last_order_date < CURRENT_DATE - INTERVAL '60 days'
  AND last_order_date >= CURRENT_DATE - INTERVAL '365 days';  -- exclude already-lost/never-active customers
```
**Concept used**: Simple aggregation + date arithmetic — shows not every production query needs window functions; know when simplicity is enough.

## Business Question 5: "Product recommendation signal — products frequently bought together"
```sql
SELECT
    oi1.product_id AS product_a,
    oi2.product_id AS product_b,
    COUNT(DISTINCT oi1.order_id) AS times_bought_together
FROM order_items oi1
JOIN order_items oi2 
    ON oi1.order_id = oi2.order_id 
    AND oi1.product_id < oi2.product_id  -- avoid duplicate pairs (A,B) and (B,A), and self-pairs
GROUP BY oi1.product_id, oi2.product_id
HAVING COUNT(DISTINCT oi1.order_id) > 10
ORDER BY times_bought_together DESC
LIMIT 20;
```
**Concept used**: Self-join on `order_items` via the shared `order_id`, with `product_id <` trick to avoid duplicate/mirrored pairs — a classic "market basket analysis" pattern.

## Why These Patterns Matter
Every one of these is a **real recurring business question** — revenue trends, quality signals, retention, churn, recommendations — solved with the exact SQL concepts from files 1-6 of this module. This is what "product-based company SQL" actually looks like: business logic wrapped in clean, readable, testable SQL.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"A generous teacher and a curious student together create knowledge that outlives them both."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
