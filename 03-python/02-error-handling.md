# 2. Error Handling — try/except/else/finally (Production-Critical)

## Why This Is Non-Negotiable in Data Engineering
Pipelines run unattended, often at 2 AM, pulling from flaky APIs and databases that occasionally time out. **Every** production DE script needs deliberate error handling — not to avoid errors, but to fail predictably, log clearly, and clean up resources properly when they happen.

## Basic try/except
```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Cannot divide by zero: {e}")
```

## The Full Structure: try / except / else / finally
```python
import logging

logger = logging.getLogger(__name__)

def load_customer_file(filepath):
    try:
        with open(filepath, "r") as f:
            data = f.read()
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        return None
    except PermissionError:
        logger.error(f"No permission to read: {filepath}")
        return None
    else:
        # runs ONLY if the try block succeeded with no exception
        logger.info(f"Successfully read {len(data)} characters from {filepath}")
        return data
    finally:
        # ALWAYS runs, whether an exception occurred or not — use for cleanup
        logger.info(f"Finished attempting to process {filepath}")
```
- **`else`**: code that should run only on success — keeps the "happy path" separate from error handling, improving readability.
- **`finally`**: guaranteed to run (cleanup, closing connections/files) — even if you `return` inside `try` or `except`.

## Catching Specific Exceptions (never use bare `except:`)
```python
# BAD — catches EVERYTHING including KeyboardInterrupt, SystemExit, typos in your own code
try:
    process_data()
except:
    print("something went wrong")

# GOOD — catch only what you expect, let unexpected errors surface (don't hide real bugs)
try:
    process_data()
except (ConnectionError, TimeoutError) as e:
    logger.warning(f"Network issue, will retry: {e}")
except ValueError as e:
    logger.error(f"Bad data encountered: {e}")
    raise   # re-raise if you can't actually recover — don't silently swallow real bugs
```
**Real production incident this prevents**: a bare `except:` silently swallowing a `KeyError` from a schema change in an upstream API, causing a pipeline to "succeed" while quietly loading zero rows — this exact bug has caused real multi-day data outages at companies that skip this practice.

## Custom Exceptions (used heavily in enterprise pipeline frameworks)
```python
class DataQualityError(Exception):
    """Raised when extracted data fails validation checks."""
    pass

class SourceUnavailableError(Exception):
    """Raised when a source system is unreachable after all retries."""
    def __init__(self, source_name, last_error):
        self.source_name = source_name
        self.last_error = last_error
        super().__init__(f"Source '{source_name}' unavailable: {last_error}")


def validate_row_count(df, min_expected=1):
    if len(df) < min_expected:
        raise DataQualityError(f"Expected at least {min_expected} rows, got {len(df)}")

try:
    validate_row_count(orders_df, min_expected=100)
except DataQualityError as e:
    logger.critical(f"DQ check failed, halting pipeline: {e}")
    raise  # stop the pipeline — don't let bad data flow downstream to BI dashboards
```
**Real use**: custom exceptions let an orchestrator (Airflow) distinguish between "retry this" (transient network error) vs "stop everything and page someone" (data quality failure) failure types.

## Retry Pattern for Flaky Network Calls (the #1 real-world need)
```python
import time
import requests

def fetch_with_retry(url, max_attempts=5, base_delay=2):
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()   # raises HTTPError for 4xx/5xx responses
            return response.json()
        except requests.exceptions.Timeout:
            logger.warning(f"Attempt {attempt}: request timed out")
        except requests.exceptions.ConnectionError:
            logger.warning(f"Attempt {attempt}: connection error")
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:   # rate limited — worth retrying
                logger.warning(f"Attempt {attempt}: rate limited, backing off")
            elif 500 <= response.status_code < 600:  # server error — worth retrying
                logger.warning(f"Attempt {attempt}: server error {response.status_code}")
            else:
                logger.error(f"Non-retryable HTTP error: {e}")
                raise   # 400/401/403/404 etc — retrying won't help, fail fast

        if attempt < max_attempts:
            sleep_time = base_delay * (2 ** (attempt - 1))  # exponential backoff: 2, 4, 8, 16...
            time.sleep(sleep_time)

    raise SourceUnavailableError("external_api", f"Failed after {max_attempts} attempts")
```
> In real production code, use the **`tenacity`** library instead of hand-rolling this (see `06-rest-api-integration.md`) — but understanding this pattern manually first is essential.

## Resource Cleanup with try/finally (when `with` isn't available)
```python
connection = None
try:
    connection = create_legacy_connection()  # some older library without context manager support
    connection.execute("SELECT * FROM orders")
except Exception as e:
    logger.error(f"Query failed: {e}")
    raise
finally:
    if connection is not None:
        connection.close()   # guaranteed to run, preventing connection leaks
```

## Logging vs print() — Production Standard
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

logger.debug("Detailed diagnostic info — only shown if level=DEBUG")
logger.info("Pipeline started successfully")
logger.warning("API responded slowly (3.2s) — within tolerance but worth watching")
logger.error("Failed to load 12 records — see details above")
logger.critical("Data quality check failed — halting pipeline entirely")
```
**Why not `print()`**: logging supports levels (filter noise in production, see everything in debugging), automatic timestamps, structured output that can be shipped to monitoring tools (CloudWatch, Datadog, ELK), and can be silenced/redirected without changing code. Production pipelines almost never use raw `print()`.

## Exception Chaining (preserving root cause context)
```python
try:
    parse_response(raw_data)
except ValueError as e:
    raise DataQualityError("Failed to parse API response") from e
    # "from e" preserves the original traceback — critical for debugging in production logs
```

## Try It Yourself
1. Write a function that reads a JSON file and raises a custom `ConfigError` if a required key is missing.
2. Write a retry decorator (reuse the pattern from `01-python-fundamentals-for-de.md`) that only retries on `ConnectionError`, not on `ValueError`.
3. Refactor a script using `print()` for status messages into one using the `logging` module with appropriate levels.

## Interview Traps
- "Why avoid bare `except:`?" — because it catches things you never intended to catch (including `SystemExit`/`KeyboardInterrupt`), silently hiding real bugs.
- "Difference between `except` and `except...else`?" — `else` only runs on success, keeping happy-path logic separate from error handling for readability.
- Be ready to explain exponential backoff and why it's better than fixed-delay retries (reduces load on an already-struggling system, avoids thundering-herd retries from many clients at once).
