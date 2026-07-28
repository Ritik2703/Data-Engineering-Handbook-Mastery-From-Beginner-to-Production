# 6. Lakehouse Table Formats — Delta Lake, Apache Iceberg, Apache Hudi

## The Problem These Solve
Plain files sitting in S3/ADLS/GCS (even Parquet) have NO transactional guarantees — a failed write mid-job can leave a corrupt, partial dataset; there's no way to `UPDATE`/`DELETE` specific rows without rewriting entire files; and there's no built-in way to see "what did this table look like yesterday." Lakehouse table formats add a **transaction log layer on top of plain files**, bringing database-like reliability (ACID transactions, schema enforcement, time travel) directly to cheap object storage.

## Delta Lake (created by Databricks, 2019)
```python
# Writing a Delta table
df.write.format("delta").mode("overwrite").save("s3a://bucket/delta/orders/")

# The magic: a "_delta_log" folder is created alongside your Parquet files,
# containing JSON transaction log entries recording every change ever made

# Reading
df = spark.read.format("delta").load("s3a://bucket/delta/orders/")

# UPDATE/DELETE/MERGE directly on lake files — impossible with plain Parquet!
from delta.tables import DeltaTable
delta_table = DeltaTable.forPath(spark, "s3a://bucket/delta/orders/")
delta_table.update(condition="status = 'pending'", set={"status": "'expired'"})
delta_table.delete(condition="order_date < '2020-01-01'")

# MERGE (upsert) — the exact SCD Type 2 / incremental-load pattern from earlier modules
delta_table.alias("target").merge(
    source=updates_df.alias("source"),
    condition="target.order_id = source.order_id"
).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()

# Time travel — query the table as it existed at a previous point
df_yesterday = spark.read.format("delta").option("versionAsOf", 5).load("s3a://bucket/delta/orders/")
df_at_time = spark.read.format("delta").option("timestampAsOf", "2026-07-24").load("s3a://bucket/delta/orders/")
```
**Why time travel matters in production**: debugging "why does this number look wrong today" by comparing against exactly how the table looked before a specific bad job ran; regulatory/compliance requirements to reconstruct historical state; safely rolling back a bad write without needing a separate backup system.

## Apache Iceberg (created at Netflix, 2018 — open-sourced to solve their own petabyte-scale reliability problems)
```sql
-- Iceberg tables work across MULTIPLE query engines (Spark, Trino, Flink, Snowflake) —
-- its defining strength is being a truly OPEN, engine-agnostic standard
CREATE TABLE catalog.db.orders (
    order_id BIGINT, customer_id BIGINT, amount DECIMAL(10,2), order_date DATE
)
USING iceberg
PARTITIONED BY (days(order_date));   -- Iceberg supports "hidden partitioning" —
                                       -- you don't need to manually add a separate
                                       -- partition column, Iceberg derives it automatically

-- Time travel via SQL directly
SELECT * FROM catalog.db.orders FOR VERSION AS OF 12345;
SELECT * FROM catalog.db.orders FOR TIMESTAMP AS OF TIMESTAMP '2026-07-24 00:00:00';
```
**Why Netflix specifically needed this**: at their scale, Hive's traditional partition-based table tracking became a bottleneck (listing/tracking millions of partitions got slow and error-prone) — Iceberg tracks individual FILES in its metadata layer (not just partition directories), enabling much more efficient query planning and safe concurrent writes at massive scale.
**Real production significance in 2026**: Iceberg has become the closest thing to a genuinely vendor-neutral, multi-engine open standard — Snowflake, Databricks, AWS, and Google Cloud all now support reading/writing Iceberg tables, making it a increasingly common choice specifically to avoid vendor lock-in to any single processing engine.

## Apache Hudi (created at Uber, 2016 — solving their specific incremental-upsert problem)
```python
# Hudi's defining strength: highly optimized for frequent UPSERTS (Uber's trip records
# are constantly updated as a trip progresses through many status changes)
hudi_options = {
    "hoodie.table.name": "trips",
    "hoodie.datasource.write.recordkey.field": "trip_id",
    "hoodie.datasource.write.precombine.field": "updated_at",
    "hoodie.datasource.write.operation": "upsert",
}
df.write.format("hudi").options(**hudi_options).mode("append").save("s3a://bucket/hudi/trips/")
```
**Why Uber specifically needed this**: a ride's record changes status many times per trip (requested -> accepted -> in progress -> completed) — Hudi's storage layout (using indexing to efficiently locate exactly which files contain a given record's previous version) makes these frequent point-updates dramatically more efficient than naive "rewrite the whole partition" approaches other formats might require for the same workload.

## Comparing the Three — Real Decision Factors
| | Delta Lake | Iceberg | Hudi |
|---|---|---|---|
| Origin | Databricks | Netflix | Uber |
| Strongest at | Deep Databricks/Spark integration, mature tooling | Multi-engine openness, vendor neutrality | High-frequency upserts/incremental CDC ingestion |
| Best choice when | Already all-in on Databricks | Want to avoid vendor lock-in, use multiple engines | Ingesting from CDC sources with constant updates |

**Real 2026 trend**: the three formats have been converging in capability over time (each adding features the others pioneered), and multi-format-reading support is increasingly common in query engines — meaning the choice matters somewhat less than it did in 2020, though Iceberg's growing multi-vendor institutional support has made it an increasingly common "default" choice for genuinely new, engine-agnostic lakehouse builds.

## Interview Traps
- "Why can't you just UPDATE a row in a plain Parquet file in S3?" — Parquet files are immutable by design (efficient for bulk reads); modifying one row would require rewriting the ENTIRE file. Lakehouse formats solve this by tracking file-level changes in a transaction log, effectively rewriting only the affected files while presenting a consistent, versioned view.
- "Why did Netflix specifically need to create Iceberg rather than use Hive tables?" — Hive's partition-directory-based metadata tracking became a bottleneck at Netflix's file-count scale; Iceberg's file-level metadata tracking scales better and enables safer concurrent writes.
- Be ready to explain time travel's practical production value (debugging, compliance, safe rollback) beyond just "it's a cool feature."


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Peace of mind is the real productivity tool no dashboard can measure."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
