# 7. Cloud Migration Playbook — The Real, Phased Strategy

## The 6 R's of Migration (the industry-standard framework)
```
1. REHOST ("lift and shift")
   Move a workload to the cloud with MINIMAL changes — e.g., take an on-prem
   VM running SQL Server, move it to an equivalent cloud VM as-is.
   Fastest, lowest immediate risk, but doesn't capture cloud-native benefits
   (elasticity, managed services) — often a deliberate FIRST step, not the end goal.

2. REPLATFORM ("lift, tinker, and shift")
   Move to the cloud with SOME optimization, without a full rearchitecture —
   e.g., move an on-prem SQL Server database to Azure SQL Managed Instance
   (managed service, but minimal application code changes needed).

3. REFACTOR / RE-ARCHITECT
   Substantially redesign the application/pipeline to be genuinely cloud-native —
   e.g., rebuild an SSIS-based ETL pipeline as ADF + Databricks + dbt,
   taking full advantage of serverless scaling, managed services, and
   modern architecture patterns. Highest effort, highest long-term payoff.

4. REPURCHASE ("drop and shop")
   Replace an existing system with a different, usually SaaS, product —
   e.g., replacing a self-hosted on-prem BI tool with Power BI Service /
   Looker, rather than migrating the old tool's infrastructure at all.

5. RETIRE
   Simply turn OFF a system that's no longer needed — a surprisingly common
   and valuable outcome of a migration ASSESSMENT (many enterprises discover
   systems still running that nobody actually uses anymore).

6. RETAIN
   Deliberately KEEP a system on-prem for now (or permanently) — for
   regulatory, latency, cost, or "not worth the migration effort" reasons,
   exactly the "coexistence" reality described in `04-etl-elt/09`.
```

## A Real Phased Migration Approach (how this actually plays out at a company)

### Phase 1: Assessment & Discovery
```
- Inventory EVERY existing data system/pipeline (you'd be surprised how many
  companies don't have a complete, accurate inventory of their own systems)
- For each system: how critical is it? How often does it change? What's its
  regulatory/compliance sensitivity? What does it currently cost to run/maintain?
- Classify EACH system into one of the 6 R's above based on this assessment
```

### Phase 2: Pilot / Proof of Concept
```
- Choose a LOW-RISK, MEDIUM-VALUE system as a first migration — not the
  most business-critical system (too risky to learn on), and not something
  trivial (won't teach the team enough or demonstrate real value)
- Use this pilot to build genuine team expertise and refine the actual
  migration process/tooling before scaling up to more critical systems
```

### Phase 3: Wave-Based Migration (the "strangler pattern" applied to migration)
```
Wave 1: Migrate systems with HIGH change-frequency and LOW regulatory risk first
        (these benefit MOST from cloud's elasticity/faster iteration, and
         migrating them first delivers the most visible business value early,
         building momentum/support for the broader migration effort)

Wave 2: Migrate medium-complexity systems, applying lessons learned from Wave 1

Wave 3+: Tackle the hardest, highest-risk, most business-critical systems LAST,
         once the team has substantial real migration experience and confidence
```
This mirrors EXACTLY the "strangler pattern" migration philosophy described in `04-etl-elt/09-legacy-vs-modern-migration.md` — gradual, risk-managed, business-value-prioritized, not a risky big-bang cutover.

### Phase 4: Coexistence Period (often lasting YEARS, not months)
```
During migration, systems will run BOTH on-prem and cloud simultaneously —
requiring careful data synchronization (often via CDC, see file 5's Datastream/
`01-fundamentals/02-core-concepts.md`) so both environments stay consistent
until the on-prem system is FULLY decommissioned. This coexistence period is
frequently underestimated in migration project timelines — a very common,
real project management mistake to be aware of.
```

### Phase 5: Decommission (Retire)
```
Only after full confidence in the new cloud system (typically after running
BOTH in parallel and validating outputs match for a meaningful period) does
the old on-prem system actually get turned off — turning it off too early,
before this validation, is a common and costly mistake if bugs surface later
without a fallback available.
```

## Real Migration Risks & How Experienced Teams Mitigate Them
```
Risk: Data loss/corruption during migration
Mitigation: run OLD and NEW systems in parallel, reconcile outputs
            (exactly the FULL OUTER JOIN reconciliation pattern from
            `02-sql/06-advanced-sql-patterns.md`) before fully cutting over

Risk: Underestimating hidden dependencies (system X secretly depends on
      system Y's exact on-prem network configuration/behavior)
Mitigation: thorough Phase 1 assessment/discovery, including tracing actual
            data lineage and less-obvious application dependencies, not
            just the systems everyone already knows about

Risk: Cost overruns (cloud costs spiraling beyond the on-prem cost being replaced)
Mitigation: FinOps practices from the start (see file 8), not as an afterthought
            bolted on after costs have already grown out of control

Risk: Team skill gap (team knows on-prem tools deeply, cloud tools barely)
Mitigation: deliberate training investment BEFORE (not during) the migration,
            and the pilot phase specifically exists to build this expertise
            on a lower-stakes system first
```

## A Realistic Example Migration Roadmap (mid-size retail company)
```
Month 1-2:   Full system inventory + 6 R's classification for every workload
Month 3-4:   Pilot — migrate a low-risk internal reporting dashboard's data
             pipeline (Repurchase: retire old BI tool, adopt Power BI)
Month 5-9:   Wave 1 — migrate marketing analytics, customer support ticketing
             data pipelines (Refactor: rebuild as ADF + Databricks + dbt)
Month 10-15: Wave 2 — migrate core e-commerce order processing analytics
             (Replatform first: lift-and-shift the warehouse to Azure SQL MI,
              THEN incrementally refactor pipeline logic over subsequent months)
Month 16-24: Wave 3 — the hardest, most critical system: financial reporting/
             compliance data warehouse (Refactor, with an extended parallel-run
             validation period given the regulatory stakes)
Ongoing:      Certain legacy systems deliberately RETAINED on-prem indefinitely
              (e.g., a stable, rarely-touched 15-year-old inventory system
              where migration ROI genuinely doesn't justify the risk/effort)
```

## Interview Traps
- "Walk me through how you'd approach migrating a company's legacy data infrastructure to the cloud." — this is one of the MOST common senior DE interview questions; structure your answer around the phased approach above (assess → pilot → wave-based migration → coexistence → decommission), not a rushed big-bang plan.
- Be ready to name and explain all 6 R's with a concrete example of each — a very commonly tested piece of migration vocabulary.
- "What's the biggest risk in a cloud migration, in your experience/understanding?" — underestimated hidden dependencies and underestimated coexistence-period duration are both strong, realistic answers.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The wise treat every obstacle as a teacher in disguise."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
