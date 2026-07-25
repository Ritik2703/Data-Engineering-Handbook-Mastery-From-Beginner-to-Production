# 3. Data Modeling

## What is Data Modeling?
The process of designing how data is structured, related, and stored so it can be queried efficiently and understood clearly. Bad data models cause slow queries, confusing metrics, and analyst mistrust — it's one of the highest-leverage skills in DE.

## Entity-Relationship (ER) Modeling (OLTP world)
- **Entity** = a "thing" (Customer, Order, Product)
- **Attribute** = a property of the entity (customer_name, order_date)
- **Relationship** = how entities connect (one-to-many, many-to-many)

```
Customer (1) ────< (many) Order ────< (many) OrderLineItem >──── (1) Product
```

## Normalization (reduce redundancy in OLTP systems)
| Normal Form | Rule | Example fix |
|---|---|---|
| **1NF** | Atomic values, no repeating groups | Split "phone1, phone2" columns into a separate phone table |
| **2NF** | 1NF + no partial dependency on composite key | Move attributes depending on only part of a composite key to their own table |
| **3NF** | 2NF + no transitive dependency | Move `city -> state -> country` chain into a separate location table |

**Why normalize?** Avoids update anomalies (change a customer's city in one row, forget another → inconsistent data). OLTP systems normalize heavily because they optimize for fast, safe writes.

**Why denormalize for analytics?** Joins are expensive at query time across billions of rows. Warehouses intentionally denormalize (Star Schema) to optimize for fast reads.

## Dimensional Modeling (OLAP / warehouse world)

### Star Schema
```
              dim_date
                 │
dim_customer ── fact_sales ── dim_product
                 │
              dim_store
```
- **Fact table**: numeric, measurable events (sales amount, quantity) + foreign keys to dimensions. Usually very tall (billions of rows), narrow.
- **Dimension table**: descriptive context (customer name, product category). Shorter, wider.

### Snowflake Schema
Dimensions normalized further into sub-dimensions (e.g., `dim_product -> dim_category -> dim_department`). Saves storage, but more joins = slower queries. Star schema is generally preferred in modern columnar warehouses since storage is cheap and joins cost more than storage.

### Fact Table Types
- **Transaction fact table** — one row per event (most granular, e.g., one row per order line item)
- **Periodic snapshot** — one row per entity per time period (e.g., daily account balance snapshot)
- **Accumulating snapshot** — one row per process, updated as it moves through stages (e.g., order: placed_date, shipped_date, delivered_date all in one row, updated as each milestone happens)

## Slowly Changing Dimensions (SCD) — full breakdown

| Type | Behavior | History kept? | Example use case |
|---|---|---|---|
| **Type 0** | Never changes, immutable | N/A | Original signup date |
| **Type 1** | Overwrite old value | ❌ No | Fixing a typo in a name |
| **Type 2** | New row per change, with effective/end dates + current flag | ✅ Full history | Customer's address (need to know address AT time of order) |
| **Type 3** | Add a "previous value" column | ⚠️ Only last change | Tracking a single prior sales region |
| **Type 4** | Separate history table, current table stays small | ✅ Full history, better performance | High-change-frequency dimensions |
| **Type 6** | Hybrid of 1+2+3 | ✅ Full + easy current lookup | Enterprise-grade dimension design |

### SCD Type 2 example (conceptual table)
| customer_id | name | city | start_date | end_date | is_current |
|---|---|---|---|---|---|
| 101 | Rahul | Delhi | 2023-01-01 | 2025-06-30 | FALSE |
| 101 | Rahul | Bangalore | 2025-07-01 | NULL | TRUE |

A fact table joining on `customer_id` + `order_date BETWEEN start_date AND end_date` gets the **historically accurate** city at the time of each order.

## Data Vault Modeling
Built for agility, auditability, and handling many fast-changing source systems (common in large enterprises/banking):
- **Hub** — business key only (e.g., `hub_customer`: customer_id, load_date, source)
- **Link** — relationships between hubs (e.g., `link_customer_order`)
- **Satellite** — descriptive attributes + history (e.g., `sat_customer_details`: name, address, valid_from)

Pros: highly auditable, easy to add new sources without redesign. Cons: many tables, complex joins, needs a presentation/mart layer on top for BI usability.

## One Big Table (OBT) / Wide Table Pattern
Modern lakehouse pattern — pre-join everything (facts + all dimension attributes) into one wide denormalized table. Trades storage for simplicity: BI tools query one table, no joins needed. Common with dbt + cheap cloud storage/compute.

## Kimball vs Inmon (methodology-level choice)
| | Kimball (bottom-up) | Inmon (top-down) |
|---|---|---|
| Approach | Build dimensional data marts per business process first, conform dimensions across marts later | Build a normalized enterprise-wide warehouse first, then derive marts |
| Speed to value | Fast — ship one mart in weeks | Slower — need full enterprise model first |
| Consistency | Requires discipline to conform dimensions | Very consistent from day one |
| Popularity today | Dominant in most modern cloud DW projects | Common in large/regulated enterprises with existing top-down investment |

## Choosing a Modeling Approach
```
Fast-moving startup, need dashboards quickly     -> Kimball Star Schema
Large enterprise, many source systems, audit need -> Data Vault (with Kimball marts on top)
BI tool needs simplicity, storage is cheap         -> One Big Table
Need to preserve full history of changes           -> SCD Type 2 for that dimension
```

## Interview Traps
- Being asked to design a star schema for "an e-commerce company" — always clarify grain first ("one row per order? per order line item?") before designing the fact table.
- SCD Type 2 is the single most commonly asked modeling question — know the exact column pattern (`start_date`, `end_date`, `is_current`) cold.
