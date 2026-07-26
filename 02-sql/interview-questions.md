# SQL Interview Questions — 40+ with Solutions

## Beginner

**Q1. Find all customers who signed up in 2026.**
```sql
SELECT * FROM customers WHERE signup_date >= '2026-01-01' AND signup_date < '2027-01-01';
```

**Q2. Find the top 5 most expensive products.**
```sql
SELECT * FROM products ORDER BY price DESC LIMIT 5;
```

**Q3. Difference between WHERE and HAVING?**
> `WHERE` filters individual rows before grouping; `HAVING` filters groups after aggregation. You can't use an aggregate function in `WHERE` because aggregates don't exist yet at that stage of execution (see execution order in `03-aggregation-grouping.md`).

**Q4. Difference between DELETE, TRUNCATE, DROP?**
> `DELETE` removes rows (can filter with WHERE, logged row-by-row, can be rolled back); `TRUNCATE` removes ALL rows instantly (minimal logging, resets identity/auto-increment, can't filter); `DROP` removes the entire table structure and data permanently.

**Q5. What is a Primary Key vs Foreign Key?**
> Primary Key uniquely identifies each row in its own table (no NULLs, no duplicates). Foreign Key references a Primary Key in another table, enforcing referential integrity (can't insert a value that doesn't exist in the parent table).

## Intermediate — Joins & Aggregation

**Q6. Find customers who have never placed an order.**
```sql
SELECT c.* FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;
```

**Q7. Find the total revenue per customer, including customers with $0 revenue.**
```sql
SELECT c.customer_id, c.name, COALESCE(SUM(o.amount), 0) AS total_revenue
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name;
```
*(`COALESCE` replaces NULL with 0 for customers with no matching orders.)*

**Q8. Find departments with more than 10 employees.**
```sql
SELECT department_id, COUNT(*) AS emp_count
FROM employees
GROUP BY department_id
HAVING COUNT(*) > 10;
```

**Q9. Find employees who earn more than their manager.**
```sql
SELECT e.name AS employee, e.salary, m.name AS manager
FROM employees e
JOIN employees m ON e.manager_id = m.employee_id
WHERE e.salary > m.salary;
```

**Q10. What's the difference between INNER JOIN and LEFT JOIN, with an example where results differ?**
> See `02-joins.md` — INNER JOIN excludes non-matching rows entirely; LEFT JOIN keeps all left-table rows with NULLs for unmatched right-table columns. Example: customers with no orders appear (with NULL order columns) in a LEFT JOIN but disappear entirely in an INNER JOIN.

## Intermediate — Subqueries

**Q11. Find products priced above the average price.**
```sql
SELECT * FROM products WHERE price > (SELECT AVG(price) FROM products);
```

**Q12. Find the 2nd highest salary (without window functions, classic approach).**
```sql
SELECT MAX(salary) FROM employees
WHERE salary < (SELECT MAX(salary) FROM employees);
```

**Q13. Why is `NOT IN` dangerous with a subquery that might return NULL?**
> If the subquery returns even one NULL, `NOT IN` returns zero rows for the entire query (NULL comparisons are unknown, not false) — a silent, hard-to-debug bug. Always prefer `NOT EXISTS` for this logic (see `04-subqueries-ctes.md`).

## Advanced — Window Functions

**Q14. Find the 2nd highest salary per department using a window function.**
```sql
SELECT department_id, name, salary
FROM (
    SELECT department_id, name, salary,
           DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rnk
    FROM employees
) t
WHERE rnk = 2;
```

**Q15. Difference between RANK, DENSE_RANK, and ROW_NUMBER — give an example where they differ.**
> See the full worked example with tied scores in `05-window-functions.md`. Key point: RANK skips numbers after ties, DENSE_RANK doesn't, ROW_NUMBER never has ties at all.

**Q16. Calculate a 7-day rolling average of daily sales.**
```sql
SELECT date, daily_sales,
       AVG(daily_sales) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_7day_avg
FROM daily_metrics;
```

**Q17. Find each customer's first order date.**
```sql
SELECT DISTINCT customer_id,
       FIRST_VALUE(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) AS first_order_date
FROM orders;
```

**Q18. Month-over-month growth rate of user signups.**
```sql
SELECT month, signups,
       ROUND(100.0 * (signups - LAG(signups) OVER (ORDER BY month)) / LAG(signups) OVER (ORDER BY month), 1) AS growth_pct
FROM monthly_signups;
```

## Advanced — Patterns

**Q19. Remove duplicate rows, keeping only the latest by `updated_at`.**
```sql
WITH ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at DESC) AS rn
    FROM raw_table
)
SELECT * FROM ranked WHERE rn = 1;
```

**Q20. Find users with a 5+ day consecutive login streak.**
> See the gaps & islands solution in `06-advanced-sql-patterns.md` — subtract a row number from the date to create a constant grouping key for consecutive dates.

**Q21. Write a query for a funnel: view → add to cart → purchase conversion rates.**
> See Business Question in `06-advanced-sql-patterns.md` — use `MAX(CASE WHEN event_type = 'x' THEN 1 ELSE 0 END)` per user, then aggregate.

**Q22. Explain how you'd implement SCD Type 2 in SQL.**
> See the `MERGE` pattern in `06-advanced-sql-patterns.md` and full explanation in `01-fundamentals/03-data-modeling.md` — close the old row (`end_date`, `is_current = FALSE`) and insert a new row for the changed record.

## Advanced — Optimization

**Q23. Why might an index not be used even though it exists on the filtered column?**
> Common causes: wrapping the column in a function (`YEAR(date_col)`), implicit type mismatch, low/stale table statistics, or the optimizer deciding a full scan is actually cheaper for a very unselective filter (e.g., filtering `status = 'active'` when 90% of rows are active).

**Q24. What is a covering index and why does it help?**
> An index that includes all columns a query needs, so the engine can answer entirely from the index without touching the base table (Index Only Scan) — see `07-query-optimization-indexing.md`.

**Q25. How would you optimize `SELECT * FROM orders WHERE UPPER(status) = 'DELIVERED'`?**
> Normalize the `status` column values at write time (always lowercase) instead of transforming at read time, so the query becomes sargable: `WHERE status = 'delivered'`, allowing index use.

## Advanced — Transactions

**Q26. What is a deadlock and how do you prevent it?**
> Two transactions circularly waiting on each other's locks. Prevent by always acquiring/updating rows in a consistent order across the application (see `08-transactions-concurrency.md`).

**Q27. Explain MVCC in one sentence.**
> Multi-Version Concurrency Control lets readers see a consistent snapshot of data as of when their transaction started, without blocking concurrent writers, and vice versa.

## System-Design-Adjacent SQL Questions (common at product companies)

**Q28. Design a query to compute monthly active users (MAU).**
```sql
SELECT DATE_TRUNC('month', activity_date) AS month, COUNT(DISTINCT user_id) AS mau
FROM user_activity
GROUP BY DATE_TRUNC('month', activity_date);
```

**Q29. Design a cohort retention query.**
> See the full Netflix-style cohort analysis in `case-studies/netflix-spotify-engagement.md`.

**Q30. How would you detect fraud patterns using only SQL?**
> See `case-studies/fintech-fraud-detection.md` — `LAG()`-based rapid-transaction detection, spend-spike detection, impossible-travel detection.

## Rapid-Fire Conceptual Questions
31. What's the difference between a clustered and non-clustered index? *(One physically orders table rows, only one per table; the other is a separate structure pointing back to rows, can have many.)*
32. What's the difference between UNION and UNION ALL? *(UNION removes duplicates, requires a sort/dedup step — slower; UNION ALL keeps everything — faster.)*
33. What does `COALESCE` do? *(Returns the first non-NULL value from a list of arguments.)*
34. What's the difference between `CHAR` and `VARCHAR`? *(CHAR is fixed-length, padded with spaces; VARCHAR is variable-length, no padding.)*
35. What is a self-join and give a real example. *(Joining a table to itself — e.g., finding employees earning more than their manager, from the same `employees` table.)*
36. What does `GROUP BY ROLLUP` do? *(Adds subtotal and grand-total rows in addition to the normal grouped rows — see `03-aggregation-grouping.md`.)*
37. Explain the logical query execution order. *(FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT.)*
38. What's a materialized view and why use one? *(A precomputed, physically stored query result — speeds up expensive repeated aggregations without recomputing from scratch.)*
39. What's the difference between `EXISTS` and `IN`? *(EXISTS checks for any matching row and short-circuits; handles NULLs safely; often faster on large subqueries. See `04-subqueries-ctes.md`.)*
40. How do you handle slowly changing data in a dimension table? *(SCD Type 2 — new row per change with effective dates and a current flag.)*

---

**Practice tip**: Don't memorize these answers word-for-word. Open [`sql-playground.html`](./sql-playground.html), rebuild each query yourself against the sample schema, and explain out loud *why* you reached for that specific concept. That's what actually gets tested in a live interview.
