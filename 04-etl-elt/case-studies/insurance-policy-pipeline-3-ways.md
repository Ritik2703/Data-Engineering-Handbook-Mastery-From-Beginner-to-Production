# Case Study: The Same Enterprise Pipeline, Built 3 Ways

## Business Scenario
A mid-size insurance company needs a **nightly pipeline**: extract policy and claims data from an on-prem SQL Server OLTP database, apply SCD Type 2 tracking on the customer dimension (policy holders change address/name over time and history must be preserved for audit/compliance), and load the result into a reporting warehouse for actuarial and finance teams.

This is exactly the kind of pipeline that exists at real insurance/banking companies, built with whichever tool was standard when it was first developed — and it illustrates why understanding multiple tools (not just "the modern one") is genuinely valuable in real enterprise DE work.

---

## Version 1: Built in SSIS (how it was built in 2015, still running in 2026)
```
SQL Server Agent Job: "Nightly_Policy_Load" (scheduled 1 AM daily)
        |
        v
Master Package: Master_Nightly_Load.dtsx
  Control Flow:
    [Execute SQL Task: read LastWatermark from Control_Table]
            |
    [Data Flow Task: Extract_Policies]
      Data Flow:
        OLE DB Source (SELECT * FROM Policies WHERE ModifiedDate > ?)
              |
        Lookup (Dim_Customer, match on CustomerID, get CustomerKey)
              |  (no match found)
        [redirect to error path -> log to Unmatched_Customers table]
              |  (match found)
        Derived Column (add LoadTimestamp)
              |
        OLE DB Destination (Fact_Policies)
            |
    [Execute Package Task: Load_Dim_Customer_SCD2.dtsx]
      (implements the Lookup + Conditional Split + OLE DB Command pattern
       to close old customer dimension rows and insert new versions)
            |
    [Execute SQL Task: update LastWatermark in Control_Table]
            |
    [Send Mail Task: on any failure above, alert data-team@company.com]
```
**Why it's still running**: this pipeline was audited and compliance-approved years ago for regulatory reporting; the actuarial team trusts it completely; rewriting it carries real business risk for a process that "just works."

---

## Version 2: Rebuilt in Azure Data Factory + Databricks (2023 modernization project)
```
ADF Tumbling Window Trigger (daily)
        |
        v
Pipeline: "Load_Policies_Daily"
    [Lookup Activity: read LastWatermark from a control table in Azure SQL]
            |
    [Copy Activity: on-prem SQL Server (via Self-Hosted Integration Runtime)
                    -> ADLS raw zone, as Parquet]
            |
    [Databricks Notebook Activity: "transform_policies"]
      PySpark logic:
        - Read raw Policies Parquet
        - Join against Dim_Customer (read from Delta Lake table)
        - Rows with no customer match -> written to a separate "unmatched_customers" Delta table
        - Apply SCD Type 2 logic using a Delta Lake MERGE statement (see below)
        - Write result to curated zone as Delta table
            |
    [Copy Activity: curated Delta table -> Synapse Analytics warehouse]
            |
    [Stored Procedure Activity: update LastWatermark]
            |
   (On Failure anywhere above)
            v
    [Web Activity: post to Teams channel webhook]
```
```python
# The SCD Type 2 logic inside the Databricks Notebook Activity — Delta Lake MERGE
# replaces the SSIS Lookup+Conditional Split+OLE DB Command pattern with one statement:
spark.sql("""
    MERGE INTO dim_customer AS target
    USING staging_customer AS source
    ON target.customer_id = source.customer_id AND target.is_current = true
    WHEN MATCHED AND (target.address <> source.address OR target.name <> source.name) THEN
        UPDATE SET target.end_date = current_date(), target.is_current = false
    WHEN NOT MATCHED THEN
        INSERT (customer_id, name, address, start_date, end_date, is_current)
        VALUES (source.customer_id, source.name, source.address, current_date(), NULL, true)
""")
```
**Why this version was built**: the finance team wanted faster iteration on new report requirements — with SSIS, adding a new derived field meant redeploying a `.dtsx` package through a formal change-control process; with ADF+Databricks, the PySpark notebook change goes through a standard Git PR + CI/CD pipeline, much faster to iterate.

---

## Version 3: Modern ELT with dbt (if rebuilt fresh today, greenfield)
```
Fivetran/custom Python extractor -> raw Policies + Customers landed in Snowflake (raw schema)
        |
        v
dbt project:
  models/staging/stg_policies.sql       -- clean/rename, 1:1 with raw
  models/staging/stg_customers.sql
        |
  snapshots/customer_snapshot.sql       -- dbt Snapshot handles SCD Type 2 automatically
        |
  models/marts/fct_policies.sql         -- join staging policies to the customer snapshot's
                                            CURRENT version, using dbt's built-in valid_from/valid_to
        |
Airflow DAG (nightly): dbt snapshot --select customer_snapshot
                        dbt run --select stg_policies+ fct_policies
                        dbt test --select fct_policies
                        (Slack alert on any test failure via Airflow callback)
```
```sql
-- models/marts/fct_policies.sql — note how much less code this needs vs. the SSIS/Databricks versions,
-- because the Snapshot already handles the entire SCD2 mechanism
SELECT
    p.policy_id,
    p.customer_id,
    c.name,
    c.address,
    p.premium_amount,
    p.policy_start_date
FROM {{ ref('stg_policies') }} p
LEFT JOIN {{ ref('customer_snapshot') }} c
    ON p.customer_id = c.customer_id
    AND c.dbt_valid_to IS NULL   -- only the CURRENT version of each customer
```
**Why this would be the choice for a brand-new build**: dramatically less custom code (the SCD2 mechanism is a config, not hand-written logic), built-in testing (`dbt test` catches broken joins/nulls automatically), and full lineage visible via `dbt docs generate` — but note this is realistic ONLY for a **new** pipeline; migrating the existing audited SSIS version to this would face all the real-world resistance described in file 9.

---

## The Actual Lesson From This Case Study
All three versions solve the **exact same business problem** (SCD2-tracked customer dimension feeding a policy fact table) — the tool changes, but the underlying concepts (staging, incremental watermark, SCD2 dimension tracking, error/unmatched-row handling, failure alerting) are **identical across all three**. This is why this module teaches concepts first, tools second — once you deeply understand what needs to happen, picking up any specific tool's syntax becomes much faster.
