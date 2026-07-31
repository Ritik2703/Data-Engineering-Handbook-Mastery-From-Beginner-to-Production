# 5. Data Modeling Under Real System Constraints

## Why This Differs From Module 05's Data Modeling Content
`05-databases/07` taught HOW to design a good schema in isolation. This file is about choosing a model when REAL-WORLD SYSTEM CONSTRAINTS (existing legacy systems, team skill level, budget, timeline) prevent the "textbook perfect" answer — a genuinely common senior-level reality.

## The Constraint-Aware Modeling Decision Tree
```
Ideal: Kimball star schema, fully conformed dimensions across the org
Reality check questions:
  - Does the team have DBT/SQL modeling maturity to maintain this well?
    (A sloppy star schema maintained poorly is WORSE than a simpler
    One-Big-Table approach maintained well.)
  - Is there an existing legacy schema/reporting layer that would break
    if redesigned from scratch? (Sometimes the pragmatic answer is
    building a NEW clean layer alongside the old one, migrating
    consumers gradually — recap `04-etl-elt/09`'s coexistence reality.)
  - What's the ACTUAL query pattern? (If 90% of queries are simple,
    single-table lookups, an OBT approach may genuinely serve better
    than a "properly normalized" star schema nobody queries efficiently
    because they don't know how to join it correctly.)
```

## Choosing Between SQL/NoSQL/NewSQL — A System Design Lens
```
This is a decision that MUST be justified by the SPECIFIC access pattern
(recap `05-databases/03`'s decision framework), but at the SYSTEM DESIGN
level, you also need to weigh:
  - Team's EXISTING expertise (a team fluent in SQL/Postgres will
    execute a relational design far better than an unfamiliar NoSQL
    choice, even if NoSQL is theoretically "more correct" for the access pattern)
  - OPERATIONAL maturity needed (Cassandra/Kafka genuinely require more
    operational sophistication to run well than a managed Postgres
    instance — recommending them to a small team without that
    experience is a common over-engineering mistake)
  - MIGRATION cost if the choice is wrong (relational-to-NoSQL migrations
    are genuinely painful; starting simpler and migrating LATER if truly
    needed is often the pragmatic senior choice over guessing "we might
    need NoSQL scale eventually")
```

## Designing the Data Contract Between Systems (a critical, often-missed concern)
```
When Team A's service produces data that Team B's pipeline consumes,
WHO decides the schema, and what happens when Team A changes it?

A genuinely senior-level practice: establish an explicit DATA CONTRACT
(a documented, versioned schema agreement, sometimes enforced via schema
registries like Confluent Schema Registry for Kafka topics) — so Team A
can't silently break Team B's pipeline by renaming a field, and schema
CHANGES go through a reviewed, communicated process rather than being
discovered by Team B's pipeline crashing at 2 AM.
```

## Schema Evolution Strategy — Designing for Change From Day One
```
Real systems' schemas WILL change over time (new fields, deprecated
fields, type changes) — a senior-level design anticipates this:
- Use FORMATS that support schema evolution gracefully (Avro, Parquet
  with additive changes, Iceberg/Delta's schema evolution features —
  recap `01-fundamentals/07` and `06-big-data/06`)
- Design ADDITIVE changes as the default-safe pattern (adding a new
  nullable column rarely breaks existing consumers; renaming/removing
  a column often does)
- Version APIs/schemas explicitly when a breaking change is genuinely
  unavoidable, giving consumers a migration window rather than an
  instant, unannounced break
```

## Interview Traps
- "Would you always recommend a fully normalized Kimball star schema?" — a nuanced answer weighs the team's actual SQL/BI-tool maturity and existing system constraints, not a blanket "yes, it's the textbook best practice" — sometimes a simpler, well-executed model beats a theoretically superior one poorly maintained.
- "How do you prevent an upstream team's schema change from silently breaking your pipeline?" — explicit, versioned data contracts (potentially enforced via a schema registry), and a reviewed change-communication process — not just hoping nobody changes anything.
- "How would you design a schema to be resilient to future changes?" — favor additive changes as the safe default, use schema-evolution-friendly formats, and version explicitly when breaking changes are unavoidable.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"A leader who can admit a better path exists earns more trust than one who cannot."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
