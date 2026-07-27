# 04 — ETL / ELT: Beginner to Enterprise-Production

Written so someone who's never heard the words "ETL" or "SSIS" before can finish this module understanding **exactly** what a Data Engineer builds, why legacy tools like SSIS/Informatica exist and how they actually work internally, and how modern tools (ADF, Glue, dbt) do the same job differently at real companies today.

## 📖 Learning Path

| # | File | Level | Covers |
|---|---|---|---|
| 1 | [`01-what-is-etl-elt.md`](./01-what-is-etl-elt.md) | Beginner | What ETL/ELT actually means, why it exists, history |
| 2 | [`02-etl-architecture-deep-dive.md`](./02-etl-architecture-deep-dive.md) | Beginner-Intermediate | Staging areas, transformation types, orchestration anatomy |
| 3 | [`03-ssis-deep-dive.md`](./03-ssis-deep-dive.md) | Intermediate | SSIS packages, Control Flow vs Data Flow, real package walkthrough |
| 4 | [`04-informatica-deep-dive.md`](./04-informatica-deep-dive.md) | Intermediate | PowerCenter mappings, sessions, workflows, transformations |
| 5 | [`05-legacy-tools-overview.md`](./05-legacy-tools-overview.md) | Intermediate | Talend, DataStage, AbInitio — quick reference |
| 6 | [`06-azure-data-factory-deep-dive.md`](./06-azure-data-factory-deep-dive.md) | Advanced | ADF pipelines, linked services, datasets, Mapping Data Flows |
| 7 | [`07-aws-glue-deep-dive.md`](./07-aws-glue-deep-dive.md) | Advanced | Glue jobs, Crawlers, Data Catalog, DynamicFrames, Glue Studio |
| 8 | [`08-dbt-deep-dive.md`](./08-dbt-deep-dive.md) | Advanced | dbt models, Jinja/macros, tests, docs, the ELT transformation standard |
| 9 | [`09-legacy-vs-modern-migration.md`](./09-legacy-vs-modern-migration.md) | Production | Side-by-side comparison, real migration strategy |
| 10 | [`case-studies/`](./case-studies/) | Production | Full enterprise-style pipeline built 3 ways (SSIS-style, ADF, dbt+Airflow) |
| 11 | [`interview-questions.md`](./interview-questions.md) | All levels | 30+ Q&A on ETL/ELT concepts and tools |

## 🎯 The Core Question This Module Answers
**"What does a Data Engineer actually DO all day with these tools?"**
By the end, you'll be able to explain:
- Why ETL existed before ELT, and why ELT became dominant with the cloud
- Exactly how an SSIS/Informatica package is built, step by step
- Why companies still run these legacy tools in 2026 (and won't fully retire them soon)
- How ADF/Glue/dbt do the same job, and why they've become the default for new builds
- How to have an intelligent conversation in an interview about "why did you pick X tool for Y scenario"

## 🗺️ Suggested Order
```
New to ETL entirely:  01 -> 02 -> 03 (SSIS) -> 04 (Informatica) -> 06 (ADF) -> 07 (Glue) -> 08 (dbt)
Already know legacy:  09 (migration) -> 06/07/08 (modern tools) -> case-studies/
Interview prep:       09 + interview-questions.md + case-studies/
```
