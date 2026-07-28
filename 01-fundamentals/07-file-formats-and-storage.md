# 7. File Formats & Storage

## Row-based vs Columnar Storage
```
Row-based (CSV, JSON, Avro):              Columnar (Parquet, ORC):
┌────┬──────┬────────┐                    ┌────┬────┬────┐
│ id │ name │ amount │                    │ id │ id │ id │  (all ids together)
├────┼──────┼────────┤                    ├────┼────┼────┤
│ 1  │ Amit │  500   │                    │name│name│name│  (all names together)
│ 2  │ Riya │  300   │                    ├────┼────┼────┤
└────┴──────┴────────┘                    │amt │amt │amt │  (all amounts together)
                                           └────┴────┴────┘
```
- **Row-based**: efficient when you need to read/write **entire records** (transactional systems, streaming events).
- **Columnar**: efficient when you need to read **specific columns** across many rows (analytics — `SELECT SUM(amount)` only touches the amount column, skips everything else). Also compresses much better (similar values stored together).

## File Format Comparison

| Format | Type | Schema | Compression | Splittable | Best For |
|---|---|---|---|---|---|
| **CSV** | Row | None (implicit) | Poor | Yes | Simple interchange, human-readable |
| **JSON** | Row | Self-describing, nested | Poor | Depends | APIs, semi-structured/nested data |
| **Avro** | Row | Schema embedded (schema evolution friendly) | Good | Yes | Streaming (Kafka), row-wise processing, schema evolution |
| **Parquet** | Columnar | Schema embedded | Excellent | Yes | Analytics, data lakes, Spark/warehouse standard |
| **ORC** | Columnar | Schema embedded | Excellent | Yes | Hive-heavy ecosystems, similar to Parquet |

**Practical rule**: land raw data in whatever format the source gives you (often JSON/CSV), convert to **Parquet** for the curated/analytics zone — this alone can cut query costs/time by 10x+ in BigQuery/Athena/Spark.

## Compression Codecs
| Codec | Speed | Compression Ratio | Splittable? |
|---|---|---|---|
| **Snappy** | Very fast | Moderate | Yes |
| **GZIP** | Slower | High | No (in most engines) |
| **ZSTD** | Fast, good ratio | High | Yes |
| **LZ4** | Fastest | Lower | Yes |

Parquet files default to Snappy in most engines — good balance of speed and size for analytics workloads. Avoid GZIP for large files you'll process in parallel (non-splittable means one worker must process the whole file).

## Data Lake Storage Layout (partitioning on disk)
```
s3://data-lake/curated/orders/
    year=2026/
        month=07/
            day=25/
                region=north/
                    part-00001.parquet
                    part-00002.parquet
                region=south/
                    part-00001.parquet
```
Partitioning by frequently-filtered columns (date, region) lets query engines (Athena, Spark, BigQuery external tables) skip entire folders instead of scanning everything — this is **partition pruning**.

## Small Files Problem
Having millions of tiny files (e.g., 1 file per streaming micro-batch) kills performance — too much metadata overhead, too many open/close operations. Fix: periodic **compaction** jobs that merge small files into larger ones (e.g., target 128MB-1GB per file).

## Lakehouse Table Formats (ACID on top of files)
| Format | Backed by | Key Feature |
|---|---|---|
| **Delta Lake** | Parquet + transaction log | ACID transactions, time travel, `MERGE` support, Databricks-native |
| **Apache Iceberg** | Parquet/ORC/Avro + metadata layer | Open standard, strong multi-engine support (Spark, Trino, Flink, Snowflake) |
| **Apache Hudi** | Parquet + timeline | Optimized for frequent upserts/CDC ingestion |

These solve the "data swamp" problem — plain files in S3 have no transactions (a failed write can leave partial/corrupt data); these formats add a transaction log so reads/writes are atomic and consistent, plus enable `MERGE`/`UPDATE`/`DELETE` directly on lake files (previously only possible in warehouses).

## Interview Traps
- "Why Parquet over CSV for analytics?" → columnar layout + predicate/column pruning + compression + schema embedded (no guessing types) + splittable for parallel processing.
- Know that GZIP is NOT splittable in most distributed engines — a common gotcha when someone picks it for huge files expecting parallel processing.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The wise engineer fixes the system, not just the symptom — just as the wise mind fixes the root, not the reaction."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
