# Cloud Platforms Interview Questions — 40+ with Answers

## Why Cloud & Fundamentals

**Q1. Why are companies migrating to the cloud NOW more than ever?**
> Exploding data volumes outpacing on-prem's slow capital-heavy provisioning cycle, the CapEx-to-OpEx financial shift, removing the physical maintenance burden, and elasticity for variable/unpredictable workloads — plus the 2023-2026 AI/ML compute boom making cloud access increasingly a competitive necessity.

**Q2. Explain the shared responsibility model.**
> The cloud provider secures the underlying infrastructure ("security OF the cloud"); the customer is responsible for their own data, IAM configuration, and network setup ("security IN the cloud") — a misconfigured public S3 bucket is ALWAYS the customer's responsibility.

**Q3. Managed vs Serverless — what's the difference?**
> Managed still requires choosing/paying for a specific capacity tier (provider handles patching/scaling within it); serverless requires zero capacity planning, scales automatically including to zero cost when idle.

**Q4. Why deploy across multiple Availability Zones?**
> Isolates against a single data-center-level failure (power, cooling, fire) within the same region — a foundational high-availability pattern.

## AWS

**Q5. What is the Glue Data Catalog and why is it central to the AWS analytics ecosystem?**
> A persistent, Hive-metastore-compatible metadata store — Athena, Redshift Spectrum, EMR, and Glue jobs all query the same S3 data consistently through it, without each tool needing its own schema definition.

**Q6. Athena vs Redshift — when would you use each?**
> Athena for ad-hoc/exploratory/infrequent serverless SQL queries directly on S3 (pay-per-TB-scanned); Redshift for a standing, frequently-queried data warehouse where provisioning dedicated (or serverless) compute is justified by consistent usage.

**Q7. Kinesis vs MSK (managed Kafka) on AWS?**
> Kinesis for simpler, fully AWS-native streaming when portability isn't a concern; MSK for genuine Kafka API compatibility, easier migration to/from other Kafka-based environments.

## Azure

**Q8. What's genuinely different about ADLS Gen2 vs plain Blob Storage?**
> A true hierarchical namespace (real directory structure) rather than S3-style flat key-prefixes simulating folders — meaningfully improves performance for folder-level operations at scale.

**Q9. What is Microsoft Fabric's OneLake solving?**
> Eliminates repeated data copying between Azure services (traditionally ADLS → Synapse → Power BI's imported dataset each needing separate storage/refresh management) by having every Fabric component read/write the same underlying Delta-Parquet data directly.

**Q10. Why would an Azure-centric enterprise specifically need Microsoft Graph API in their data platform?**
> Significant real business data lives in SharePoint lists, Teams, and Outlook at Microsoft 365 enterprises — Graph API is the unified endpoint pulling all of it into the data platform, a genuinely Azure-specific integration advantage no other cloud serves as natively.

## GCP

**Q11. What makes BigQuery's pricing model distinctive?**
> Storage is nearly-free and automatically managed; compute is billed EITHER per-TB-scanned (on-demand) OR via reserved flat-rate slots — letting the same warehouse serve both sporadic and heavy steady-state workloads cost-effectively.

**Q12. Why would a company choose Dataflow/Apache Beam over separate batch + streaming tools?**
> One unified programming model handles BOTH batch and streaming logic, avoiding the maintenance burden of two separate codebases for similar business logic (the exact reason Spotify adopted this approach).

## Multi-Cloud & Hybrid

**Q13. Is "multi-cloud for redundancy" generally a good strategy?**
> Usually not recommended without a SPECIFIC driver (M&A, best-of-breed tool needs, regulatory data residency) — the real costs (duplicated expertise, egress fees, fragmented governance) usually outweigh generic "redundancy" benefits; picking one cloud and going deep is the more pragmatic default.

**Q14. How can a company achieve SOME cloud portability without full multi-cloud complexity?**
> Cloud-agnostic tools — Snowflake, Databricks, dbt, Terraform, open table formats (Iceberg/Delta) — that work across clouds, without needing to run duplicate full infrastructure on multiple providers.

**Q15. What's a common real hybrid cloud pattern, and why?**
> Keeping core, latency-critical, or heavily-regulated systems on-prem while running analytics/new systems in the cloud, connected via private dedicated network links (Direct Connect/ExpressRoute/Cloud Interconnect) — the most common real "multi-environment" pattern in large enterprises, not full multi-cloud.

## Migration Strategy

**Q16. Name and explain the 6 R's of cloud migration.**
> Rehost (lift-and-shift, minimal changes), Replatform (some optimization, minimal rearchitecture), Refactor (substantial cloud-native redesign), Repurchase (replace with SaaS), Retire (turn off unused systems), Retain (deliberately keep on-prem).

**Q17. Walk through how you'd approach migrating a company's legacy data infrastructure to the cloud.**
> Phased: Assessment/inventory → Pilot on a low-risk system → Wave-based migration (high-value/low-risk first) → extended coexistence/parallel-run period with reconciliation → decommission only after validated confidence — never a risky big-bang cutover.

**Q18. What's the biggest commonly underestimated risk in a cloud migration?**
> Hidden dependencies discovered too late, and underestimating how long the coexistence/parallel-run period actually needs to last before safe decommissioning.

**Q19. How would you validate that a migrated system produces correct results before fully cutting over?**
> Run old and new systems in parallel, reconcile outputs using a FULL OUTER JOIN comparison pattern to catch any mismatches, over a meaningful validation period before decommissioning the source system.

## Cost Optimization (FinOps)

**Q20. What's the single most common real-world cause of unexpectedly high cloud data costs?**
> Unpartitioned tables being fully scanned repeatedly (`SELECT *` on huge tables) in pay-per-scan warehouses/query engines (BigQuery, Athena, Redshift Spectrum).

**Q21. When would you use reserved/committed pricing vs on-demand/serverless?**
> Reserved/committed for genuinely predictable, steady, long-term workloads (significant discounts, 1-3 year commitment); on-demand/serverless for spiky, uncertain, or short-lived workloads — mixing both is the mature real-world default.

**Q22. How would you investigate an unexpected cloud cost spike?**
> Check cost breakdown by resource TAGS to find which team/project grew, drill into that team's specific expensive queries/jobs, identify the root technical cause (e.g., a missing partition/clustering config), fix it, and verify the next billing period confirms the fix.

**Q23. What are Spot/Preemptible instances and when are they appropriate?**
> Discounted spare cloud compute capacity (60-90% off) that the provider can reclaim with short notice — appropriate for fault-tolerant, checkpointed batch jobs that can handle a worker being interrupted and restarted, not for time-critical or stateful workloads without careful design.

## Security & IAM

**Q24. Explain the principle of least privilege with an example.**
> Grant only the exact permissions an identity needs — e.g., a pipeline gets read access to ONE specific S3 prefix and write access to ONE specific target table, nothing broader — so a compromised credential's blast radius is limited to only what it was actually granted.

**Q25. How should a data pipeline authenticate to cloud services?**
> Via a service account/managed identity scoped with least-privilege permissions — never a human's personal credentials, never long-lived hardcoded access keys in code.

**Q26. Walk through a real, common cloud data breach scenario and how to prevent it.**
> A publicly-readable S3 bucket left open "temporarily" for testing, forgotten, exposing customer PII for months — prevented by starting with maximally restrictive permissions always, and using automated tools (AWS Config, Azure Policy, GCP Security Command Center) that flag/block public storage configurations by default.

**Q27. Encryption at rest vs in transit — what's the difference?**
> At rest protects data stored on disk against unauthorized physical/storage-level access; in transit (TLS/SSL) protects data moving across a network against eavesdropping — both are typically enabled by default on modern cloud services, though key management (provider-managed vs customer-managed keys) is a further real choice.

## Infrastructure as Code

**Q28. Why use Terraform instead of manually configuring resources through the cloud console?**
> Repeatability, version control + PR review for infrastructure changes, consistency across dev/staging/prod environments, and avoiding undocumented "how did this get configured" mysteries.

**Q29. What is Terraform state, and why does remote state matter?**
> Terraform's record of currently-existing infrastructure, used to determine what needs to change on the next apply; remote state (with locking, e.g., S3 + DynamoDB) prevents team members' local state files from conflicting and provides one shared source of truth.

**Q30. How would you enforce consistent security practices across many teams' cloud infrastructure?**
> Reusable Terraform modules encoding least-privilege IAM, encryption, and tagging standards ONCE — every team's infrastructure inherits these defaults automatically rather than each team reinventing (and likely under-securing) their own configuration.

## Real Company Journeys

**Q31. What triggered Netflix's cloud migration, and how did their approach differ from a simple lift-and-shift?**
> A significant on-prem database corruption incident in 2008 exposed the fragility of relying entirely on their own data center; they rearchitected as genuinely cloud-native, failure-resilient microservices (famously building Chaos Monkey to continuously test resilience) rather than just relocating existing systems.

**Q32. Why is Capital One's cloud migration frequently cited as significant?**
> It demonstrated that even one of the most historically cloud-hesitant, heavily-regulated industries (banking) can migrate successfully when security/compliance is treated as a first-class concern from the start of the migration plan, not bolted on afterward.

## Rapid-Fire
33. What's the difference between a Region and an Availability Zone? *(Region = geographic area with multiple data centers; AZ = an isolated individual data center within that region.)*
34. What's CapEx vs OpEx, in the cloud context? *(CapEx = large upfront hardware purchases; OpEx = ongoing pay-as-you-go cloud costs — a major financial/accounting shift driving cloud adoption.)*
35. What's a Self-Hosted Integration Runtime (ADF) used for? *(Securely connecting cloud-native ADF to on-premises data sources still behind a corporate firewall.)*
36. What's the difference between rehosting and refactoring in a migration? *(Rehost = minimal-change lift-and-shift; refactor = substantial cloud-native redesign for long-term benefit.)*
37. Why might a company deliberately RETAIN a system on-prem rather than migrate it? *(Regulatory/latency requirements, or the migration ROI genuinely not justifying the risk/effort for a stable, rarely-touched system.)*
38. What's a private endpoint / PrivateLink used for? *(Accessing a cloud service from within your VPC without traffic traversing the public internet — improves both security and often performance/cost.)*
39. Why is `terraform plan` considered a critical safety practice? *(Shows exactly what will change BEFORE anything actually happens, catching mistakes like unintended resource deletion before they occur.)*
40. What's the practical difference between data residency and data sovereignty concerns in cloud region selection? *(Residency = data must physically stay within a specific geographic/legal boundary; broader sovereignty concerns can also include which laws/government jurisdiction can compel access to the data — both directly influence which cloud region a regulated company must choose.)*

---

**Practice tip**: For migration and cost-optimization questions especially, ground your answers in a REAL, specific example (from this module's case studies or company journeys) rather than abstract theory — interviewers consistently rate concrete, reasoned examples far higher than generic textbook answers.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"A heart free of envy learns faster from others' success rather than resenting it."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
