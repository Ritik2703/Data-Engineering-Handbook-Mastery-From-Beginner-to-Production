# 13 — Projects: End-to-End Pipelines (All Knowledge, Implemented)

This module is where every module from 01-12 comes together into REAL, complete, working pipelines — from the legacy enterprise stack (SSIS + Python + SQL + Tableau) still running at thousands of companies, to the cutting-edge modern stack (Kafka + S3 + Glue + dbt + Snowflake + Databricks) being built fresh today.

## 📖 The 6 Projects

| # | Project | Stack | What It Demonstrates |
|---|---|---|---|
| 1 | [`project-01-legacy-ssis-python-tableau/`](./project-01-legacy-ssis-python-tableau/) | SSIS + Python + SQL Server + Tableau | The classic enterprise stack — CSV/Excel/DB ingestion, API + SharePoint Graph API pulls, stored-proc transformation, audit triggers, Tableau views |
| 2 | [`project-02-modern-cloud-kafka-glue-dbt-snowflake/`](./project-02-modern-cloud-kafka-glue-dbt-snowflake/) | Kafka + S3 + AWS Glue + dbt + Snowflake | The modern ELT stack — streaming ingestion, serverless transform, SQL-based modeling with tests |
| 3 | [`project-03-databricks-lakehouse-delta/`](./project-03-databricks-lakehouse-delta/) | Databricks + Delta Lake + Airflow | The lakehouse pattern — Medallion architecture, Delta MERGE for SCD2, orchestrated end-to-end |
| 4 | [`project-04-realtime-streaming-analytics/`](./project-04-realtime-streaming-analytics/) | Kafka + Spark Structured Streaming + Power BI | Real-time analytics — windowed aggregation, live dashboard refresh |
| 5 | [`project-05-azure-full-stack/`](./project-05-azure-full-stack/) | ADF + Databricks + Synapse + Power BI | A complete single-cloud (Azure) enterprise pipeline |
| 6 | [`project-06-aws-full-stack-serverless/`](./project-06-aws-full-stack-serverless/) | Lambda + Glue + Redshift + QuickSight | A complete serverless-first (AWS) enterprise pipeline |

## 🎯 How to Use These Projects
```
Each project folder contains:
- README.md — architecture diagram (as text/mermaid), requirements,
  and a full narrative walkthrough of EVERY stage
- Actual code for each stage (SQL, Python, dbt models, notebooks)
  wherever a stage benefits from seeing the real implementation, not
  just a description

These are designed to be READ end-to-end like a story first (understand
the WHY behind each stage), then used as a TEMPLATE to build your own
portfolio project (recap `12-interview-prep/02`'s portfolio guidance) —
don't just copy-paste; rebuild pieces yourself to genuinely internalize them.
```

## 🗺️ Suggested Order
```
If you come from an enterprise/legacy background: start with Project 1,
  then jump to Project 2 or 3 to see the modern equivalent of the same
  problem you already understand from Project 1

If you're building fresh, modern-stack skills: start with Project 2,
  then Project 3 (Databricks) and Project 4 (streaming) for depth

If preparing for a SPECIFIC cloud's job interviews: go straight to
  Project 5 (Azure) or Project 6 (AWS) for that cloud's complete story
```


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"What is practiced with real hands, not just read with tired eyes, becomes true skill."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
