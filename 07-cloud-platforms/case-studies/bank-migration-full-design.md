# Case Study: Designing a Full On-Prem-to-Cloud Migration (Regional Retail Bank)

## Starting Point
```
- On-prem SQL Server data warehouse (10 years old, core financial reporting)
- SSIS packages handling nightly ETL from 15 different branch/core-banking systems
- On-prem file shares where branch managers drop Excel reports monthly
- A physical data center with an aging hardware refresh due in 18 months
  (the actual TRIGGER forcing this decision — a concrete, real business driver,
  exactly as file 11 emphasizes)
- Strict regulatory requirements: data residency (must stay within-country),
  audit trails for every data change, and disaster recovery mandates
```

## Phase 1: Assessment (Month 1-2)
```
Inventory findings:
  - Core financial reporting warehouse: HIGH regulatory sensitivity,
    LOW change frequency (stable, rarely modified) -> candidate for REPLATFORM,
    not full refactor, given the stability and regulatory comfort with the
    existing logic
  - Branch Excel report ingestion: LOW regulatory sensitivity, currently
    entirely manual/error-prone -> strong candidate for REFACTOR (modernize
    entirely, likely using Microsoft Graph API/SharePoint integration per
    `03-python/10-sharepoint-graph-api-integration.md`, given this is
    already a Microsoft-stack enterprise)
  - 3 of the 15 branch source systems: genuinely obsolete, feeding reports
    nobody actually uses anymore (discovered during this assessment) ->
    RETIRE candidates, removing them from migration scope entirely
  - Core banking transactional system itself: HIGHEST regulatory sensitivity,
    extremely latency-critical -> RETAIN on-prem for now, connect to the
    cloud analytics platform via a private network link (Azure ExpressRoute,
    given the Microsoft-stack context) rather than migrating this system itself
```

## Phase 2: Cloud & Architecture Decision
```
Chosen cloud: Azure (already a Microsoft SQL Server / Windows Server shop,
              existing Enterprise Agreement, and needs Microsoft Graph API
              integration for the branch report modernization — see
              `01-fundamentals/08-cloud-fundamentals.md`'s decision framework)

Target architecture:
  Core banking (on-prem, RETAINED) --ExpressRoute private link-->
  Azure Data Factory (orchestration, using Self-Hosted Integration Runtime
                       to securely reach on-prem core banking data)
  --> ADLS Gen2 (raw zone)
  --> Azure Databricks (transform — dedupe, clean, apply SCD Type 2 on
                          customer/account dimensions per regulatory audit needs)
  --> Azure SQL Managed Instance (REPLATFORMED warehouse — familiar SQL Server
                                    engine, minimal query rewrite needed,
                                    but now cloud-managed: automated backups,
                                    patching, and built-in high availability)
  --> Power BI (reporting layer, replacing older on-prem reporting tools)

  Branch Excel reports (REFACTORED):
  SharePoint (branch managers upload here instead of file shares)
  --> Microsoft Graph API extraction (scheduled Python/ADF pipeline)
  --> ADLS Gen2 --> Databricks validation/cleaning --> Azure SQL MI
```

## Phase 3: Security & Compliance Design (treated as first-class, per file 9 and 11's lessons)
```
- Data residency: Azure region selected specifically within the required
  country/jurisdiction (a real, common regulatory constraint driving cloud
  region selection, not just picking the cheapest/closest option)
- Encryption: customer-managed keys (CMK) for the warehouse and ADLS,
  satisfying stricter regulatory key-control requirements
- IAM: least-privilege service principals for every pipeline (per file 9),
  each ADF pipeline/Databricks job scoped to EXACTLY the specific
  ADLS paths/SQL tables it needs, nothing broader
- Audit: Azure Activity Log + Microsoft Purview data lineage tracking,
  satisfying the "trace every data change" regulatory audit requirement
- Network: ExpressRoute private connectivity for the on-prem core banking
  link, and Private Endpoints for ADLS/SQL MI access from within the Azure
  VNet — no public internet exposure for any sensitive data path
```

## Phase 4: Migration Execution (Wave-Based, per file 7)
```
Wave 1 (Month 3-6): Branch Excel report modernization — chosen FIRST as
                     the lowest-risk, highest visible-improvement win
                     (eliminates manual, error-prone Excel handling
                     entirely), building team confidence and stakeholder
                     buy-in before tackling the core warehouse.

Wave 2 (Month 7-14): Core financial warehouse REPLATFORM — migrate to
                      Azure SQL Managed Instance, running in PARALLEL with
                      the still-live on-prem warehouse, reconciling outputs
                      daily (FULL OUTER JOIN comparison pattern from
                      `02-sql/06-advanced-sql-patterns.md`) for several
                      months before any cutover decision.

Wave 3 (Month 15-18): Full cutover of the core warehouse once parallel-run
                       reconciliation shows consistent, trusted results;
                       decommission on-prem warehouse hardware exactly
                       ahead of the looming hardware refresh deadline that
                       originally triggered this whole project.

Ongoing: Core banking transactional system remains RETAINED on-prem
         indefinitely (or until a FUTURE, separate migration decision) —
         connected via ExpressRoute for analytics purposes only.
```

## Cost Optimization Built In From the Start (per file 8's lessons)
```
- ADLS lifecycle policies: raw landing data moves to cool/archive tier after
  30/180 days automatically
- Databricks jobs use auto-scaling clusters, sized for typical (not peak)
  daily volume, avoiding a permanently oversized cluster running 24/7
- Azure SQL MI sized based on the REPLATFORMED workload's actual measured
  usage (informed by the parallel-run period's real query patterns),
  not a rough on-prem-hardware-equivalent guess
- Reserved capacity purchased for the SQL MI instance (a genuinely
  predictable, steady, long-term workload) once sizing was confirmed
  during the parallel-run validation period
```

## Why This Design Reflects Every Lesson From This Module
```
- 6 R's framework applied thoughtfully per-system, not a single blanket
  migration strategy (file 7)
- Security/compliance designed in from Phase 1, not bolted on later (file 9,
  reinforced by file 11's Capital One lesson)
- Wave-based, risk-managed rollout with genuine parallel-run validation,
  not a risky big-bang cutover (file 7)
- Cost optimization considered from the architecture stage, not an
  afterthought once bills arrived (file 8)
- A concrete business trigger (the hardware refresh deadline) drove the
  decision, exactly matching the realistic pattern from file 11
- Hybrid/coexistence accepted as the genuine, deliberate end-state for the
  core banking system, not treated as an incomplete migration (file 6)
```

## Try It Yourself
Using this same phased, security-first, cost-aware reasoning, design a migration plan for:
1. A healthcare provider migrating patient records analytics to the cloud (consider HIPAA-equivalent regulatory constraints).
2. A retail company migrating its on-prem Hadoop cluster to a modern cloud lakehouse (consider which of the 6 R's applies to different pieces of their existing Hadoop ecosystem).


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The truest teacher leads by quiet example, not loud instruction."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
