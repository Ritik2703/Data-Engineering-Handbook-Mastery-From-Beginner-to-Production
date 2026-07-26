# 1. Python Fundamentals for Data Engineers (Absolute Beginner Start)

## Why Python for Data Engineering?
Python is the "glue" language of data engineering — every cloud SDK (AWS boto3, Azure SDK, GCP client libraries), every orchestrator (Airflow, Dagster, Prefect), and most transformation tools (PySpark, pandas, dbt is SQL but its CLI is Python) are Python-based. Learn Python once, use it everywhere in this field.

## Variables & Basic Types
```python
customer_name = "Rahul Sharma"      # string
order_count = 42                     # integer
total_spent = 1499.50                # float
is_active = True                     # boolean
tags = None                          # represents "no value" — NOT the same as 0 or ""
```

## Core Data Structures (know these cold — used constantly in DE code)

### List — ordered, changeable collection
```python
cities = ["Bangalore", "Mumbai", "Delhi"]
cities.append("Pune")          # add an item
first_city = cities[0]         # "Bangalore" — indexing starts at 0
last_two = cities[-2:]         # slicing — last 2 items
for city in cities:
    print(city)
```
**Real use**: holding a batch of rows pulled from an API before writing to a database.

### Dictionary — key-value pairs (THE most-used structure in DE, mirrors JSON exactly)
```python
customer = {
    "customer_id": 101,
    "name": "Rahul Sharma",
    "city": "Bangalore"
}
print(customer["name"])              # access by key
print(customer.get("phone", "N/A"))  # safe access — returns "N/A" if key doesn't exist (no crash)
customer["email"] = "rahul@example.com"  # add/update a key
```
**Real use**: every API response is JSON, which Python's `requests` library automatically parses into nested dicts/lists — you'll manipulate this structure constantly.

### Tuple — ordered, unchangeable collection
```python
coordinates = (12.9716, 77.5946)  # (latitude, longitude) — immutable, used when data shouldn't change
```

### Set — unique, unordered collection
```python
unique_cities = set(["Bangalore", "Mumbai", "Bangalore"])  # {"Bangalore", "Mumbai"} — duplicate auto-removed
```
**Real use**: deduplicating a list of IDs pulled from multiple sources.

## Functions
```python
def calculate_discount(price: float, discount_pct: float) -> float:
    """Returns the discounted price. Type hints (: float, -> float) aren't enforced
    but massively help readability and catch bugs with tools like mypy."""
    return price * (1 - discount_pct / 100)

final_price = calculate_discount(1000, 20)  # 800.0
```

### Default arguments & *args / **kwargs
```python
def fetch_orders(customer_id, limit=100, **filters):
    """limit has a default; **filters captures any extra named arguments as a dict."""
    print(f"Fetching up to {limit} orders for customer {customer_id} with filters: {filters}")

fetch_orders(101)                                  # uses default limit=100
fetch_orders(101, limit=50, status="delivered")     # filters = {"status": "delivered"}
```
**Real use**: building flexible extraction functions where callers can pass arbitrary query parameters.

## Loops & Comprehensions
```python
# Standard loop
squared = []
for n in range(5):
    squared.append(n ** 2)

# List comprehension — the "Pythonic" way, used constantly in data transforms
squared = [n ** 2 for n in range(5)]

# Filtering with comprehension
active_customers = [c for c in customers if c["is_active"]]

# Dict comprehension — very common when reshaping API responses
id_to_name = {c["customer_id"]: c["name"] for c in customers}
```

## String Formatting (f-strings — the modern standard)
```python
customer_id = 101
name = "Rahul"
print(f"Customer {customer_id}: {name}")          # f-string, use this always
log_message = f"Processed {len(records)} records in {elapsed_time:.2f} seconds"
```

## Context Managers (`with`) — Critical for Resource Safety
```python
# File handling — the file automatically closes even if an error occurs inside the block
with open("data.csv", "r") as f:
    content = f.read()
# f is guaranteed closed here, no matter what happened above

# Database connections follow the exact same pattern (see 05-database-connectivity.md)
with psycopg2.connect(**db_config) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM orders;")
```
**Why this matters in production**: forgetting to close a database connection or file handle causes resource leaks that eventually crash long-running pipelines — `with` makes this class of bug structurally impossible.

## Generators — Memory-Efficient Processing (crucial for big files)
```python
def read_large_file_in_chunks(filepath, chunk_size=10000):
    """Yields chunks instead of loading the entire file into memory at once."""
    with open(filepath) as f:
        chunk = []
        for line in f:
            chunk.append(line)
            if len(chunk) == chunk_size:
                yield chunk
                chunk = []
        if chunk:
            yield chunk

for batch in read_large_file_in_chunks("huge_orders.csv"):
    process_batch(batch)   # process 10,000 rows at a time instead of loading millions into RAM
```
**Real scenario**: processing a 50GB CSV export on a machine with only 8GB RAM — generators make this possible.

## Decorators (used everywhere in production pipelines — retries, logging, timing)
```python
import time
import functools

def retry(max_attempts=3, delay_seconds=2):
    """A decorator factory — wraps any function with automatic retry logic."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    print(f"Attempt {attempt} failed: {e}")
                    time.sleep(delay_seconds)
            raise last_exception
        return wrapper
    return decorator

@retry(max_attempts=3, delay_seconds=5)
def call_flaky_api():
    # ... code that might fail due to network issues ...
    pass
```
**Real use**: this exact pattern is why the `tenacity` library exists (see `06-rest-api-integration.md`) — every production API call in this module uses retry logic like this.

## Classes / OOP Basics (used for building reusable pipeline components)
```python
class DataExtractor:
    """Base pattern for building reusable, testable extraction classes."""
    def __init__(self, source_name: str, api_key: str):
        self.source_name = source_name
        self.api_key = api_key

    def extract(self):
        raise NotImplementedError("Subclasses must implement extract()")

    def __repr__(self):
        return f"DataExtractor(source={self.source_name})"


class SalesforceExtractor(DataExtractor):
    """Inherits shared behavior, implements source-specific logic."""
    def extract(self):
        print(f"Extracting data from {self.source_name} using API key ending in ...{self.api_key[-4:]}")
        # actual API call logic here
        return {"records": []}

extractor = SalesforceExtractor(source_name="Salesforce", api_key="sk_live_abcd1234")
data = extractor.extract()
```
**Real use**: large data platforms define a common `BaseExtractor`/`BaseLoader` class, then each source system (Salesforce, SAP, internal APIs) implements its own subclass — keeps pipeline code consistent and testable.

## Modules & Imports
```python
# standard library
import os
import json
from datetime import datetime, timedelta

# third-party (after pip install)
import pandas as pd
import requests

# your own code, organized in files
from utils.db_helpers import get_connection
from extractors.api_extractor import fetch_orders
```

## Try It Yourself
1. Write a function that takes a list of order dicts and returns only orders above ₹1000.
2. Write a generator that reads a file and yields one line at a time, uppercased.
3. Write a decorator that logs how long a function took to run.
4. Build a simple `BaseExtractor` class with two subclasses for two different fake data sources.
