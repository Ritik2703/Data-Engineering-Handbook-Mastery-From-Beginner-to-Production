# 6. MLOps for Data Engineers — The DE↔MLOps Boundary

## Why Data Engineers Increasingly Touch This
As covered in `05-databases/06` (vector databases) and briefly in `07-cloud-platforms`'s GCP file (BigQuery ML), the line between "Data Engineering" and "ML Engineering/MLOps" has genuinely blurred — a Data Engineer is now commonly responsible for building and maintaining the PIPELINES that feed ML models (feature engineering, feature serving) even without owning the model training/algorithm work itself. This file defines exactly where that boundary sits and what a DE needs to know on their side of it.

## The ML Data Pipeline — Where DE Responsibility Typically Starts and Ends
```
[Raw data: transactions, clickstream, user profiles]
        |
   Data Engineering territory:
   Feature ENGINEERING (transforming raw data into model-ready features
   -- recap Spark/dbt transformation skills from modules 04/06)
        |
   Feature STORE (storing/serving features consistently -- THIS file's focus)
        |
   Data Science / ML Engineering territory:
   Model TRAINING, hyperparameter tuning, algorithm selection
        |
   MLOps territory (often a blend of DE + ML Engineering):
   Model DEPLOYMENT, serving infrastructure, MONITORING (drift, performance)
        |
   Back to Data Engineering territory (the loop closes):
   Feeding model PREDICTIONS/outputs back into the data platform for
   analysis, and feeding NEW data back in for retraining
```
**The key insight**: DE's core responsibility is the DATA feeding ML (feature engineering + serving), and increasingly the DEPLOYMENT PIPELINE infrastructure — NOT typically the model algorithm/training science itself, though these roles blend significantly at smaller companies.

## The Feature Store — The Central MLOps Concept a DE Must Understand
```
The problem a feature store solves: a data scientist computes a
"customer_avg_order_value_last_30_days" feature for TRAINING a model
(often in a notebook, using batch historical data) -- but when the
model is DEPLOYED to production, the SAME feature must be computed
IDENTICALLY, in REAL TIME, for a live prediction request -- and subtly
different logic between training and serving ("training-serving
skew") is one of the most common, hardest-to-debug real ML production
bugs.

A Feature Store solves this by being the SINGLE place feature logic is
defined ONCE, serving BOTH:
  Offline store: large-scale historical feature values for TRAINING
    (often backed by the data warehouse/lake itself -- recap modules
    04-06)
  Online store: low-latency, current feature values for real-time
    INFERENCE (often backed by Redis/DynamoDB -- recap the exact
    fast-serving-layer pattern from the ride-hailing case study in
    `05-databases/case-studies/` and the recommendation system case
    study in `11-system-design/case-studies/`)
```
```python
# Conceptual feature store usage (Feast, an open-source feature store)
from feast import FeatureStore

store = FeatureStore(repo_path=".")

# TRAINING: pull historical feature values for a training dataset
training_df = store.get_historical_features(
    entity_df=orders_df,  # which entities (customers) and WHEN
    features=["customer_features:avg_order_value_30d", "customer_features:total_orders_90d"],
).to_df()

# SERVING: pull CURRENT feature values for a real-time prediction
online_features = store.get_online_features(
    features=["customer_features:avg_order_value_30d", "customer_features:total_orders_90d"],
    entity_rows=[{"customer_id": "CUST-12345"}],
).to_dict()
```
**Feast vs Tecton**: Feast is the leading open-source feature store (self-hosted, flexible); Tecton is a commercial, fully-managed feature platform built by some of Feast's original creators — the exact same "open-source vs managed commercial" tradeoff pattern seen throughout this repo (recap the build-vs-buy discussions in modules 04, 08, 11).

## ML Pipeline Orchestration — Reusing (and Extending) Module 08's Skills
```python
# ML training/retraining pipelines are ORCHESTRATED using the exact
# same tools covered in module 08 -- Airflow is genuinely common for
# scheduled retraining pipelines, not just traditional ETL
from airflow.decorators import dag, task
from datetime import datetime

@dag(schedule="@weekly", start_date=datetime(2026, 1, 1), catchup=False)
def model_retraining_pipeline():

    @task
    def extract_training_features():
        # pulls from the offline feature store
        ...

    @task
    def train_model(features):
        # calls out to a training job (e.g., a SageMaker/Databricks/
        # Vertex AI training job -- the DE pipeline TRIGGERS this,
        # doesn't necessarily implement the ML algorithm itself)
        ...

    @task
    def validate_model_quality(model):
        # a genuinely important DE-adjacent responsibility: automated
        # checks BEFORE deploying a new model version -- does it beat
        # the current production model on a held-out validation set?
        if model.validation_accuracy < CURRENT_PROD_ACCURACY:
            raise ValueError("New model underperforms current production model -- blocking deployment")

    @task
    def deploy_model(model):
        ...

    features = extract_training_features()
    model = train_model(features)
    validate_model_quality(model)
    deploy_model(model)

model_retraining_pipeline()
```
This directly reuses the retry/idempotency/DAG-dependency skills from module 08, applied to an ML-specific workflow — a genuinely common real responsibility for Data/ML Engineers at companies without a dedicated separate MLOps team.

## Model Monitoring — Where DE Observability Skills Directly Transfer
```
Data/Concept Drift: the STATISTICAL DISTRIBUTION of incoming production
  data diverges from the data the model was TRAINED on -- e.g., a
  fraud model trained on pre-pandemic spending patterns seeing
  genuinely different spending behavior post-pandemic. Detected using
  the EXACT SAME distribution-monitoring techniques from file 5's
  data observability discussion, applied specifically to model INPUT features.

Model Performance Monitoring: tracking real-world prediction accuracy
  (when ground truth eventually becomes known, e.g., did a "will this
  transaction be fraudulent" prediction turn out correct) -- genuinely
  distinct from data drift (data can look statistically normal while
  the model's real-world accuracy still degrades for other reasons).

Prediction Serving Latency/Availability: standard application
  observability (recap `10-devops/09`'s three pillars) applied to the
  model-serving endpoint specifically.
```

## A/B Testing for Model Deployment (recap + ML-specific application)
```
Directly reuses the canary deployment concept from `10-devops/03` --
a new model version is deployed to serve a SMALL percentage of
production traffic first, with its real-world performance compared
against the current production model, before a full rollout -- the
EXACT same gradual-rollout risk-management principle from DevOps,
applied specifically to model deployment.
```

## Interview Traps
- "What's a feature store, and why does it matter?" — solves training-serving skew by defining feature logic ONCE, serving both an offline store (for training) and online store (for real-time inference) — a genuinely common, important MLOps pattern.
- "Where does Data Engineering responsibility typically end and ML Engineering begin?" — DE typically owns feature engineering, feature serving infrastructure, and increasingly deployment pipeline orchestration; ML Engineering/Data Science typically owns model algorithm selection and training — though these blend significantly at smaller companies.
- "How does data drift differ from a normal data quality anomaly (file 5)?" — the TECHNIQUE (distribution monitoring) is genuinely the same; the APPLICATION is specifically to a model's INPUT features, checked against what the model was originally trained on, not just "is this normal for this table historically."


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The quality of one's work is a quiet reflection of the quality of one's character."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
