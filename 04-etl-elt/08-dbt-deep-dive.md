# 8. dbt (Data Build Tool) — Deep Dive

## What dbt Is and Why It's THE Modern ELT Transformation Standard
dbt handles ONLY the **T** (Transform) in ELT — it assumes data is already extracted and loaded (raw) into your warehouse (by Fivetran/Airbyte/a custom Python extractor/ADF/Glue), and its whole job is turning that raw data into clean, tested, documented, business-ready tables using **just SQL** (plus a templating layer called Jinja) — no Spark cluster, no Python required for the core workflow.

**Why it took over from SSIS/Informatica-style transformation for new builds**: transformation logic becomes **version-controlled, testable, and documented SQL files** living in Git — reviewed via pull requests exactly like application code — instead of GUI-based mappings/packages that are hard to diff, hard to code-review, and hard to test automatically.

## Project Structure
```
my_dbt_project/
├── models/
│   ├── staging/
│   │   ├── stg_orders.sql
│   │   ├── stg_customers.sql
│   │   └── sources.yml          -- defines the RAW source tables dbt reads from
│   ├── intermediate/
│   │   └── int_orders_enriched.sql
│   └── marts/
│       ├── fct_orders.sql
│       ├── dim_customer.sql
│       └── schema.yml            -- defines TESTS and documentation for these models
├── macros/
│   └── cents_to_dollars.sql      -- reusable SQL snippets (like a SQL "function")
├── tests/
│   └── assert_positive_amounts.sql
├── dbt_project.yml                -- project configuration
└── profiles.yml                   -- warehouse connection details (per environment)
```

## A Model — Just a SELECT Statement in a `.sql` File
```sql
-- models/staging/stg_orders.sql
-- dbt automatically wraps this in a CREATE VIEW/TABLE AS — you only write the SELECT
{{ config(materialized='view') }}

SELECT
    order_id,
    customer_id,
    CAST(amount AS NUMERIC(10,2)) AS amount,
    LOWER(TRIM(status)) AS status,
    CAST(created_at AS TIMESTAMP) AS order_created_at
FROM {{ source('raw', 'orders') }}
WHERE order_id IS NOT NULL
```
`{{ source('raw', 'orders') }}` references a source table defined in `sources.yml` — dbt tracks this as a dependency, enabling automatic lineage graphs and freshness checks.

## Referencing Other Models — `{{ ref() }}` (the core dbt magic)
```sql
-- models/marts/fct_orders.sql
{{ config(materialized='table') }}

SELECT
    o.order_id,
    o.customer_id,
    c.customer_segment,
    o.amount,
    o.status
FROM {{ ref('stg_orders') }} o
LEFT JOIN {{ ref('dim_customer') }} c ON o.customer_id = c.customer_id
```
`{{ ref() }}` does two things: (1) resolves to the correct fully-qualified table name in whatever environment you're running in (dev schema vs prod schema), and (2) **automatically builds a dependency graph** — dbt knows `stg_orders` and `dim_customer` must be built BEFORE `fct_orders`, without you writing any explicit orchestration logic. Run `dbt docs generate` and you get a full visual lineage graph of your entire warehouse for free.

## Materializations — How a Model Gets Built
| Materialization | Behavior | Use Case |
|---|---|---|
| **view** | Creates a SQL view (no data duplication, always live) | Staging models, lightweight/frequently-changing logic |
| **table** | Creates a physical table (data copied, faster to query, needs rebuild to refresh) | Mart/fact tables queried heavily by BI tools |
| **incremental** | Only processes NEW/changed rows on subsequent runs, appends/merges into existing table | Very large fact tables where full rebuild is too slow/expensive |
| **ephemeral** | Not built as a database object at all — inlined as a CTE into whatever references it | Small reusable logic snippets that don't need their own table/view |

### Incremental Models (dbt's answer to watermark-based incremental loads)
```sql
-- models/marts/fct_orders.sql
{{ config(materialized='incremental', unique_key='order_id') }}

SELECT order_id, customer_id, amount, status, updated_at
FROM {{ source('raw', 'orders') }}

{% if is_incremental() %}
  WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
{% endif %}
```
`{% if is_incremental() %}` is Jinja templating — this WHERE clause only applies on incremental runs (not the very first full build), and `{{ this }}` refers to the model's own already-built table, letting dbt automatically find "the last watermark" without a separate control table.

## Tests — Automated Data Quality, Built Into the Framework
```yaml
# models/marts/schema.yml
models:
  - name: fct_orders
    columns:
      - name: order_id
        tests: [unique, not_null]
      - name: status
        tests:
          - accepted_values:
              values: ['pending', 'delivered', 'cancelled', 'returned']
      - name: customer_id
        tests:
          - relationships:
              to: ref('dim_customer')
              field: customer_id
```
Run `dbt test` and every one of these checks runs automatically — `unique`/`not_null`/`accepted_values`/`relationships` are dbt's built-in "generic tests"; you can also write fully custom SQL-based tests (a query that should return zero rows if data is valid) in the `tests/` folder. This is the direct dbt equivalent of the manual DQ checks/Great Expectations covered in `03-python/12-data-quality-validation.md` — but native to the transformation layer itself, run as part of every deploy.

## Macros — Reusable SQL Logic (dbt's "functions")
```sql
-- macros/cents_to_dollars.sql
{% macro cents_to_dollars(column_name) %}
    ({{ column_name }} / 100.0)
{% endmacro %}
```
```sql
-- used in any model:
SELECT order_id, {{ cents_to_dollars('amount_cents') }} AS amount_dollars
FROM {{ ref('stg_orders') }}
```
Macros prevent copy-pasting the same SQL logic across dozens of models — exactly like a function in regular programming, but for SQL snippets.

## Snapshots — dbt's Built-In SCD Type 2 Implementation
```sql
-- snapshots/customer_snapshot.sql
{% snapshot customer_snapshot %}
{{
    config(
      target_schema='snapshots',
      unique_key='customer_id',
      strategy='timestamp',
      updated_at='updated_at',
    )
}}
SELECT * FROM {{ source('raw', 'customers') }}
{% endsnapshot %}
```
Running `dbt snapshot` automatically maintains full SCD Type 2 history (`dbt_valid_from`, `dbt_valid_to` columns) for the `customers` source — this is dbt's direct, much simpler answer to the manual SCD2 MERGE logic covered in `02-sql/06-advanced-sql-patterns.md` and the SSIS/Informatica SCD2 patterns in files 3 and 4 of this module.

## Orchestrating dbt in Production
dbt itself does NOT schedule anything — it needs an orchestrator to trigger `dbt run`/`dbt test` on a schedule:
```
Airflow (BashOperator or the dbt-specific Cosmos/Astronomer provider) -> dbt run --select fct_orders+
ADF (Web Activity calling dbt Cloud API, or a Databricks Notebook Activity running dbt)
dbt Cloud (dbt Labs' own managed scheduler/orchestrator, if not using Airflow/ADF)
```

## Real Enterprise Example: SaaS Company's Modern ELT Stack
```
Fivetran (managed EL connectors) -> raw tables in Snowflake (raw schema, untouched copies of Salesforce/Stripe/app DB)
        |
dbt (staging models: clean/rename/type-cast each raw source, 1:1)
        |
dbt (intermediate models: join staging models together, apply business logic)
        |
dbt (mart models: final fct_/dim_ tables, tested via schema.yml, documented via dbt docs)
        |
Airflow (triggers `dbt run` + `dbt test` nightly, alerts Slack on any test failure)
        |
Looker / Power BI (business users query the mart layer directly)
```
This "Fivetran + dbt + Snowflake + Airflow" combination (sometimes swapping any one piece for an equivalent) is close to the most common modern data stack at product companies building fresh in 2024-2026 — a direct contrast to the SSIS/Informatica-centric stacks common at older enterprises.

## Interview Traps
- "How does dbt know the order to build models in?" — the dependency graph built automatically from `{{ ref() }}` calls between models; no manual orchestration logic needed within dbt itself.
- "How do you implement SCD Type 2 in dbt?" — Snapshots, not a hand-written MERGE (though know the manual SQL pattern too, since it's still asked and Snapshots use it internally).
- "Difference between a dbt test and Great Expectations?" — dbt tests are lightweight, SQL-based, and live directly alongside the transformation models they test; Great Expectations is a more comprehensive standalone framework often used earlier in the pipeline (validating raw/staged data before it even reaches dbt) or for more complex statistical/distributional checks.
