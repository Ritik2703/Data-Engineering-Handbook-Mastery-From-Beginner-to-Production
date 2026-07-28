# 🏆 Data Engineering Golden Repo

A one-stop, A-to-Z reference for Data Engineers — SQL, Python, ETL/ELT, Cloud (AWS/Azure/GCP), Big Data, Orchestration, Visualization, System Design, and Interview Prep. Covers **legacy techs still running in production** (Hive, SSIS, Informatica) and **modern stacks** (dbt, Airflow, Delta Lake, Snowflake) side by side.

> ⭐ Star this repo if it helps you. PRs welcome — see `CONTRIBUTING.md`.

---

## 🗺️ Roadmap (Beginner → Advanced)

```
Fundamentals → SQL → Python → Databases → ETL/ELT → Orchestration
     → Big Data → Cloud (pick 1, learn all 3 concepts) → Visualization
     → DevOps/CI-CD → System Design → Projects → Interviews
```

## 📂 Repo Structure

| Folder | What's Inside |
|---|---|
| `01-fundamentals/` | Data modeling, warehousing concepts, OLTP vs OLAP |
| `02-sql/` | Window functions, query optimization, indexing, practice queries |
| `03-python/` | Core Python for DE, pandas, PySpark, API→DB pull scripts |
| `04-etl-elt/` | Airflow DAGs, dbt models, legacy tools (SSIS/Informatica) notes |
| `05-databases/` | Connection code for Postgres, MongoDB, Snowflake, Redshift |
| `06-big-data/` | Spark jobs, Kafka producer/consumer, Hadoop ecosystem notes |
| `07-cloud-platforms/` | AWS (Glue/S3/boto3), Azure (ADF + Microsoft Graph API), GCP (BigQuery) |
| `08-orchestration/` | Airflow, Prefect, Dagster comparisons + sample DAGs |
| `09-visualization/` | Tableau & Power BI concepts, Python viz (matplotlib/plotly) |
| `10-devops/` | Dockerfile for pipelines, GitHub Actions CI/CD |
| `11-system-design/` | Architecture diagrams (Mermaid), scalability patterns |
| `12-interview-prep/` | SQL, Python, system design Q&A |
| `13-projects/` | End-to-end pipeline: API → S3 → Spark → Warehouse → Power BI |
| `resources/` | Books, courses, YouTube channels, blogs |

## 🧭 Legacy vs Modern (know both — most companies run a mix)

| Layer | Legacy (still in prod) | Modern |
|---|---|---|
| ETL Tool | SSIS, Informatica, Talend | dbt, Airflow, Fivetran |
| Storage | On-prem SQL Server/Oracle | Snowflake, BigQuery, Redshift |
| Big Data | Hadoop/Hive/MapReduce | Spark, Databricks, Delta Lake |
| Streaming | Batch cron jobs | Kafka, Kinesis, Flink |
| Scheduling | Windows Task Scheduler / cron | Airflow, Dagster, Prefect |
| Modeling | Star/Snowflake schema | + Data Vault, One Big Table (OBT) |

## 🚀 Quick Start
```bash
git clone [https://github.com/<your-username>/Data-Engineering-Handbook-Mastery-From-Beginner-to-Production.git]
cd Data-Engineering-Handbook-Mastery-From-Beginner-to-Production
pip install -r requirements.txt   # per-folder requirements where relevant
```

## 🤝 Contributing
Found a gap? Add a folder following the existing pattern: `README.md` (concept) + `code-examples/` (runnable) + `resources.md` (links). Open a PR.

## 📜 License
MIT — use freely, attribution appreciated.

---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The one who finds joy in the process rarely feels the weight of the destination."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>

