# 8. DevOps for Data Engineers — What Actually Matters for YOUR Job

## Why "Normal" DevOps Advice Doesn't Fully Transfer to Data Pipelines
Most DevOps content is written for stateless web APPLICATIONS (a web server, a mobile app backend) — but data pipelines have genuinely different characteristics: they process STATEFUL, often large data; failures can mean CORRUPTED DATA, not just downtime; testing requires REPRESENTATIVE data, not just mocked API calls; and "deployment" often means deploying a DAG/dbt project, not a running service.

## Version Controlling the Full Data Platform
```
What SHOULD live in Git (exactly like application code):
- Airflow DAGs (`08-orchestration/`)
- dbt models, tests, and Semantic Layer definitions (`04-etl-elt/08`)
- Python extraction/transformation scripts (`03-python/`)
- Terraform configs for data infrastructure (`07-cloud-platforms/10`)
- SQL DDL/schema definitions (`05-databases/12`)

What should NOT live in Git:
- The actual DATA itself (use S3/a data lake, not Git — see file 2's
  Git LFS discussion)
- Secrets/credentials (use a secrets manager, per `03-python/07-09`)
```

## CI/CD for dbt Projects — A Concrete, Common Real Pattern
```yaml
# .github/workflows/dbt-ci.yml
name: dbt CI
on: [pull_request]
jobs:
  dbt-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install dbt-snowflake
      - run: dbt deps
      - run: dbt build --target ci   # runs models AND tests against a
                                       # dedicated CI/staging schema —
                                       # NEVER directly against production
```
**Why a dedicated CI target/schema matters**: running `dbt build` during CI against a SEPARATE schema (not production) lets you validate that new SQL logic actually works and passes data quality tests BEFORE it ever touches real production data — exactly the staging-environment principle from file 3, applied specifically to a dbt/warehouse context.

## Testing Data Pipelines — Genuinely Different From Testing Applications
```python
# Unit testing PURE transformation logic (no external dependencies) —
# straightforward, exactly like testing any Python function
def test_calculate_discount():
    assert calculate_discount(100, 20) == 80

# Testing code that TALKS TO external systems (APIs, databases) — MOCK
# the external call, never hit a real API/database in a unit test
# (recap from `03-python/13-production-best-practices.md`)
@patch("pipeline.requests.get")
def test_extract_handles_api_error(mock_get):
    mock_get.side_effect = ConnectionError()
    with pytest.raises(ConnectionError):
        extract_orders()

# Testing with REPRESENTATIVE sample data — a genuinely DE-specific testing
# concern: does your transformation logic handle realistic edge cases
# (nulls, duplicates, unexpected values) present in REAL data, not just
# clean, idealized test fixtures?
def test_deduplication_handles_real_world_messy_data():
    messy_sample = pd.read_csv("tests/fixtures/sample_with_duplicates_and_nulls.csv")
    result = clean_orders(messy_sample)
    assert result["order_id"].is_unique
```

## CI/CD for Airflow DAGs
```yaml
# Common pattern: CI validates DAG integrity BEFORE deployment
- name: Validate DAGs
  run: |
    python -c "
    from airflow.models import DagBag
    dagbag = DagBag(dag_folder='dags/', include_examples=False)
    assert len(dagbag.import_errors) == 0, dagbag.import_errors
    "
- name: Run DAG-specific unit tests
  run: pytest tests/dags/ -v
```
This catches a genuinely common real mistake BEFORE it reaches production: a syntax error or import error in a DAG file that would otherwise silently prevent that DAG (and potentially degrade the Scheduler's overall performance, per `08-orchestration/02`'s warning) from running correctly.

## Environment Parity — Dev/Staging/Production for Data Platforms
```
A genuinely common DE-specific challenge: production data is often
MUCH LARGER and MESSIER than any hand-crafted test dataset — a pipeline
that works perfectly on a small, clean sample can still fail in
production on data volume/edge cases the sample never covered.

Real mitigation approaches:
- Use a SAMPLED, ANONYMIZED subset of real production data for staging
  (never raw, unmasked PII in a lower environment — a real security/
  compliance requirement)
- Run data quality checks (`03-python/12`) as an automated CI/CD gate,
  not just a manual, occasional check
- Consider "shadow" deployments — running a NEW pipeline version
  ALONGSIDE the existing production version temporarily, comparing
  outputs (the FULL OUTER JOIN reconciliation pattern from
  `02-sql/06-advanced-sql-patterns.md`), before fully cutting over
```

## Containerizing Data Pipelines (tying file 4 directly to DE work)
```dockerfile
# A containerized PySpark/Python ETL job — ensures the EXACT same
# library versions/environment run in dev, CI, and production,
# eliminating the "works on my machine" class of pipeline bugs entirely
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENTRYPOINT ["python", "run_pipeline.py"]
```
This directly enables Airflow's KubernetesExecutor pattern (`08-orchestration/02`) — each pipeline task runs in its own consistent, isolated container.

## Infrastructure as Code for Data Platforms (tying file 7/`07-cloud-platforms/10` to DE)
```hcl
# A genuinely common real Terraform pattern for a data platform
resource "aws_glue_catalog_database" "analytics" {
  name = "analytics"
}
resource "aws_s3_bucket" "curated_zone" {
  bucket = "my-company-curated-data"
}
resource "snowflake_warehouse" "etl_warehouse" {
  name           = "ETL_WH"
  warehouse_size = "MEDIUM"
  auto_suspend   = 60   # cost optimization, recap from `07-cloud-platforms/08`
}
```
Data warehouses, Glue catalogs, and even Snowflake resources themselves are increasingly managed via Terraform in mature data platforms — applying the SAME "infrastructure as reviewable, version-controlled code" discipline to data infrastructure specifically, not just traditional application servers.

## Monitoring/Observability for Data Pipelines (preview of file 9, DE-specific angle)
```
Beyond standard application monitoring (is the service up), data
pipelines need SPECIFICALLY:
- Data freshness monitoring ("when was this table last successfully updated")
- Data quality monitoring (row counts, null rates, schema drift — see
  `03-python/12` and `08-orchestration/08`)
- Pipeline SLA monitoring (did the nightly load finish before the
  business needs it)
```

## The Real DevOps Maturity Checklist for a Data Platform
```
[ ] All pipeline code (DAGs, dbt, Python) lives in Git, with PR review required
[ ] CI runs automated tests (unit + dbt tests) on every PR, before merge
[ ] A dedicated staging/CI environment exists, separate from production
[ ] Pipelines are containerized for environment consistency
[ ] Infrastructure (warehouses, buckets, IAM roles) is defined via Terraform
[ ] Deployments are automated (not manual SSH/console clicks)
[ ] Data quality checks run automatically as part of the pipeline, not
    manually/occasionally
[ ] Monitoring/alerting covers infrastructure health, pipeline execution,
    AND data quality (the three layers from `08-orchestration/08`)
[ ] Rollback is fast and well-understood (both for code AND for
    reprocessing bad data, e.g., via time-travel table formats from
    `06-big-data/06`)
```

## Interview Traps
- "How is testing a data pipeline genuinely different from testing a typical web application?" — needs representative, realistic sample data covering real-world messiness (nulls, duplicates, edge cases), not just clean idealized fixtures; and often needs a dedicated staging schema/environment for validating transformation logic against real-scale data before touching production.
- "How would you set up CI/CD for a dbt project?" — a pipeline that runs `dbt build`/`dbt test` against a dedicated CI/staging schema on every PR, never directly against production, gating merge on all tests passing.
- "What does 'DevOps maturity' look like specifically for a data platform, not just a typical application?" — reference the maturity checklist above, emphasizing the DATA-specific additions (data quality gates, freshness monitoring, staging with representative data) beyond generic application DevOps practices.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Every rollback done gracefully is a lesson learned without a scar left behind."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
