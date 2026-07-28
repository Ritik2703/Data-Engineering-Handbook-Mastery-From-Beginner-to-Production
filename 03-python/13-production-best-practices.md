# 13. Production Best Practices

## Project Structure (how real DE teams organize pipeline code)
```
my_pipeline/
├── config/
│   ├── base.yaml
│   └── prod.yaml
├── src/
│   ├── extractors/
│   │   ├── api_extractor.py
│   │   └── sharepoint_extractor.py
│   ├── transformers/
│   │   └── orders_transformer.py
│   ├── loaders/
│   │   └── warehouse_loader.py
│   ├── utils/
│   │   ├── logging_config.py
│   │   └── db_helpers.py
│   └── main.py
├── tests/
│   ├── test_extractors.py
│   └── test_transformers.py
├── requirements.txt
├── Dockerfile
└── README.md
```

## Configuration Management (never hardcode environment-specific values)
```python
# config/base.yaml
database:
  host: localhost
  port: 5432
  name: mydb

api:
  base_url: https://api.example.com
  timeout_seconds: 30
```
```python
import yaml
import os

def load_config(env="prod"):
    with open(f"config/{env}.yaml") as f:
        config = yaml.safe_load(f)
    # Environment variables override file config for secrets
    config["database"]["password"] = os.getenv("DB_PASSWORD")
    return config

config = load_config(os.getenv("PIPELINE_ENV", "prod"))
```

## Logging Configuration (structured, production-grade)
```python
# utils/logging_config.py
import logging
import sys

def setup_logging(log_level="INFO"):
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),          # for container/Airflow log capture
            logging.FileHandler("pipeline.log"),          # local file for debugging
        ],
    )

# In main.py
from utils.logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)
```

## Environment Variables & Secrets (`.env` for local dev, secrets manager for prod)
```python
# .env (gitignored, NEVER committed)
DB_PASSWORD=local_dev_password
API_KEY=local_dev_key
```
```python
import os
from dotenv import load_dotenv

load_dotenv()  # only loads .env locally; in prod, real env vars/secrets manager are used instead

db_password = os.getenv("DB_PASSWORD")
if not db_password:
    raise EnvironmentError("DB_PASSWORD environment variable is required but not set")
```

## Testing Pipeline Code (unit tests with pytest)
```python
# tests/test_transformers.py
import pandas as pd
import pytest
from src.transformers.orders_transformer import clean_orders

def test_clean_orders_removes_duplicates():
    df = pd.DataFrame({
        "order_id": [1, 1, 2],
        "amount": [100, 100, 200],
    })
    result = clean_orders(df)
    assert len(result) == 2

def test_clean_orders_raises_on_empty_input():
    empty_df = pd.DataFrame(columns=["order_id", "amount"])
    with pytest.raises(ValueError):
        clean_orders(empty_df, allow_empty=False)

def test_clean_orders_handles_null_amounts():
    df = pd.DataFrame({"order_id": [1, 2], "amount": [100, None]})
    result = clean_orders(df)
    assert result["amount"].isnull().sum() == 0
```
Run with: `pytest tests/ -v`

## Mocking External Calls in Tests (never hit real APIs/DBs in unit tests)
```python
from unittest.mock import patch, MagicMock

@patch("src.extractors.api_extractor.requests.get")
def test_fetch_orders_handles_api_error(mock_get):
    mock_get.side_effect = ConnectionError("Simulated network failure")
    with pytest.raises(ConnectionError):
        fetch_orders_from_api("https://fake-api.com/orders")

@patch("src.extractors.api_extractor.requests.get")
def test_fetch_orders_parses_response(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": [{"order_id": 1}]}
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    result = fetch_orders_from_api("https://fake-api.com/orders")
    assert len(result) == 1
```

## Packaging as a CLI Tool (production pipelines are often run this way)
```python
# main.py
import argparse
import logging

def main():
    parser = argparse.ArgumentParser(description="Run the orders ETL pipeline")
    parser.add_argument("--env", default="prod", choices=["dev", "staging", "prod"])
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--dry-run", action="store_true", help="Extract and validate only, skip loading")
    args = parser.parse_args()

    config = load_config(args.env)
    logger = logging.getLogger(__name__)

    try:
        logger.info(f"Starting pipeline for {args.start_date} (env={args.env}, dry_run={args.dry_run})")
        df = extract(config, args.start_date)
        df = transform(df)
        validate(df)
        if not args.dry_run:
            load(df, config)
        logger.info("Pipeline completed successfully")
    except Exception as e:
        logger.critical(f"Pipeline failed: {e}")
        raise SystemExit(1)  # non-zero exit code so Airflow/orchestrator marks the task as failed

if __name__ == "__main__":
    main()
```
Run: `python main.py --env prod --start-date 2026-07-25`

## Type Hints & Static Checking (catch bugs before runtime)
```python
from typing import Optional
import pandas as pd

def clean_orders(df: pd.DataFrame, allow_empty: bool = True) -> pd.DataFrame:
    if df.empty and not allow_empty:
        raise ValueError("Input DataFrame is empty")
    return df.drop_duplicates(subset=["order_id"])
```
Run `mypy src/` in CI to catch type mismatches before they become runtime bugs.

## Code Quality Tools (standard in CI/CD, see `10-devops/ci-cd/`)
```bash
black src/           # auto-formatter — consistent style, no debates in code review
flake8 src/           # linter — catches unused imports, style issues, some bugs
mypy src/             # static type checking
pytest tests/ -v --cov=src   # tests + coverage report
```

## Idempotent Script Design (safe to re-run — ties back to `01-fundamentals/02-core-concepts.md`)
```python
def load_to_warehouse(df, table_name, engine):
    """Uses a MERGE/UPSERT pattern instead of blind INSERT so re-running after
    a partial failure doesn't create duplicate rows."""
    from sqlalchemy import text
    with engine.begin() as conn:
        conn.execute(text(f"CREATE TEMP TABLE staging_{table_name} AS SELECT * FROM {table_name} WHERE 1=0"))
        df.to_sql(f"staging_{table_name}", conn, if_exists="append", index=False)
        conn.execute(text(f"""
            INSERT INTO {table_name}
            SELECT * FROM staging_{table_name}
            ON CONFLICT (order_id) DO UPDATE SET
                amount = EXCLUDED.amount, status = EXCLUDED.status;
        """))
```

## Try It Yourself
1. Restructure a single-file script into the `extractors/transformers/loaders` folder pattern above.
2. Write 3 pytest unit tests for a transformation function, including one that mocks an API call.
3. Convert a script with hardcoded config values into one using `argparse` + a YAML config file.

## Interview Traps
- "How do you test a pipeline that depends on an external API?" — mock the external call (`unittest.mock.patch`), never hit the real API in unit tests.
- "How do you make a pipeline re-runnable safely?" — idempotent design via `MERGE`/upsert, not blind `INSERT`.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"A peaceful mind sees the pattern in the chaos that an anxious mind misses entirely."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
