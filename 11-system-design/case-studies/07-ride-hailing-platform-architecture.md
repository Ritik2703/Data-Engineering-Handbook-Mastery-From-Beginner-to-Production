# Case Study 7: Ride-Hailing Full Data Platform (Uber-style) — Architect-Level Scope

*This case study operates at a broader ARCHITECT-level scope (recap file 9) than the others — designing the OVERALL data platform strategy across multiple teams/systems, not just one pipeline.*

## Step 1: Requirements (Organizational Scope)
```
Business context: a ride-hailing company has grown from a startup (one
  small data team, one Postgres database) to a mid-size company with
  MULTIPLE product teams (rider app, driver app, pricing/surge team,
  safety team, finance) each wanting their own data needs served,
  currently creating duplicated, inconsistent pipelines and growing
  data warehouse costs with no clear ownership model.

Architect-level requirements:
  - Enable MULTIPLE teams to build their own data pipelines/models
    WITHOUT creating a bottleneck on one central data team (recap
    file 3's Data Mesh discussion)
  - Establish CONSISTENT definitions for core business metrics (recap
    `09-visualization/06`'s semantic layer discussion) so "active
    driver" means the SAME thing across pricing, safety, and finance teams
  - Real-time needs (matching, surge pricing) MUST coexist with batch
    analytics needs (financial reporting, growth metrics) — recap
    the ride-hailing DATABASE case study (`05-databases/case-studies/`),
    now extended to the FULL data platform level
  - Cost governance — as pipeline count grows across teams, cost
    accountability (recap `07-cloud-platforms/08`'s FinOps) must scale too
```

## Step 2: The Organizational + Technical Architecture
```
                    ┌─────────────────────────────────────┐
                    │   PLATFORM TEAM (shared foundation)    │
                    │  - Kafka infrastructure (event backbone)│
                    │  - Warehouse infrastructure (Snowflake) │
                    │  - dbt Semantic Layer (core metric      │
                    │    definitions: "active driver",        │
                    │    "completed trip", "surge multiplier")│
                    │  - Orchestration platform (Airflow,      │
                    │    shared, metadata-driven per           │
                    │    `08-orchestration/case-studies/`)      │
                    │  - Data catalog/governance standards      │
                    └─────────────────────────────────────┘
                                      |
        ┌─────────────────┬──────────┴──────────┬─────────────────┐
        v                 v                     v                 v
  Pricing Team      Safety Team           Finance Team      Growth Team
  (owns their OWN   (owns their OWN       (owns their OWN   (owns their OWN
   dbt models for    dbt models for        dbt models for    dbt models for
   surge/matching    incident detection    revenue/payout     activation/
   data, using        models, using         reconciliation,    retention
   shared real-time   shared event data)    using shared       metrics, using
   event backbone)                          warehouse infra)   shared infra)
```
**Key architectural insight (this is the CORE of what makes this an architect-level, not senior-engineer-level, problem)**: the design decision isn't "which database/streaming tool" — it's ORGANIZATIONAL: a Data Mesh-inspired model where a PLATFORM team provides shared, well-governed INFRASTRUCTURE and CORE metric definitions, while INDIVIDUAL product teams own their OWN domain-specific pipelines/models on top of that shared foundation — directly solving the stated "one central team is a bottleneck" problem while maintaining consistency where it matters most (core metrics).

## Step 3: Capacity Estimation (Organizational Scale)
```
At this company's scale (recap the ride-hailing DATABASE case study's
  numbers): millions of location pings/minute, hundreds of thousands of
  trips/day across the core event backbone — but the ARCHITECT-level
  estimation question is different: "how many PIPELINES/dbt models
  will exist across ALL teams in 2 years, and does our platform
  (Airflow scheduler capacity, dbt project structure, warehouse compute)
  scale to support DOZENS of teams each building 10-50 models, not just
  ONE team's needs?" — this is capacity planning for ORGANIZATIONAL
  GROWTH, not just data volume growth.
```

## Step 4: Technology/Governance Choices, Justified

**A dbt Semantic Layer for CORE cross-team metrics, but NOT for every team-specific metric**
> Justification: recap `09-visualization/06` — the semantic layer solves metric INCONSISTENCY specifically for metrics MULTIPLE teams need to agree on (revenue, active drivers); forcing EVERY team-specific metric through central semantic layer governance would recreate the exact central-bottleneck problem this architecture is meant to solve. The judgment call here — WHICH metrics need central governance vs which can be team-owned — is itself a genuinely architect-level decision.

**Shared Kafka event backbone, team-owned downstream consumers**
> Justification: recap file 3's event-driven architecture pattern — the core trip/location event stream is produced ONCE by the platform team, and EACH product team (pricing, safety) builds their OWN consumer logic independently, without needing the platform team to build custom integration for each team's specific need.

**A metadata-driven, shared Airflow platform (recap `08-orchestration/case-studies/`) rather than each team running its own separate orchestrator**
> Justification: avoids the operational overhead/cost of MULTIPLE teams each maintaining their own Airflow deployment, while the metadata-driven pattern lets each team register their OWN DAGs/pipelines without needing platform-team approval for every single new pipeline — balancing shared infrastructure efficiency against team autonomy.

**A lightweight architectural review process for NEW shared infrastructure decisions (not for every individual pipeline)**
> Justification: the architect-level judgment here is deciding WHAT requires cross-team review (e.g., "should we adopt a new warehouse technology," "should we change the core event schema") vs what teams should decide autonomously (their own specific dbt models/dashboards) — over-governing everything recreates the bottleneck; under-governing shared/foundational decisions risks fragmentation.

## Step 5: Failure Modes & Scale (Organizational)
```
"What happens when Team A's dbt model changes a shared upstream table's
schema, breaking Team B's downstream model?"
  -> Directly connects to file 5's data contract discussion — this
     needs an explicit, ENFORCED schema change/review process for
     shared tables specifically (not every table), with the semantic
     layer's core metrics given the STRICTEST protection since the
     most teams depend on them.

"How do you prevent cost from spiraling as team count and pipeline
count both grow?"
  -> Recap `07-cloud-platforms/08`'s FinOps tagging discipline, applied
     ORGANIZATIONALLY: every team's warehouse usage/pipelines are
     tagged by team, with visible cost dashboards PER team (chargeback/
     showback) — making cost a visible, owned concern for each team,
     not an opaque central platform-team problem alone.

"A new team (e.g., a new 'insurance products' team) joins — how do
they onboard onto this platform?"
  -> A genuinely architect-level concern: is there DOCUMENTED,
     SELF-SERVICE onboarding (a template dbt project structure, clear
     platform documentation, a "how to register a new DAG" guide) or
     does every new team require bespoke, time-consuming platform-team
     hand-holding? — the ANSWER to this question is itself a measure
     of whether this architecture will genuinely scale organizationally,
     not just technically.
```

## Step 6: Summary
> "Given the organizational bottleneck problem (one central team, multiple product teams needing data capability), I'm proposing a Data Mesh-inspired architecture: a platform team providing shared infrastructure (Kafka, warehouse, orchestration) and a semantic layer for CORE cross-team metrics specifically, while individual product teams own their own domain-specific pipelines on top of that foundation. The central tradeoff is accepting LESS centralized control over team-specific data logic in exchange for removing the central-team bottleneck — justified because the stated problem is explicitly about team velocity being blocked by centralization. This only works with genuine organizational discipline: clear standards for what requires cross-team review (core metrics, shared schemas) versus team autonomy (their own models/dashboards), and self-service onboarding documentation so this scales to new teams without constant platform-team hand-holding."

## Why This Case Study Is Different From the Other 6
```
Case studies 1-6 each design ONE coherent system/pipeline for a specific
technical requirement. This case study operates at the SCOPE described
in file 9's "Data Architect" description — designing not just a
pipeline, but the ORGANIZATIONAL STRUCTURE and GOVERNANCE MODEL under
which MANY teams' pipelines coexist — precisely the kind of problem
that separates Senior Data Engineer interviews from Staff/Principal/
Architect-level interviews, and exactly why this module exists.
```


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The mind that stays curious never stops finding better ways to serve others."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
