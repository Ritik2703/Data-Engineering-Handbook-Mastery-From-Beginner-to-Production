# Case Study: A Full Governance Program for a Healthcare Analytics Company

## Business Context
A healthcare analytics company processes patient appointment, billing, and clinical data (recap the lakehouse Project 3 in `13-projects/project-03-databricks-lakehouse-delta/`) across multiple hospital clients. HIPAA compliance is non-negotiable; a violation risks the business's entire operating license.

## Step 1: Data Classification (recap file 1)
```
PHI (Protected Health Information) -- highest sensitivity:
  patient name, diagnosis codes, treatment history, SSN

PII -- high sensitivity, not health-specific:
  patient contact info, billing address

INTERNAL -- provider scheduling data, appointment slot availability
  (not tied to a specific patient's health condition)

PUBLIC -- aggregate, de-identified statistics published in reports
  (e.g., "average wait time across all hospitals: 12 minutes")
```

## Step 2: Catalog & Tagging (recap file 2)
```sql
-- Every PHI column tagged in Unity Catalog, driving automated masking
ALTER TABLE gold.dim_patient ALTER COLUMN diagnosis_code
SET TAGS ('classification' = 'PHI', 'masking_policy' = 'restricted_role_only');

ALTER TABLE gold.dim_patient ALTER COLUMN patient_name
SET TAGS ('classification' = 'PHI', 'masking_policy' = 'restricted_role_only');
```
Analysts querying `dim_patient` for operational metrics (appointment volume, no-show rates) see masked/tokenized values for PHI columns automatically, UNLESS they're in a specifically authorized clinical-review role — implemented via the catalog's row/column-level security (recap file 2's Unity Catalog discussion), not by manually rewriting every analyst query.

## Step 3: MDM for the Patient Golden Record (recap file 3)
```
Patients often appear in MULTIPLE hospital systems (a patient visiting
2 different hospital clients) with slightly different demographic data
entered at each. A golden `dim_patient` record is built via:
  - Deterministic matching first (exact SSN match = same patient,
    highest confidence)
  - Probabilistic matching as a fallback (name + birthdate + address
    similarity scoring) for cases without a reliable SSN match, with
    LOW-confidence matches routed to manual review rather than
    automatic merging -- given the genuinely high stakes of incorrectly
    merging two different patients' health records
  - Survivorship rule: most recently updated hospital system's
    demographic info wins, but diagnosis/treatment HISTORY is always
    retained from ALL source systems (never overwritten) -- recap the
    SCD Type 2 pattern from Project 3, applied here specifically
    because clinical history must NEVER be lost, only added to
```

## Step 4: Data Quality & Contracts (recap file 4)
```yaml
# A data contract between each hospital's source system feed and the
# central platform -- catching a hospital's system changing its export
# format BEFORE it silently corrupts the shared pipeline
apiVersion: v1
kind: DataContract
metadata:
  name: hospital_claims_feed_contract
spec:
  schema:
    - name: patient_id
      type: string
      required: true
    - name: diagnosis_code
      type: string
      required: true
      constraints: {pattern: "^[A-Z][0-9]{2}\\.[0-9]{1,2}$"}  # ICD-10 format validation
  sla:
    freshness: "24 hours"
  breaking_change_policy: "requires 60-day hospital IT notification (healthcare
                            systems often have slower internal change cycles)"
```

## Step 5: Observability for a Compliance-Critical Signal (recap file 5)
```sql
-- A genuinely important healthcare-specific observability check:
-- sudden drop in claims volume from a specific hospital could indicate
-- either a benign issue OR a genuine data pipeline failure hiding real
-- clinical/billing data -- caught via the same 3-sigma pattern from file 5
WITH hospital_daily_volume AS (
    SELECT hospital_id, DATE(created_at) AS load_date, COUNT(*) AS claim_count
    FROM gold.fct_claims
    GROUP BY hospital_id, DATE(created_at)
)
-- ... anomaly detection logic exactly as shown in file 5, applied PER hospital_id
```

## Step 6: Governance Operating Model (recap file 8)
```
Data Governance Council: includes the company's Compliance Officer
  (legal HIPAA accountability), Head of Data Engineering, and a
  representative Clinical Data Steward from the largest hospital client

RACI for "onboarding a new hospital client's data feed":
  Responsible: the Data Engineering team building the ingestion pipeline
  Accountable: the Compliance Officer (sign-off that the new feed meets
               HIPAA requirements before going live)
  Consulted: the hospital's own IT/compliance contact
  Informed: the Governance Council (aware of every new feed, without
            needing to approve each one individually)

Metrics tracked monthly: catalog/classification coverage (must be 100%
  for any table containing PHI, enforced via the policy-as-code CI
  check from file 8), MTTD for data quality incidents, and access
  request turnaround time for clinical staff needing dashboard access
```

## Why This Case Study Ties the Whole Module Together
```
Every file in this module appears here, applied to ONE coherent,
realistically high-stakes scenario: classification (file 1) drives
catalog tagging (file 2) which enables automated access control;
MDM (file 3) resolves the multi-hospital patient identity problem
while preserving clinical history integrity; data contracts and
quality checks (file 4) protect against silent upstream corruption;
observability (file 5) catches compliance-critical anomalies
automatically; and a genuine operating model with RACI and metrics
(file 8) ensures all of this is actually enforced in practice, not
just documented and forgotten.
```

## Try It Yourself
Using this same layered approach, design a governance program for:
1. A fintech company handling PCI-regulated payment card data across multiple merchant partners.
2. An EdTech company handling student data under FERPA (US education privacy law) across multiple school district clients.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Responsibility shared clearly among many hands lightens the burden on all."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
