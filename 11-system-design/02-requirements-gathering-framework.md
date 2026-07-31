# 2. Requirements Gathering — The Skill That Comes BEFORE Any Design

## Why This Is Listed First (and Why Skipping It Is the #1 Junior Mistake)
The single most common mistake in system design — at any level, junior to senior — is jumping straight to "I'll use Kafka + Spark + Snowflake" before actually understanding what problem is being solved. A perfectly-executed WRONG design (solving a problem the business doesn't actually have) is worse than a mediocre RIGHT design.

## Functional Requirements — What Must the System DO?
```
Questions to ask:
- What data needs to be ingested/processed/served? From where?
- What are the KEY BUSINESS QUESTIONS this system must answer? (recap
  from `05-databases/07-database-design-and-modeling.md`'s design process)
- Who are the CONSUMERS of this system's output — a dashboard, an ML
  model, another downstream service, an analyst running ad-hoc queries?
- What TRANSFORMATIONS/business logic need to happen to the data?
```

## Non-Functional Requirements — How WELL Must It Do It? (often more important, often skipped)
```
LATENCY: How fresh does the data need to be? Sub-second? Within a minute?
         Nightly is fine? — THIS SINGLE ANSWER often determines whether
         you need streaming (Kafka+Flink) or batch (Airflow+Spark) —
         see `01-fundamentals/09-data-pipeline-architecture.md`

THROUGHPUT: How much data volume, how many events per second, at PEAK
            (not average) load?

CONSISTENCY: Can the system tolerate briefly stale/eventually-consistent
             data, or does it need strong consistency? (recap CAP theorem,
             `05-databases/03` and `10-transactions-consistency-deep-dive.md`)

AVAILABILITY: What's the acceptable downtime? Does a failure need to be
              invisible to users (high availability), or is "retry in
              a few minutes" acceptable?

DURABILITY: Can we EVER lose data, even briefly, even during a failure?
            (Usually no for financial/transactional data; sometimes
            acceptable for less critical telemetry/logs.)

SCALABILITY: What's the expected GROWTH over 1 year? 3 years? Designing
             for today's scale ALONE is a common mistake if 10x growth
             is realistically expected soon.

SECURITY/COMPLIANCE: Any regulatory requirements (data residency, PII
                      handling, audit trails)? See `07-cloud-platforms/09`.

COST: What's the actual budget? A technically "ideal" design that costs
      10x more than the business value it creates is not actually a good design.
```

## The Right Questions for Common Scenarios (memorize this pattern, adapt it)
```
"We need a real-time dashboard" ->
  - How real-time, EXACTLY? (this word means different things to different people)
  - Who's the audience — executives glancing occasionally, or ops
    monitoring continuously?
  - What happens if the dashboard shows slightly stale data for 2 minutes —
    genuinely bad, or nobody would notice?

"We need to handle more data" ->
  - How much more, specifically, and over what timeframe?
  - Is it MORE VOLUME of the same kind of data, or NEW data sources/types
    (variety) being added?
  - Where's the CURRENT bottleneck — storage, compute, a specific slow query?

"We need this to be reliable" ->
  - What's the actual COST of an hour of downtime — lost revenue,
    a compliance violation, or just an annoyed internal team?
  - Reliable against WHAT specifically — a single server dying? An
    entire region outage? A bad code deploy?
```

## Capturing Requirements as a Concrete Artifact (not just a mental note)
```
A genuinely good practice: write requirements down EXPLICITLY before
designing, e.g.:
  "This system must ingest ~500 events/second at peak, with data
  visible in the dashboard within 5 minutes of occurring, tolerating
  up to 1 hour of downtime per month, retaining full history for 7 years
  for compliance, at a target infrastructure cost under $X/month."

This becomes the OBJECTIVE YARDSTICK against which any proposed design
is judged — "does this design actually meet these stated requirements,"
rather than a vague, unfalsifiable "does this seem like a good design."
```

## Interview Traps
- Interviewers DELIBERATELY give vague prompts ("design a system to handle user analytics") specifically to see if you ask clarifying questions BEFORE designing — silence and jumping straight to a solution is one of the most common ways strong candidates lose points in these interviews.
- "How would you gather requirements for a new data pipeline request?" — walk through BOTH functional (what must it do) and non-functional (latency, throughput, consistency, availability, cost) categories explicitly — many candidates only think of functional requirements and miss half the picture.
- Be ready to explain WHY non-functional requirements often matter MORE than functional ones for architecture decisions — the SAME functional requirement ("show sales data") leads to a completely different design depending on the latency/consistency/scale answers.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Clarity sought before action prevents most of the confusion found after it."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
