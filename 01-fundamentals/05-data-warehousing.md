# 5. Data Warehousing

## OLTP vs OLAP (recap + deeper)
| | OLTP | OLAP |
|---|---|---|
| Purpose | Run the business (transactions) | Analyze the business (insights) |
| Schema | Normalized (3NF) | Denormalized (Star/Snowflake) |
| Query pattern | Short, simple, high frequency | Complex, aggregations, scans over large data |
| Users | Application, end customers | Analysts, executives, BI tools |
| Examples | App's Postgres/MySQL DB | Snowflake, BigQuery, Redshift, Synapse |

## MPP (Massively Parallel Processing) Architecture
Modern cloud warehouses (Redshift, Synapse, older Teradata) use MPP: data is distributed across many compute nodes, and each node processes its own slice of data in parallel, then results are combined.
```
                     Leader/Coordinator Node
                    (parses query, plans, combines results)
                              │
        ┌─────────────────────┼─────────────────────┐
   Compute Node 1        Compute Node 2         Compute Node 3
  (slice of data)       (slice of data)        (slice of data)
```
**Snowflake's twist**: fully separates storage (shared, in cloud object storage) from compute (independent "virtual warehouses" that can scale up/down/pause independently) — this is why Snowflake/BigQuery pricing separates storage cost from compute cost.

## Distribution & Sort Keys (Redshift/Synapse-style warehouses)
- **Distribution key**: determines which node stores each row — choose a high-cardinality column used in joins (e.g., `customer_id`) to minimize data shuffling between nodes during joins.
- **Sort key**: determines physical row order on disk — choose commonly filtered columns (e.g., `order_date`) so range queries skip irrelevant blocks (zone maps/min-max pruning).

## Partitioning & Clustering (BigQuery/Snowflake-style)
- **Partitioning**: physically splits a table by a column (usually date) — queries filtering on that column scan only relevant partitions (huge cost/speed win).
- **Clustering**: sorts data within partitions by additional columns — further prunes scanned data for filters on those columns.

```sql
-- BigQuery example
CREATE TABLE sales.fct_orders
PARTITION BY DATE(order_date)
CLUSTER BY region, product_category
AS SELECT * FROM staging.orders;
```

## Semantic Layer / Metrics Layer
A layer that defines business metrics **once**, consistently, so every tool (Power BI, Tableau, ad-hoc SQL) uses the same definition of "Active User" or "Revenue" instead of every analyst writing slightly different logic.
- Traditional: defined inside BI tool (Power BI measures, Tableau calculated fields) — risk of inconsistency across tools.
- Modern: **dbt Semantic Layer**, **Cube**, **LookML (Looker)** — metric defined once in code, queried by any downstream tool via API.

## Materialized Views
Precomputed query results stored physically, refreshed on a schedule or incrementally — speeds up expensive repeated aggregations without recomputing from scratch every time.
```sql
CREATE MATERIALIZED VIEW mv_daily_sales AS
SELECT sale_date, region, SUM(amount) AS total_sales
FROM fct_orders
GROUP BY sale_date, region;
```

## Data Warehouse vs Data Lake vs Lakehouse (recap + why it evolved)
```
2000s: Data Warehouse only (structured, expensive, rigid schema-on-write)
        ↓ problem: couldn't handle unstructured/semi-structured data cheaply
2010s: Data Lake added (S3/HDFS, cheap, schema-on-read, any file type)
        ↓ problem: lakes became "data swamps" — no ACID, no schema enforcement, hard to trust
2020s: Lakehouse (Delta Lake/Iceberg/Hudi) — ACID transactions + schema enforcement
        + time travel, ON TOP of cheap lake storage — best of both worlds
```

## Cost Optimization in Cloud Warehouses (real production concern)
1. **Partition pruning** — always filter on partition columns to avoid full scans
2. **Right-size compute** — Snowflake warehouses/BigQuery slots shouldn't run bigger than needed
3. **Auto-suspend** idle compute (Snowflake auto-suspend, BigQuery is serverless by default)
4. **Materialize expensive repeated queries** instead of recomputing
5. **Monitor `bytes scanned`** (BigQuery bills per TB scanned) — `SELECT *` on huge tables is a common cost mistake

## Interview Traps
- Explain WHY separating storage and compute (Snowflake/BigQuery model) was a big deal — it lets you scale each independently and pay only for what you use, vs traditional fixed-cluster warehouses (Teradata/on-prem) where you pay for peak capacity 24/7.
- Distribution key choice can make or break MPP query performance — a bad choice causes "data skew" (one node doing most of the work while others idle).


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Small, consistent effort every day outperforms burst of motivation once a month."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
