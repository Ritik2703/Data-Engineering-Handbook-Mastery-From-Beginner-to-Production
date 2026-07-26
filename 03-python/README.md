# 03 — Python for Data Engineers: Zero to Enterprise-Production

Written so someone who has **never written a line of Python** can work through this and come out able to build/debug real production data pipelines used at product companies — API pulls, cloud SDKs, database connections, file processing, data quality checks, all with proper error handling.

> 🗂️ Want everything in ONE file to reference quickly? See [`MASTER_LIBRARY_REFERENCE.py`](./MASTER_LIBRARY_REFERENCE.py) — every library, every use case, one place.

## 📖 Learning Path

| # | File | Level | Covers |
|---|---|---|---|
| 1 | [`01-python-fundamentals-for-de.md`](./01-python-fundamentals-for-de.md) | Beginner | Variables, data structures, functions, decorators, generators, context managers, OOP |
| 2 | [`02-error-handling.md`](./02-error-handling.md) | Beginner-Intermediate | try/except/else/finally, custom exceptions, retries, logging |
| 3 | [`03-file-handling-all-formats.md`](./03-file-handling-all-formats.md) | Intermediate | CSV, JSON, Excel, Parquet, XML, YAML, text, compressed files |
| 4 | [`04-pandas-for-data-engineers.md`](./04-pandas-for-data-engineers.md) | Intermediate | pandas for ETL: cleaning, merging, reshaping, performance |
| 5 | [`05-database-connectivity.md`](./05-database-connectivity.md) | Intermediate | Every major DB, connection pooling, bulk operations |
| 6 | [`06-rest-api-integration.md`](./06-rest-api-integration.md) | Intermediate-Advanced | requests, auth types, pagination, retry/backoff, rate limits |
| 7 | [`07-cloud-sdk-aws-boto3.md`](./07-cloud-sdk-aws-boto3.md) | Advanced | boto3: S3, Glue, Redshift, Lambda, Secrets Manager |
| 8 | [`08-cloud-sdk-azure.md`](./08-cloud-sdk-azure.md) | Advanced | Azure SDK: Blob/ADLS, Key Vault, Data Factory triggers |
| 9 | [`09-cloud-sdk-gcp.md`](./09-cloud-sdk-gcp.md) | Advanced | GCP SDK: BigQuery, Cloud Storage, Secret Manager |
| 10 | [`10-sharepoint-graph-api-integration.md`](./10-sharepoint-graph-api-integration.md) | Advanced | Microsoft Graph API: SharePoint, Teams, Outlook, Users |
| 11 | [`11-pyspark-for-python-developers.md`](./11-pyspark-for-python-developers.md) | Advanced | PySpark from a Python-dev lens |
| 12 | [`12-data-quality-validation.md`](./12-data-quality-validation.md) | Advanced | Great Expectations, Pandera, custom validation frameworks |
| 13 | [`13-production-best-practices.md`](./13-production-best-practices.md) | Production | Logging, config management, testing, packaging, CI/CD |
| — | [`case-studies/`](./case-studies/) | Production | Full real-company-style end-to-end scripts |
| — | [`MASTER_LIBRARY_REFERENCE.py`](./MASTER_LIBRARY_REFERENCE.py) | Reference | Every library + use case in one runnable-structure file |

## 🧠 Suggested Path (never coded before → production-ready)
```
Week 1: 01-fundamentals + 02-error-handling      (get comfortable with Python itself)
Week 2: 03-file-handling + 04-pandas             (data manipulation core skills)
Week 3: 05-database-connectivity + 06-rest-api   (moving data in/out of systems)
Week 4: 07/08/09-cloud SDKs (pick your target cloud first, others for breadth)
Week 5: 10-sharepoint-graph-api + 11-pyspark
Week 6: 12-data-quality + 13-production-best-practices
Ongoing: case-studies/ + MASTER_LIBRARY_REFERENCE.py for quick lookup
```

## 🎯 What makes this "enterprise-level"
Every code example in this module follows the same production discipline:
- **Explicit error handling** — no bare `except:`, specific exceptions caught, meaningful messages
- **Resource cleanup** — `finally` blocks / context managers (`with`) so connections/files always close
- **Retry logic** — network calls assume failure will happen and handle it gracefully
- **Logging, not print()** — production code logs with levels (INFO/WARNING/ERROR), not `print()` statements
- **Credentials never hardcoded** — environment variables / secrets managers, always
- **Real company scenario framing** — every concept tied to why a product company actually needs it
