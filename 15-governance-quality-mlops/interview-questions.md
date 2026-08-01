# Governance, Quality & MLOps Interview Questions — 30+ with Answers

## Governance Fundamentals

**Q1. What is data governance, in your own words?**
> The overall system of decision rights, policies, and accountability determining how data is collected, classified, secured, accessed, and used — answering who is allowed to do what with which data, and who is accountable if it goes wrong.

**Q2. What's the difference between GDPR's "right to erasure" and a normal DELETE operation?**
> Right to erasure requires tracing and deleting a SPECIFIC individual's data across potentially many systems (raw, staged, aggregated, backups) — a genuinely hard system design problem, not a single DELETE statement.

**Q3. What counts as PII, beyond obvious fields like name and SSN?**
> Quasi-identifiers that can identify someone when COMBINED (e.g., ZIP code + birth date + gender has been shown to uniquely identify most of the US population) — PII isn't just "obviously personal" fields.

**Q4. Anonymization vs pseudonymization — what's the difference?**
> Pseudonymization replaces identifiers with a consistent token, reversible via a securely-stored mapping (enables joins/aggregation while hiding identity from most users); true anonymization aims to be irreversible and is genuinely harder to achieve correctly than simply removing obvious identifying columns.

**Q5. What's the difference between a Data Owner, Data Steward, and Data Custodian?**
> Owner (typically business-side) is accountable for policy decisions; Steward maintains day-to-day documentation/quality/classification; Custodian (often Data Engineering) implements the technical enforcement.

## Catalog & Lineage

**Q6. Why is a data catalog considered governance infrastructure, not just a search tool?**
> It's what makes classification tagging, access policy enforcement, and lineage-based impact analysis actually operational at scale, rather than theoretical policy nobody can consistently apply.

**Q7. Static vs runtime lineage capture — what's the tradeoff?**
> Static/parse-based analyzes code text (works well for SQL, easier to implement); runtime-based captures actual execution flow (catches dynamic logic static parsing might miss, needs instrumentation). Mature tools combine both.

**Q8. Why might a company choose DataHub/Amundsen over Purview/Unity Catalog?**
> Avoiding vendor lock-in to one cloud and potentially lower cost at scale, accepting the tradeoff of self-hosting/operating the infrastructure themselves.

## Master Data Management

**Q9. What's a "golden record"?**
> The single, trusted, reconciled version of an entity across multiple disagreeing source systems, produced via matching + survivorship rules.

**Q10. Deterministic vs probabilistic matching — tradeoffs?**
> Deterministic (exact-match rules) is simple/high-precision but misses genuine matches with data variation; probabilistic/fuzzy matching catches more matches via confidence scoring but risks false-positive merges without careful threshold tuning.

**Q11. How would you decide which source wins when two systems disagree on a customer's address?**
> Explicit, documented survivorship rules (recency-based, trusted-source-hierarchy, or completeness-based), owned by a Data Steward.

## Data Quality & Observability

**Q12. What's the difference between data testing and data observability?**
> Testing catches anticipated failure modes via explicit rules; observability catches unanticipated anomalies via automated statistical baseline monitoring — complementary practices.

**Q13. Name the 5 pillars of data observability.**
> Freshness, Volume, Schema, Distribution, Lineage.

**Q14. What's a data contract, and why has it become an important practice?**
> A formal, often cross-team agreement (schema + SLA) validated on the producer side before shipping a change — prevents the classic "upstream team silently renamed a field and broke downstream pipelines" incident, increasingly important as more teams produce/consume shared data (Data Mesh).

**Q15. Great Expectations vs Soda — what's the real tradeoff?**
> Great Expectations offers a comprehensive, programmatic Python framework with rich reporting; Soda offers simpler, declarative YAML, lowering the barrier for less-technical contributors.

**Q16. How would you build basic data observability without a commercial tool?**
> A scheduled statistical anomaly query (e.g., 3-sigma row-count deviation check) run via dbt/Airflow with Slack alerting.

**Q17. Where should data quality checks be placed across a platform, and why?**
> Multiple layers: ingestion (catch garbage early), transformation (business logic validation), contract boundaries (catch breaking changes before they ship), and serving (final sanity checks before reaching a dashboard/model) — different layers catch different failure classes.

## MLOps

**Q18. What's a feature store, and what problem does it solve?**
> Solves "training-serving skew" by defining feature logic once, serving both an offline store (historical data for training) and an online store (low-latency current values for real-time inference).

**Q19. Where does Data Engineering responsibility typically end and ML Engineering begin?**
> DE typically owns feature engineering, feature serving infrastructure, and increasingly deployment pipeline orchestration; ML Engineering/Data Science typically owns model algorithm selection and training — though these blend at smaller companies.

**Q20. How does data drift differ from a normal data quality anomaly?**
> The technique (distribution monitoring) is the same; the application is specifically to a model's input features, checked against the data the model was originally trained on.

**Q21. Feast vs Tecton — what's the tradeoff?**
> Feast is open-source, self-hosted, flexible; Tecton is a commercial, fully-managed feature platform — the same open-source-vs-managed tradeoff seen throughout data tooling generally.

## Data Mesh

**Q22. What are the 4 principles of Data Mesh?**
> Domain-oriented decentralized data ownership, Data as a Product, Self-serve data infrastructure as a platform, Federated computational governance.

**Q23. Is Data Mesh always the right architecture?**
> No — it requires genuine organizational maturity (domain teams with real DE capability, genuine cross-team governance discipline, truly self-service platform infrastructure); without this maturity, it can leave an organization worse off (more fragmented) than a well-run centralized team.

**Q24. How is Data Mesh different from microservices?**
> Microservices decompose application/service logic; Data Mesh is fundamentally an organizational pattern decomposing data OWNERSHIP across business domains, with technical implementation second.

## Governance Operating Model

**Q25. How would you get a data governance policy actually adopted, not just written?**
> An operating model (Governance Council + explicit RACI + policy-as-code automated enforcement), genuine executive sponsorship, and low-friction self-service tooling — a policy document alone accomplishes nothing.

**Q26. What metrics would prove a governance program is actually working?**
> Catalog/classification coverage, data quality score, Mean Time To Detect (MTTD) for incidents, access request turnaround time, and policy violation rate trend over time.

**Q27. What's the tension between governance and engineering velocity, and how do you resolve it?**
> Mirrors the classic Dev/Ops tension — overly strict/slow governance creates pressure to bypass it; the resolution is making compliant behavior the easy, fast, automated default (policy-as-code, self-service tooling) rather than a slow manual gate.

## Rapid-Fire
28. What's "data as a product" mean in a Data Mesh context? *(Treating published data with the same rigor as a customer-facing product — documented, versioned, tested, with defined SLAs.)*
29. Why is k-anonymity or differential privacy needed beyond simple pseudonymization? *(Rigorous, mathematically-grounded techniques for TRUE anonymization, since simply removing "obvious" identifying columns is often insufficient given quasi-identifier combinations.)*
30. What's "policy as code" and why does it matter? *(Enforcing governance rules automatically in CI/CD, e.g., failing a build if a PII-like column lacks a classification tag — catching violations before production, not just via a manual audit.)*

---

**Practice tip**: This module's questions are increasingly common at senior/staff-level interviews specifically, since governance/quality/MLOps maturity is exactly the kind of organizational-scope concern that differentiates senior candidates (recap `11-system-design/09`) — practice tying each answer to a concrete example, not abstract definitions alone.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"To measure what truly matters is itself an act of honesty toward oneself."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
