# 📖 Master Glossary — A to Z Across All 15 Modules

A single, repo-wide reference. Each module also has its own embedded terminology (e.g., `01-fundamentals/glossary.md`); this is the CROSS-MODULE index for quick lookup during interview prep.

**ACID** — Atomicity, Consistency, Isolation, Durability; transactional guarantees. *(01, 05)*
**Airflow** — Open-source workflow orchestration tool using Python-defined DAGs. *(08)*
**AI Agent** — An LLM given tools and a loop (observe-reason-act-repeat) to complete multi-step tasks autonomously. *(16)*
**Anonymization** — Irreversibly removing an individual's identifiability from data. *(15)*
**Backpressure** — What happens when ingestion rate exceeds processing rate. *(11)*
**Blast Radius** — How much of a system is affected if a component fails. *(10, 11)*
**Blue-Green Deployment** — Running two complete environments, switching traffic instantly for zero-downtime rollback. *(10)*
**Bronze/Silver/Gold** — Medallion architecture layers: raw, cleaned, business-ready data. *(01, 06, 13)*
**CAP Theorem** — Distributed systems guarantee only 2 of Consistency, Availability, Partition Tolerance. *(01, 05)*
**CDC (Change Data Capture)** — Capturing row-level DB changes from the transaction log. *(01, 07)*
**Chaos Engineering** — Deliberately breaking production to test resilience (Netflix's Chaos Monkey). *(10)*
**CI/CD** — Continuous Integration / Continuous Delivery / Continuous Deployment. *(10)*
**Circuit Breaker** — Failing fast after repeated failures instead of continuing to retry. *(11)*
**Data Contract** — A formal, versioned schema/SLA agreement between a data producer and consumer. *(11, 15)*
**Data Mesh** — Domain-oriented decentralized data ownership architecture. *(03, 04, 11, 15)*
**Data Vault** — Modeling methodology using Hubs, Links, Satellites for auditable warehousing. *(01)*
**DAX** — Data Analysis Expressions, Power BI's formula language. *(09)*
**DAG (Directed Acyclic Graph)** — A dependency graph with no cycles. *(01, 08, 11)*
**Denormalization** — Deliberately duplicating data for query performance. *(01, 05)*
**Docker** — Containerization platform packaging apps with their runtime environment. *(10)*
**Elasticity** — Cloud infrastructure automatically scaling with demand. *(07)*
**ELT** — Extract, Load, Transform; transform happens inside the warehouse. *(01, 04)*
**Error Budget** — The allowed unreliability implied by an SLO. *(10)*
**ETL** — Extract, Transform, Load; transform happens before loading. *(01, 04)*
**Fact Table** — Central table in a star schema holding measurable business events. *(01, 05)*
**Feature Store** — A system storing feature logic once, serving both training and inference. *(15)*
**FinOps** — Financial Operations; disciplined cloud cost management. *(07)*
**GitOps** — Git as the single source of truth for infrastructure/deployment state. *(10)*
**Golden Record** — The single, trusted, reconciled version of an entity across systems (MDM). *(15)*
**GDPR/CCPA** — Major data privacy regulations (EU / California). *(15)*
**Idempotency** — An operation safe to retry without duplicating/corrupting results. *(01, 08, 11)*
**Iceberg / Delta Lake / Hudi** — Open lakehouse table formats adding ACID transactions to lake storage. *(01, 06)*
**Kappa Architecture** — Streaming-only architecture; reprocessing via replaying the event log. *(01, 11)*
**Kubernetes** — Container orchestration platform managing containers at scale. *(10)*
**Lambda Architecture** — Separate batch and speed layers, merged at a serving layer. *(01, 11)*
**Lineage** — A traceable graph of where data came from and what depends on it. *(15)*
**LookML** — Looker's semantic modeling language, defining metrics once centrally. *(09)*
**MCP (Model Context Protocol)** — An open standard letting AI models connect to external data systems via standardized servers. *(16)*
**MDM (Master Data Management)** — Reconciling entity data across systems into golden records. *(15)*
**Medallion Architecture** — See Bronze/Silver/Gold. *(01, 06, 13)*
**MLOps** — Practices for reliably deploying/monitoring ML models in production. *(15)*
**MVCC** — Multi-Version Concurrency Control; lets readers avoid blocking writers. *(01, 05)*
**Normalization** — Organizing relational data to reduce redundancy (1NF/2NF/3NF). *(01, 05)*
**OLAP/OLTP** — Online Analytical Processing vs Online Transaction Processing. *(01, 05)*
**Partitioning** — Splitting data physically by a column (often date) for query pruning. *(01, 05, 06)*
**Policy as Code** — Enforcing governance rules automatically in CI/CD. *(15)*
**Prompt Injection** — An attack embedding hidden instructions in untrusted content an AI model processes. *(16)*
**RACI** — Responsible, Accountable, Consulted, Informed — a role-clarity framework. *(15)*
**RAG (Retrieval-Augmented Generation)** — Retrieving relevant data to ground an LLM's answer. *(05, 16)*
**Replication** — Copying data across nodes for availability/read scaling. *(01, 05)*
**RPO/RTO** — Recovery Point/Time Objective; how much data loss / downtime is tolerable. *(11)*
**Schema-on-Read/Write** — Schema applied at query time (lake) vs at write time (warehouse). *(01)*
**SCD (Slowly Changing Dimension)** — Techniques for tracking dimension attribute history over time. *(01, 02, 04)*
**Semantic Layer** — A layer defining business metrics once, consistently, for all consuming tools. *(09, 15)*
**Shuffle** — Movement of data across nodes during distributed joins/group-bys. *(01, 06)*
**SLI/SLO/SLA** — Service Level Indicator (measurement) / Objective (internal target) / Agreement (external commitment). *(10)*
**Snowflake Schema** — Star schema with dimension tables further normalized. *(01)*
**Spark** — Distributed in-memory processing engine, the modern big data standard. *(06)*
**Star Schema** — Fact table surrounded by denormalized dimension tables. *(01, 05)*
**Terraform** — Infrastructure as Code tool, cloud-agnostic. *(07, 10)*
**Vector Database** — A database optimized for similarity search over embedding vectors. *(05)*
**Watermark (streaming)** — Threshold for how late an event can arrive and still be processed. *(01, 06)*
**Window Function** — SQL functions computing across a set of rows related to the current row. *(02)*
**YARN** — Hadoop's native cluster resource manager. *(06)*

## How to Use This
```
Use Ctrl+F to jump to any term you've forgotten mid-interview-prep.
Each entry lists the module(s) where it's covered in FULL depth —
this glossary gives you the one-line reminder, not the full explanation.
```


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Every ending is the seed of a new, wiser beginning -- go now and build with care."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
