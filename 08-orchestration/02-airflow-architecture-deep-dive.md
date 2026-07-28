# 2. Airflow Architecture — Deep Dive

## The Core Components
```
┌─────────────────────────────────────────────────────────────────────┐
│                          AIRFLOW ARCHITECTURE                        │
├──────────────┬──────────────┬──────────────┬─────────────────────────┤
│  Scheduler    │  Webserver    │  Executor     │  Metadata Database      │
│  (decides     │  (the UI you  │  (decides HOW │  (Postgres/MySQL —      │
│   WHEN tasks  │   see in a    │   and WHERE   │   stores DAG state,     │
│   should run) │   browser)    │   tasks run)  │   task history, etc.)   │
└──────────────┴──────────────┴──────────────┴─────────────────────────┘
                                      |
                            ┌─────────┴─────────┐
                        Worker 1              Worker 2
                    (actually executes      (actually executes
                     the task's code)         the task's code)
```

### Scheduler — The Brain
Continuously scans your DAG files, determines which DAG runs are due based on their schedule, and which individual tasks within those DAG runs are now eligible to execute (their dependencies have been satisfied) — then hands them off to the Executor. **The Scheduler is often the first thing to investigate when "my DAG isn't running at all"** — a Scheduler that's down, overloaded, or has a parsing error in a DAG file can silently prevent runs from being triggered.

### Webserver — The UI
Renders the visual DAG graph, task logs, execution history — reads from the Metadata Database to show this. Doesn't execute anything itself.

### Executor — The "How Tasks Actually Run" Decision
```
SequentialExecutor: runs one task at a time, NO parallelism — dev/testing only,
                     never use in production

LocalExecutor: runs multiple tasks in parallel on the SAME machine as the
               Scheduler — fine for small-to-medium deployments, single point
               of failure (if that machine goes down, everything stops)

CeleryExecutor: distributes tasks across MULTIPLE worker machines via a
                message queue (Redis/RabbitMQ) — genuine horizontal scaling,
                the traditional production choice before Kubernetes became common

KubernetesExecutor: spins up a NEW POD for EVERY task run, then tears it down
                     after completion — maximum isolation (each task gets its
                     own clean environment/dependencies) and efficient resource
                     usage (no idle worker capacity sitting around), the
                     increasingly dominant modern production choice
```
**Real production guidance**: KubernetesExecutor has become the default recommendation for new production Airflow deployments specifically because of per-task isolation (one task's messy Python dependencies can't conflict with another's) and genuinely elastic resource usage (you're not paying for idle worker capacity between task runs).

### Metadata Database — The Source of Truth
Stores EVERYTHING: DAG run history, task instance states (success/failed/running/queued), variables, connections, XCom data (see file 3) — if this database goes down or gets corrupted, Airflow effectively loses its memory of what happened and what's currently running. Production Airflow deployments treat this database with the same care as any other critical production database (backups, monitoring, appropriately sized).

## The DAG File Parsing Process (a common source of confusion)
```
Every DAG Python file in your dags/ folder is RE-PARSED (re-executed as
Python code) by the Scheduler REPEATEDLY, on a configurable interval —
NOT just once when you first add it.

Why this matters: putting SLOW or EXPENSIVE code directly at the top level
of a DAG file (e.g., making an API call to determine which tasks to create)
means that expensive operation runs EVERY SINGLE PARSING CYCLE, potentially
every few seconds, even when the DAG itself isn't actually running —
a very common, very real Airflow performance mistake.
```
```python
# BAD — this API call runs on EVERY scheduler parse cycle, not just when the DAG executes
import requests
config = requests.get("https://config-service/pipeline-config").json()  # DON'T DO THIS at file top-level

# GOOD — defer expensive operations to actually run INSIDE a task, only when the DAG executes
def get_config_and_process(**context):
    config = requests.get("https://config-service/pipeline-config").json()
    # ... use config here ...
```

## Airflow's Execution Model — "Logical Date" / "Data Interval" (a famous source of confusion)
```
A DAG scheduled to run "daily" at midnight for July 25th actually represents
the interval July 24th 00:00 -> July 25th 00:00 — Airflow's "execution_date"
(older terminology) / "data_interval_start"/"data_interval_end" (modern
terminology) refers to the START of that period, NOT the moment the DAG
actually executes.

Practical implication: a DAG run labeled "2026-07-25" that's scheduled daily
typically represents "process the data FOR July 25th" and often doesn't
actually EXECUTE until July 26th 00:00 (once the full day's data interval
has passed) — this confuses nearly every Airflow beginner at least once,
and is worth understanding deeply before writing incremental-load logic
that depends on these dates being correct.
```

## Airflow 2.x vs 3.x — What Changed (staying current)
```
Airflow 2.x (long-standing, most widely deployed in production as of 2026):
  TaskFlow API (@task decorator) simplified writing Pythonic DAGs
  significantly compared to older explicit Operator instantiation style

Airflow 3.x (newer major version): further modernization — improved
  scheduler performance/architecture, better UI, and continued refinement
  of the "DAG as code" developer experience; check current Airflow
  documentation for the latest specifics, as this space continues evolving
  rapidly and this repo's information should be verified against
  up-to-date official docs when working with a specific version.
```

## Interview Traps
- "What's the difference between the Scheduler and the Executor?" — Scheduler decides WHAT should run and WHEN based on dependencies/schedule; Executor decides HOW and WHERE that work actually gets executed (locally, via Celery workers, via Kubernetes pods).
- "Why shouldn't you put expensive/slow code at the top level of a DAG file?" — DAG files are re-parsed repeatedly by the Scheduler (not just once), so expensive top-level code runs far more often than intended, potentially degrading Scheduler performance across your ENTIRE Airflow deployment, not just that one DAG.
- "What's the KubernetesExecutor's main advantage over CeleryExecutor?" — per-task isolation (independent dependency environments) and elastic resource usage (no idle worker capacity), at the cost of some per-task pod-startup overhead.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The path of steady humility outlasts the path of proud haste."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
