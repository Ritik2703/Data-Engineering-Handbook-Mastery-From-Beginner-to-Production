# System Design Interview Questions — 30+ Prompts with Guided Approaches

## How to Use This File
Unlike other modules' interview-questions files, most system design questions don't have ONE correct answer — they're prompts to practice the 6-step framework (file 10) on. For each, a guided approach is given, not a single "correct" solution — work through each one yourself FIRST, then compare your reasoning process against the guidance.

## Foundational Understanding

**Q1. What's the difference between a Data Engineer and a Data Architect?**
> See file 9 in depth. Core answer: scope of ambiguity handled (given clear requirements vs figuring out what's actually needed) and scope of influence (one system vs organizational strategy across teams).

**Q2. Why should you ALWAYS ask clarifying questions before designing, even under time pressure?**
> Interviewers deliberately give vague prompts to test this; a design solving the WRONG problem (however well-executed) scores worse than a simpler design solving the RIGHT, clarified problem.

**Q3. Walk through the difference between functional and non-functional requirements with an example.**
> Functional: "show sales data." Non-functional: how fresh (latency), how much data (throughput), can it be briefly stale (consistency) — the SAME functional requirement leads to completely different designs depending on non-functional answers.

## Design Prompts (Practice These With the 6-Step Framework)

**Q4. Design a data pipeline to detect and prevent duplicate customer accounts across signups.**
> Guided approach: clarify — is "duplicate" exact-match (same email) or fuzzy (similar name+address)? Real-time (block at signup) or batch (nightly cleanup)? This single answer determines whether you need a real-time lookup service (Redis/a dedicated matching service) or a batch dedup job (recap `02-sql/06`'s dedup patterns).

**Q5. Design a system to track and analyze website A/B test results.**
> Guided approach: clarify sample size/statistical significance requirements (a product/data science concern affecting how long data must be collected), and whether results need to be visible in real-time during the test or only in a final report — heavily influences whether you need streaming aggregation or nightly batch is sufficient.

**Q6. Design a data pipeline for a food delivery app's real-time driver-order matching.**
> Guided approach: this closely mirrors the ride-hailing database case study (`05-databases/case-studies/`) — practice reproducing that reasoning: Redis for current driver locations, a separate historical/analytics path, and explicit reasoning for why NOT putting everything in one database.

**Q7. Design a system for detecting and alerting on data quality issues across 100+ warehouse tables.**
> Guided approach: recap `03-python/12` and `08-orchestration/08` — distinguish EXPLICIT rule-based checks (dbt tests, Great Expectations) from anomaly-detection-based observability tools, and design a SEVERITY-classified alerting strategy avoiding alert fatigue.

**Q8. Design a data platform for a company migrating from on-premises to the cloud.**
> Guided approach: recap `07-cloud-platforms/07`'s 6 R's and phased migration playbook — apply it explicitly to a specific scenario, classifying different systems into different R's with justification.

**Q9. Design a system to compute and serve personalized pricing (surge pricing) in real time.**
> Guided approach: closely mirrors case study 1 (fraud detection)'s latency-driven architecture reasoning — clarify the EXACT latency requirement, and justify Flink/streaming vs a simpler polling-based approach based on that specific number.

**Q10. Design a system for a news website to show "most popular articles right now."**
> Guided approach: mirrors case study 3 (social media trending) — clarify how "right now" is defined (last 10 minutes? Last hour?), and design the windowed streaming aggregation accordingly.

**Q11. Design a data platform to support a company with 5 different business units, each wanting data autonomy.**
> Guided approach: mirrors case study 7's Data Mesh reasoning — the core answer is organizational (platform team + domain team ownership split), not purely technical.

**Q12. Design a system to migrate a legacy on-premises SSIS-based data warehouse to a modern cloud stack.**
> Guided approach: recap `04-etl-elt/09`'s legacy-vs-modern migration guidance combined with `07-cloud-platforms/07`'s migration playbook — emphasize the PHASED, coexistence-based approach over a risky big-bang rewrite.

**Q13. Design a data pipeline for processing and analyzing IoT sensor data from smart home devices.**
> Guided approach: closely mirrors case study 6 — practice the capacity estimation step explicitly (devices x reading frequency), and the watermarking/late-data handling reasoning.

**Q14. Design a system for a company to build a 360-degree customer view across 10 different data sources.**
> Guided approach: mirrors case study 5's e-commerce integration reasoning — emphasize the staging-layer-per-source pattern and schema drift detection given the MANY-source integration challenge, more than raw scale.

## Tradeoff & Judgment Questions

**Q15. When would you recommend AGAINST using Kafka, even though it's a popular, powerful tool?**
> A strong answer: when the actual throughput/latency requirements don't justify its operational complexity — e.g., a low-volume, latency-tolerant batch scenario where a simpler queue or even direct batch processing would suffice, avoiding unjustified sophistication (recap file 8's tradeoff framework).

**Q16. A stakeholder insists on real-time processing for a use case that doesn't actually need it. How do you handle this conversation?**
> A strong answer demonstrates requirements-gathering skill applied to STAKEHOLDER MANAGEMENT specifically — asking WHY they believe they need real-time (often reveals the actual underlying need is something else, like wanting to trust the data more, which a different solution might address), and articulating the real cost tradeoff (file 8's structure) in terms the stakeholder cares about (cost, delivery timeline), not just technical purity.

**Q17. How do you decide whether to build a custom solution or buy/adopt a SaaS tool for a data platform need?**
> Recap file 3's build vs buy tradeoff axis — consider: is this a genuinely differentiating capability for the business (worth custom investment) or a commodity problem many vendors solve well already (buy); ongoing maintenance burden of building vs recurring cost/vendor lock-in of buying; team's available bandwidth.

**Q18. How would you approach a situation where your proposed architecture is more complex than a colleague's simpler alternative?**
> A strong, senior-level answer doesn't defend complexity reflexively — genuinely re-evaluate whether the SPECIFIC requirements actually justify the added complexity (file 8's "argue for simplicity" instinct), and be willing to adopt the simpler approach if it genuinely meets the stated requirements just as well.

## Capacity Estimation Practice

**Q19. Estimate the storage needed for a company with 10 million users each performing an average of 5 transactions/day, each transaction generating a 2 KB record, retained for 7 years.**
> Guided approach: 10M x 5 = 50M transactions/day x 2KB = 100 GB/day raw; x 365 x 7 years ≈ 255 TB raw, then apply a realistic compression ratio (~5-8x for structured transactional data) to get a more realistic ~32-50 TB actual stored volume — practice narrating this calculation clearly.

**Q20. Estimate the required Kafka partition count for a topic needing to sustain 50,000 events/second, where each partition can handle roughly 5,000 events/second.**
> Guided approach: 50,000 / 5,000 = 10 partitions minimum, but practice explaining WHY you'd likely provision MORE than the bare minimum (headroom for growth, uneven partition key distribution risk) rather than the exact theoretical minimum.

## Reliability & Failure-Mode Questions

**Q21. Design a system to be resilient to a complete regional cloud outage.**
> Guided approach: recap `07-cloud-platforms/02`'s multi-region concepts and file 6's RTO/RPO framework — clarify the ACTUAL business tolerance for downtime/data loss FIRST (this determines whether you need expensive hot multi-region standby or can accept a slower, cheaper cold-recovery approach).

**Q22. How would you design a pipeline to be safely re-runnable (idempotent) if it fails halfway through processing a large batch?**
> Recap `01-fundamentals/02`'s idempotency discussion and file 6's system-design-level framing — MERGE/UPSERT patterns keyed on a unique identifier, rather than blind INSERTs, designed in from the start rather than retrofitted.

## Rapid-Fire Judgment Prompts
23. When is a monolithic "one team owns everything" data architecture actually the RIGHT choice, not an anti-pattern? *(Smaller organizations/teams where the coordination overhead of a Data Mesh-style split isn't yet justified by genuine multi-team bottleneck pain.)*
24. Why might you recommend AGAINST adopting the newest, most sophisticated technology for a given problem? *(If simpler, more mature/well-understood tools already meet the actual stated requirements — sophistication itself carries a real cost in complexity/maintenance/team learning curve.)*
25. What's the danger of designing a system based ONLY on today's data volume, with zero consideration of growth? *(Risk of a costly, disruptive re-architecture very soon if realistic near-term growth isn't designed for — balanced against the equal danger of over-engineering for unrealistic hypothetical scale.)*
26. Why is it important to explicitly state your assumptions during a system design interview, rather than silently assuming them? *(Lets the interviewer correct a wrong assumption immediately rather than you designing an entire system around it; demonstrates transparent reasoning.)*
27. What's a "data contract," and why does it matter more as an organization scales to more teams? *(An explicit, versioned schema agreement between a data-producing and data-consuming team, preventing silent breaking changes — becomes more critical as more teams depend on shared data, mirroring case study 7's reasoning.)*
28. Why might a senior engineer recommend a SIMPLER architecture than what they'd personally find most technically interesting to build? *(Genuine seniority means optimizing for the business's actual needs and the team's ability to maintain the system, not for personal technical satisfaction — file 8's simplicity-argument instinct.)*
29. How do RTO and RPO requirements directly influence whether you need synchronous or asynchronous database replication? *(A tight RPO — near-zero data loss tolerance — requires synchronous replication despite its latency cost; a looser RPO tolerates cheaper asynchronous replication.)*
30. What's the first question you should ask when given ANY vague system design prompt? *(Some version of "what are the key use cases/business questions this needs to answer, and what does success look like" — always requirements first, per file 2 and the Step 1 framework.)*

---

**Final practice tip**: Work through ALL 7 case studies yourself, from a blank page, BEFORE reading the provided reasoning — then compare your own requirements-gathering questions and tradeoff justifications against what's shown. The goal isn't memorizing these specific answers; it's building the REPEATABLE REASONING PROCESS (file 10) that lets you handle a system design prompt you've never seen before, which is exactly what real system design interviews (and real architect-level jobs) actually test.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"True mastery is knowing when the simple path is also the wisest one."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
