# 4. Informatica PowerCenter — Deep Dive

## What is Informatica and Why It Exists
Informatica PowerCenter is one of the oldest and most widely deployed enterprise ETL tools, especially dominant in **banking, insurance, telecom, and healthcare** — industries with strict data governance/audit requirements and large, complex legacy source systems (mainframes, Oracle, SAP). It's a separate ETL engine (not tied to any one database vendor, unlike SSIS which is Microsoft-only) — this vendor-neutrality is part of why it became so dominant in heterogeneous enterprise environments.

## Core Architecture — Three Main Components

### 1. PowerCenter Designer — where you build **Mappings**
A **Mapping** is the data-flow blueprint — sources, transformations, and targets, connected visually, conceptually very similar to an SSIS Data Flow but more transformation-rich out of the box.
```
[Source Qualifier: Orders_Raw table]
              |
              v
[Expression Transformation: derive total_amount = quantity * unit_price]
              |
              v
[Lookup Transformation: fetch customer_key from Dim_Customer]
              |
              v
[Filter Transformation: exclude rows where status = 'test']
              |
              v
[Aggregator Transformation: SUM(total_amount) GROUP BY customer_key, order_date]
              |
              v
[Target: Fact_Daily_Customer_Sales]
```

### 2. Workflow Manager — where you build **Workflows** and **Sessions**
A **Session** wraps a single Mapping with runtime configuration (source/target connection details, commit intervals, error handling behavior). A **Workflow** is the orchestration layer — chains Sessions and other tasks (Email, Command, Decision, Event-Wait) together, exactly like SSIS's Control Flow or an Airflow DAG.
```
Workflow: "wf_Nightly_Sales_Load"
  Start --> Session: s_m_Load_Orders --> Session: s_m_Load_Customers
                    |                              |
              (on success)                   (on success)
                    v                              v
                        Session: s_m_Aggregate_Daily_Sales
                                    |
                              Decision Task: "Row count > 0?"
                              /                          \
                          (Yes)                        (No)
                            v                              v
                    Command Task:                   Email Task:
                    "Trigger downstream BI refresh"   "Alert: zero rows loaded"
```

### 3. Workflow Monitor — operational dashboard
Shows real-time and historical execution status, row counts processed, session logs — the equivalent of checking Airflow's UI or SSIS catalog reports to see if last night's load succeeded and how long it took.

## Key Transformations (Informatica's transformation library, richer than SSIS's out of the box)
| Transformation | Purpose |
|---|---|
| **Source Qualifier** | Defines the SQL query pulling data from a relational source |
| **Expression** | Row-level calculations (derive new columns, string/date manipulation) |
| **Filter** | Keep only rows matching a condition |
| **Router** | Like a "switch statement" — routes rows to multiple different output groups based on conditions (more flexible than SSIS's single-condition Conditional Split) |
| **Lookup** | Join against a reference/dimension table to fetch related values |
| **Aggregator** | GROUP BY-style summarization |
| **Joiner** | Combine two data streams (like a SQL JOIN, when sources are from different systems that can't be joined at the database level) |
| **Sorter** | Order rows (often required before Aggregator for performance) |
| **Update Strategy** | Explicitly mark each row as INSERT/UPDATE/DELETE/REJECT — core to implementing SCD Type 2 logic |
| **Sequence Generator** | Generate surrogate keys |
| **Normalizer** | Flatten repeating groups (common with mainframe/COBOL source data) |

## Real Walkthrough: Implementing SCD Type 2 in Informatica (classic enterprise interview scenario)
```
[Source Qualifier: Customer_Staging]
              |
              v
[Lookup: Dim_Customer WHERE is_current = 'Y', matching on customer_id]
              |
              v
[Expression: compare incoming city/name to looked-up city/name -> flag "changed" if different]
              |
              v
[Router: split into 3 groups]
   Group 1: "New Customer" (no match found in Lookup)
   Group 2: "Changed Customer" (match found, but attributes differ)
   Group 3: "Unchanged Customer" (match found, attributes identical)
              |
   Group 1 & 2 --> [Update Strategy: DD_INSERT] --> [Target: Dim_Customer] (insert new version row)
   Group 2 also --> [Update Strategy: DD_UPDATE] --> [Target: Dim_Customer] (close old row: set end_date, is_current='N')
   Group 3 --> discarded (no target, nothing to do)
```
This is a textbook Informatica SCD Type 2 mapping pattern — asked constantly in enterprise DE interviews specifically because Informatica shops (banking/insurance) rely on it heavily for customer/account dimension history.

## Parameter Files (Informatica's equivalent of environment-specific config)
```ini
[Global]
$$SourceConnection=PROD_ORACLE_CONN
$$TargetConnection=PROD_DW_CONN
$$IncrementalWatermark=2026-07-24 02:00:00
```
A **parameter file** is passed into a Workflow at runtime, letting the exact same Workflow/Mapping run against dev/test/prod environments (or process different incremental date ranges) without hardcoding values into the mapping itself — the direct equivalent of SSIS Project Parameters or ADF pipeline parameters.

## Error Handling & Recovery
- **Session-level error handling**: configure whether a session stops on first error, or continues and logs errors to a reject file (`.bad` file) for later review.
- **Row error logging**: Informatica can log every individual rejected row with the specific reason (e.g., "primary key violation", "data type mismatch") to a relational error table — valuable for enterprise audit requirements.
- **Recovery**: a failed Workflow can often be restarted from the point of failure rather than from scratch, similar to SSIS checkpoints.

## Why Enterprises Still Run Informatica in 2026
- Massive existing investment — thousands of tested, audited, compliance-approved mappings built over 15-20 years; rewriting all of it carries real business risk.
- Strong governance/lineage features valued in regulated industries (banking, insurance, pharma) where auditors need to trace exactly how a number in a financial report was calculated.
- Informatica itself has evolved — **Informatica Intelligent Data Management Cloud (IDMC)** is their modern cloud-native platform, so "Informatica" isn't purely legacy anymore; many enterprises run a hybrid of on-prem PowerCenter (legacy, stable) + IDMC (new cloud-native builds).

## Interview Traps
- Be ready to walk through the SCD Type 2 mapping pattern above from memory — it's asked extremely often for Informatica-specific roles.
- "Difference between a Filter and a Router transformation?" — Filter has ONE condition and one output (rows either pass or don't); Router can have MULTIPLE conditions producing MULTIPLE output groups simultaneously (like an if/elif/elif chain vs a single if).
- "What's an Update Strategy transformation for?" — explicitly tagging each row for INSERT/UPDATE/DELETE/REJECT, essential for any mapping that needs to both insert new records and update existing ones (like SCD2) in a single pass.
