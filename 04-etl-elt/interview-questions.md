# ETL/ELT Interview Questions — 30+ with Answers

## Conceptual — Beginner

**Q1. What's the difference between ETL and ELT?**
> ETL transforms data BEFORE loading into the warehouse (on a separate ETL server); ELT loads raw data first, then transforms using the warehouse's own compute (typically via SQL/dbt). ELT became dominant because cloud warehouse compute is cheap/elastic, unlike the expensive/limited compute of legacy on-prem warehouses that made ETL the necessary approach originally.

**Q2. Why do we need a staging area?**
> Decouples extraction from transformation — enables re-running transforms without re-extracting, provides an audit trail of exactly what the source sent, and isolates extraction failures from transformation bugs. See `02-etl-architecture-deep-dive.md`.

**Q3. What's the difference between a full load and an incremental load?**
> Full load reloads the entire dataset every run (simple, wasteful for large tables); incremental load only pulls new/changed records since the last run (efficient, but needs a reliable watermark, CDC, or incrementing key).

**Q4. What is CDC (Change Data Capture)?**
> Capturing row-level inserts/updates/deletes directly from a source database's transaction log, avoiding the need to poll/query the source repeatedly — more efficient and lower-impact on the source system than timestamp-based polling.

## Legacy Tools — SSIS / Informatica

**Q5. Explain SSIS Control Flow vs Data Flow.**
> Control Flow is the orchestration layer (what order tasks run in, branching on success/failure); Data Flow is the actual row-level data movement/transformation that happens inside a Data Flow Task. See `03-ssis-deep-dive.md`.

**Q6. How would you implement an SCD Type 2 dimension load in SSIS?**
> Lookup transformation against the current dimension rows, a Conditional Split to separate new/changed/unchanged rows, then an OLE DB Command (or separate destination) to close old rows (set end_date, is_current=false) and insert new versions for changed/new records.

**Q7. What's the difference between a Filter and a Router transformation in Informatica?**
> Filter has one condition, rows either pass or are dropped; Router supports multiple conditions producing multiple simultaneous output groups (like an if/elif chain), useful when rows need to be split into 3+ categories in one pass. See `04-informatica-deep-dive.md`.

**Q8. What's an Update Strategy transformation used for?**
> Explicitly tagging each row as INSERT/UPDATE/DELETE/REJECT within a single Informatica mapping — essential for mappings that need to both insert new records and update existing ones (like SCD2) in one pass.

**Q9. How do you handle a failed package/workflow partway through in SSIS/Informatica?**
> SSIS supports checkpoints to restart from point of failure; Informatica supports session/workflow recovery. Both also support redirecting bad rows to error/reject paths instead of failing the entire job, via Data Flow error outputs (SSIS) or session-level reject file configuration (Informatica).

**Q10. Why do enterprises still run SSIS/Informatica in 2026 instead of fully migrating?**
> Migration risk on audited/compliance-approved processes, regulatory recertification burden, specialist knowledge lock-in on old mappings, and the "if it's not broken, don't touch it" reality for stable, rarely-changed pipelines. See `09-legacy-vs-modern-migration.md`.

## Modern Tools — ADF / Glue / dbt

**Q11. What's the difference between a Linked Service and a Dataset in ADF?**
> Linked Service defines the connection itself (credentials, server, how to connect); Dataset points to a specific table/file/endpoint WITHIN that Linked Service.

**Q12. How would you build a single ADF pipeline that loads 100 different source tables without hand-building 100 pipelines?**
> A parameterized "generic" pipeline combined with a ForEach Activity iterating over rows from a metadata/control table (source name, target name, load type, watermark) — the metadata-driven pipeline pattern.

**Q13. What is the Glue Data Catalog and why does it matter?**
> A persistent, Hive-metastore-compatible metadata store for tables sitting in S3 — lets Athena, Redshift Spectrum, EMR, and Glue jobs all query the same data consistently without redefining schema in each tool separately.

**Q14. What's the difference between a Glue DynamicFrame and a Spark DataFrame?**
> DynamicFrame is Glue's own structure designed to gracefully handle semi-structured/schema-inconsistent data (won't crash on a column with mixed types across files); DataFrame is the standard Spark structure. Production Glue jobs typically convert DynamicFrame -> DataFrame for transformation logic, then back for the Glue-native write path.

**Q15. How does dbt know what order to build models in?**
> Automatically, from the dependency graph built by `{{ ref() }}` calls between models — no manual orchestration logic needed within dbt itself; it topologically sorts the DAG of model dependencies.

**Q16. How do you implement SCD Type 2 in dbt?**
> Snapshots — a built-in dbt feature that automatically tracks row-level history with `dbt_valid_from`/`dbt_valid_to` columns, based on a chosen strategy (timestamp or check-based).

**Q17. What's the difference between a dbt `view`, `table`, and `incremental` materialization?**
> `view`: no data duplication, always live, recomputed on every query. `table`: physically stored, faster to query, needs a full rebuild to refresh. `incremental`: only processes new/changed rows on subsequent runs (via a WHERE clause guarded by `is_incremental()`), avoiding a full rebuild for large fact tables.

**Q18. How would you handle rate limits or transient failures when extracting from an external API in a modern pipeline?**
> Exponential backoff retry logic (`tenacity` in Python, or built-in retry policies in ADF Copy Activity/Web Activity), respecting `Retry-After` headers, and alerting if retries are exhausted. See `03-python/06-rest-api-integration.md`.

## Design & Architecture

**Q19. How would you design an ETL pipeline to be idempotent (safe to re-run)?**
> Use MERGE/UPSERT operations keyed on a natural/business key instead of blind INSERTs, so re-running after a partial failure doesn't create duplicates. Parametrize by execution date so backfills are a config change, not a rewrite.

**Q20. Walk me through how you'd migrate a legacy SSIS-based data warehouse load to a modern cloud stack.**
> Prioritize by business value/change-frequency (migrate high-churn pipelines first via a "strangler pattern"), keep legacy and modern coexisting during transition, map each legacy concept to its modern equivalent, and be honest that some stable pipelines may never get migrated if the ROI/risk tradeoff doesn't justify it. See `09-legacy-vs-modern-migration.md`.

**Q21. What's a "metadata-driven" pipeline and why would you build one?**
> A generic, parameterized pipeline driven by a config/control table listing sources, targets, and load types — avoids hand-building near-identical pipelines for every single table, letting one pipeline definition scale to hundreds of tables.

**Q22. How do you decide between building a transformation in a Databricks Notebook vs an ADF Mapping Data Flow?**
> Mapping Data Flows suit simpler, visually-representable transforms and teams preferring low-code; Databricks Notebooks (full PySpark) suit complex business logic needing full code control, better testability (unit tests), and more flexibility — most production-grade complex logic favors the code-first Databricks approach.

**Q23. How would you detect and handle schema drift in a source system feeding your pipeline?**
> A schema validation step comparing incoming columns against an expected set before transformation runs (raising a warning for new columns, failing on missing expected columns) — see the schema drift check pattern in `03-python/12-data-quality-validation.md`. Modern lake table formats (Delta/Iceberg) also support schema evolution natively for additive changes.

## Rapid-Fire

24. What does "idempotent" mean in the context of a pipeline? *(Safe to re-run without duplicating/corrupting data.)*
25. What's a watermark in incremental loading? *(The timestamp/value marking how far a previous run successfully processed, used as the starting point for the next run.)*
26. Name three things that can go wrong in extraction and how you'd handle each. *(API timeout -> retry with backoff; schema change -> validation + alert; rate limiting -> respect Retry-After header.)*
27. What's the "strangler pattern" in the context of legacy migration? *(Gradually replacing pieces of a legacy system with new components, rather than a risky big-bang rewrite.)*
28. Why is `SELECT *` discouraged in production ETL/ELT SQL? *(Extra I/O/cost, breaks when source schema changes unexpectedly, prevents column-pruning optimizations.)*
29. What's the role of a Data Catalog (Glue Data Catalog / Unity Catalog / Purview) in a modern data platform? *(Centralized, consistent metadata so multiple tools/engines can query the same data without redefining schema separately in each.)*
30. How does dbt's `{{ ref() }}` differ from just hardcoding a table name in a SQL query? *(Enables automatic dependency graph resolution, environment-aware table name resolution across dev/prod, and lineage documentation — hardcoding loses all of this.)*

---

**Practice tip**: For any tool-specific question you don't know the exact syntax for, answer with the underlying CONCEPT first ("this needs a staging area + incremental watermark + SCD2 dimension handling") and then map it to whichever tool's terminology you DO know — interviewers consistently value this conceptual fluency over rote tool-specific memorization.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"A mind untroubled by ego solves problems that a proud mind cannot even see clearly."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
