# 9. What Real Companies Use — Orchestration Stacks

## Airbnb — Created Airflow, Still Runs It at Massive Scale
As covered in `06-big-data/09-what-companies-use.md`, Airbnb created Airflow specifically because their growing number of interdependent scheduled data pipelines (hundreds, then thousands) became unmanageable to track manually. Airbnb continues to run Airflow at enormous scale internally, and remains one of the most active contributors to the open-source project — a genuine, ongoing "eating your own dog food" commitment.

## Spotify — Apache Beam/Dataflow-Centric, With Airflow-Adjacent Orchestration
As covered in `06-big-data/09-what-companies-use.md`, Spotify's core data processing philosophy centers on Apache Beam's unified batch/streaming model (via GCP Dataflow) — their orchestration layer coordinates these Beam pipelines alongside other data platform components, often using Airflow (or GCP's managed Cloud Composer) as the scheduling/dependency layer wrapping around their Beam-based processing logic.

## Netflix — Built Its Own Orchestration Tooling (Genie, Conductor)
Netflix, true to the recurring pattern from earlier modules, built SOME of its own internal orchestration tooling (e.g., Conductor, a workflow orchestration engine Netflix open-sourced) tailored to their specific microservices-heavy, resilience-first architecture — while also using Airflow for more traditional batch data pipeline scheduling in parts of their data platform. This reflects a broader theme: **very large tech companies often run a MIX of open-source standards (Airflow) and internally-built tools for their most specific/unusual needs**, rather than a single one-size-fits-all orchestrator company-wide.

## Enterprises on Microsoft Stack — Azure Data Factory as the Default
Large enterprises already standardized on Microsoft/Azure overwhelmingly default to ADF pipelines for orchestration (see `04-etl-elt/06`) — not necessarily because it's technically superior to Airflow, but because of its native integration with the rest of their Azure investment, and because it doesn't require standing up/maintaining a separate Airflow deployment for teams without existing Airflow expertise.

## AWS-Centric Companies — A Genuine Mix of MWAA and Step Functions
Companies deeply embedded in AWS often use BOTH: **MWAA (Managed Workflows for Apache Airflow)** for complex, code-heavy data pipeline orchestration (leveraging Airflow's broader ecosystem/community), and **Step Functions** for simpler, more lightweight AWS-service-to-service orchestration (e.g., "when a file lands in S3, trigger a Lambda, then a Glue job, then send an SNS notification") — genuinely using each tool for the specific type of workflow it suits best, exactly the "use both" pattern described in file 7's comparison.

## The Broader 2024-2026 Trend — dbt + Airflow/Dagster as the Modern Default Combo
```
Across MANY modern product companies building fresh data platforms today,
a very common combination has emerged:
  - Airflow (or increasingly, Dagster) handles SCHEDULING and cross-system
    orchestration (waiting for an upstream API extract, then triggering...)
  - dbt handles the actual SQL TRANSFORMATION logic within the warehouse
    (see `04-etl-elt/08-dbt-deep-dive.md`)
  - The orchestrator's job is often reduced to simply: "run `dbt run` and
    `dbt test` on a schedule, and alert on failure" — with the CxOMPLEX
    transformation dependency logic itself living inside dbt's own
    `{{ ref() }}`-based dependency graph, not hand-wired in the orchestrator
```
This division of responsibility (orchestrator handles scheduling/cross-system coordination; dbt handles in-warehouse transformation dependencies) has become a genuinely common, pragmatic modern pattern — reducing the complexity that used to live entirely within massive, sprawling Airflow DAGs.

## The Recurring Pattern (once again)
```
Just as with big data tools (file 9 of module 06) and databases (file 11
of module 05), orchestration tooling follows the same pattern: widely-used
open-source standards (Airflow) coexist with cloud-native options (ADF,
Step Functions) AND internally-built tools at the very largest companies
(Netflix's Conductor) — the "right" choice depends genuinely on a
company's existing stack, team skills, and SPECIFIC workflow needs, not
a single universally correct answer.
```

## Interview Traps
- "Does every company just use Airflow?" — no; a nuanced answer acknowledges the real mix (Airflow's broad open-source dominance, cloud-native alternatives for cloud-committed teams, and internal tooling at the very largest companies with sufficiently unusual needs to justify building their own).
- "What's the modern relationship between an orchestrator and dbt?" — the orchestrator handles scheduling/cross-system coordination, while dbt manages the actual in-warehouse transformation dependency graph internally — a common, pragmatic division of responsibility in 2024-2026 data platforms.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Let go of comparison, and you will find your own pace is enough."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
