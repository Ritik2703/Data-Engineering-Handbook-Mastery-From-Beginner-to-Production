# 1. Data Governance Fundamentals — A to Z

## What Data Governance Actually Means (Beyond the Buzzword)
Data Governance is the overall system of DECISION RIGHTS, POLICIES, and ACCOUNTABILITY that determines how an organization's data is collected, classified, secured, accessed, and used — answering "who is allowed to do what with which data, and who is accountable if it goes wrong." It's not a single tool; it's a discipline that TOOLS (Purview, Glue Catalog, IAM) help enforce.

## Why This Became Business-Critical (Not Just "Nice to Have")
```
- Regulatory fines are genuinely large and enforced: GDPR fines can
  reach 4% of GLOBAL annual revenue for serious violations — a real,
  board-level financial risk, not an abstract compliance checkbox
- High-profile data breaches/misuse scandals have made customers and
  regulators genuinely more scrutinous of how companies handle data
- As companies adopt AI/ML at scale, UNGOVERNED data becomes a direct
  liability — a model trained on improperly-sourced or biased data
  creates real legal and reputational exposure
```

## The Core Regulations Every Data Engineer Should Understand (conceptually, not as a lawyer)

### GDPR (General Data Protection Regulation — EU, 2018)
```
Key principles a Data Engineer must design around:
- Right to Access: a user can request ALL data a company holds about them
- Right to Erasure ("right to be forgotten"): a user can request their
  data be DELETED — this has REAL pipeline design implications (can
  you actually find and delete a specific person's data across every
  system, including backups and derived/aggregated tables?)
- Data Minimization: collect only what's genuinely needed, not "just in case"
- Purpose Limitation: data collected for one purpose can't be silently
  repurposed for another without new consent
- Data Residency: personal data of EU citizens often has geographic
  storage/processing constraints (recap `07-cloud-platforms/09`'s
  region-selection discussion)
```

### CCPA/CPRA (California Consumer Privacy Act — US)
```
Similar spirit to GDPR (right to know, right to delete, right to
opt-out of data sale) but with different specific mechanics and
narrower geographic scope (California residents) — many US companies
design ONE compliant system that satisfies BOTH GDPR and CCPA
simultaneously rather than building separate systems per regulation.
```

### HIPAA (Health Insurance Portability and Accountability Act — US healthcare)
```
Governs Protected Health Information (PHI) specifically — stricter
access logging, encryption, and audit trail requirements than general
PII; directly relevant to the healthcare case study pattern seen in
`06-big-data/06` (Delta Lake time travel for compliance) and this
module's own case study.
```

### PCI-DSS (Payment Card Industry Data Security Standard)
```
Governs how payment card data is stored/transmitted/processed — directly
relevant to the "isolated payments database" design decision in the
ride-hailing case study (`05-databases/case-studies/`) — PCI-DSS is
part of WHY that isolation is a genuinely standard real-world practice,
not just a performance optimization.
```

## Data Classification — The Practical Starting Point
```
Before you can govern data, you must CLASSIFY it. A standard framework:

PUBLIC: no restriction (a public blog post, published pricing)
INTERNAL: for employees only, low sensitivity (an internal wiki page)
CONFIDENTIAL: business-sensitive, restricted (financial forecasts,
               unreleased product plans)
RESTRICTED/PII/PHI/PCI: highest sensitivity, legally regulated
   (customer SSNs, health records, credit card numbers, precise
   location history)

Every table/column in a data platform should ideally be TAGGED with
its classification level (recap the data catalog discussion in file 2)
— this tagging is what makes automated policy enforcement (masking,
access control, retention rules) possible at scale, rather than
manually tracking sensitivity in someone's head.
```

## PII Specifically — What Counts (broader than people assume)
```
Direct identifiers: name, SSN/national ID, email, phone number

Indirect/quasi-identifiers (can identify someone when COMBINED):
  ZIP code + birth date + gender has been shown to uniquely identify
  the majority of the US population EVEN WITHOUT a name — a genuinely
  important, often-missed nuance: PII isn't just "obviously personal"
  fields, it's anything that COULD identify an individual, especially
  in combination with other fields.

This is why anonymization/pseudonymization requires real care (see
below) — simply removing the "obvious" name/email column is often
NOT sufficient to make data genuinely non-identifying.
```

## Anonymization, Pseudonymization, and Masking — Real Techniques
```
Masking: replacing sensitive values with a fixed pattern for display
  purposes (e.g., showing "****-****-****-1234" for a credit card) —
  reversible IF the underlying real value is stored separately and
  securely.

Pseudonymization: replacing an identifier with a consistent token
  (e.g., customer_id 12345 always maps to token "a8f3e2") — the
  MAPPING is stored securely and separately, so the data is only
  re-identifiable by someone with access to that mapping — commonly
  used so analysts can still JOIN/aggregate data by customer without
  ever seeing real identifying information.

Anonymization (true): irreversibly removing the ability to
  re-identify an individual — genuinely much harder to achieve
  correctly than most people assume (recap the ZIP+birthdate+gender
  example above) — techniques like k-anonymity (ensuring any record
  is indistinguishable from at least k-1 others) and differential
  privacy (adding calibrated statistical noise) are the rigorous,
  mathematically-grounded approaches real privacy engineering uses.
```
```sql
-- A practical pseudonymization pattern in a dbt staging model
SELECT
    {{ dbt_utils.generate_surrogate_key(['customer_id']) }} AS customer_token,
    -- real customer_id is NEVER exposed past this staging layer
    order_amount,
    order_date
FROM {{ source('raw', 'orders') }}
```

## Data Stewardship & Ownership — The Organizational Layer
```
Data Owner: typically a business-side role (e.g., "VP of Sales owns
  customer data") — accountable for defining WHO should have access
  and WHY, and for the data's overall quality/appropriate use

Data Steward: typically a more hands-on, often technical role — actually
  maintains documentation, classification tags, and quality rules for
  specific datasets day-to-day, reporting to/coordinating with the Data Owner

Data Custodian: the team (often Data Engineering itself) responsible
  for the TECHNICAL implementation of access controls, encryption, and
  retention — executing the policies Owners/Stewards define, not
  necessarily deciding them unilaterally
```
This three-role separation (Owner decides policy, Steward maintains day-to-day documentation/quality, Custodian implements technically) is a genuinely important organizational pattern — Data Engineers are usually Custodians, sometimes Stewards, rarely the sole Owner of a business dataset's governance policy.

## Data Retention Policies — How Long to Keep What
```
A genuinely important, often-neglected practice: define EXPLICIT
retention rules per data classification/type, not "keep everything forever":
  - Transactional/financial data: often 7 years (tax/audit requirements)
  - Marketing engagement data: often much shorter (e.g., 1-2 years),
    balanced against genuine analytical value
  - Raw clickstream/log data: often has its OWN shorter retention than
    aggregated/summarized derivatives (keep detailed raw data for a
    bounded window, keep aggregates indefinitely)

Implemented technically via S3/ADLS lifecycle policies (recap
`07-cloud-platforms/03`) combined with warehouse table-level retention
configuration — governance POLICY driving technical IMPLEMENTATION,
exactly the Owner->Steward->Custodian chain above in action.
```

## Interview Traps
- "What's the difference between anonymization and pseudonymization?" — pseudonymization is reversible with access to a secure mapping (enables joins/aggregation while hiding identity from most users); true anonymization aims to be irreversible, and is genuinely harder to achieve correctly than simply removing "obvious" identifying columns.
- "How would you design a pipeline to support GDPR's 'right to be forgotten'?" — needs a way to trace and delete a specific individual's data across ALL systems (raw, staged, aggregated, even backups) — a genuinely hard system design problem worth discussing thoughtfully rather than a one-line answer.
- "What's the difference between a Data Owner and a Data Steward?" — Owner is typically business-side, accountable for policy decisions; Steward is a more hands-on role maintaining day-to-day documentation/quality/classification.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"True governance is not control born of fear, but care born of responsibility."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
