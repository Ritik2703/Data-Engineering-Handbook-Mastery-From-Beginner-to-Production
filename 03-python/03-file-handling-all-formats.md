# 3. File Handling — Every Format a Data Engineer Encounters

## CSV (most common interchange format)
```python
import csv

# Reading
with open("orders.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)   # each row becomes a dict using the header row as keys
    for row in reader:
        print(row["order_id"], row["amount"])

# Writing
with open("output.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["order_id", "amount", "status"])
    writer.writeheader()
    writer.writerow({"order_id": 1001, "amount": 599.0, "status": "delivered"})
```
> ⚠️ Always pass `newline=""` when opening CSV files in Python — otherwise Windows-style line endings can cause blank rows to appear.

### Pandas (the practical default for CSV in real DE work)
```python
import pandas as pd

df = pd.read_csv("orders.csv", encoding="utf-8", dtype={"customer_id": str})
df.to_csv("output.csv", index=False)

# Handling large files that don't fit in memory — read in chunks
for chunk in pd.read_csv("huge_file.csv", chunksize=100_000):
    process(chunk)
```

## JSON (APIs, semi-structured data, config files)
```python
import json

# Reading a JSON file
with open("config.json", "r") as f:
    config = json.load(f)

# Reading JSON from a string (e.g., an API response body)
data = json.loads('{"customer_id": 101, "name": "Rahul"}')

# Writing JSON
with open("output.json", "w") as f:
    json.dump({"status": "success", "rows_loaded": 5000}, f, indent=2)

# JSON Lines (JSONL) — one JSON object per line, common for large event logs/streaming exports
with open("events.jsonl", "r") as f:
    for line in f:
        event = json.loads(line)
        process_event(event)
```
**Real scenario**: Kafka/event pipeline exports are almost always JSONL — one event per line — because it's streamable (you don't need to load the whole file to start processing).

## Excel (business teams love sending data this way)
```python
import pandas as pd

# Reading — specify sheet_name if the workbook has multiple sheets
df = pd.read_excel("sales_report.xlsx", sheet_name="Q3_Data", engine="openpyxl")

# Reading ALL sheets into a dict of DataFrames
all_sheets = pd.read_excel("sales_report.xlsx", sheet_name=None)
for sheet_name, sheet_df in all_sheets.items():
    print(sheet_name, sheet_df.shape)

# Writing with multiple sheets and formatting (openpyxl for fine control)
with pd.ExcelWriter("output.xlsx", engine="openpyxl") as writer:
    summary_df.to_excel(writer, sheet_name="Summary", index=False)
    detail_df.to_excel(writer, sheet_name="Detail", index=False)
```
**Real scenario**: Finance sends a monthly budget file as `.xlsx` with 5 tabs — a common recurring ETL source at almost every company, however "modern" the rest of the stack is.

## Parquet (the analytics-standard columnar format)
```python
import pandas as pd

df = pd.read_parquet("orders.parquet", engine="pyarrow")
df.to_parquet("output.parquet", engine="pyarrow", compression="snappy", index=False)

# Reading only specific columns (huge performance win — columnar pruning)
df = pd.read_parquet("orders.parquet", columns=["order_id", "amount"])

# Reading a partitioned dataset directly (common data lake layout)
df = pd.read_parquet("s3://my-bucket/curated/orders/", columns=["order_id", "amount"])
```
See `01-fundamentals/07-file-formats-and-storage.md` for why Parquet is preferred for analytics.

## XML (legacy enterprise systems, SOAP APIs, some government/finance data feeds)
```python
import xml.etree.ElementTree as ET

tree = ET.parse("orders.xml")
root = tree.getroot()

for order in root.findall("order"):
    order_id = order.find("id").text
    amount = float(order.find("amount").text)
    print(order_id, amount)

# For very large/complex XML, use lxml (faster, more features) or xmltodict for JSON-like access
import xmltodict
with open("orders.xml") as f:
    data = xmltodict.parse(f.read())
```
**Real scenario**: Many legacy enterprise systems (SAP, older banking platforms, government data feeds) still export XML — expect this in enterprise DE roles even in 2026.

## YAML (config files — Airflow, dbt, Kubernetes all use this)
```python
import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)   # ALWAYS use safe_load, never load() (security risk — arbitrary code execution)

print(config["database"]["host"])

with open("output.yaml", "w") as f:
    yaml.dump({"pipeline": "orders_etl", "schedule": "0 2 * * *"}, f)
```

## Compressed Files (gzip, zip — common for large exports/archives)
```python
import gzip
import zipfile
import pandas as pd

# Reading a gzip-compressed CSV directly (pandas handles this transparently)
df = pd.read_csv("orders.csv.gz", compression="gzip")

# Reading a specific file from within a zip archive
with zipfile.ZipFile("export.zip") as z:
    with z.open("orders.csv") as f:
        df = pd.read_csv(f)

# Writing gzip-compressed output
df.to_csv("output.csv.gz", compression="gzip", index=False)
```

## Fixed-Width Files (legacy mainframe exports — still real in banking/insurance)
```python
import pandas as pd

# colspecs defines the character position ranges for each field
colspecs = [(0, 10), (10, 30), (30, 40)]  # e.g., (customer_id, name, city)
df = pd.read_fwf("legacy_export.txt", colspecs=colspecs, names=["customer_id", "name", "city"])
```
**Real scenario**: A bank's core mainframe system exports nightly customer data as fixed-width text — extremely common in enterprise DE work that touches legacy systems.

## Detecting Encoding Issues (a real, recurring production headache)
```python
import chardet

with open("mystery_file.csv", "rb") as f:
    raw_data = f.read(10000)
    result = chardet.detect(raw_data)
    print(result)  # {'encoding': 'ISO-8859-1', 'confidence': 0.73}

df = pd.read_csv("mystery_file.csv", encoding=result["encoding"])
```
**Real scenario**: A vendor sends a file with unexpected special characters (names with accents, currency symbols) causing a `UnicodeDecodeError` — this is one of the most common "why did the pipeline fail overnight" incidents in real DE jobs.

## File Handling Cheat Sheet — Library Choice
| Format | Library | Notes |
|---|---|---|
| CSV | `csv` (stdlib) or `pandas` | pandas for anything beyond trivial scripts |
| JSON | `json` (stdlib) | Built-in, no install needed |
| JSONL | `json` + line iteration | One `json.loads()` per line |
| Excel | `pandas` + `openpyxl` | `openpyxl` for formatting/writing control |
| Parquet | `pandas` + `pyarrow` | Standard for lake/warehouse interchange |
| XML | `xml.etree.ElementTree` or `xmltodict` | `xmltodict` for JSON-like ease of use |
| YAML | `pyyaml` | Always `safe_load`, never `load()` |
| Fixed-width | `pandas.read_fwf` | Legacy mainframe/enterprise exports |

## Try It Yourself
1. Read a CSV in chunks and count total rows without loading the whole file into memory.
2. Read an Excel file with 3 sheets and combine them into one DataFrame with a `source_sheet` column.
3. Convert a JSON Lines event log into a Parquet file.
4. Handle a `UnicodeDecodeError` gracefully by detecting encoding first.
