# 4. Pandas for Data Engineers

## Why pandas (and its limits)
pandas is the default tool for in-memory tabular data manipulation in Python — cleaning, joining, reshaping. It's excellent for datasets that fit in RAM (up to a few GB typically); beyond that, reach for PySpark or Polars (see `11-pyspark-for-python-developers.md`).

## Reading & Inspecting Data
```python
import pandas as pd

df = pd.read_csv("orders.csv")

df.head()           # first 5 rows
df.info()           # column types, non-null counts — ALWAYS run this first on new data
df.describe()       # statistical summary of numeric columns
df.shape             # (rows, columns)
df.dtypes            # data type of each column
df.isnull().sum()   # count of nulls per column — critical first data-quality check
```

## Cleaning Data (the bulk of real DE work)
```python
# Drop duplicates
df = df.drop_duplicates(subset=["order_id"], keep="last")

# Handle missing values
df["status"] = df["status"].fillna("unknown")
df = df.dropna(subset=["customer_id"])   # drop rows missing a critical field

# Type conversion (very common — data arrives as strings from CSV/APIs)
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")  # invalid values become NaN, not a crash
df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

# String cleaning
df["city"] = df["city"].str.strip().str.title()   # "  bangalore " -> "Bangalore"
df["email"] = df["email"].str.lower()

# Renaming columns to a consistent convention
df = df.rename(columns={"OrderID": "order_id", "CustAmt": "amount"})
df.columns = df.columns.str.lower().str.replace(" ", "_")  # bulk-normalize all column names
```

## Filtering
```python
delivered = df[df["status"] == "delivered"]
high_value = df[(df["amount"] > 1000) & (df["status"] == "delivered")]
recent = df[df["order_date"] >= "2026-01-01"]
selected_cities = df[df["city"].isin(["Bangalore", "Mumbai", "Delhi"])]
```

## GroupBy & Aggregation (pandas equivalent of SQL's GROUP BY)
```python
revenue_by_city = df.groupby("city")["amount"].sum().reset_index()

summary = df.groupby("city").agg(
    total_revenue=("amount", "sum"),
    order_count=("order_id", "count"),
    avg_order_value=("amount", "mean")
).reset_index()
```

## Merging (pandas equivalent of SQL JOINs)
```python
customers = pd.read_csv("customers.csv")
orders = pd.read_csv("orders.csv")

# Inner join (default)
merged = orders.merge(customers, on="customer_id", how="inner")

# Left join
merged = orders.merge(customers, on="customer_id", how="left")

# Joining on differently-named columns
merged = orders.merge(customers, left_on="cust_id", right_on="customer_id", how="left")
```

## Reshaping — pivot / melt
```python
# Wide to long (melt) — common when normalizing a messy Excel export
long_df = wide_df.melt(id_vars=["product_id"], var_name="month", value_name="sales")

# Long to wide (pivot) — common for a business-facing report
wide_df = long_df.pivot(index="product_id", columns="month", values="sales")
```

## Window-Function-Style Operations in Pandas
```python
# Running total (equivalent to SQL SUM() OVER)
df = df.sort_values(["customer_id", "order_date"])
df["running_total"] = df.groupby("customer_id")["amount"].cumsum()

# Rank within group (equivalent to SQL RANK())
df["rank_within_customer"] = df.groupby("customer_id")["amount"].rank(ascending=False, method="dense")

# Row number equivalent — latest order per customer
df["rn"] = df.sort_values("order_date", ascending=False).groupby("customer_id").cumcount() + 1
latest_orders = df[df["rn"] == 1]

# Shift (equivalent to SQL LAG/LEAD)
df["prev_amount"] = df.groupby("customer_id")["amount"].shift(1)
df["mom_change"] = df["amount"] - df["prev_amount"]
```

## Applying Custom Logic
```python
# apply() — flexible but slower; use vectorized operations when possible
df["discount_tier"] = df["amount"].apply(lambda x: "high" if x > 1000 else "low")

# Vectorized equivalent (much faster on large data — prefer this)
df["discount_tier"] = pd.cut(df["amount"], bins=[0, 1000, float("inf")], labels=["low", "high"])

# np.where for simple conditional columns (faster than apply)
import numpy as np
df["is_high_value"] = np.where(df["amount"] > 1000, True, False)
```
> ⚠️ **Performance rule**: avoid `.apply()` with a Python function in a loop over millions of rows — it's often 10-100x slower than a vectorized pandas/numpy operation. Reach for `.apply()` only when there's no vectorized alternative.

## Writing Output
```python
df.to_csv("output.csv", index=False)
df.to_parquet("output.parquet", index=False)
df.to_sql("orders_summary", engine, if_exists="replace", index=False, chunksize=1000)
```

## Memory Optimization (important for large files)
```python
# Downcast numeric types to save memory
df["quantity"] = pd.to_numeric(df["quantity"], downcast="integer")
df["price"] = pd.to_numeric(df["price"], downcast="float")

# Use category dtype for low-cardinality repeated strings (huge memory saver)
df["status"] = df["status"].astype("category")

print(df.memory_usage(deep=True).sum() / 1024**2, "MB")  # check memory footprint
```

## Method Chaining (production-style readable pandas)
```python
result = (
    pd.read_csv("orders.csv")
    .drop_duplicates(subset=["order_id"])
    .assign(amount=lambda d: pd.to_numeric(d["amount"], errors="coerce"))
    .dropna(subset=["amount"])
    .query("amount > 0")
    .groupby("city", as_index=False)["amount"].sum()
    .sort_values("amount", ascending=False)
)
```
This chaining style (common in production ETL scripts and dbt-adjacent Python transforms) reads like a pipeline top-to-bottom, avoiding a pile of reassigned intermediate variables.

## Try It Yourself
1. Load a CSV, clean nulls, deduplicate on a key, and compute a running total per group.
2. Merge two DataFrames and identify rows present in one but not the other (anti-join).
3. Convert a wide monthly-columns DataFrame into a long/tidy format with `melt`.
4. Rewrite an `.apply()`-based transformation using a vectorized approach and compare readability.
