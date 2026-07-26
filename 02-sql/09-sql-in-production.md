# 9. SQL in Production (What Product Companies Actually Do)

## SQL Dialect Differences (know these — they trip people up in real jobs)

| Feature | PostgreSQL | MySQL | Snowflake | BigQuery | SQL Server |
|---|---|---|---|---|---|
| Limit rows | `LIMIT n` | `LIMIT n` | `LIMIT n` | `LIMIT n` | `TOP n` (different syntax placement) |
| String concat | `\|\|` | `CONCAT()` | `\|\|` or `CONCAT()` | `CONCAT()` | `+` |
| Current date | `CURRENT_DATE` | `CURDATE()` | `CURRENT_DATE()` | `CURRENT_DATE()` | `GETDATE()` |
| Auto-increment ID | `SERIAL` / `GENERATED ALWAYS AS IDENTITY` | `AUTO_INCREMENT` | `AUTOINCREMENT` | N/A (use `GENERATE_UUID()`) | `IDENTITY` |
| Regex match | `~` | `REGEXP` | `RLIKE` | `REGEXP_CONTAINS()` | Requires CLR/custom function |
| Semi-structured (JSON) | `->`, `->>`, `jsonb` | `JSON_EXTRACT()` | `:` (dot notation on VARIANT) | `JSON_EXTRACT()` | `JSON_VALUE()` |
| Case-insensitive compare | `ILIKE` | `LIKE` (case-insensitive by default in most collations) | `ILIKE` | `LOWER(a) = LOWER(b)` | Depends on collation |

> Real job tip: interviews and take-home tests will often specify a dialect ("assume Postgres", "assume Snowflake") — always confirm which one, since these small differences matter for exact syntax.

## dbt-Style SQL (how transformation logic is actually written at modern companies)
Modern product companies (post-2019 especially) write almost all warehouse SQL through **dbt** — SQL files organized in layers, version-controlled, tested.

```
models/
  staging/
    stg_orders.sql       -- 1:1 with source, light cleaning/renaming only
  intermediate/
    int_orders_with_customer.sql   -- joins, business logic building blocks
  marts/
    fct_orders.sql       -- final, business-ready fact table
    dim_customer.sql     -- final dimension table
```

**Staging layer** (`stg_orders.sql`) — clean and rename, nothing fancy:
```sql
SELECT
    order_id,
    customer_id,
    CAST(amount AS NUMERIC(10,2)) AS amount,
    LOWER(TRIM(status)) AS status,
    CAST(created_at AS TIMESTAMP) AS order_created_at
FROM {{ source('raw', 'orders') }}
```

**Mart layer** (`fct_orders.sql`) — business logic, references other models via `{{ ref() }}`:
```sql
SELECT
    o.order_id,
    o.customer_id,
    c.customer_segment,
    o.amount,
    o.status
FROM {{ ref('stg_orders') }} o
LEFT JOIN {{ ref('dim_customer') }} c ON o.customer_id = c.customer_id
```

**Why this matters**: `{{ ref() }}` builds a dependency graph automatically — dbt knows to build `stg_orders` before `fct_orders`, and can generate a visual lineage graph. This is the actual day-to-day SQL-writing experience at most modern data teams, not one giant monolithic query.

## SQL Style Guide (what senior engineers expect in code review)
```sql
-- GOOD: readable, consistent casing, CTEs for each logical step
WITH customer_orders AS (
    SELECT
        customer_id,
        COUNT(*) AS order_count,
        SUM(amount) AS total_spent
    FROM orders
    WHERE order_date >= '2026-01-01'
    GROUP BY customer_id
)
SELECT
    c.customer_id,
    c.name,
    co.order_count,
    co.total_spent
FROM customers c
JOIN customer_orders co ON c.customer_id = co.customer_id
ORDER BY co.total_spent DESC;
```
Conventions:
- SQL keywords in `UPPERCASE`, identifiers in `lowercase_snake_case`
- One clause per line for anything non-trivial (helps diffs in git/PRs)
- Always alias tables when joining 2+ tables, use meaningful short aliases (`c` for customers, `o` for orders)
- CTEs named descriptively (`customer_orders`, not `cte1`)
- Explicit column lists — avoid `SELECT *` in any model that will be built on top of

## Data Quality Tests in Production SQL (dbt tests, conceptually)
```yaml
# schema.yml
models:
  - name: fct_orders
    columns:
      - name: order_id
        tests: [unique, not_null]
      - name: status
        tests:
          - accepted_values:
              values: ['pending', 'completed', 'cancelled']
      - name: customer_id
        tests:
          - relationships:
              to: ref('dim_customer')
              field: customer_id
```
This is how production teams catch bad data automatically — every model has tests that run on every deploy, not just manual spot-checks.

## Query Cost Awareness in Cloud Warehouses (real production concern)
```sql
-- BigQuery: this could scan terabytes and cost real money if the table is huge/unpartitioned
SELECT * FROM `project.dataset.huge_events_table`;

-- Always filter on partition column first
SELECT * FROM `project.dataset.huge_events_table`
WHERE event_date = '2026-07-25';
```
Senior engineers get paged/questioned in Slack when a single query burns an unexpectedly large compute bill — cost-consciousness is a real, daily production skill, not just a performance nicety.

## Version Control for SQL
All production SQL (dbt models, stored procedures, migration scripts) lives in **Git**, goes through **PR review**, and deploys via **CI/CD** — never edited directly in a warehouse console for anything beyond ad-hoc exploration. See `10-devops/` in this repo for the CI/CD pattern.

## Interview Traps
- Being asked "write this in SQL" without a specified dialect — always ask/clarify, and mention the dialect you're assuming if not told.
- "How do you ensure data quality in a dbt-based warehouse?" — mention `dbt test` (unique, not_null, accepted_values, relationships) as the standard answer.
