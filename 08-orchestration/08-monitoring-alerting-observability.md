# 8. Monitoring, Alerting & Observability — The Production Reality

## Why This Is Its Own Critical Topic
A pipeline that fails silently is worse than one that never existed — a business user makes a decision based on a stale/wrong dashboard, trusting it completely, with nobody aware anything went wrong until much later (often when the wrong decision's consequences surface). **Real production orchestration work is at least as much about knowing WHEN and WHY something broke as it is about the pipeline logic itself.**

## The Three Layers of Pipeline Observability
```
1. INFRASTRUCTURE health: is the orchestrator itself (Scheduler, workers)
   healthy and responsive? (covered in file 2/4's monitoring checklist)

2. PIPELINE execution health: did each DAG run / task complete successfully,
   on time, within expected resource usage?

3. DATA quality health: even if the pipeline "succeeded" (no errors thrown),
   is the ACTUAL DATA correct? (row counts reasonable, no unexpected nulls,
   freshness within SLA) — see `03-python/12-data-quality-validation.md`
```
A common, costly mistake: monitoring ONLY layer 2 (did the code run without throwing an exception) while completely missing layer 3 (the code ran "successfully" but produced garbage data, e.g., an API silently returned an empty result and nothing downstream caught it).

## Alerting Design — Getting the RIGHT People Notified for the RIGHT Reasons
```python
# A well-designed failure callback — not just "something broke," but WHO
# should know and HOW urgently
def notify_on_failure(context):
    task_instance = context["task_instance"]
    dag_id = context["dag"].dag_id
    exception = context.get("exception")

    severity = classify_severity(dag_id, task_instance)  # your own business logic

    if severity == "critical":
        page_oncall_engineer(f"CRITICAL: {dag_id} failed - {exception}")
        post_to_slack("#data-eng-critical-alerts", f"🚨 {dag_id} failed")
    elif severity == "warning":
        post_to_slack("#data-eng-alerts", f"⚠️ {dag_id} failed (non-critical): {exception}")
    # else: log only, no notification (avoid alert fatigue for low-stakes pipelines)
```
**Alert fatigue is a genuine, real production problem**: if EVERY minor pipeline failure pages someone at 3 AM, engineers start ignoring/muting alerts entirely — including the genuinely critical ones. Deliberate severity classification (which pipelines are truly business-critical vs which can wait until business hours) is essential, not optional, production design work.

## SLAs in Practice — Setting Realistic, Meaningful Thresholds
```
Common mistake: setting an SLA of "must finish in 30 minutes" because that's
                 roughly how long it currently takes, with zero margin —
                 leading to constant SLA-miss alerts for entirely normal
                 minor variance, training the team to ignore SLA alerts entirely.

Better approach: set SLAs based on the ACTUAL BUSINESS DEADLINE (e.g., "the
                  finance team needs this data by 6 AM"), with reasonable
                  margin, and treat repeated SLA misses as a genuine signal
                  to investigate/re-architect (add more compute, optimize
                  the slow step) rather than just repeatedly loosening the
                  SLA threshold to stop the alerts.
```

## Data Observability Tools (beyond basic pipeline success/failure)
```
Great Expectations / Pandera / dbt tests (see `03-python/12` and `04-etl-elt/08`):
  Explicit, code-defined data quality assertions run as part of the pipeline

Monte Carlo / Bigeye / Databand (dedicated "data observability" platforms):
  Automatically detect ANOMALIES in data patterns (a table's row count
  suddenly dropping 90%, a column's null rate suddenly spiking) WITHOUT
  requiring you to have explicitly anticipated and coded a check for that
  SPECIFIC failure mode in advance — using statistical baselines learned
  from historical data patterns, catching the "unknown unknowns" that
  explicit rule-based checks inherently can't anticipate
```
**Real production value of dedicated data observability tools**: explicit checks (Great Expectations, dbt tests) only catch problems you thought to anticipate; anomaly-detection-based observability tools can catch GENUINELY SURPRISING failures (an upstream schema change nobody told you about, a silent partial data loss) that no one wrote an explicit rule for — a meaningfully different, complementary layer of protection.

## Dashboards — What to Actually Show (and to Whom)
```
For the DATA ENGINEERING TEAM (operational dashboard):
  - Current running/queued/failed task counts across all DAGs
  - Historical success rate trends per DAG (is a specific pipeline getting
    flakier over time — an early warning sign worth investigating proactively)
  - Resource utilization (worker capacity, queue depth)

For BUSINESS STAKEHOLDERS (data freshness/trust dashboard):
  - "As of when was this dashboard's data last successfully refreshed?"
    (a simple, visible timestamp — surprisingly rare in practice, and
    genuinely valuable for building/maintaining stakeholder trust in the data)
  - Known data quality issues currently being investigated (proactive
    transparency beats a business user discovering a problem independently
    and losing trust in the ENTIRE data platform, not just the one pipeline)
```

## On-Call Reality for Data Engineers (the practical, human side)
```
Real production data teams typically maintain an on-call ROTATION —
someone specifically responsible for responding to critical pipeline
alerts outside business hours, with:
  - A clear RUNBOOK for common failure types (what to check first,
    common root causes, how to safely re-run/backfill)
  - Clear ESCALATION paths for issues beyond the on-call engineer's
    ability to resolve alone
  - A blameless POST-MORTEM culture after significant incidents — focused
    on "how do we prevent this class of failure system-wide" rather than
    "whose fault was this," which genuinely improves long-term reliability
    far more than blame-focused reactions do
```

## Interview Traps
- "How would you design an alerting strategy for a data platform with hundreds of pipelines?" — severity-based classification (not every failure pages someone at 3 AM), realistic SLA thresholds tied to actual business deadlines, and the three-layer observability model (infrastructure/execution/data quality) — not just "send a Slack message on any failure."
- "What's the difference between explicit data quality checks and dedicated data observability tools?" — explicit checks (Great Expectations/dbt tests) catch anticipated failure modes you coded for; anomaly-detection-based observability tools catch genuinely unexpected/unanticipated failures using statistical baselines — complementary, not either/or.
- "How do you avoid alert fatigue on a data team?" — deliberate severity classification, realistic SLA thresholds with appropriate margin, and treating repeated false-alarm SLA misses as a signal to fix the underlying pipeline/SLA rather than simply ignoring or endlessly loosening the alert.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The quiet discipline of daily practice is the real secret behind every visible success."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
