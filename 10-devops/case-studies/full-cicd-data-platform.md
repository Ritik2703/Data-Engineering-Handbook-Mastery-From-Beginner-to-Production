# Case Study: Full CI/CD Pipeline for a Data Platform (Real Design)

## The System Being Deployed
```
- A dbt project (staging + mart models, tests)
- Python extraction scripts (pulling from 3 APIs)
- Airflow DAGs orchestrating the whole pipeline
- Terraform-managed Snowflake warehouse + AWS infrastructure
```

## The Full CI/CD Design

### Repository Structure
```
data-platform/
├── dbt_project/          # dbt models, tests, semantic layer
├── extractors/            # Python extraction scripts
├── dags/                  # Airflow DAG definitions
├── terraform/             # infrastructure as code
├── tests/                 # unit tests for extractors
└── .github/workflows/     # CI/CD pipeline definitions
```

### CI Pipeline (triggered on every Pull Request)
```yaml
name: Data Platform CI
on: [pull_request]

jobs:
  python-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.11"}
      - run: pip install -r requirements.txt
      - run: black --check extractors/     # enforce consistent formatting
      - run: flake8 extractors/              # lint
      - run: mypy extractors/                # type checking
      - run: pytest tests/ -v --cov=extractors

  dag-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install apache-airflow
      - name: Validate DAG integrity
        run: |
          python -c "
          from airflow.models import DagBag
          dagbag = DagBag(dag_folder='dags/', include_examples=False)
          assert len(dagbag.import_errors) == 0, dagbag.import_errors
          "

  dbt-ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install dbt-snowflake
      - working-directory: dbt_project
        run: |
          dbt deps
          dbt build --target ci   # runs against a DEDICATED CI schema,
                                    # never production — see 08-devops-for-data-engineers.md

  terraform-plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - working-directory: terraform
        run: |
          terraform init
          terraform plan -out=tfplan
      - name: Post plan as PR comment
        run: echo "Terraform plan reviewed above" # (real setup posts actual plan output)
```
Every category of change (Python code, DAGs, dbt models, infrastructure) has its OWN dedicated validation job, running in PARALLEL — a failure in any ONE blocks the merge, but they don't need to wait for each other sequentially, keeping CI feedback fast.

### CD Pipeline (triggered on merge to main)
```yaml
name: Data Platform CD
on:
  push:
    branches: [main]

jobs:
  deploy-infrastructure:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - working-directory: terraform
        run: |
          terraform init
          terraform apply -auto-approve   # safe because `plan` was already
                                            # reviewed in the PR before merge

  deploy-dags:
    needs: deploy-infrastructure
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Sync DAGs to Airflow (e.g., MWAA S3 bucket)
        run: aws s3 sync dags/ s3://my-airflow-bucket/dags/ --delete

  deploy-dbt:
    needs: deploy-infrastructure
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install dbt-snowflake
      - working-directory: dbt_project
        run: |
          dbt deps
          dbt run --target production   # NOTE: only runs models, doesn't
                                          # need to re-test here since CI
                                          # already validated this exact
                                          # commit passed all tests

  build-and-push-extractor-image:
    needs: deploy-infrastructure
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          docker build -t my-registry/extractors:${{ github.sha }} .
          docker push my-registry/extractors:${{ github.sha }}
```
Note the DEPENDENCY ordering (`needs: deploy-infrastructure`) — DAGs, dbt, and the extractor image all depend on infrastructure being deployed FIRST, since they might reference newly-created resources (a new Snowflake warehouse, a new S3 bucket) — directly applying the DAG dependency concept from module 08 to the CI/CD pipeline's OWN structure.

## Why This Design Reflects Every Lesson From This Module
```
- Every change type has dedicated CI validation (file 3's pipeline stages)
- dbt CI runs against a dedicated schema, never production directly (file 8)
- DAG integrity is validated BEFORE deployment, catching import errors early (file 8)
- Terraform plan is reviewed in the PR before merge; apply happens
  automatically but SAFELY afterward, since the plan was already
  human-reviewed (file 7, `07-cloud-platforms/10`)
- The extractor Python code is containerized (file 4), ensuring consistent
  environments between CI, and however it eventually runs (e.g., via
  Airflow's KubernetesExecutor)
- CD respects dependency order between infrastructure and the things
  that depend on it (file 5's Kubernetes dependency concepts, applied
  at the pipeline level)
```

## What's Still Missing (a mature team would add next)
```
- Automated rollback: if `dbt run` fails in CD, automatically alert AND
  potentially revert to the last known-good dbt state
- Canary/gradual rollout for the extractor container image, rather than
  deploying the new version everywhere simultaneously (file 3's deployment
  strategies)
- Post-deployment smoke tests: after CD completes, automatically run a
  lightweight validation (e.g., "does the warehouse have fresh data within
  the last 25 hours") before considering the deployment fully successful
- Monitoring/alerting integration (file 9) tied directly to this pipeline's
  outcomes, not just manual observation of the GitHub Actions UI
```

## Try It Yourself
Using this same structure, design a CI/CD pipeline for:
1. A PySpark-based ETL project running on Databricks, including notebook/job deployment.
2. A multi-cloud data platform where Terraform manages resources across both AWS and Azure.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Real strength is fixing the system, not just silencing the alarm."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
