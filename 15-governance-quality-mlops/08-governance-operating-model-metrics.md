# 8. Governance Operating Model & Metrics — Making Governance Actually Happen

## Why Governance Fails Without an Operating Model
Writing a beautiful data governance POLICY document that sits unread in Confluence (recap `14-internal-tools`) accomplishes nothing. Governance requires an OPERATING MODEL — clear roles, decision rights, enforcement mechanisms, and metrics proving it's actually working — turning policy into genuine practice.

## The Data Governance Council — The Decision-Making Body
```
A typical structure at a mature organization:
  Executive Sponsor: senior leadership backing (CDO/CTO-level) --
    without genuine executive support, governance initiatives
    consistently lose priority against feature-delivery pressure

  Data Governance Council: cross-functional representatives (Legal/
    Compliance, Security, Data Engineering leadership, key business
    domain Data Owners -- recap file 1's Owner/Steward/Custodian
    framework) meeting regularly to set POLICY (classification
    standards, retention rules, access request processes) and resolve
    cross-domain disputes

  Working groups: smaller, more technical groups (often including
    Data Engineers directly) implementing the Council's policy
    decisions into actual technical enforcement (catalog tagging
    standards, automated policy-as-code checks)
```

## RACI — Clarifying WHO Does WHAT (a genuinely practical tool)
```
RACI = Responsible, Accountable, Consulted, Informed -- a standard
framework for clarifying roles on any governance initiative:

Example: "Classifying a new table's sensitivity level"
  Responsible: the Data Engineer who created the table (does the actual work)
  Accountable: the Data Steward for that domain (ensures it's done correctly)
  Consulted: the Legal/Compliance team (for genuinely ambiguous PII cases)
  Informed: the broader Data Governance Council (aware it happened,
            not involved in the decision itself)

Without an explicit RACI, governance responsibilities silently fall
through the cracks -- "I assumed someone else was classifying that
table" is a genuinely common, real governance failure mode.
```

## Policy as Code — Moving Governance From Documents to Automated Enforcement
```python
# A genuinely important 2020s-2026 shift: governance policies
# increasingly enforced AUTOMATICALLY in CI/CD (recap 10-devops/03),
# not just documented and hoped for
# ci_governance_check.py
def check_pii_columns_are_tagged(dbt_manifest):
    """CI check: fails the build if a column matching PII patterns
    (email, ssn, phone) exists WITHOUT a classification tag -- catches
    ungoverned PII exposure BEFORE it reaches production, not after an audit."""
    violations = []
    for model in dbt_manifest["nodes"].values():
        for column_name, column_meta in model.get("columns", {}).items():
            if looks_like_pii(column_name) and "classification" not in column_meta.get("tags", []):
                violations.append(f"{model['name']}.{column_name}")
    if violations:
        raise SystemExit(f"Ungoverned PII-like columns found: {violations}")
```
This directly extends the CI/CD gating philosophy from `10-devops/03` and `10-devops/08` — governance checks become just ANOTHER automated gate in the pipeline, alongside tests and linting, rather than a separate, manual, easily-skipped audit process.

## The Metrics That Actually Measure Governance Maturity
```
A genuinely important, often-missing practice: governance programs
need MEASURABLE KPIs, not just "we have a policy document" as proof
of success. Real, trackable metrics:

CATALOG COVERAGE: % of production tables that are documented/tagged
  in the data catalog (recap file 2) -- a low number signals
  governance existing on paper but not in practice

CLASSIFICATION COVERAGE: % of columns with sensitivity classification
  tags (recap file 1) -- directly measurable via the catalog

DATA QUALITY SCORE: % of tables with AT LEAST a baseline set of tests
  (recap file 4) -- e.g., "does every table have unique/not_null tests
  on its primary key" as a minimum bar

MEAN TIME TO DETECT (MTTD) a data quality incident: how long between
  an anomaly OCCURRING and it being CAUGHT (recap file 5's
  observability discussion) -- a shrinking MTTD over time is genuine
  evidence observability investment is working

ACCESS REQUEST TURNAROUND TIME: how long does it genuinely take
  someone to get approved, appropriate access to a dataset they need
  -- a governance program that's too slow/bureaucratic here creates
  real pressure for people to find risky workarounds (shadow IT,
  informally-shared spreadsheets with sensitive data) that UNDERMINE
  governance rather than support it

POLICY VIOLATION RATE (from the policy-as-code checks above): trending
  DOWN over time as teams internalize standards, ideally caught in CI
  before reaching production rather than discovered later in an audit
```

## The Genuine Tension: Governance vs Velocity (an honest, senior-level discussion point)
```
Overly strict, slow governance processes create real pressure for
teams to bypass them entirely -- exactly mirroring the classic Dev/Ops
tension from `10-devops/01` that originally motivated DevOps culture.
The SAME lesson applies here: the goal is governance that's genuinely
EASY TO COMPLY WITH (self-service catalog tagging, automated
policy-as-code checks that run in seconds, not a multi-week manual
approval committee) -- making the RIGHT thing to do also the EASY
thing to do, rather than governance that's such friction that people
route around it, which is worse than no governance policy at all.
```

## Interview Traps
- "How would you actually get a data governance policy adopted, not just written?" — an operating model (Council + RACI + policy-as-code enforcement), executive sponsorship, and genuinely low-friction self-service tooling — a policy document alone accomplishes nothing without this.
- "What metrics would you use to prove a governance program is working?" — catalog/classification coverage, data quality score, MTTD for incidents, access request turnaround time, and policy violation rate trend — concrete, trackable numbers, not just "we have a policy."
- "What's the tension between governance and engineering velocity, and how do you resolve it?" — directly mirrors the DevOps Dev/Ops tension (`10-devops/01`) — the resolution is making compliant behavior the EASY, fast, automated default (policy-as-code, self-service tooling) rather than a slow manual gate people are incentivized to bypass.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Every boundary set with wisdom protects more than it restricts."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
