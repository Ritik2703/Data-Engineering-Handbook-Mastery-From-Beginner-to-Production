# 3. Master Data Management (MDM) — Golden Records & Entity Resolution

## The Problem MDM Solves
A large company's "customer" data often lives in MULTIPLE disconnected systems — the CRM has one record, the billing system has another, the support ticketing tool has a third — each with slightly different (sometimes conflicting) information for the SAME real-world person. Without MDM, "how many customers do we actually have" or "what's this customer's true current address" has no single trustworthy answer.

## Core MDM Concepts

### The Golden Record
```
A GOLDEN RECORD is the single, trusted, authoritative version of an
entity (a customer, a product, a supplier) — reconciled from all
source systems, representing the organization's BEST understanding of
the truth for that entity.

Example: three source systems disagree on a customer's address (an
older CRM entry, a newer billing system entry, a support ticket entry
from last week) — the MDM system applies SURVIVORSHIP RULES (e.g.,
"most recently updated source wins" or "billing system is always
authoritative for address") to determine which value becomes the
golden record's address.
```

### Entity Resolution / Record Matching
```
The hard technical problem MDM must solve: determining that "John
Smith, 123 Main St" in System A and "J. Smith, 123 Main Street, Apt 4"
in System B are actually the SAME real person, despite non-identical
text representations.

Deterministic matching: exact-match rules (e.g., same email AND same
  phone number = definitely the same person) — simple, high precision,
  but misses genuine matches with any data variation.

Probabilistic/fuzzy matching: scoring similarity across MULTIPLE
  fields (name similarity via edit distance, address similarity,
  partial phone match) and computing a CONFIDENCE SCORE that two
  records represent the same entity — catches more genuine matches,
  but requires careful THRESHOLD tuning to avoid false-positive merges
  (incorrectly merging two DIFFERENT people) — a genuinely important,
  non-trivial data engineering problem in its own right.
```
```python
# A simplified fuzzy-matching illustration (real MDM tools use much
# more sophisticated, tuned algorithms)
from fuzzywuzzy import fuzz

def match_score(record_a, record_b):
    name_score = fuzz.ratio(record_a["name"], record_b["name"])
    address_score = fuzz.ratio(record_a["address"], record_b["address"])
    email_match = 100 if record_a["email"] == record_b["email"] else 0
    # Weighted combination -- email exact match is the strongest signal
    return (email_match * 0.5) + (name_score * 0.3) + (address_score * 0.2)

# A score above a tuned threshold (e.g., 85) suggests a likely match,
# often routed to human review rather than fully automatic merging for
# high-stakes entities
```

### Survivorship Rules
```
Once records are matched as the SAME entity, survivorship rules decide
WHICH source's value wins for each conflicting field:
  - "Most recently updated" (freshness-based)
  - "Most trusted source system" (a hierarchy, e.g., billing system >
    CRM > support tickets, for financial fields specifically)
  - "Most complete" (a record with a filled-in phone number beats one
    with a blank field, regardless of recency)

These rules should be EXPLICITLY documented and owned by a Data
Steward (recap file 1's Owner/Steward/Custodian framework) — not
buried as an undocumented technical implementation detail.
```

## MDM Architecture Patterns
```
Registry style (lightweight): the MDM system stores ONLY the matching/
  linking information (which source records belong to which golden
  entity) — the actual DATA stays in source systems, queried/joined
  at read time via the registry's links. Lower implementation cost,
  but query-time performance/complexity cost.

Centralized/Repository style (heavyweight): the MDM system stores the
  FULL golden record data itself, becoming the authoritative source
  systems must synchronize FROM (and sometimes TO, in a "co-existence"
  bidirectional model) — higher implementation investment, but a
  genuinely authoritative, fast-to-query single source.

Hybrid: increasingly common — a centralized golden record for CORE
  attributes (name, primary contact info) with registry-style linking
  for less critical, system-specific attributes.
```

## MDM in a Modern Data Platform (tying to earlier modules)
```
A practical, common modern implementation pattern:
1. Extract customer data from ALL source systems into the warehouse
   (recap module 04's ETL/ELT patterns)
2. A dedicated dbt model (or a specialized MDM tool like Informatica
   MDM, Reltio, or a custom Spark job) performs matching/survivorship,
   producing a `dim_customer_golden` table
3. This golden dimension becomes the SINGLE dimension joined against
   in fact tables platform-wide (recap the star schema design from
   `01-fundamentals/03` and `05-databases/07`) -- ensuring "how many
   unique customers" gets ONE consistent answer everywhere, not a
   different count depending which source system a given report happens
   to query
```

## Interview Traps
- "What's a 'golden record' and why does it matter?" — the single, trusted, reconciled version of an entity across multiple disagreeing source systems, produced via matching + survivorship rules — without it, basic questions like "how many customers do we have" have no consistent answer.
- "Deterministic vs probabilistic matching — what's the tradeoff?" — deterministic (exact-match rules) is simple and high-precision but misses genuine matches with any data variation; probabilistic/fuzzy matching catches more matches via confidence scoring but risks false-positive merges without careful threshold tuning.
- "How would you decide which source system 'wins' when two systems disagree on a customer's address?" — explicit, documented survivorship rules (recency-based, trusted-source-hierarchy-based, or completeness-based), owned by a Data Steward, not an undocumented implementation detail.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The wisest steward asks not 'what can I extract' but 'what must I safeguard.'"*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
