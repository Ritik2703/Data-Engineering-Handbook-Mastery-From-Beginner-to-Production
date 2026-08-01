# 4. Data Quality & Testing — Deep Dive

## Why This Deserves Its Own Deep Module (Beyond the Earlier Mentions)
`03-python/12` and `04-etl-elt/08` introduced data quality checks and dbt tests as PART of building a pipeline. This file treats Data Quality as its own DISCIPLINE — a full philosophy of WHAT to test, WHEN, and HOW to scale testing across an entire data platform, not just individual pipelines.

## The Data Quality Dimensions (recap + full framework)
```
Recap from 01-fundamentals/02-core-concepts.md's 6 pillars, now applied
as a genuine TESTING framework:

Completeness: are required fields populated? (not-null tests)
Uniqueness: no unintended duplicates (unique tests)
Validity: conforms to expected format/type/range (accepted_values,
          range checks)
Consistency: same value represented the same way everywhere (recap
             MDM's survivorship rules, file 3)
Accuracy: does the data reflect REALITY (hardest to test automatically
          — often needs reconciliation against an external source of
          truth, recap the FULL OUTER JOIN pattern from `02-sql/06`)
Timeliness: is data fresh within the expected SLA (recap
            `08-orchestration/08`'s freshness monitoring)
```

## dbt Tests — The Foundation Layer (recap + expanded philosophy)
```yaml
# Generic tests (built-in) -- the FIRST line of defense, cheap to write
models:
  - name: fct_orders
    columns:
      - name: order_id
        tests: [unique, not_null]
      - name: customer_id
        tests:
          - relationships: {to: ref('dim_customer'), field: customer_id}
```
```sql
-- Custom "singular" tests -- for business-logic-specific rules that
-- generic tests can't express
-- tests/assert_revenue_never_negative.sql
SELECT * FROM {{ ref('fct_orders') }}
WHERE amount < 0
-- dbt test PASSES if this query returns ZERO rows
```
**The dbt testing philosophy**: tests live ALONGSIDE the models they validate, version-controlled, run automatically in CI (recap `10-devops/08`) — testing is treated as a first-class part of the transformation code itself, not a separate, occasionally-run audit.

## Great Expectations — The Comprehensive Framework (recap + deeper)
```python
# Beyond the introduction in 03-python/12 -- Great Expectations' real
# power is its "Expectation Suite" as a REUSABLE, SHAREABLE artifact
import great_expectations as gx

context = gx.get_context()
suite = context.add_expectation_suite("orders_suite")

validator = context.sources.pandas_default.read_dataframe(orders_df)
validator.expect_column_values_to_not_be_null("order_id")
validator.expect_column_values_to_be_between("amount", min_value=0, max_value=100000)
validator.expect_column_pair_values_a_to_be_greater_than_b("ship_date", "order_date")
validator.save_expectation_suite()

# The suite can be reused across MULTIPLE pipelines/environments,
# and Great Expectations auto-generates human-readable "Data Docs" --
# an HTML report of what's expected and what actually happened,
# genuinely useful as living documentation for non-technical stakeholders
```

## Soda — The Declarative, YAML-Based Alternative
```yaml
# checks.yml -- Soda's checks-as-config approach, an alternative
# philosophy to Great Expectations' Python-API style
checks for orders:
  - row_count > 0
  - missing_count(order_id) = 0
  - duplicate_count(order_id) = 0
  - avg(amount) between 10 and 500
  - freshness(order_date) < 1d
```
**Why some teams prefer Soda over Great Expectations**: a simpler, more declarative YAML syntax lowers the barrier for less Python-heavy team members (analysts, analytics engineers) to write/maintain checks themselves, versus Great Expectations' more programmatic, Python-first approach — a genuine tradeoff between simplicity/accessibility and programmatic flexibility.

## Data Contracts — Testing as a FORMAL Agreement, Not Just an Internal Check
```yaml
# A data contract (recap the concept introduced in 11-system-design/05,
# now as a fully worked example) -- an explicit, enforced agreement
# between a data PRODUCER and CONSUMER
apiVersion: v1
kind: DataContract
metadata:
  name: orders_events_contract
  owner: checkout-team
spec:
  schema:
    - name: order_id
      type: string
      required: true
    - name: amount
      type: decimal
      required: true
      constraints: {minimum: 0}
  sla:
    freshness: "15 minutes"
  breaking_change_policy: "requires 30-day consumer notification"
```
**Why data contracts are a genuinely growing practice (2023-2026)**: as more teams produce/consume shared data (recap Data Mesh, file 7), an EXPLICIT, VERSIONED, TESTED contract prevents the classic "upstream team silently renamed a field and broke five downstream pipelines" incident — the contract itself can be validated automatically in CI on the PRODUCER side, catching a breaking change BEFORE it ships, not after a consumer's pipeline crashes.

## Testing Strategy Across a Whole Platform (not just one pipeline)
```
Where to place tests, and why (a genuinely important architectural decision):

At INGESTION (Bronze layer): schema validation, basic type/null checks
  -- catch garbage data as EARLY as possible, before it propagates

At TRANSFORMATION (Silver/Gold, dbt tests): business logic validation
  -- uniqueness, referential integrity, accepted values, custom
  business rules

At the CONTRACT boundary (between producer/consumer teams): schema
  and SLA validation -- catching breaking changes before they ship

At SERVING (BI/ML feature layer): sanity checks on FINAL numbers before
  they reach a dashboard or a model -- e.g., "did total revenue change
  by more than 50% since yesterday" as a final circuit-breaker check
```

## Interview Traps
- "How would you design a comprehensive testing strategy for a data platform, not just one pipeline?" — layer tests across MULTIPLE stages (ingestion, transformation, contract boundary, serving), not just one — different stages catch different failure classes.
- "What's a data contract, and how is it different from a regular dbt test?" — a data contract is a FORMAL, often cross-team agreement (schema + SLA) validated on the PRODUCER side before shipping a change; a dbt test typically validates data WITHIN one team's own transformation pipeline.
- "Great Expectations vs Soda — what's the real tradeoff?" — Great Expectations offers a comprehensive, programmatic Python framework with rich reporting; Soda offers a simpler, more declarative YAML approach lowering the barrier for less-technical contributors — pick based on team composition and complexity needs.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Trust, once earned through consistent integrity, is the rarest and most valuable currency."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
