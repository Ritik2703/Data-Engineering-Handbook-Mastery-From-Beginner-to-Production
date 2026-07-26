# 5. Window Functions — The #1 Most-Asked Interview Topic

## Why Window Functions Exist
Normal `GROUP BY` collapses rows into one row per group — you lose the individual row detail. **Window functions let you calculate an aggregate WHILE keeping every original row visible.** This is the single most important "aha" moment in intermediate SQL.

```sql
-- GROUP BY: one row per customer (loses individual order rows)
SELECT customer_id, SUM(amount) FROM orders GROUP BY customer_id;

-- Window function: every order row IS kept, PLUS the customer's total is attached to each row
SELECT customer_id, order_id, amount,
       SUM(amount) OVER (PARTITION BY customer_id) AS customer_total
FROM orders;
```

## Anatomy of a Window Function
```sql
FUNCTION() OVER (
    PARTITION BY column   -- "group" for the window (optional — omit for whole table)
    ORDER BY column        -- order within each partition (needed for ranking/running totals)
    ROWS/RANGE BETWEEN ... -- frame boundary (optional, advanced)
)
```

## ROW_NUMBER() — Unique Sequential Number
**Real scenario (Amazon-style)**: "Get each customer's most recent order" (a very common production pattern).
```sql
WITH ranked AS (
    SELECT *, 
           ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS rn
    FROM orders
)
SELECT * FROM ranked WHERE rn = 1;
```
This same pattern is THE standard way to **deduplicate** data in ETL pipelines (keep latest record per key) — see `06-advanced-sql-patterns.md`.

## RANK() vs DENSE_RANK() vs ROW_NUMBER() — the classic interview trio
```sql
-- Sample: scores 100, 90, 90, 80
SELECT name, score,
       ROW_NUMBER() OVER (ORDER BY score DESC) AS row_num,
       RANK()       OVER (ORDER BY score DESC) AS rank_val,
       DENSE_RANK() OVER (ORDER BY score DESC) AS dense_rank_val
FROM scores;
```
| name | score | ROW_NUMBER | RANK | DENSE_RANK |
|---|---|---|---|---|
| A | 100 | 1 | 1 | 1 |
| B | 90 | 2 | 2 | 2 |
| C | 90 | 3 | 2 | 2 |
| D | 80 | 4 | 4 | 3 |

- **ROW_NUMBER**: always unique, no ties — arbitrary tiebreak order.
- **RANK**: ties share the same rank, but **skips** the next rank(s) (2, 2, then jumps to 4).
- **DENSE_RANK**: ties share the same rank, **no gaps** (2, 2, then 3).

**Real scenario (Swiggy-style leaderboard)**: "Top 3 restaurants by revenue per city" — must decide: do restaurants tied for 3rd BOTH count as "top 3"? That decision determines RANK vs DENSE_RANK vs ROW_NUMBER choice.

## Nth Highest Value (classic interview question, solved properly)
**Real scenario**: "Find the 2nd highest-paid employee per department."
```sql
SELECT department_id, name, salary
FROM (
    SELECT department_id, name, salary,
           DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rnk
    FROM employees
) ranked
WHERE rnk = 2;
```
> Use `DENSE_RANK` here, not `ROW_NUMBER` — if two people are tied for highest salary, `ROW_NUMBER` would arbitrarily call one of them "2nd highest" which is wrong; `DENSE_RANK` correctly treats the next distinct value as 2nd.

## Running Totals — SUM() OVER
**Real scenario (Finance/banking-style)**: "Running account balance after each transaction."
```sql
SELECT transaction_id, transaction_date, amount,
       SUM(amount) OVER (PARTITION BY account_id ORDER BY transaction_date) AS running_balance
FROM transactions;
```

## LAG() and LEAD() — Compare to Previous/Next Row
**Real scenario (Netflix/Spotify-style)**: "Month-over-month growth in subscribers."
```sql
SELECT month, subscriber_count,
       LAG(subscriber_count) OVER (ORDER BY month) AS prev_month_count,
       subscriber_count - LAG(subscriber_count) OVER (ORDER BY month) AS mom_change,
       ROUND(100.0 * (subscriber_count - LAG(subscriber_count) OVER (ORDER BY month))
             / LAG(subscriber_count) OVER (ORDER BY month), 2) AS mom_growth_pct
FROM monthly_subscribers;
```
**Real scenario (Uber-style)**: "Time between consecutive rides for a driver" (used to detect idle time / suggest better positioning).
```sql
SELECT driver_id, trip_id, trip_start_time,
       LAG(trip_end_time) OVER (PARTITION BY driver_id ORDER BY trip_start_time) AS prev_trip_end,
       trip_start_time - LAG(trip_end_time) OVER (PARTITION BY driver_id ORDER BY trip_start_time) AS idle_time
FROM trips;
```

## FIRST_VALUE() / LAST_VALUE()
**Real scenario**: "Compare each order's amount to that customer's very first order amount" (detecting spend growth/decline per customer).
```sql
SELECT customer_id, order_id, order_date, amount,
       FIRST_VALUE(amount) OVER (PARTITION BY customer_id ORDER BY order_date) AS first_order_amount
FROM orders;
```

## NTILE() — Bucketing into N groups
**Real scenario (Marketing segmentation)**: "Split customers into 4 spending quartiles (VIP, High, Medium, Low)."
```sql
SELECT customer_id, total_spent,
       NTILE(4) OVER (ORDER BY total_spent DESC) AS spend_quartile
FROM customer_totals;
```

## Frame Clauses (ROWS/RANGE) — Advanced Control
**Real scenario**: "7-day rolling average of daily active users" (extremely common in growth/analytics dashboards).
```sql
SELECT date, daily_active_users,
       AVG(daily_active_users) OVER (
           ORDER BY date
           ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ) AS rolling_7day_avg
FROM daily_metrics;
```

## Window Functions vs GROUP BY — Decision Guide
```
Need ONE row per group, don't need individual row detail  -> GROUP BY
Need to KEEP every row but attach an aggregate/rank/comparison to it -> Window Function
Need "Nth highest per group", "latest record per key",
  "running total", "compare to previous row"               -> Window Function, almost always
```

## Try It Yourself (in the playground)
1. Rank customers by total spend using `DENSE_RANK`.
2. Find each customer's first and most recent order using `ROW_NUMBER`.
3. Calculate a running total of daily revenue.
4. Calculate month-over-month order count growth using `LAG`.

## Interview Traps
- RANK vs DENSE_RANK vs ROW_NUMBER — expect this in almost every SQL interview; know the exact tie-handling difference.
- "Find 2nd/3rd/Nth highest X per group" is asked so often it's worth memorizing the `DENSE_RANK` + subquery/CTE pattern exactly.
- Window functions execute **after** `WHERE`/`GROUP BY`/`HAVING` but **before** `ORDER BY`/`LIMIT` in logical processing order — you cannot filter directly on a window function result in the same-level `WHERE` (must wrap in a subquery/CTE, as shown above).
