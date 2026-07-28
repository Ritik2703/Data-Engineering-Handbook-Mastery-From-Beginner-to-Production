# 10. Tools Landscape (Complete Map — Legacy + Modern)

## Ingestion / Extraction
| Category | Legacy | Modern |
|---|---|---|
| ETL suites | Informatica PowerCenter, SSIS, Talend, DataStage | Fivetran, Airbyte, Stitch (managed EL connectors) |
| CDC | Custom triggers, Oracle GoldenGate | Debezium, AWS DMS, Azure DMS, Datastream |
| API extraction | Custom scripts (SOAP/XML era) | Python + requests, Airbyte connectors, Meltano |

## Orchestration
| Legacy | Modern |
|---|---|
| cron, Windows Task Scheduler, Control-M, AutoSys | Apache Airflow, Prefect, Dagster, Azure Data Factory (also does orchestration), Cloud Composer |

## Storage
| Category | Legacy | Modern |
|---|---|---|
| File storage | On-prem NAS/SAN, HDFS | S3, ADLS Gen2, GCS |
| Table format on lake | Plain Hive tables | Delta Lake, Apache Iceberg, Apache Hudi |
| OLTP DB | Oracle, SQL Server, DB2 | PostgreSQL, MySQL, Aurora, Cloud SQL |
| NoSQL | — (NoSQL is inherently modern) | MongoDB, Cassandra, DynamoDB, Cosmos DB, Redis |

## Processing / Transformation
| Legacy | Modern |
|---|---|
| MapReduce, Pig, custom stored procedures | Apache Spark, dbt, Polars (fast pandas alternative), PySpark |
| SSIS Data Flow transformations | Databricks notebooks, dbt models |

## Data Warehouses
| Legacy | Modern |
|---|---|
| Teradata, Oracle Exadata, on-prem SQL Server DW | Snowflake, BigQuery, Redshift, Synapse Analytics, Databricks SQL Warehouse |

## Streaming
| Legacy | Modern |
|---|---|
| Batch-only cron jobs simulating "near real-time" | Apache Kafka, AWS Kinesis, Azure Event Hubs, GCP Pub/Sub, Apache Flink, Spark Structured Streaming |

## BI / Visualization
| Legacy | Modern |
|---|---|
| Crystal Reports, SSRS, Cognos | Power BI, Tableau, Looker, Metabase, Apache Superset (OSS) |

## Data Quality / Testing
| Legacy | Modern |
|---|---|
| Manual QA scripts, ad-hoc SQL checks | Great Expectations, Soda, dbt tests, Monte Carlo / Bigeye (observability) |

## Data Catalog / Governance / Lineage
| Legacy | Modern |
|---|---|
| Excel spreadsheets (yes, really — very common historically), Informatica Metadata Manager | Amundsen, DataHub, Alation, Collibra, Purview (Azure), Dataplex (GCP) |

## Infrastructure as Code
| Legacy | Modern |
|---|---|
| Manual server provisioning, shell scripts | Terraform (multi-cloud), CloudFormation (AWS), Bicep/ARM (Azure), Pulumi |

## CI/CD & DevOps
| Legacy | Modern |
|---|---|
| Manual FTP deploys, Jenkins (still used, semi-modern) | GitHub Actions, GitLab CI, CircleCI, Jenkins |

## Containerization / Compute Orchestration
| Legacy | Modern |
|---|---|
| Bare-metal servers, VMs only | Docker, Kubernetes (EKS/AKS/GKE), Databricks clusters |

## Machine Learning Adjacent (DE increasingly touches this)
| Category | Tools |
|---|---|
| Feature stores | Feast, Tecton, Databricks Feature Store |
| ML pipeline orchestration | Kubeflow, MLflow, Airflow (also used for ML pipelines) |
| Vector databases (for AI/RAG use cases) | Pinecone, Weaviate, pgvector (Postgres extension) |

## Full-Stack "Modern Data Stack" (2024-2026 common combination in startups)
```
Ingestion:      Fivetran / Airbyte
Storage:        Snowflake or BigQuery
Transformation: dbt
Orchestration:  Airflow / Dagster
BI:             Looker / Power BI / Tableau
Data Quality:   dbt tests + Great Expectations
Catalog:        DataHub / Atlan
```

## Enterprise Legacy Stack (still very common — banking, insurance, government)
```
Ingestion:      Informatica PowerCenter / SSIS
Storage:        Oracle / SQL Server / Teradata
Orchestration:  Control-M / AutoSys
BI:             Cognos / SSRS / older Tableau deployments
```

> Real-world tip: most companies run a **hybrid** of legacy + modern — expect to work with both, especially at larger/older organizations mid-migration to cloud.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"A student who questions deeply respects the subject more than one who memorizes blindly."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
