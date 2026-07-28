# 6. Advanced SQL Patterns (Production ETL Scenarios)

## 1. Deduplication — Keep Latest Record Per Key
**Real scenario**: A CDC pipeline lands multiple versions of the same customer record (every update creates a new row) — you need only the latest.
```sql
WITH ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY updated_at DESC) AS rn
    FROM customers_raw
)
SELECT * FROM ranked WHERE rn = 1;
```

## 2. SCD Type 2 Merge (Upsert with History)
**Real scenario**: Customer moves city — you need to preserve the OLD city for historical order analysis, while tracking the NEW city going forward.
```sql
MERGE INTO dim_customer AS target
USING staging_customer AS source
ON target.customer_id = source.customer_id AND target.is_current = TRUE
WHEN MATCHED AND (target.city <> source.city) THEN
    UPDATE SET target.end_date = CURRENT_DATE, target.is_current = FALSE
WHEN NOT MATCHED THEN
    INSERT (customer_id, name, city, start_date, end_date, is_current)
    VALUES (source.customer_id, source.name, source.city, CURRENT_DATE, NULL, TRUE);
```

## 3. Gaps & Islands (Consecutive Streak Detection)
**Real scenario (Swiggy/Zomato-style)**: "Find users with a 3+ day consecutive ordering streak" (for a loyalty/streak reward feature).
```sql
WITH numbered AS (
    SELECT user_id, order_date,
           order_date - (ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY order_date))::int AS grp
    FROM daily_orders
)
SELECT user_id, MIN(order_date) AS streak_start, MAX(order_date) AS streak_end, COUNT(*) AS streak_length
FROM numbered
GROUP BY user_id, grp
HAVING COUNT(*) >= 3;
```
**How it works**: subtracting a sequential row number from the date creates a constant value for consecutive dates — rows with the same `grp` value belong to the same unbroken streak.

## 4. Sessionization (grouping events into sessions)
**Real scenario (Netflix/Amazon-style)**: "Group a user's page views into sessions, where a gap of 30+ minutes starts a new session" — foundational for engagement analytics.
```sql
WITH events_with_gap AS (
    SELECT user_id, event_time,
           LAG(event_time) OVER (PARTITION BY user_id ORDER BY event_time) AS prev_event_time
    FROM page_views
),
session_flags AS (
    SELECT *,
           CASE WHEN prev_event_time IS NULL 
                     OR event_time - prev_event_time > INTERVAL '30 minutes'
                THEN 1 ELSE 0 END AS is_new_session
    FROM events_with_gap
),
sessions AS (
    SELECT *, SUM(is_new_session) OVER (PARTITION BY user_id ORDER BY event_time) AS session_id
    FROM session_flags
)
SELECT user_id, session_id, MIN(event_time) AS session_start, MAX(event_time) AS session_end, COUNT(*) AS event_count
FROM sessions
GROUP BY user_id, session_id;
```

## 5. Pivot (Rows to Columns)
**Real scenario**: Finance wants a report with quarters as columns, not rows.
```sql
SELECT
    product_id,
    SUM(CASE WHEN quarter = 'Q1' THEN sales END) AS Q1,
    SUM(CASE WHEN quarter = 'Q2' THEN sales END) AS Q2,
    SUM(CASE WHEN quarter = 'Q3' THEN sales END) AS Q3,
    SUM(CASE WHEN quarter = 'Q4' THEN sales END) AS Q4
FROM quarterly_sales
GROUP BY product_id;
```

## 6. Unpivot (Columns to Rows)
**Real scenario**: A wide table with `jan_sales, feb_sales, mar_sales` columns needs to become tidy (one row per month) for a BI tool.
```sql
-- Postgres/standard approach using UNION ALL
SELECT product_id, 'Jan' AS month, jan_sales AS sales FROM wide_sales
UNION ALL
SELECT product_id, 'Feb', feb_sales FROM wide_sales
UNION ALL
SELECT product_id, 'Mar', mar_sales FROM wide_sales;
```

## 7. Cohort Analysis
**Real scenario (SaaS/product company-style)**: "Of users who signed up in January, what % were still active in each following month?" — foundational retention metric.
```sql
WITH signup_cohort AS (
    SELECT user_id, DATE_TRUNC('month', signup_date) AS cohort_month
    FROM users
),
activity AS (
    SELECT user_id, DATE_TRUNC('month', activity_date) AS activity_month
    FROM user_activity
)
SELECT
    sc.cohort_month,
    a.activity_month,
    COUNT(DISTINCT a.user_id) AS active_users
FROM signup_cohort sc
JOIN activity a ON sc.user_id = a.user_id
GROUP BY sc.cohort_month, a.activity_month
ORDER BY sc.cohort_month, a.activity_month;
```

## 8. Funnel Analysis
**Real scenario (E-commerce-style)**: "Of users who viewed a product, how many added to cart, and how many completed checkout?"
```sql
WITH funnel AS (
    SELECT
        user_id,
        MAX(CASE WHEN event_type = 'view' THEN 1 ELSE 0 END) AS viewed,
        MAX(CASE WHEN event_type = 'add_to_cart' THEN 1 ELSE 0 END) AS added_to_cart,
        MAX(CASE WHEN event_type = 'checkout' THEN 1 ELSE 0 END) AS checked_out
    FROM events
    GROUP BY user_id
)
SELECT
    SUM(viewed) AS step1_viewed,
    SUM(added_to_cart) AS step2_added_to_cart,
    SUM(checked_out) AS step3_checked_out,
    ROUND(100.0 * SUM(added_to_cart) / NULLIF(SUM(viewed), 0), 1) AS view_to_cart_pct,
    ROUND(100.0 * SUM(checked_out) / NULLIF(SUM(added_to_cart), 0), 1) AS cart_to_checkout_pct
FROM funnel;
```

## 9. Anti-Join Pattern (find records in A that DON'T exist in B)
**Real scenario**: "Find products that have never been ordered" (candidates for delisting).
```sql
SELECT p.product_id, p.product_name
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
WHERE oi.product_id IS NULL;

-- Equivalent, often clearer/faster:
SELECT p.product_id, p.product_name
FROM products p
WHERE NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.product_id = p.product_id);
```

## Interview Traps
- Gaps & islands and sessionization look intimidating but always follow the same recipe: **generate a group marker using a window function, then GROUP BY that marker.** Recognize this pattern instantly.
- Funnel analysis questions are extremely common at product companies (Amazon, Swiggy, Uber) — practice writing conditional aggregation (`MAX(CASE WHEN ...)`) fluently.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"When the mind is still, the right solution often reveals itself without force."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
