# 8. Cloud Fundamentals (AWS / Azure / GCP)

## Why Cloud for Data Engineering
On-prem infrastructure requires buying/maintaining physical servers, guessing capacity in advance, and slow provisioning. Cloud gives **elastic, pay-as-you-go** compute/storage — spin up a 100-node Spark cluster for 2 hours and pay only for that, then it's gone.

## Service Models
```
IaaS (Infrastructure as a Service)   -> You manage OS, runtime, app. Cloud manages hardware.
    Examples: EC2, Azure VMs, GCE

PaaS (Platform as a Service)         -> Cloud manages OS/runtime too. You manage just app/data/config.
    Examples: Glue, Azure Data Factory, BigQuery, Databricks (managed)

SaaS (Software as a Service)         -> Fully managed application, you just use it.
    Examples: Snowflake (arguably), Power BI Service, Salesforce
```
Most modern Data Engineering work lives in the **PaaS** layer — you rarely manage raw servers directly anymore (Glue/ADF/Dataflow/BigQuery abstract the infrastructure away).

## Shared Responsibility Model
Cloud provider secures the **infrastructure** (physical data centers, hypervisor, network); you're responsible for **your data, access control (IAM), and configuration** (e.g., don't leave an S3 bucket public). This is the #1 cause of cloud data breaches — misconfigured permissions, not provider failures.

## Core Cloud Concepts (apply across all 3 providers)
- **Region**: a geographic location with a cluster of data centers (e.g., `ap-south-1` = Mumbai on AWS).
- **Availability Zone (AZ)**: isolated data center within a region — deploy across multiple AZs for high availability.
- **IAM (Identity and Access Management)**: who can do what — always follow **least privilege** (grant only the permissions needed, nothing more).
- **VPC (Virtual Private Cloud)**: your isolated private network within the cloud — data pipelines often need VPC peering/private endpoints to securely reach on-prem or other cloud resources.
- **Managed vs Serverless**: Managed = cloud handles patching/scaling but you still choose cluster size (e.g., EMR, Databricks); Serverless = you don't think about servers at all, pay per query/execution (e.g., BigQuery, Athena, Lambda, Glue serverless).

## Full Service Mapping — AWS vs Azure vs GCP

| Category | AWS | Azure | GCP |
|---|---|---|---|
| **Object Storage** | S3 | Blob Storage / ADLS Gen2 | Cloud Storage (GCS) |
| **Data Warehouse** | Redshift | Synapse Analytics (SQL Pool) | BigQuery |
| **Managed Spark** | EMR | Databricks / Synapse Spark Pools | Dataproc |
| **Serverless ETL** | Glue | ADF Mapping Data Flows / Databricks | Dataflow (Apache Beam) |
| **Orchestration** | MWAA (managed Airflow) / Step Functions | Azure Data Factory pipelines / Logic Apps | Cloud Composer (managed Airflow) |
| **Streaming ingestion** | Kinesis | Event Hubs | Pub/Sub |
| **Serverless SQL on lake** | Athena | Synapse Serverless SQL | BigQuery (native external tables) |
| **NoSQL (Key-Value/Document)** | DynamoDB | Cosmos DB | Firestore / Bigtable |
| **Relational OLTP (managed)** | RDS / Aurora | Azure SQL Database | Cloud SQL |
| **Data Catalog** | Glue Data Catalog | Purview | Data Catalog / Dataplex |
| **Secrets Management** | Secrets Manager | Key Vault | Secret Manager |
| **Serverless Functions** | Lambda | Azure Functions | Cloud Functions |
| **Container Orchestration** | EKS (Kubernetes) / ECS | AKS | GKE |
| **BI Tool (native)** | QuickSight | Power BI | Looker / Looker Studio |
| **CDC / Migration** | DMS (Database Migration Service) | Azure Database Migration Service | Datastream |
| **IAM** | IAM | Entra ID (formerly Azure AD) | Cloud IAM |
| **Infra as Code (native)** | CloudFormation | ARM Templates / Bicep | Deployment Manager |
| **Data Governance** | Lake Formation | Purview | Dataplex |

> Terraform (third-party, multi-cloud) is used far more in practice than any single cloud's native IaC tool — worth learning over CloudFormation/ARM/Bicep if you want one skill across all three clouds.

## Cost Model Differences (important for interviews and real budgeting)
- **AWS Redshift**: cluster-based — pay for provisioned nodes 24/7 (or Redshift Serverless now available).
- **Azure Synapse**: similar cluster/DWU-based pricing, or serverless SQL pool pay-per-TB-scanned.
- **GCP BigQuery**: fully serverless by default — pay per TB scanned per query (or flat-rate for heavy/predictable usage) — storage billed separately and very cheap.
- **Snowflake** (multi-cloud, runs on top of AWS/Azure/GCP): pay per-second compute (auto-suspend when idle) + storage — pioneered clean separation of storage/compute billing.

## Choosing a Cloud (real-world decision factors, not just tech)
```
Existing Microsoft/Office 365 enterprise agreement       -> Azure (often mandated by IT/procurement)
Broadest general market adoption, largest talent pool    -> AWS
Strong existing Google Workspace / heavy ML-Ops focus     -> GCP
Data warehouse specifically, cloud-agnostic               -> Snowflake (works on any of the 3 underneath)
```
Most large enterprises actually run **multi-cloud or hybrid** environments — knowing the concept mapping (this table) matters more than mastering one provider's exact button locations.

## Microsoft Graph API (Azure ecosystem — DE relevance)
Beyond core Azure data services, enterprises on Microsoft 365 often need to pull **organizational and collaboration data** — users/licenses (Entra ID), SharePoint lists (used as informal databases by business teams), Teams messages, Outlook calendar data — into the warehouse for HR analytics, compliance, or engagement dashboards. Microsoft Graph API is the single unified REST endpoint for all of this. See `07-cloud-platforms/azure/microsoft_graph_api_pull.py` in this repo for a working extraction script (OAuth2 client-credentials flow, pagination handling).

## Interview Traps
- Don't confuse "serverless" with "free" — BigQuery/Athena serverless pricing can spike hard if someone runs `SELECT *` on a huge unpartitioned table (billed per TB scanned).
- Know the shared responsibility model cold — "who's responsible for a misconfigured public S3 bucket?" (Answer: the customer, always, regardless of cloud provider.)


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Every failure in a pipeline, like every failure in life, is data for the next attempt — not a verdict on your worth."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
