# Case Study: Bank/Fintech-style Fraud Detection & Transaction Analytics

## Schema
```sql
accounts     (account_id, customer_id, account_type, opened_date, balance)
transactions (transaction_id, account_id, transaction_type, amount, transaction_time, merchant, location)
```

## Business Question 1: "Running account balance after each transaction (statement generation)"
```sql
SELECT
    account_id, transaction_id, transaction_time, amount,
    SUM(amount) OVER (PARTITION BY account_id ORDER BY transaction_time 
                       ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_balance
FROM transactions
ORDER BY account_id, transaction_time;
```
**Concept used**: `SUM() OVER` with explicit frame — the exact query that generates every bank statement's running balance column.

## Business Question 2: "Flag suspicious rapid-fire transactions — same account, 3+ transactions within 5 minutes (potential fraud/card testing pattern)"
```sql
WITH tx_with_prev AS (
    SELECT account_id, transaction_id, transaction_time,
           LAG(transaction_time, 2) OVER (PARTITION BY account_id ORDER BY transaction_time) AS time_2_txns_ago
    FROM transactions
)
SELECT account_id, transaction_id, transaction_time
FROM tx_with_prev
WHERE transaction_time - time_2_txns_ago <= INTERVAL '5 minutes';
```
**Concept used**: `LAG(column, 2)` — looking back 2 rows instead of 1, to detect "3 transactions within a tight window" — a real fraud-detection SQL pattern.

## Business Question 3: "Detect impossible travel — same customer, transactions in two distant locations within an implausibly short time"
```sql
WITH tx_with_prev_location AS (
    SELECT
        account_id, transaction_id, transaction_time, location,
        LAG(location) OVER (PARTITION BY account_id ORDER BY transaction_time) AS prev_location,
        LAG(transaction_time) OVER (PARTITION BY account_id ORDER BY transaction_time) AS prev_time
    FROM transactions
)
SELECT *
FROM tx_with_prev_location
WHERE location <> prev_location
  AND transaction_time - prev_time < INTERVAL '1 hour';
  -- In production: prev_location and location would be geo-coordinates,
  -- with a distance calculation (haversine formula) instead of simple inequality
```
**Concept used**: `LAG()` on both a value and a timestamp simultaneously — comparing consecutive events for both content and timing.

## Business Question 4: "Monthly spend by category, flag accounts with sudden month-over-month spend spikes (potential fraud or account takeover)"
```sql
WITH monthly_spend AS (
    SELECT account_id, DATE_TRUNC('month', transaction_time) AS month, SUM(amount) AS total_spend
    FROM transactions
    WHERE transaction_type = 'debit'
    GROUP BY account_id, DATE_TRUNC('month', transaction_time)
),
spend_with_prev AS (
    SELECT *,
           LAG(total_spend) OVER (PARTITION BY account_id ORDER BY month) AS prev_month_spend
    FROM monthly_spend
)
SELECT account_id, month, total_spend, prev_month_spend,
       ROUND(100.0 * (total_spend - prev_month_spend) / NULLIF(prev_month_spend, 0), 1) AS spend_change_pct
FROM spend_with_prev
WHERE prev_month_spend IS NOT NULL
  AND total_spend > prev_month_spend * 3;   -- flag if spend more than tripled month over month
```
**Concept used**: `LAG()` + percentage change + a business-defined threshold — a realistic simplified version of an anomaly detection rule engine's SQL layer.

## Business Question 5: "Reconcile transactions between our system and the payment gateway's records (data quality / financial audit)"
```sql
-- FULL OUTER JOIN reveals mismatches on either side
SELECT
    our.transaction_id AS our_tx_id,
    gateway.transaction_id AS gateway_tx_id,
    our.amount AS our_amount,
    gateway.amount AS gateway_amount
FROM our_transactions our
FULL OUTER JOIN gateway_transactions gateway
    ON our.transaction_id = gateway.transaction_id
WHERE our.transaction_id IS NULL          -- exists in gateway but not our system
   OR gateway.transaction_id IS NULL      -- exists in our system but not gateway
   OR our.amount <> gateway.amount;        -- exists in both but amounts don't match
```
**Concept used**: `FULL OUTER JOIN` — the standard reconciliation pattern for financial audits between two independent systems that should agree.

## Why Financial/Fintech SQL Is Its Own Category
Banking and fintech interviews lean heavily on:
- **Precision** — always `DECIMAL`/`NUMERIC`, never `FLOAT`, for money (see `01-sql-basics.md`)
- **Auditability** — reconciliation queries (`FULL OUTER JOIN`), immutable transaction logs, SCD Type 2 for account attribute history
- **Time-series pattern detection** — `LAG`/`LEAD` heavy, since fraud and anomaly detection is fundamentally about comparing an event to what came before it
- **Idempotency** — a transaction pipeline must NEVER double-process a payment on retry (ties back to `01-fundamentals/02-core-concepts.md`)
