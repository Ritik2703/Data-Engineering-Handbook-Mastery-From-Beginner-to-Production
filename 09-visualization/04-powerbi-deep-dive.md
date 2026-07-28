# 4. Power BI — Deep Dive

## Power BI's Core Philosophy
Power BI's defining strategy: meet business users where they ALREADY are — familiar Excel-like formulas (DAX deliberately resembles Excel functions), tight Office 365 integration, and an aggressive price point that made self-service BI accessible to companies that couldn't justify Tableau's historically higher enterprise pricing. This strategy is directly why Power BI has become the most widely deployed BI tool by user count in many markets today.

## The Three Core Components
```
Power Query: the DATA LOADING/TRANSFORMATION layer (same engine as Excel's
             Power Query, see file 2) — connects to sources, cleans/reshapes
             data BEFORE it enters the model

Data Model: defines TABLES and RELATIONSHIPS between them (exactly the star
            schema concepts from `01-fundamentals/03-data-modeling.md` —
            fact tables, dimension tables, and the relationships connecting them)

DAX (Data Analysis Expressions): the FORMULA language for creating Measures
     and calculated columns — see file 5 for full depth
```

## Power Query — Transform Before Loading
```
# Power Query steps (recorded, repeatable, similar in spirit to a dbt
# staging model's cleaning logic) — each step visible and editable:
1. Source: Connect to SQL Server database
2. Remove Columns: drop unnecessary columns
3. Changed Type: cast "OrderDate" column to Date type
4. Filtered Rows: keep only Status = "Completed"
5. Merged Queries: join with the Customer table (Power Query's UI-based JOIN)
```
Each step is preserved and re-appliable — refreshing the report re-runs this ENTIRE recorded transformation sequence against the current source data automatically, without manual redo.

## The Data Model — Star Schema in Practice
```
Power BI STRONGLY recommends (and performs best with) a proper star schema:
  fact_sales (many rows, numeric measures, foreign keys to dimensions)
  dim_customer, dim_product, dim_date (fewer rows, descriptive attributes)

Relationships are defined in the Model view — typically ONE-TO-MANY from
a dimension to a fact table, with a chosen CROSS-FILTER DIRECTION
(single vs bidirectional) controlling how filtering one table affects
related tables — a subtle but important setting that affects both
performance and calculation correctness.
```
**Real production guidance**: importing a single, giant, flat denormalized table (instead of a proper star schema) is a very common Power BI beginner mistake — it works for small datasets but degrades badly in performance and calculation flexibility (especially with DAX time intelligence, file 5) as data grows; building a genuine star schema, exactly as taught in `01-fundamentals/03-data-modeling.md`, is the real production-grade approach.

## Import Mode vs DirectQuery — Power BI's Version of Tableau's Extract/Live Choice
```
Import Mode: data is loaded/cached INTO Power BI's own compressed columnar
             engine (VertiPaq) — extremely fast interaction, but data is
             only as fresh as the last scheduled refresh

DirectQuery: Power BI sends queries LIVE to the source database on every
             interaction — always current, but performance depends
             entirely on the source system, and DAX calculation
             capabilities are more limited in this mode

Composite Models: MIX both — some tables imported (fast, less frequently
                  changing dimension data), others via DirectQuery (large,
                  frequently changing fact tables needing freshness) —
                  a genuinely powerful middle-ground option
```

## Row-Level Security (RLS) — Critical for Enterprise Deployment
```dax
// A DAX filter expression applied to a security Role, e.g., restricting
// a sales rep to see only their OWN region's data
[Region] = USERPRINCIPALNAME()  -- or a lookup against a security mapping table
```
RLS lets ONE published report/dataset be shared across an entire organization while each individual user only sees the data they're authorized to see — critical for scaling BI deployment beyond small teams without either building N separate reports or over-sharing sensitive data.

## Power BI Service — The Publishing/Governance Layer
```
Workspaces: organize related reports/datasets for a team, with permission
            controls over who can view/edit/manage them

Scheduled Refresh: automatically refresh Import-mode datasets on a schedule
                    (tied to when upstream ETL actually finishes — the same
                    orchestration integration point as Tableau Server)

Power BI Premium/Fabric capacity: dedicated compute for larger
    organizations needing more refresh frequency, larger dataset sizes,
    and advanced features beyond the shared/free tier's limits
```

## Power BI REST API — Programmatic Control (a real DE integration point)
```python
import requests

# Triggering a dataset refresh programmatically after an ETL pipeline completes —
# tying Power BI directly into the orchestration workflows from module 08
url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/refreshes"
headers = {"Authorization": f"Bearer {access_token}"}
requests.post(url, headers=headers)
```
This is exactly how a production Airflow/ADF pipeline would trigger a Power BI refresh as its FINAL step, ensuring the dashboard only refreshes AFTER the warehouse data has actually finished updating — avoiding a race condition where the dashboard refreshes against half-updated data.

## Interview Traps
- "Import mode vs DirectQuery — how do you choose?" — Import for performance-critical, less-frequently-changing data; DirectQuery for genuinely real-time requirements where the source can handle the load; Composite Models for a deliberate mix of both within one report.
- "Why does Power BI recommend a star schema over one big flat table?" — performance (smaller, well-related tables compress and query faster than one giant denormalized table) and DAX calculation correctness (time intelligence and many DAX patterns assume a proper relationship-based model).
- "How would you ensure a Power BI dashboard doesn't refresh before the underlying ETL pipeline finishes?" — trigger the Power BI refresh programmatically via the REST API as the FINAL step of the orchestrated pipeline (Airflow/ADF), rather than relying on independent, possibly-misaligned scheduled refresh times.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Every sincere attempt, even an imperfect one, moves you closer than standing still."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
