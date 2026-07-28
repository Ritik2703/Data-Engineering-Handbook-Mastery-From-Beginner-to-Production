# 3. Tableau — Deep Dive

## Tableau's Core Philosophy
Tableau's founding insight: visual data exploration should feel as natural and immediate as DRAWING — drag a field onto a shelf, see the chart appear/update INSTANTLY, iterate visually rather than writing code or configuring dialog boxes repeatedly. This "direct manipulation" philosophy remains Tableau's defining strength even against newer competitors.

## Architecture — Extract vs Live Connection
```
LIVE Connection: Tableau sends a query to the SOURCE DATABASE every time
                 you interact with the dashboard (change a filter, drill down)
                 - Always shows CURRENT data
                 - Adds real query load to the source database on every interaction
                 - Performance depends entirely on the source database's speed

EXTRACT (.hyper file): Tableau pulls a SNAPSHOT of the data into its own
                        optimized, COLUMNAR internal format (.hyper)
                        - Much faster interaction (no live database round-trip)
                        - Data is only as fresh as the last extract refresh
                        - Needs a scheduled refresh (via Tableau Server/Cloud)
                        to stay reasonably current
```
**Real production guidance**: extracts are usually preferred for dashboards viewed frequently by many users (better performance, less source database load); live connections are chosen when genuinely real-time/current data is a hard requirement (e.g., an operations monitoring dashboard) and the source database can handle the query load.

## Dimensions vs Measures — The Fundamental Data Model
```
Dimensions: qualitative/categorical fields used to SLICE data (Region,
            Product Category, Customer Name) — typically NOT aggregated
Measures: quantitative/numeric fields that get AGGREGATED (Sales Amount,
          Quantity, Profit) — SUM, AVG, COUNT, etc. applied to these
```
This dimension/measure split maps directly onto the star schema concept from `01-fundamentals/03-data-modeling.md` — Dimensions correspond to your dimension tables' attributes, Measures correspond to your fact table's numeric columns — understanding this connection helps a Data Engineer design warehouse tables that map cleanly onto how Tableau (and Power BI) naturally want to consume data.

## Calculated Fields — Tableau's Formula Layer
```
-- Simple calculated field
IF [Sales] > 1000 THEN "High Value" ELSE "Low Value" END

-- Using built-in functions
DATEDIFF('day', [Order Date], [Ship Date])

-- String manipulation
LEFT([Product Code], 3)
```

## LOD (Level of Detail) Expressions — Tableau's Most Powerful, Most Confusing Feature
```
The core problem LOD solves: a normal calculated field/aggregation respects
the CURRENT VIEW's level of detail (whatever dimensions are on the current
chart) — but sometimes you need a calculation at a DIFFERENT granularity
than what's currently displayed.

{FIXED [Customer ID] : SUM([Sales])}
  Computes total sales PER CUSTOMER, regardless of what other dimensions
  are currently in the view — e.g., you can show this customer-level total
  on a chart that's actually broken down by REGION and DATE, letting you
  compare "this order's amount" against "this customer's ALL-TIME total"
  in the same view.

{INCLUDE [Customer ID] : AVG([Sales])}
  Computes at a MORE granular level than the current view, then aggregates
  UP — useful for "average per customer" style calculations shown at a
  coarser (e.g., regional) level.

{EXCLUDE [Region] : SUM([Sales])}
  Computes IGNORING a specific dimension that's otherwise in the view —
  e.g., total company-wide sales shown alongside a region-level breakdown.
```
**Real scenario (why LOD genuinely matters)**: "show each customer's percentage of their OWN total spend that came from this specific product category" requires comparing a category-level number against a CUSTOMER-level total simultaneously in the same view — exactly the kind of multi-granularity calculation LOD expressions are built for, and a very common real business request.

## Table Calculations — A Different Kind of "Different Granularity" Tool
```
Running Total, Percent of Total, Rank, Moving Average — these are computed
AFTER the main query returns results, operating across the ROWS of the
CURRENT VIEW specifically (unlike LOD, which affects the underlying query
itself) — conceptually similar to SQL window functions
(`02-sql/05-window-functions.md`), but computed client-side over
whatever's currently displayed.
```

## Joins vs Blending — Combining Multiple Data Sources
```
JOINING: combine tables at the DATA SOURCE level (same connection, or
         compatible connections) — happens BEFORE aggregation, like a SQL JOIN

BLENDING: combine data from DIFFERENT, INDEPENDENT data sources
          (e.g., a Salesforce data source blended with an Excel file) —
          each source is aggregated SEPARATELY first, then combined at
          the dashboard level on a shared linking field — less flexible
          than joining, but necessary when sources genuinely can't be
          joined at the database level
```

## Publishing to Tableau Server/Cloud — The Governance Layer
Once a dashboard is built, publishing to Tableau Server (self-hosted) or Tableau Cloud (SaaS) provides: centralized access control (row-level security, so different users see only their permitted data), scheduled extract refreshes (tied to when upstream ETL pipelines actually finish — a real integration point with the orchestration tools from module 08), and usage analytics (which dashboards are actually being used, informing what to maintain vs retire).

## Interview Traps
- "Live connection vs extract — how do you choose?" — extracts for performance/reduced source load on frequently-viewed dashboards; live connections when genuinely current data is a hard requirement and the source can handle the query load.
- "Explain an LOD expression with a real business example." — the "customer's share of their own total spend by category" example above demonstrates genuine understanding better than reciting the FIXED/INCLUDE/EXCLUDE syntax alone.
- "Joining vs blending — what's the real difference?" — joining combines data at the source/query level before aggregation (like SQL JOIN); blending aggregates each source separately first, then combines at the dashboard level — a meaningfully different, less flexible mechanism used when sources can't be joined directly.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The truest test of learning is not what you remember, but how you act because of it."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
