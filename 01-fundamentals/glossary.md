# Glossary — A to Z

**ACID** — Atomicity, Consistency, Isolation, Durability; transactional guarantees in databases.
**Airflow** — Open-source workflow orchestration tool using Python-defined DAGs.
**Batch Processing** — Processing data in scheduled chunks rather than continuously.
**Bronze/Silver/Gold** — Medallion architecture layers: raw, cleaned, business-ready data.
**CAP Theorem** — Distributed systems can guarantee only 2 of Consistency, Availability, Partition Tolerance.
**CDC (Change Data Capture)** — Capturing row-level changes from a source DB's transaction log.
**Clustering (warehouse)** — Sorting data within partitions by additional columns for query pruning.
**Columnar Storage** — Storing data column-by-column instead of row-by-row; optimized for analytics.
**Data Lake** — Storage repository holding raw data in native format at scale (S3/ADLS/GCS).
**Data Mart** — A subset of a data warehouse focused on a specific business area.
**Data Vault** — Modeling methodology using Hubs, Links, Satellites for auditable, agile warehousing.
**Data Warehouse** — Centralized repository of structured, integrated data for analytics.
**DAG (Directed Acyclic Graph)** — A dependency graph with no cycles; how Airflow/dbt represent task order.
**dbt** — Data Build Tool; SQL-based transformation framework with testing/docs/version control.
**ELT** — Extract, Load, Transform; transform happens inside the warehouse after loading.
**ETL** — Extract, Transform, Load; transform happens before loading into the warehouse.
**Fact Table** — Central table in a star schema holding measurable, numeric business events.
**Idempotency** — Property where re-running an operation produces the same result without side effects.
**Kappa Architecture** — Streaming-only architecture; reprocessing via replaying the event log.
**Lakehouse** — Combines data lake storage with warehouse-like ACID transactions (Delta/Iceberg/Hudi).
**Lambda Architecture** — Separate batch and speed layers merged at a serving layer.
**MPP (Massively Parallel Processing)** — Distributing query execution across many nodes in parallel.
**Normalization** — Organizing relational data to reduce redundancy (1NF, 2NF, 3NF).
**OLAP** — Online Analytical Processing; optimized for complex read/aggregation queries.
**OLTP** — Online Transaction Processing; optimized for fast, frequent read/write transactions.
**Partitioning** — Splitting a table/dataset physically by a column (commonly date) for query pruning.
**Parquet** — Columnar file format optimized for analytics, widely used in data lakes.
**Replication** — Copying data across multiple nodes for fault tolerance/availability.
**SCD (Slowly Changing Dimension)** — Techniques for handling changes to dimension attributes over time.
**Schema-on-Read** — Schema applied at query time (data lakes); flexible but less strict.
**Schema-on-Write** — Schema enforced at write time (RDBMS/warehouses); strict but safer.
**Sharding** — Horizontally splitting data across multiple database servers by a key.
**Shuffle** — Movement of data across nodes during distributed operations like joins/group-bys.
**Snowflake Schema** — Star schema with dimension tables further normalized into sub-dimensions.
**Spark** — Distributed in-memory processing engine; modern standard for big data transformation.
**Star Schema** — Fact table surrounded by denormalized dimension tables; standard dimensional model.
**Streaming** — Processing data continuously as events arrive, rather than in scheduled batches.
**Watermark (streaming)** — Threshold defining how late an event can arrive and still be processed.
