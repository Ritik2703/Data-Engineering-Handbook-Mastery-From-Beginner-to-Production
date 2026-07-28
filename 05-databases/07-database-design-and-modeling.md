# 7. Database Design & Modeling — Full Walkthrough

## The Design Process (step by step, for a real system)

### Step 1: Gather Requirements — What Questions Must This Database Answer?
Before drawing a single table, list the actual questions the system needs to serve. For a **food delivery app** (Swiggy/Zomato-style):
```
- What restaurants are near this customer?
- What's in a customer's current order?
- What's a restaurant's order history and revenue?
- Which delivery partner is assigned to which order, and where are they now?
- How do we handle a customer having multiple saved addresses?
```

### Step 2: Identify Entities and Relationships (Conceptual Model)
```
Customer ---(places)---> Order ---(contains)---> OrderItem ---(references)---> MenuItem
   |                        |                                                      |
(has many)               (assigned to)                                       (belongs to)
   |                        v                                                      v
Address              DeliveryPartner                                        Restaurant
```

### Step 3: Define Attributes and Keys
```
Customer: customer_id (PK), name, phone, email, created_at
Address: address_id (PK), customer_id (FK), label, street, city, latitude, longitude
Restaurant: restaurant_id (PK), name, city, cuisine_type, rating
MenuItem: item_id (PK), restaurant_id (FK), name, price, is_available
Order: order_id (PK), customer_id (FK), restaurant_id (FK), delivery_partner_id (FK),
       delivery_address_id (FK), status, order_time, total_amount
OrderItem: order_item_id (PK), order_id (FK), item_id (FK), quantity, unit_price
DeliveryPartner: partner_id (PK), name, current_latitude, current_longitude, is_available
```

### Step 4: Normalize (for the OLTP/transactional side)
Check every table against 3NF (see file 2): does `Order` need to store `restaurant_name` directly? No — it's derivable via the `restaurant_id` foreign key, avoiding duplication and the update-anomaly risk of a restaurant renaming itself and now having stale names scattered across millions of historical orders.

### Step 5: Decide What to Denormalize (deliberately, for performance) — and Why
```
Example: storing unit_price directly on OrderItem (rather than always looking up MenuItem.price)
Why: menu prices CHANGE over time — if OrderItem only referenced item_id and looked up the
     current price, a historical order's total would incorrectly change when the restaurant
     updates today's menu prices. This is a deliberate, CORRECT denormalization — not laziness.
```
This illustrates an important design principle: **denormalization should be a deliberate choice justified by a specific real requirement** (here: historical price accuracy), not just "joins are annoying."

## Choosing Primary Keys — Natural vs Surrogate
```
Natural key: an attribute that's inherently unique in the real world (e.g., email, national ID)
Surrogate key: a database-generated artificial ID (auto-increment integer, UUID) with no business meaning

Real guidance: prefer SURROGATE keys for primary keys in almost all cases —
  natural keys can change (a customer's email changes), can have format inconsistencies
  across source systems, and using them as foreign keys everywhere makes future changes painful.
  Keep natural keys as a UNIQUE constraint instead, not the primary key.
```
```sql
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,       -- surrogate key, stable forever
    email VARCHAR(255) UNIQUE NOT NULL,   -- natural key, enforced unique but NOT the PK
    name VARCHAR(255)
);
```

## UUID vs Auto-Increment Integer — A Real, Common Production Debate
| | Auto-increment INT | UUID |
|---|---|---|
| Storage size | Smaller (4-8 bytes) | Larger (16 bytes) |
| Index performance | Better (sequential inserts are index-friendly) | Can cause index fragmentation (random inserts) unless using UUIDv7 (time-ordered) |
| Generated where | Must ask the database (round-trip needed before insert) | Can be generated in application code BEFORE hitting the database |
| Multi-region/distributed systems | Risk of collision across independently-scaling nodes | No collision risk — ideal for distributed/offline-first systems |
| Predictability/security | Sequential IDs leak information (competitor can guess "how many orders do you have") | Non-guessable |

**Real production guidance**: use auto-increment/sequential IDs for single-database systems where performance matters most; use UUIDs (ideally UUIDv7 or similar time-ordered variants) for distributed systems, systems needing to generate IDs offline/client-side before syncing, or where ID predictability is a security concern.

## Handling Many-to-Many Relationships — The Junction/Bridge Table Pattern
```sql
-- A student can enroll in many courses; a course can have many students
CREATE TABLE students (student_id SERIAL PRIMARY KEY, name VARCHAR(255));
CREATE TABLE courses (course_id SERIAL PRIMARY KEY, title VARCHAR(255));

-- Junction table resolves the many-to-many relationship
CREATE TABLE enrollments (
    student_id INT REFERENCES students(student_id),
    course_id INT REFERENCES courses(course_id),
    enrolled_date DATE,
    grade CHAR(2),
    PRIMARY KEY (student_id, course_id)   -- composite key prevents duplicate enrollment
);
```

## Designing for the Actual Query Patterns (a critical, often-skipped step)
A common beginner mistake: designing a "textbook-perfect" normalized schema without ever checking whether the MOST COMMON real queries will be fast against it.
```sql
-- If "show a customer's order history, most recent first" is a extremely common query,
-- make sure there's an index supporting exactly this access pattern:
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_time DESC);
```
Real-world database design isn't purely academic normalization — it's normalization **informed by** the actual, measured query patterns the application will run millions of times per day.

## OLTP Schema vs OLAP Schema — Same Business, Different Design Goals
The food delivery OLTP schema above (normalized, optimized for fast small transactional writes) would be **transformed** into a very different OLAP star schema for the data warehouse/analytics side:
```sql
-- Analytics warehouse: denormalized star schema (see 01-fundamentals/03-data-modeling.md)
fact_orders (order_id, customer_key, restaurant_key, delivery_partner_key, date_key,
             total_amount, delivery_time_minutes)
dim_customer (customer_key, name, city, signup_date, ...)
dim_restaurant (restaurant_key, name, cuisine_type, city, ...)
dim_date (date_key, day, month, quarter, year, is_weekend, ...)
```
This is exactly the OLTP-to-OLAP transformation pipeline that ETL/ELT tools (`04-etl-elt/`) exist to build and maintain — the OLTP schema serves the live application; the OLAP schema serves analytics/BI, and a Data Engineer builds the pipeline connecting the two.

## Try It Yourself
1. Design a normalized OLTP schema for a ride-hailing app (Uber-style) — identify entities, relationships, and keys.
2. For that same schema, identify one deliberate denormalization decision you'd make and justify it with a specific business reason.
3. Sketch the corresponding OLAP star schema you'd build for analytics on top of it.

## Interview Traps
- "Design a database for X" questions are extremely common — always start by asking/stating the KEY QUERIES the system must support before drawing any tables; jumping straight to schema design without this step is a common signal of weaker design instinct.
- Be ready to justify ANY denormalization decision with a specific business reason (like the historical price example above), not just "it's faster."
- "UUID or auto-increment for a new table's primary key?" — a nuanced answer depends on whether the system is distributed/multi-region, and whether ID predictability is a security concern — not a one-size-fits-all answer.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The one who works without attachment to praise builds the most enduring things."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
