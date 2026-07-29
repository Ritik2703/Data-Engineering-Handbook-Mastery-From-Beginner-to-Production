# 9. Monitoring & Observability — Knowing When Something's Wrong

## The Three Pillars of Observability
```
METRICS: numeric measurements over time (CPU usage, request count, task
         failure rate) — good for TRENDS and ALERTING thresholds

LOGS: detailed, timestamped records of discrete events ("task X started,"
      "error: connection refused at 14:32:01") — good for DEBUGGING
      "what exactly happened, in what order"

TRACES: following a SINGLE request/transaction's full path across
        MULTIPLE services/components — good for understanding "where,
        specifically, in a complex multi-step system did the slowdown/
        failure actually occur"
```
**Real production insight**: all three are complementary, not substitutes — metrics tell you SOMETHING is wrong (error rate spiked), logs tell you WHAT happened (the specific error message), traces tell you WHERE in a complex system it happened (which specific service/step).

## Prometheus — The Metrics Standard
```
Prometheus PULLS metrics from configured targets at regular intervals
(rather than applications pushing metrics to it) — a "pull-based" model
that's become the de facto standard for cloud-native/Kubernetes metrics
collection, with a powerful query language (PromQL) for analysis:

rate(http_requests_total{status="500"}[5m])   -- rate of 500 errors
                                                  over the last 5 minutes
```

## Grafana — The Visualization Layer (often paired with Prometheus)
Grafana doesn't COLLECT metrics itself — it connects to data sources (Prometheus, and many others including databases) and provides dashboards/alerting on TOP of that data, conceptually similar in spirit to how Tableau/Power BI (module 09) visualize BUSINESS data, but specifically built for OPERATIONAL/infrastructure metrics.

## The ELK/EFK Stack — Centralized Logging
```
Elasticsearch: stores and indexes log data for fast searching
Logstash / Fluentd: collects and processes logs from many sources,
                      shipping them to Elasticsearch
Kibana: the visualization/search UI on top of Elasticsearch

Why centralized logging matters: in a distributed system with dozens of
containers/services, logs scattered across each individual machine are
nearly impossible to search/correlate manually — centralizing them into
one searchable system is essential once you're beyond a single-server setup.
```

## Distributed Tracing — OpenTelemetry
```
OpenTelemetry (an increasingly dominant open standard, merging earlier
separate projects OpenTracing and OpenCensus) provides a unified way to
instrument code for METRICS, LOGS, and TRACES together, avoiding vendor
lock-in to any one specific observability tool — a genuinely important
2020s standardization trend, letting teams switch observability BACKENDS
(Datadog, New Relic, self-hosted Prometheus/Jaeger) without rewriting
all their application instrumentation code.
```

## Application Performance Monitoring (APM) — Commercial Alternatives
```
Datadog, New Relic, Dynatrace: commercial, fully-managed observability
  platforms combining metrics/logs/traces/alerting in one product —
  trading the cost of a paid subscription for significantly less
  operational overhead than self-hosting Prometheus/Grafana/ELK yourself.
```

## Alerting Design (recap + DevOps-wide angle, extending `08-orchestration/08`)
```
The SAME alert fatigue and severity-classification principles from
orchestration monitoring apply to ALL of DevOps monitoring broadly:
- Alert on SYMPTOMS that matter to users/business (error rate, latency),
  not just every possible internal metric fluctuation
- Use METRIC-BASED alerting (e.g., "error rate > 5% for 5 minutes") rather
  than single-event alerting (one error ≠ an incident) to avoid noise
- Tie alert severity to actual business impact, routing critical
  production issues to immediate paging and lower-priority issues to
  async channels (Slack) reviewed during business hours
```

## SLOs, SLIs, and SLAs — The Vocabulary of Reliability
```
SLI (Service Level Indicator): an actual MEASUREMENT (e.g., "99.2% of
     requests succeeded in the last 30 days")

SLO (Service Level Objective): an internal TARGET for that measurement
     (e.g., "we aim for 99.9% success rate") — used to guide engineering
     priorities (if you're comfortably meeting your SLO, maybe invest
     engineering time elsewhere; if you're missing it, reliability work
     becomes the priority)

SLA (Service Level Agreement): an external, often CONTRACTUAL commitment
     to a customer (e.g., "we guarantee 99.9% uptime or you get a
     refund") — typically LOOSER than your internal SLO, giving you
     margin before an SLO miss becomes a costly SLA breach
```
**Error Budgets** (a related, powerful concept): if your SLO is 99.9% uptime, you have an implicit "budget" of 0.1% allowed downtime/errors — teams use this error budget deliberately to decide how much RISK they can take with new deployments/experiments before needing to slow down and prioritize stability, a genuinely useful framework for balancing feature velocity against reliability.

## Interview Traps
- "What are the three pillars of observability, and why do you need all three?" — metrics (trends/alerting), logs (detailed event debugging), traces (following a request across services) — complementary, each answering a different diagnostic question (something's wrong / what happened / where did it happen).
- "What's the difference between an SLI, SLO, and SLA?" — SLI is the actual measurement; SLO is your internal target; SLA is an external, often contractual commitment, typically looser than your SLO to provide margin.
- "What's an error budget, and how is it used?" — the allowed amount of unreliability implied by your SLO (e.g., 0.1% for a 99.9% SLO), used to deliberately guide how much deployment/experimentation risk a team can take before needing to prioritize stability over new features.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"To watch quietly and act only when needed is its own form of mastery."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
