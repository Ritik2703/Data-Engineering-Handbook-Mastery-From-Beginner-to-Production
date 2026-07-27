# 1. What is ETL / ELT? (Absolute Beginner Start)

## The Simplest Possible Explanation
Imagine your company has data scattered everywhere — customer info in one app's database, orders in another system, payment records at a third-party gateway, marketing data in Google Ads, support tickets in Zendesk. **Nobody can answer a simple business question** like "what's our total revenue by city this month?" because the data needed lives in 4 different disconnected systems in 4 different formats.

**ETL/ELT is the process of pulling all of that scattered data into ONE place (a data warehouse), in a consistent, clean, combined form, so business questions can actually be answered.**

```
ETL / ELT = Extract (get the data) + Transform (clean/combine it) + Load (store it somewhere queryable)
```

## E — Extract
Pulling raw data OUT of source systems.
```
Source systems a real company has:
- Application database (Postgres/MySQL) — orders, users, products
- Third-party SaaS APIs — Salesforce, Stripe, Zendesk, Google Ads
- Files — Excel/CSV sent by vendors or business teams, SharePoint lists
- Legacy systems — mainframe exports, SAP, on-prem Oracle
- Event streams — clickstream, app telemetry (Kafka)
```
Extraction has to handle: different formats (JSON, CSV, database rows), different access methods (API calls, direct DB queries, file drops, CDC), and doing it **without breaking the source system** (a badly-written extraction query can slow down the live application database that customers are actively using).

## T — Transform
Cleaning, reshaping, and combining the raw extracted data into something usable.
```
Examples of transformation work:
- Fix inconsistent formats: "USA", "US", "United States" -> all become "USA"
- Handle nulls/missing data: blank email fields, negative quantities that shouldn't exist
- Deduplicate: same customer submitted 3 signup forms accidentally
- Join/combine: attach customer city to every order row for easier reporting
- Aggregate: turn millions of individual transaction rows into "daily revenue per store"
- Apply business logic: calculate "customer lifetime value" using a formula the business defined
```

## L — Load
Writing the final, clean, transformed data into a destination system where business users/analysts/dashboards can query it.
```
Common destinations:
- Cloud data warehouse: Snowflake, BigQuery, Redshift, Synapse
- Data lake: S3, ADLS, GCS (for less structured/larger volume data)
```

## ETL vs ELT — The Order Actually Matters
```
ETL (traditional, pre-cloud era):
Source --Extract--> Staging Server (Transform HERE, using ETL server's own compute)
                                          |
                                    Load (clean data only)
                                          v
                                     Data Warehouse

ELT (modern, cloud era):
Source --Extract--> Load raw data AS-IS into Warehouse/Lake
                                          |
                                  Transform HERE (using the warehouse's own compute — SQL/dbt)
                                          v
                              Clean, business-ready tables
```

### Why did ETL come first?
In the 1990s-2000s, data warehouses (Teradata, on-prem Oracle) had **expensive, limited compute**. You couldn't afford to dump messy raw data into the warehouse and clean it there — that would waste precious warehouse resources. So companies bought a **separate ETL server** (running SSIS/Informatica) whose whole job was to do the cleaning/transforming BEFORE the data ever touched the expensive warehouse.

### Why did ELT take over?
Cloud warehouses (Snowflake, BigQuery, Redshift) made compute **cheap, elastic, and scalable** — you can spin up massive parallel processing power for a few minutes and pay only for that. So the smarter strategy became: **just load the raw data in immediately** (fast, simple, cheap), and do the transformation using the warehouse's own powerful SQL engine, especially now that tools like **dbt** make SQL-based transformation clean, tested, and version-controlled.

## A Real Analogy
```
ETL = Cooking the meal in the kitchen (separate prep station) before bringing it to the dining table
ELT = Bringing all the raw ingredients directly to the dining table, and cooking/plating right there
      because the dining table now has its own professional kitchen built in (cloud warehouse compute)
```

## What a Data Engineer Actually Builds (concretely)
```
1. A SCHEDULE — "run this every night at 2 AM" (Airflow, ADF trigger, cron)
2. EXTRACTION LOGIC — code/config that knows HOW to pull data from each specific source
   (API call with auth, SQL query against a source DB, reading a file from SharePoint)
3. TRANSFORMATION LOGIC — SQL/Python/dbt code that cleans, joins, and reshapes the data
4. LOAD LOGIC — code/config that writes the final data into the warehouse tables
5. MONITORING/ALERTING — so if step 2, 3, or 4 fails, someone gets notified immediately,
   not three days later when a business user complains the dashboard looks wrong
6. DATA QUALITY CHECKS — automated checks that catch bad data before it reaches step 4/5
```
Every tool covered in this module (SSIS, Informatica, ADF, Glue, dbt) is really just a different **way to build and manage these same 6 things**. Once you understand what needs to happen conceptually, learning any specific tool becomes much easier — you're just learning its particular buttons/syntax for the same underlying job.

## Try It Yourself (conceptual exercise, no coding needed yet)
Think of a real company (e.g., a food delivery app). List out:
1. What are 3 source systems it probably has? (app database, payment gateway, delivery partner API)
2. What's one transformation each source's data probably needs before it's useful?
3. What business question would the final warehouse table answer?

This exercise — thinking in terms of sources → transforms → business questions — is the actual daily mental model of a Data Engineer, regardless of which specific tool they're using.
