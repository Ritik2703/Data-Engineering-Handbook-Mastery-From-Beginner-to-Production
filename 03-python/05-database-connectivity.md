# 5. Database Connectivity — Every Major DB, Production-Grade

## The Production Pattern (applies to every DB below)
```python
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@contextmanager
def get_db_connection(config):
    """Reusable context manager pattern — guarantees connection cleanup."""
    conn = None
    try:
        conn = psycopg2.connect(**config)
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database operation failed, rolled back: {e}")
        raise
    finally:
        if conn:
            conn.close()

# Usage
with get_db_connection(db_config) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM orders WHERE order_date >= %s", ("2026-01-01",))
        rows = cur.fetchall()
```
This pattern — connect, commit-on-success, rollback-on-failure, always close — is the backbone of every production database interaction. Never omit the rollback/close handling, even in "quick scripts," because quick scripts become production pipelines faster than you'd expect.

## PostgreSQL
```python
import psycopg2
from psycopg2.extras import execute_values, RealDictCursor

conn = psycopg2.connect(
    host="localhost", port=5432, dbname="mydb", user="postgres", password="secret",
    connect_timeout=10
)

# Use RealDictCursor to get rows as dicts instead of tuples (much more readable)
with conn.cursor(cursor_factory=RealDictCursor) as cur:
    cur.execute("SELECT * FROM orders WHERE customer_id = %s", (101,))
    rows = cur.fetchall()   # [{"order_id": 1, "amount": 500, ...}, ...]

# Parameterized queries — ALWAYS use %s placeholders, NEVER f-strings for SQL (SQL injection risk)
# WRONG: cur.execute(f"SELECT * FROM orders WHERE customer_id = {customer_id}")
# RIGHT:
cur.execute("SELECT * FROM orders WHERE customer_id = %s", (customer_id,))

# Bulk insert (much faster than row-by-row for large loads)
data = [(1, "Rahul", 500.0), (2, "Priya", 750.0)]
execute_values(cur, "INSERT INTO orders (customer_id, name, amount) VALUES %s", data)
conn.commit()
```

## MySQL
```python
import pymysql

conn = pymysql.connect(
    host="localhost", port=3306, db="mydb", user="root", password="secret",
    cursorclass=pymysql.cursors.DictCursor
)
with conn.cursor() as cur:
    cur.execute("SELECT * FROM orders WHERE status = %s", ("delivered",))
    rows = cur.fetchall()
conn.close()
```

## SQL Server (legacy enterprise, via pyodbc)
```python
import pyodbc

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;DATABASE=mydb;UID=sa;PWD=secret;"
    "Connection Timeout=10;"
)
cur = conn.cursor()
cur.execute("SELECT * FROM orders WHERE order_date >= ?", "2026-01-01")  # ? placeholder for SQL Server
rows = cur.fetchall()
conn.close()
```

## Oracle (legacy enterprises — banking, insurance)
```python
import cx_Oracle

conn = cx_Oracle.connect(user="system", password="secret", dsn="localhost:1521/orclpdb")
cur = conn.cursor()
cur.execute("SELECT * FROM orders WHERE customer_id = :cid", cid=101)  # named placeholder
rows = cur.fetchall()
conn.close()
```

## MongoDB (NoSQL Document Store)
```python
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
    client.admin.command("ping")  # force a connection check early
    db = client["mydb"]
    orders_collection = db["orders"]

    # Query
    results = list(orders_collection.find({"status": "delivered"}).limit(100))

    # Insert
    orders_collection.insert_many([{"order_id": 1, "amount": 500}])

    # Update
    orders_collection.update_one({"order_id": 1}, {"$set": {"status": "shipped"}})

except (ConnectionFailure, ServerSelectionTimeoutError) as e:
    logger.error(f"Could not connect to MongoDB: {e}")
finally:
    client.close()
```

## Snowflake
```python
import snowflake.connector

conn = snowflake.connector.connect(
    user="my_user", password="secret",
    account="xy12345.ap-south-1",
    warehouse="COMPUTE_WH", database="ANALYTICS", schema="PUBLIC"
)
try:
    cur = conn.cursor()
    cur.execute("SELECT * FROM fact_sales LIMIT 10;")
    rows = cur.fetchall()

    # Bulk load via pandas (very common pattern)
    from snowflake.connector.pandas_tools import write_pandas
    success, num_chunks, num_rows, _ = write_pandas(conn, df, "ORDERS_STAGING")
finally:
    conn.close()
```

## Redshift (uses Postgres protocol)
```python
import psycopg2

conn = psycopg2.connect(
    host="my-cluster.xxxx.ap-south-1.redshift.amazonaws.com",
    port=5439, dbname="dev", user="awsuser", password="secret"
)
# Bulk loading in Redshift is almost always done via COPY from S3, not row-by-row inserts:
with conn.cursor() as cur:
    cur.execute("""
        COPY orders FROM 's3://my-bucket/staging/orders.parquet'
        IAM_ROLE 'arn:aws:iam::123456789:role/RedshiftLoadRole'
        FORMAT AS PARQUET;
    """)
conn.commit()
```

## SQLAlchemy — Universal Engine (recommended default for pandas integration)
```python
from sqlalchemy import create_engine, text
import pandas as pd

engine = create_engine("postgresql+psycopg2://postgres:secret@localhost:5432/mydb", pool_size=5, pool_pre_ping=True)

df = pd.read_sql("SELECT * FROM orders WHERE order_date >= '2026-01-01'", engine)
df.to_sql("orders_summary", engine, if_exists="replace", index=False, chunksize=1000)

# Raw parameterized query via SQLAlchemy
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM orders WHERE customer_id = :cid"), {"cid": 101})
    rows = result.fetchall()
```
`pool_pre_ping=True` checks connections are still alive before using them — prevents "server closed the connection unexpectedly" errors common with long-idle pooled connections.

## Connection Pooling (why it matters at scale)
Opening a new DB connection is expensive (network handshake, auth). Running 100 parallel Airflow tasks that each open/close their own connection can overwhelm a database. A connection pool keeps a fixed set of open connections and hands them out/returns them as needed.
```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://user:pass@host/db",
    pool_size=10,        # keep 10 connections open
    max_overflow=5,       # allow 5 extra under heavy load
    pool_recycle=1800,    # recycle connections every 30 min (avoids stale connection errors)
)
```

## Secure Credential Handling (never hardcode passwords)
```python
import os
from dotenv import load_dotenv

load_dotenv()  # loads variables from a local .env file (gitignored, never committed)

db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),  # NEVER: password="hardcoded123"
}
```
In production, credentials come from a secrets manager (AWS Secrets Manager, Azure Key Vault, GCP Secret Manager) — see the cloud SDK files for exact retrieval code.

## Try It Yourself
1. Write a context-manager-based function that connects to Postgres, runs a query, and guarantees the connection closes even if the query fails.
2. Convert a hardcoded-credential script to read from environment variables using `python-dotenv`.
3. Write a bulk-insert function using `execute_values` and compare its speed to a naive row-by-row loop on 10,000 rows.

## Interview Traps
- "How do you prevent SQL injection in Python?" — always parameterized queries (`%s`, `?`, `:name` placeholders), never string formatting/f-strings to build SQL.
- "Why use connection pooling?" — opening connections is expensive; pooling amortizes that cost across many requests/tasks, and prevents overwhelming the DB with too many simultaneous raw connections.
