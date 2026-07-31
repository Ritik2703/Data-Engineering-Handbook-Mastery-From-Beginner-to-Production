# Project 1: The Classic Enterprise Stack — SSIS + Python + SQL Server + Tableau

## Business Scenario
A mid-size retail company (recap the case study pattern from `04-etl-elt/case-studies/`) needs a nightly pipeline that:
1. Loads sales data from CSV/Excel files dropped by regional stores
2. Pulls order data from an on-prem SQL Server OLTP database
3. Pulls organizational/HR data via Microsoft Graph API (SharePoint list + Azure AD users)
4. Pulls a third-party API (currency exchange rates)
5. Transforms everything via SQL stored procedures
6. Maintains a full audit trail via SQL triggers
7. Exposes clean views for Tableau dashboards

## Architecture
```
[Regional store CSV/Excel files]  [On-prem SQL Server OLTP]  [SharePoint + Azure AD]  [Currency API]
         |                                |                          |                      |
    SSIS Package                    SSIS Package              Python script          Python script
    (File System Task +             (OLE DB Source)           (msal + Graph API,     (requests, see
     Data Flow: Excel/Flat                                     see 03-python/10)      03-python/06)
     File Source)                                                    |                      |
         |                                |                          v                      v
         └────────────────┬───────────────┘                  Staging tables in SQL Server (via
                           v                                   pyodbc/sqlalchemy bulk insert)
                  Staging tables (SQL Server)  <───────────────────────┘
                           |
                  SQL Stored Procedures (transformation + business logic)
                           |
                  Fact/Dimension tables (star schema)
                           |
                  SQL Views (Tableau-ready, pre-joined/pre-aggregated)
                           |
                       Tableau (Live or Extract connection)

  [SQL Triggers on staging + fact tables -> Audit_Log table throughout]
```

## Stage 1: SSIS Package — Loading CSV/Excel Store Files
```
Package: Load_Store_Sales.dtsx

Control Flow:
  [ForEach Loop Container: iterate over files in \\fileserver\store_drops\*.csv]
        |
        v
  [Data Flow Task: Load_Single_Store_File]
     Data Flow:
       Flat File Source (dynamic filename via variable, set by ForEach)
             |
       Derived Column: add SourceFileName, LoadTimestamp
             |
       Conditional Split: route rows with NULL store_id or negative amount
                            to an "errors" path
             |
       OLE DB Destination: stg_store_sales table
        |
  [File System Task: move processed file to \\fileserver\store_drops\processed\]
```
```sql
-- Corresponding staging table with an audit-friendly structure
CREATE TABLE stg_store_sales (
    store_sales_id INT IDENTITY PRIMARY KEY,
    store_id VARCHAR(20),
    sale_date DATE,
    amount DECIMAL(10,2),
    source_file_name VARCHAR(255),
    load_timestamp DATETIME DEFAULT GETDATE()
);
```
This directly mirrors the SSIS package walkthrough pattern from `04-etl-elt/03-ssis-deep-dive.md` — the ForEach Loop handling variable numbers of dropped files is the SSIS equivalent of the metadata-driven pattern used throughout this repo.

## Stage 2: SSIS Package — Extracting from On-Prem OLTP
```
Package: Load_Orders.dtsx (incremental, watermark-based)

Control Flow:
  [Execute SQL Task: read LastWatermark from Control_Table]
        |
  [Data Flow Task: Extract_Orders]
     OLE DB Source: SELECT * FROM Orders WHERE ModifiedDate > ?
        |
     Lookup: Dim_Customer (get CustomerKey), redirect unmatched to error log
        |
     OLE DB Destination: stg_orders
        |
  [Execute SQL Task: update LastWatermark]
```

## Stage 3: Python — Microsoft Graph API + SharePoint Extraction
```python
# extract_hr_and_sharepoint.py — feeds the SQL Server staging layer
# Reuses the exact pattern from 03-python/10-sharepoint-graph-api-integration.md
import msal, requests, pyodbc, pandas as pd
import logging

logger = logging.getLogger(__name__)

def get_graph_token():
    app = msal.ConfidentialClientApplication(
        CLIENT_ID, authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET,
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" not in result:
        raise RuntimeError(f"Graph auth failed: {result.get('error_description')}")
    return result["access_token"]

def pull_store_manager_list():
    """Pulls the 'Store Managers' SharePoint list — business team maintains
    this manually, exactly the scenario from 03-python/10."""
    token = get_graph_token()
    headers = {"Authorization": f"Bearer {token}"}
    base = "https://graph.microsoft.com/v1.0"
    site_id = requests.get(f"{base}/sites/contoso.sharepoint.com:/sites/RetailOps", headers=headers).json()["id"]
    lists = requests.get(f"{base}/sites/{site_id}/lists", headers=headers).json()["value"]
    list_id = next(l["id"] for l in lists if l["displayName"] == "Store Managers")
    items = requests.get(f"{base}/sites/{site_id}/lists/{list_id}/items?expand=fields", headers=headers).json()["value"]
    return pd.DataFrame([item["fields"] for item in items])

def pull_azure_ad_users():
    token = get_graph_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://graph.microsoft.com/v1.0/users?$select=id,displayName,mail,department"
    resp = requests.get(url, headers=headers).json()
    return pd.DataFrame(resp["value"])

def load_to_sql_server(df, table_name, conn_string):
    """Bulk load into a SQL Server staging table -- reuses the connectivity
    pattern from 03-python/05-database-connectivity.md."""
    conn = pyodbc.connect(conn_string)
    cursor = conn.cursor()
    cursor.execute(f"TRUNCATE TABLE {table_name}")
    cursor.fast_executemany = True
    cols = ",".join(df.columns)
    placeholders = ",".join("?" * len(df.columns))
    cursor.executemany(
        f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})",
        df.values.tolist()
    )
    conn.commit()
    conn.close()
    logger.info(f"Loaded {len(df)} rows into {table_name}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    conn_str = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=...;DATABASE=RetailDW;Trusted_Connection=yes;"
    load_to_sql_server(pull_store_manager_list(), "stg_store_managers", conn_str)
    load_to_sql_server(pull_azure_ad_users(), "stg_azure_ad_users", conn_str)
```

## Stage 4: Python — Currency Exchange Rate API
```python
# extract_exchange_rates.py — reuses the retry pattern from 03-python/06
from tenacity import retry, stop_after_attempt, wait_exponential
import requests, pyodbc
from datetime import date

@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=2, min=2, max=30))
def fetch_rates(base_currency="USD"):
    resp = requests.get(f"https://api.exchangerate-host.com/latest?base={base_currency}", timeout=15)
    resp.raise_for_status()
    return resp.json()["rates"]

def load_rates(conn_string):
    rates = fetch_rates()
    conn = pyodbc.connect(conn_string)
    cursor = conn.cursor()
    for currency, rate in rates.items():
        cursor.execute(
            "INSERT INTO stg_exchange_rates (currency_code, rate, as_of_date) VALUES (?, ?, ?)",
            currency, rate, date.today()
        )
    conn.commit()
    conn.close()
```

## Stage 5: SQL Stored Procedures — The Transformation Layer
```sql
CREATE PROCEDURE usp_Transform_Load_FactSales
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRANSACTION;

        -- SCD Type 2 merge for Dim_Store (recap 02-sql/06 and 04-etl-elt/04)
        UPDATE d
        SET d.EndDate = GETDATE(), d.IsCurrent = 0
        FROM Dim_Store d
        JOIN stg_store_managers s ON d.StoreID = s.StoreID AND d.IsCurrent = 1
        WHERE d.ManagerName <> s.ManagerName;

        INSERT INTO Dim_Store (StoreID, ManagerName, StartDate, EndDate, IsCurrent)
        SELECT s.StoreID, s.ManagerName, GETDATE(), NULL, 1
        FROM stg_store_managers s
        LEFT JOIN Dim_Store d ON s.StoreID = d.StoreID AND d.IsCurrent = 1
        WHERE d.StoreID IS NULL
           OR d.ManagerName <> s.ManagerName;

        -- Fact table load with currency conversion applied
        INSERT INTO Fact_Sales (StoreKey, SaleDate, AmountLocal, AmountUSD, LoadTimestamp)
        SELECT
            d.StoreKey,
            s.sale_date,
            s.amount,
            s.amount * ISNULL(r.rate, 1.0),
            GETDATE()
        FROM stg_store_sales s
        JOIN Dim_Store d ON s.store_id = d.StoreID AND d.IsCurrent = 1
        LEFT JOIN stg_exchange_rates r ON r.currency_code = d.LocalCurrency
                                        AND r.as_of_date = CAST(GETDATE() AS DATE);

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        INSERT INTO Error_Log (ProcedureName, ErrorMessage, ErrorTime)
        VALUES ('usp_Transform_Load_FactSales', ERROR_MESSAGE(), GETDATE());
        THROW;
    END CATCH
END;
```

## Stage 6: SQL Triggers — The Audit Trail
```sql
-- Directly implements audit logging at the database level, catching
-- ANY change regardless of which process (SSIS, a stored proc, or an
-- ad-hoc query) made it -- a genuine enterprise compliance pattern
CREATE TRIGGER trg_Audit_FactSales
ON Fact_Sales
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO Audit_Log (TableName, Operation, RecordId, ChangedBy, ChangeTime, OldValue, NewValue)
    SELECT
        'Fact_Sales',
        CASE
            WHEN EXISTS(SELECT 1 FROM inserted) AND EXISTS(SELECT 1 FROM deleted) THEN 'UPDATE'
            WHEN EXISTS(SELECT 1 FROM inserted) THEN 'INSERT'
            ELSE 'DELETE'
        END,
        COALESCE(i.SalesKey, d.SalesKey),
        SYSTEM_USER,
        GETDATE(),
        (SELECT d.* FOR JSON PATH),
        (SELECT i.* FOR JSON PATH)
    FROM inserted i
    FULL OUTER JOIN deleted d ON i.SalesKey = d.SalesKey;
END;
```

## Stage 7: SQL Views — Tableau-Ready Layer
```sql
-- A clean, pre-joined view Tableau connects to directly -- keeps the
-- star schema complexity hidden from the BI layer (recap
-- 09-visualization/03's dimensions/measures discussion)
CREATE VIEW vw_Tableau_Sales_Summary AS
SELECT
    fs.SaleDate,
    ds.StoreID,
    ds.ManagerName,
    ds.Region,
    fs.AmountUSD,
    dc.CustomerSegment
FROM Fact_Sales fs
JOIN Dim_Store ds ON fs.StoreKey = ds.StoreKey
LEFT JOIN Dim_Customer dc ON fs.CustomerKey = dc.CustomerKey;
```

## Stage 8: SQL Server Agent Orchestration
```sql
-- The SQL Server Agent job chaining everything together nightly,
-- mirroring the Master Package pattern from 04-etl-elt/03
EXEC msdb.dbo.sp_add_job @job_name = 'Nightly_Retail_ETL';
-- Step 1: Run SSIS Load_Store_Sales.dtsx
-- Step 2: Run SSIS Load_Orders.dtsx
-- Step 3: Run Python extract_hr_and_sharepoint.py (via a CmdExec step)
-- Step 4: Run Python extract_exchange_rates.py
-- Step 5: EXEC usp_Transform_Load_FactSales
-- Step 6: Send success/failure email notification
```

## Stage 9: Tableau — The Dashboard Layer
```
Connection: Live connection to vw_Tableau_Sales_Summary (recap
  09-visualization/03's extract-vs-live tradeoff -- live chosen here
  since the SQL Server view is already pre-aggregated/lightweight,
  and the retail ops team wants current-day numbers)

Dashboard: "Store Performance" -- KPI cards (Total Sales, MoM Growth),
  a ranked bar chart by region, drill-down to individual store detail
  (directly following the design principles from 09-visualization/07
  and the case study in 09-visualization/case-studies/)
```

## What This Project Demonstrates
```
This single project touches: SSIS package design (04-etl-elt/03),
Python + Microsoft Graph API (03-python/10), API integration with
retry logic (03-python/06), SQL Server connectivity (03-python/05),
SCD Type 2 implementation (02-sql/06, 04-etl-elt/04), stored procedure
transaction/error handling, database-level audit triggers, star schema
design (01-fundamentals/03), and Tableau dashboard design
(09-visualization/03, 07) -- a genuinely complete, realistic enterprise
pipeline exactly as it exists at thousands of real companies today.
```


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The builder who studies both the old and the new paths walks wisely into the future."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
