# Orchestration Interview Questions — 35+ with Answers

## Fundamentals

**Q1. Why isn't cron sufficient for real production data pipelines?**
> Cron can't express dependencies between tasks, doesn't retry failures automatically, doesn't alert on failure, provides no visual execution history, and doesn't handle backfilling historical dates cleanly — all essential needs for pipelines beyond trivial single-script scheduling.

**Q2. What is a DAG and why must it be acyclic?**
> A Directed Acyclic Graph — nodes are tasks, edges are dependencies, direction shows execution order. It must be acyclic because a cycle (Task A depends on B, B depends on A) creates an impossible circular wait with no valid starting point.

**Q3. What are the core responsibilities of an orchestration tool?**
> Scheduling (when), dependency management (what order), execution (running the actual work, often delegated to other systems), retry/failure handling, monitoring/visibility, and backfilling.

## Airflow Architecture

**Q4. Explain the difference between the Scheduler and the Executor.**
> The Scheduler determines WHAT should run and WHEN based on schedules and dependency satisfaction; the Executor determines HOW and WHERE that work actually executes (locally, via Celery workers, or via Kubernetes pods).

**Q5. Why shouldn't you put expensive/slow code at the top level of a DAG file?**
> DAG files are re-parsed repeatedly by the Scheduler (not just once) — expensive top-level code runs on every parse cycle, potentially degrading the entire Airflow instance's scheduling performance, not just that one DAG.

**Q6. What's the KubernetesExecutor's main advantage?**
> Per-task isolation (each task gets its own pod/environment, avoiding dependency conflicts between tasks) and elastic resource usage (no idle worker capacity between runs), at the cost of some per-task pod-startup overhead.

**Q7. What does "logical date" / "data interval" mean in Airflow, and why does it confuse beginners?**
> It represents the START of the period being processed, not necessarily when the DAG actually executes — a daily DAG run labeled for July 25th typically represents processing July 25th's data and often doesn't execute until July 26th, after that full interval has passed.

## DAG Authoring

**Q8. What's the difference between Sensor `poke` mode and `reschedule` mode?**
> `poke` holds a worker slot occupied for the entire wait period (wasteful for long waits); `reschedule` releases the worker slot between checks, freeing it for other tasks — always prefer `reschedule` for waits longer than a few minutes.

**Q9. Why shouldn't you pass a large DataFrame through XCom?**
> XComs are stored in the Metadata Database and meant for small values (counts, paths, flags); large data should be written to external storage (S3/a database) with only a reference/path passed via XCom.

**Q10. How do you make a cleanup task run regardless of whether upstream tasks succeeded or failed?**
> Trigger rules — `TriggerRule.ALL_DONE` runs regardless of upstream outcome, unlike the default `all_success`.

## Production Patterns

**Q11. Why is idempotency even more critical in an orchestrated pipeline than a standalone script?**
> Airflow will automatically retry failed tasks and explicitly re-run historical dates during backfills — both completely normal, expected behaviors that will silently corrupt data (duplicate rows) if the pipeline isn't idempotent.

**Q12. What's `catchup` and why is it dangerous if misunderstood?**
> Controls whether Airflow automatically creates a DAG run for every missed historical interval since `start_date` when a DAG is first enabled; forgetting `catchup=False` on a new DAG with an old `start_date` can trigger an unwanted flood of backfill runs.

**Q13. How do you handle a variable, config-driven number of tasks (e.g., processing an unknown number of source tables)?**
> Dynamic Task Mapping (`.expand()`), Airflow's native pattern for creating one task instance per item in a runtime-determined list — see the metadata-driven case study.

**Q14. How would you prevent many DAGs from overwhelming a single shared source database?**
> Airflow Pools, which limit how many tasks using a specific pool can run concurrently, regardless of overall worker capacity.

**Q15. How do you set a meaningful SLA on a task, and what happens when it's missed?**
> Set the SLA based on the actual business deadline (not just current typical runtime with zero margin); a configured `sla_miss_callback` fires to alert the team when a task exceeds its SLA threshold.

## Dagster & Prefect

**Q16. What's the core philosophical difference between Airflow and Dagster?**
> Airflow's fundamental unit is a Task (execute this code, in this order); Dagster's fundamental unit is an Asset (a specific data artifact with tracked lineage and quality checks) — a genuinely different mental model, not just different syntax.

**Q17. Why might data quality checks be more naturally integrated in Dagster than Airflow?**
> Dagster's Asset Checks are directly attached to the specific asset they validate within the lineage graph, rather than being a separate, loosely-connected task in an Airflow DAG.

**Q18. What's Prefect's core positioning difference from Airflow?**
> Dynamic, genuinely Pythonic workflow structure determined at runtime (normal loops/conditionals) versus Airflow's more rigid requirement to define the full DAG structure upfront/statically.

**Q19. Why might a smaller team prefer Prefect?**
> A smoother local development experience — flows can be run and tested like normal Python scripts without needing a full orchestrator infrastructure (Scheduler/Webserver/Metadata DB) standing up first.

## Comparison & Strategy

**Q20. When would you recommend migrating from Airflow to Dagster/Prefect?**
> Only with a genuine, significant, recurring pain point (e.g., a desperate need for real data lineage visibility Airflow can't reasonably provide) — never purely because a newer tool has a nicer feature list; migration cost on existing production DAGs is real.

**Q21. Why do many companies use BOTH a cloud-native orchestrator (Step Functions/ADF) AND Airflow?**
> Cloud-native tools suit simple, within-one-cloud service-to-service triggers well; Airflow (or Dagster/Prefect) suits complex, cross-system data pipeline orchestration needing a broader ecosystem of integrations — using each for what it's genuinely best at.

**Q22. What's the modern relationship between an orchestrator and dbt?**
> The orchestrator typically handles scheduling and cross-system coordination (waiting for an extract, then triggering `dbt run`), while dbt manages the actual in-warehouse transformation dependency graph internally via `{{ ref() }}` — a common division of responsibility reducing orchestrator DAG complexity.

## Monitoring & Observability

**Q23. What are the three layers of pipeline observability?**
> Infrastructure health (is the orchestrator itself healthy), pipeline execution health (did tasks complete successfully/on time), and data quality health (is the actual data correct, even if no errors were thrown) — many teams monitor only the first two and miss real data problems.

**Q24. How do you avoid alert fatigue on a data engineering team?**
> Deliberate severity classification (not every failure pages someone at 3 AM), SLA thresholds tied to actual business deadlines with reasonable margin, and treating repeated false-alarm SLA misses as a signal to fix the underlying issue rather than endlessly loosening or ignoring the alert.

**Q25. What's the difference between explicit data quality checks and dedicated data observability tools?**
> Explicit checks (Great Expectations, dbt tests) catch anticipated failure modes you coded a rule for; anomaly-detection-based observability tools (Monte Carlo, Bigeye) catch genuinely unexpected failures using statistical baselines — catching "unknown unknowns" explicit rules inherently can't anticipate.

## Real-World / Company Choices

**Q26. Why did Airbnb create Airflow instead of using an existing tool?**
> Their growing number of interdependent scheduled data pipelines (hundreds, then thousands) became unmanageable to track manually — no existing tool at the time adequately solved this specific dependency-management-at-scale problem.

**Q27. Does every company just standardize on Airflow?**
> No — large tech companies often run a mix of Airflow (broad open-source standard), cloud-native tools (for teams committed to one cloud), and even internally-built tools (like Netflix's Conductor) for their most specific/unusual needs.

## Rapid-Fire
28. What's the difference between an Operator and a Sensor in Airflow? *(An Operator executes a task's actual work; a Sensor waits for a condition to become true before allowing downstream tasks to proceed.)*
29. What does `max_active_tasks` control? *(Limits overall concurrent task execution within a DAG, preventing resource overload.)*
30. Why is the Metadata Database so critical to an Airflow deployment? *(It stores all DAG run history, task states, variables, and XComs — losing it effectively loses Airflow's memory of what happened and what's currently running.)*
31. What's a Task Group in Airflow used for? *(Purely visual/organizational grouping of related tasks in the UI graph view — no functional execution difference.)*
32. What's the SequentialExecutor appropriate for? *(Development/testing only — runs one task at a time with no parallelism, never appropriate for production.)*
33. Why is a blameless post-mortem culture valuable after a pipeline incident? *(Focuses on preventing the CLASS of failure system-wide rather than assigning individual blame, genuinely improving long-term reliability.)*
34. What's a runbook, in the on-call context? *(A documented guide for common failure types — what to check first, common root causes, safe remediation steps — reducing response time and inconsistency during incidents.)*
35. Why does a business-facing "data last refreshed" timestamp matter? *(Builds/maintains stakeholder trust by making data freshness visible, rather than users discovering staleness themselves and losing trust in the whole platform.)*

---

**Practice tip**: For architecture/comparison questions especially, always explain the underlying TRADEOFF (not just naming the "better" tool) — this consistently distinguishes strong, senior-level answers from surface-level tool name-dropping.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The steady flame of consistent effort outlasts the brief blaze of frantic urgency."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
