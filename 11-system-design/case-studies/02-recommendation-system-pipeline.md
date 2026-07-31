# Case Study 2: Recommendation System Data Pipeline (Netflix/Spotify-style)

## Step 1: Requirements
```
Functional: generate personalized content recommendations for millions
            of users, based on their viewing/listening history and
            similar users' behavior; recommendations shown on the
            homepage every time a user opens the app

Non-functional:
  - Latency: recommendations must be served in under 100ms when a user
    opens the app (a hard UX requirement — this is a SERVING latency
    requirement, distinct from how fresh the underlying MODEL needs to be)
  - Freshness: the underlying model/recommendations can be updated
    DAILY (not real-time) — acceptable per business requirements, since
    taste doesn't change minute-to-minute
  - Scale: 50 million active users, average 30 content interactions/day each
  - Cost: must be cost-efficient at this scale — recomputing ALL
    recommendations for ALL users too frequently would be wasteful
```

## Step 2: High-Level Data Flow
```
User interaction events (Kafka) -> Data Lake (raw interaction history)
   -> Batch feature engineering (Spark, nightly) -> Model training
   (collaborative filtering / deep learning, on a schedule — e.g., weekly
   full retrain, daily incremental update) -> Batch INFERENCE (Spark,
   nightly — precompute recommendations for ALL users) -> Fast-serving
   store (Redis/DynamoDB — precomputed recommendations per user)
   -> App reads from fast-serving store at request time (meets the
   100ms requirement, since it's just a KEY-VALUE lookup, not live
   model inference)
```
**Key architectural insight**: the 100ms SERVING requirement does NOT mean the whole pipeline must be real-time — it's satisfied by precomputing recommendations in batch and serving them from a fast key-value store, decoupling "how fresh does the underlying data need to be" (daily, acceptable) from "how fast must the USER-FACING lookup be" (100ms, met by Redis/DynamoDB, not by live model computation).

## Step 3: Capacity Estimation
```
50,000,000 users x 30 interactions/day = 1,500,000,000 events/day
At ~0.5 KB per interaction event: 1.5B x 0.5 KB = 750 GB/day raw
Annual (compressed ~5x): ≈ 750 GB x 365 / 5 ≈ ~55 TB/year — genuine
  big-data scale, clearly justifying Spark for batch processing.

Precomputed recommendations storage: 50M users x ~50 recommended items
  x small metadata (~100 bytes each) ≈ 50M x 5KB ≈ 250 GB total in the
  fast-serving store — comfortably fits in a well-sized Redis
  Cluster/DynamoDB table.
```

## Step 4: Technology Choices, Justified

**Batch processing — Spark, not streaming**
> Justification: the DAILY freshness requirement explicitly does NOT need streaming — using Kappa/streaming here would add real operational complexity (per file 3's tradeoff analysis) with zero corresponding business benefit, since users don't need minute-by-minute updated recommendations. This is a deliberate, justified choice of the SIMPLER option.

**Model training — offline, scheduled (not online/real-time learning)**
> Justification: recommendation models benefit from stable, well-validated periodic retraining rather than continuous online updates that risk instability from noisy real-time signals; the daily/weekly cadence matches the stated freshness requirement exactly.

**Serving layer — Redis/DynamoDB precomputed lookups, not live inference**
> Justification: meets the hard 100ms requirement trivially (a key-value lookup is essentially always fast) while avoiding the cost/complexity of running expensive ML model inference on every single app open — precomputing once per day and serving many times is dramatically more cost-efficient at this user scale.

**Storage — Data lake (Parquet/Iceberg) for raw interaction history**
> Justification: need to retain full historical interaction data for model retraining and potential future model architecture changes (a new model type might need to reprocess history differently) — cheap object storage is the right fit for this large, less-frequently-accessed-in-full history.

## Step 5: Failure Modes & Scale
```
"What happens if the nightly batch job fails?"
  -> Users see YESTERDAY's (or older) precomputed recommendations —
     a GRACEFUL DEGRADATION, not a total outage, precisely because the
     serving layer is decoupled from the batch job's real-time success.
     This is a genuinely important, deliberate resilience property of
     this architecture, worth calling out explicitly in an interview.

"Where does this break first at 10x user growth (500M users)?"
  -> Batch processing time is the first likely bottleneck (Spark job
     needs to scale out with more executors — recap `06-big-data/04`);
     the serving layer (Redis/DynamoDB) scales more straightforwardly
     via standard horizontal sharding.

"What about new users with no interaction history (cold start)?"
  -> A genuinely important real ML/data engineering edge case: the
     pipeline needs a FALLBACK path (e.g., popular/trending content)
     for users without enough history for personalized recommendations
     — a design detail easy to overlook but important to raise proactively.
```

## Step 6: Summary
> "Given the daily freshness requirement and hard 100ms serving latency, I'm proposing a batch Spark pipeline (nightly feature engineering + inference) writing precomputed recommendations to a fast-serving key-value store, deliberately AVOIDING a streaming architecture since it isn't justified by the actual requirements. This decouples serving latency from batch freshness, and gives graceful degradation if the batch job fails. The main tradeoff is that recommendations are at most a day stale — acceptable per the stated requirements, but I'd flag that if the business later wants more real-time responsiveness to say, a user just watching something, we'd need to revisit this toward a hybrid batch + lightweight real-time re-ranking approach."


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Real leadership is building a system where good decisions don't depend only on you."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
