# Case Study 4: Multi-Tenant SaaS Analytics Platform (Embedded Analytics)

## Step 1: Requirements
```
Functional: a B2B SaaS product (e.g., a project management tool) needs
            to offer EACH of its customers (tenants) their own
            analytics dashboard, embedded directly in the product
            (recap `09-visualization/08`'s embedded analytics discussion)

Non-functional:
  - Isolation: Tenant A must NEVER see Tenant B's data — a hard,
    non-negotiable security requirement
  - Scale: 5,000 tenant companies, ranging from tiny (10 users) to huge
    (50,000 users) — a genuinely SKEWED tenant size distribution
  - Latency: dashboards should load within 2-3 seconds
  - Cost: must be cost-efficient — cannot provision fully dedicated
    infrastructure PER tenant, given the long tail of tiny tenants
  - Customization: some large tenants want CUSTOM metrics beyond the
    standard dashboard — a genuine flexibility requirement
```

## Step 2: High-Level Data Flow
```
Each tenant's application events (Kafka, tagged with tenant_id)
   -> Shared ingestion pipeline (Spark, processes ALL tenants together
      for efficiency, but ALWAYS carries tenant_id through every stage)
   -> Shared warehouse (Snowflake/BigQuery), with tenant_id as a
      MANDATORY column on every table
   -> Row-Level Security (recap `09-visualization/04`) enforced at the
      warehouse/BI-tool layer, ensuring each tenant's dashboard query
      is automatically filtered to ONLY their own tenant_id
   -> Embedded BI tool (Power BI Embedded / Looker) rendering each
      tenant's dashboard within the SaaS product's own UI
```
**Key architectural insight**: the CORE design decision here is "shared infrastructure with enforced logical isolation" (multi-tenant, RLS-based) vs "dedicated infrastructure per tenant" (single-tenant, physically isolated) — this is one of THE most common, most important tradeoff decisions in real SaaS system design.

## Step 3: Capacity Estimation
```
5,000 tenants, average ~500 users each (skewed distribution, some much
  bigger) x ~20 events/user/day ≈ 50,000,000 events/day total across
  ALL tenants — this shared-infrastructure total is what actually needs
  sizing, NOT each tenant individually, since the pipeline processes
  everyone together.

50M events/day x 1 KB ≈ 50 GB/day raw, ≈ ~3.5 TB/year compressed —
  a genuinely MODEST total scale, reinforcing that SHARED infrastructure
  (not per-tenant dedicated clusters) is the clearly cost-appropriate choice here.
```

## Step 4: Technology Choices, Justified

**Shared multi-tenant infrastructure with Row-Level Security, NOT per-tenant dedicated infrastructure**
> Justification: the capacity estimate shows genuinely modest TOTAL scale (3.5 TB/year) — provisioning 5,000 SEPARATE dedicated pipelines/warehouses would be wildly wasteful and operationally unmanageable (5,000x the maintenance burden) for a workload that comfortably fits in ONE well-designed shared system. Tradeoff accepted: RLS implementation must be RIGOROUSLY correct (a bug here is a severe cross-tenant data leak, the hard "never" requirement) — this justifies investing real engineering effort in RLS testing/auditing specifically.

**tenant_id as a mandatory, enforced column on every single table**
> Justification: makes the isolation boundary EXPLICIT and consistently enforceable at the query layer, rather than relying on separate databases/schemas per tenant (which would reintroduce the "5,000x maintenance burden" problem the shared-infrastructure choice was meant to avoid).

**Handling the largest tenants (50,000 users) differently within the shared system**
> Justification: the SKEWED tenant size distribution (file 4's data skew concept, applied at the TENANT level rather than the data-row level) means the biggest tenants could dominate shared compute resources — mitigated via resource quotas/prioritization (similar to Airflow Pools, `08-orchestration/04`) ensuring one huge tenant's heavy usage doesn't degrade smaller tenants' dashboard performance.

**Embedded BI with per-tenant RLS tokens (recap `09-visualization/08`)**
> Justification: lets each tenant see a fully customized-feeling dashboard embedded natively in the SaaS product, while the underlying data/infrastructure remains efficiently SHARED — directly solving the "cost-efficient but still feels dedicated" requirement.

## Step 5: Failure Modes & Scale
```
"How would you CATCH a potential RLS bug before it causes a real leak?"
  -> Automated tests SPECIFICALLY verifying cross-tenant isolation
     (e.g., a test querying "as Tenant A" and asserting Tenant B's
     data NEVER appears in results) run in CI (recap `10-devops/08`) —
     treating this as a security-critical test suite, not just a
     functional nice-to-have.

"What happens when the single largest tenant (50,000 users) wants a
custom metric no other tenant needs?"
  -> A genuinely common real tension in multi-tenant systems: fully
     custom per-tenant logic reintroduces the maintenance-burden problem
     the shared architecture was meant to avoid. A senior-level answer
     proposes a CONFIGURABLE metrics framework (parameterized, not
     hand-coded per tenant) as the scalable middle ground, rather than
     either refusing all customization OR building fully bespoke logic
     per large customer.

"Where does this break first if tenant count grows from 5,000 to 50,000?"
  -> The SHARED warehouse's total query concurrency (many tenants'
     dashboards being viewed simultaneously) is a likely first
     bottleneck, mitigated by warehouse compute scaling (recap
     `05-databases/05`'s serverless/elastic warehouse concepts) and
     potentially BI-tool-level caching for frequently-viewed dashboards.
```

## Step 6: Summary
> "Given the modest total data scale (3.5 TB/year) but strict cross-tenant isolation requirement, I'm proposing a SHARED multi-tenant architecture with mandatory tenant_id columns and rigorously-tested Row-Level Security, rather than per-tenant dedicated infrastructure — the shared approach is dramatically more cost-efficient and operationally manageable at this scale. The critical risk this design accepts is that RLS MUST be implemented flawlessly, which I'd address with a dedicated cross-tenant-isolation test suite treated as security-critical. I'd also want to establish a configurable-metrics framework early, rather than allowing ad-hoc custom logic per large tenant, to keep this shared architecture maintainable as the tenant base grows."


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The wisest builder measures success by what still stands long after they've moved on."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
