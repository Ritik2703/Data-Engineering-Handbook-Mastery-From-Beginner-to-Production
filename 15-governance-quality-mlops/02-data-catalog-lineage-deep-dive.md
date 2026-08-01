# 2. Data Catalog & Lineage — Deep Dive

## Why a Data Catalog Is Foundational (Not Optional) Infrastructure
As an organization's data platform grows to hundreds/thousands of tables across multiple teams (recap the Data Mesh discussion in `03-architecture-patterns-deep-dive.md` and file 7 of this module), a genuinely critical question becomes impossible to answer without tooling: "does this data already exist somewhere, what does it mean, who owns it, and can I trust it?" A Data Catalog is the searchable, centralized system answering exactly this.

## What a Modern Data Catalog Actually Provides
```
1. DISCOVERY: search across all datasets by name, description, tags,
   or even by column name ("which tables have a column called
   'customer_email'?")

2. METADATA: schema, row counts, last-updated timestamp, data
   classification tags (recap file 1), owning team

3. LINEAGE: a visual/queryable graph showing WHERE a table's data
   came from (upstream sources) and WHAT depends on it (downstream
   consumers) — directly extending dbt's own `{{ ref() }}`-based
   lineage (recap `04-etl-elt/08`) to the ENTIRE platform, across
   tools, not just within one dbt project

4. GLOSSARY: business term definitions tied to actual technical
   columns (e.g., "Active User" officially means X, defined here,
   linked to the specific column implementing it — directly connecting
   to the semantic layer discussion in `09-visualization/06`)

5. USAGE ANALYTICS: which tables/columns are actually queried, by
   whom, how often — genuinely useful for deprecating unused tables
   and understanding true data value
```

## AWS Glue Data Catalog (recap + governance-specific depth)
Already covered technically in `04-etl-elt/07` as the metadata layer enabling Athena/Redshift Spectrum/EMR — from a GOVERNANCE lens specifically, its **Lake Formation** companion service adds fine-grained, column-level and row-level access control ENFORCED at the catalog level, so permissions are defined ONCE centrally and respected consistently across every query engine reading from it, rather than each tool implementing its own separate access control.

## Microsoft Purview (Azure)
```
Automatically SCANS across ADLS, Synapse, SQL Database, and even
multi-cloud/on-prem sources, building a catalog with automatic
SENSITIVE DATA CLASSIFICATION (built-in detection rules for PII
patterns like SSNs, credit card numbers, email addresses — recap file
1's classification framework, largely automated) and lineage tracking
across ADF pipelines specifically (recap `04-etl-elt/06` and
`07-cloud-platforms/04`) — Purview is explicitly positioned as the
GOVERNANCE layer sitting across Azure's whole data estate, not a
per-service feature.
```

## Databricks Unity Catalog
```
Unity Catalog's genuinely distinctive positioning: a SINGLE governance
layer spanning MULTIPLE workspaces and even (increasingly) multiple
clouds, providing fine-grained access control down to the ROW and
COLUMN level directly on Delta tables, automatic lineage capture
between notebooks/jobs/dashboards, and centralized AUDIT LOGGING of
every query — a genuinely significant unification, since historically
Databricks workspace-level permissions were more fragmented before
Unity Catalog's introduction.
```

## Open-Source Alternatives — DataHub & Amundsen
```
Amundsen (created at Lyft): one of the earliest open-source data
  discovery/catalog tools, search-centric UI, strong at basic
  discovery and popularity-based ranking of tables.

DataHub (created at LinkedIn): a more comprehensive, actively-developed
  open-source platform combining catalog, lineage, and increasingly
  data quality/observability features — notable for a "push-based"
  metadata ingestion architecture (sources actively publish metadata
  changes) alongside traditional "pull-based" scanning, enabling
  more REAL-TIME catalog freshness than periodic-scan-only catalogs.

Why companies choose open-source over a cloud-native catalog: avoiding
  vendor lock-in to one cloud (recap the cloud-agnostic tooling
  discussion in `07-cloud-platforms/06`), and often lower direct cost
  at scale — at the cost of needing to self-host and operate the catalog
  infrastructure themselves (the same tradeoff pattern seen throughout
  this repo's "build vs buy" discussions).
```

## Automated Lineage — How It's Actually Captured (the technical mechanism)
```
Static/parse-based lineage: analyzing SQL/dbt code text itself to
  determine dependencies (e.g., dbt's own `{{ ref() }}` graph, or a
  catalog tool parsing SQL queries to infer table-to-table dependencies)
  — works well for SQL-based transformations, harder for complex
  procedural code.

Runtime/execution-based lineage: capturing ACTUAL data flow as jobs
  run (e.g., Spark job execution plans, or query logs showing which
  tables a specific query actually read/wrote) — captures what
  GENUINELY happened, including dynamic/conditional logic static
  parsing might miss, at the cost of needing runtime instrumentation.

Most mature catalog tools combine BOTH approaches for the most
complete, trustworthy lineage graph.
```

## A Practical Governance Tagging Pattern (tying file 1's classification to real catalog tooling)
```sql
-- Tagging a column's sensitivity directly in the catalog (conceptual,
-- syntax varies by specific catalog tool)
ALTER TABLE customers ALTER COLUMN email 
SET TAGS ('classification' = 'PII', 'masking_policy' = 'partial_mask');

-- This tag then DRIVES automated enforcement -- e.g., Unity Catalog or
-- Lake Formation applying a masking policy automatically to any query
-- against this column from a role that isn't explicitly authorized to
-- see raw PII, WITHOUT needing to rewrite every single downstream query
-- to manually mask it themselves
```

## Interview Traps
- "Why is a data catalog considered governance infrastructure, not just a search tool?" — it's what makes classification tagging, access policy enforcement, and lineage-based impact analysis (recap `11-system-design/05`'s data contract discussion) actually OPERATIONAL at scale, rather than theoretical policy nobody can consistently apply.
- "Static vs runtime lineage capture — what's the tradeoff?" — static/parse-based is easier to implement for SQL-heavy stacks but can miss dynamic logic; runtime-based captures what genuinely happened but needs execution instrumentation — mature tools combine both.
- "Why might a company choose an open-source catalog (DataHub/Amundsen) over a cloud-native one (Purview/Unity Catalog)?" — avoiding vendor lock-in and potentially lower cost at scale, accepting the tradeoff of self-hosting/operating the infrastructure themselves.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"To protect what is entrusted to you is itself a sacred form of service."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
