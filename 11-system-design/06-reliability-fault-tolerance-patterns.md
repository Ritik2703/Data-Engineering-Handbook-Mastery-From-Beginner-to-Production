# 6. Reliability & Fault Tolerance — Designing FOR Failure, Not Around It

## The Core Mindset Shift
Junior design assumes things will work. Senior/architect design assumes things WILL fail — a server will die, an API will time out, a disk will fill up, a bad deploy will happen — and asks "what happens THEN, and does the system degrade gracefully or catastrophically?"

## Single Points of Failure (SPOFs) — Find and Eliminate Them
```
The system design exercise: trace through your ENTIRE architecture and
ask "if THIS ONE component died right now, what breaks?"

Common data platform SPOFs to specifically check for:
- A single Airflow Scheduler instance (recap `08-orchestration/02` — mitigated
  by running Scheduler in HA mode in mature deployments)
- A single database connection pool exhausted by one runaway process
  (recap `05-databases/09`'s connection pooling discussion)
- A hardcoded dependency on ONE specific region/AZ (recap
  `07-cloud-platforms/02`'s multi-AZ design)
- A manual, undocumented process that only ONE specific person on the
  team knows how to run ("bus factor" of 1 — a genuine organizational
  SPOF, not just a technical one)
```

## Graceful Degradation vs Catastrophic Failure
```
BAD design: if the recommendation service is down, the ENTIRE e-commerce
            page fails to load

GOOD design: if the recommendation service is down, the page loads
             WITHOUT personalized recommendations (a slightly worse but
             still FUNCTIONAL experience) — the failure of one component
             doesn't cascade into total system failure

Applied to data pipelines: if a non-critical ENRICHMENT step (e.g.,
adding a "customer segment" label) fails, should the ENTIRE pipeline
halt, or should it proceed WITHOUT that enrichment and flag it for
follow-up? — a genuinely important design decision, not an accident.
```

## Retry Strategies — Beyond "Just Retry" (recap + system design depth)
```
Recap from `03-python/02-error-handling.md` and `03-python/06`: exponential
backoff, distinguishing retryable vs non-retryable errors.

SYSTEM DESIGN addition — the "retry storm" problem: if a downstream
service goes down and 1000 upstream callers ALL retry simultaneously
with the same backoff timing, the retries THEMSELVES can prevent the
downstream service from recovering (a self-inflicted DDoS). Mitigation:
JITTER (adding small randomness to retry timing so retries spread out
rather than synchronizing) and CIRCUIT BREAKERS (after N consecutive
failures, STOP retrying for a cooldown period, failing fast instead of
continuing to hammer a clearly-struggling downstream system).
```

## Idempotency at the System Design Level (recap + why it's an architecture decision, not just a coding practice)
```
Recap from `01-fundamentals/02-core-concepts.md`: idempotent operations
are safe to retry. At the SYSTEM DESIGN level, this becomes an
architecture-wide REQUIREMENT you design INTO every component from the
start — every message consumer, every pipeline task, every API endpoint
that might be retried needs an idempotency strategy (a unique key +
MERGE/UPSERT pattern, or a deduplication check) — retrofitting
idempotency onto an already-built system is far harder than designing
for it from the beginning.
```

## Disaster Recovery — RTO and RPO (critical system design vocabulary)
```
RTO (Recovery Time Objective): how QUICKLY must the system be restored
     after a disaster? ("We must be back online within 4 hours.")

RPO (Recovery Point Objective): how much DATA LOSS is acceptable,
     measured in TIME? ("We can afford to lose up to 15 minutes of
     data since the last backup/replication point.")

These two numbers DIRECTLY drive real architecture decisions:
  - A tight RPO (near-zero data loss tolerance) requires SYNCHRONOUS
    replication (more expensive, adds write latency)
  - A looser RPO tolerates ASYNCHRONOUS replication (cheaper, no write
    latency penalty, but a real chance of losing the last few
    minutes/seconds of data in a disaster)
  - A tight RTO requires WARM/HOT standby infrastructure ALREADY
    running, ready to take over instantly (expensive, running duplicate
    infrastructure); a looser RTO can rely on COLD standby (cheaper,
    but takes longer to spin up and restore from backups)
```

## Chaos Engineering — Testing Reliability Proactively (recap + why it matters at design time)
As covered in `10-devops/10-what-companies-use.md`, Netflix's Chaos Monkey deliberately breaks production to verify resilience — the SYSTEM DESIGN lesson: if you're not confident enough in your failure-handling design to deliberately TEST it via controlled chaos, you probably don't actually know how the system behaves under failure, you're just hoping.

## Interview Traps
- "How would you design this system to handle a downstream service outage gracefully?" — discuss graceful degradation (does a failure of ONE component cascade or stay contained), circuit breakers, and retry-with-jitter — not just "we'd retry."
- "What's RTO and RPO, and how do they drive architecture decisions?" — RTO = how fast you must recover; RPO = how much data loss is tolerable — tight requirements on either drive toward more expensive, synchronous/hot-standby architecture; looser requirements allow cheaper async/cold-standby approaches.
- "How do you prevent a 'retry storm' from making an outage worse?" — jitter (randomizing retry timing to avoid synchronized retries) and circuit breakers (failing fast after repeated failures instead of continuing to hammer a struggling system).


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"What is designed with foresight rarely needs to be rebuilt in haste."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
