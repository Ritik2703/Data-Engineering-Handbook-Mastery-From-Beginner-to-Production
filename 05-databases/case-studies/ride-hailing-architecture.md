# Case Study: Full Database Architecture for a Ride-Hailing App (Uber-style)

## Business Requirements
```
- Riders request rides, drivers accept them, trips are tracked in real time
- Millions of location updates per minute from active drivers
- Payment processing must be strongly consistent (no lost/duplicate charges)
- Trip history and analytics for both riders and the business
- Real-time ETA/matching needs very low latency
- Global operation across many cities/countries
```

## Architecture Decision: Multiple Databases, Each for Its Access Pattern
```
┌─────────────────────────────────────────────────────────────────────┐
│                         RIDE-HAILING PLATFORM                        │
├─────────────────────┬─────────────────────┬─────────────────────────┤
│  Core Transactional  │  Real-Time Location  │  Payments               │
│  (PostgreSQL)         │  (Redis + Cassandra) │  (PostgreSQL, isolated) │
├─────────────────────┼─────────────────────┼─────────────────────────┤
│  Trip Analytics       │  Search/Matching      │  Caching                │
│  (Snowflake/BigQuery) │  (Elasticsearch)       │  (Redis)                │
└─────────────────────┴─────────────────────┴─────────────────────────┘
```

### 1. Core Transactional Data — PostgreSQL
```sql
CREATE TABLE riders (rider_id SERIAL PRIMARY KEY, name VARCHAR(255), phone VARCHAR(20) UNIQUE, ...);
CREATE TABLE drivers (driver_id SERIAL PRIMARY KEY, name VARCHAR(255), vehicle_id INT, ...);
CREATE TABLE trips (
    trip_id BIGSERIAL PRIMARY KEY,
    rider_id INT REFERENCES riders(rider_id),
    driver_id INT REFERENCES drivers(driver_id),
    status VARCHAR(20) CHECK (status IN ('requested','accepted','in_progress','completed','cancelled')),
    requested_at TIMESTAMP,
    completed_at TIMESTAMP,
    fare NUMERIC(8,2)
);
```
**Why relational here**: trip lifecycle state (requested -> accepted -> in progress -> completed) and rider/driver core profile data benefit from strong ACID guarantees, foreign key integrity, and standard SQL querying for operational dashboards — a textbook OLTP use case.

### 2. Real-Time Driver Location — Redis (hot/current) + Cassandra (historical)
```python
# Redis: current location of every active driver, updated every few seconds
redis_client.geoadd("driver_locations", longitude, latitude, f"driver:{driver_id}")

# Find nearby available drivers for matching — Redis's GEO commands are purpose-built for this
nearby_drivers = redis_client.georadius("driver_locations", rider_lng, rider_lat, 5, unit="km")
```
```sql
-- Cassandra: historical location pings, write-heavy, queried by trip_id + time range
CREATE TABLE trip_location_history (
    trip_id BIGINT,
    ping_time TIMESTAMP,
    latitude DOUBLE,
    longitude DOUBLE,
    PRIMARY KEY (trip_id, ping_time)
) WITH CLUSTERING ORDER BY (ping_time ASC);
```
**Why NOT PostgreSQL for this**: driver location updates happen every few seconds for potentially millions of simultaneously active drivers — an enormous, constant write volume that would overwhelm a relational database's B-Tree indexing overhead (see file 8). Redis's in-memory speed handles the "where is everyone RIGHT NOW" query; Cassandra's LSM-tree write path handles the historical logging volume.

### 3. Payments — Isolated PostgreSQL Instance, Strong Consistency Required
Deliberately kept as a SEPARATE database instance (not shared with the core trip database) — payment processing needs the strongest possible consistency guarantees and its own dedicated capacity/security perimeter (PCI compliance considerations), and isolating it limits the "blast radius" if the busier trip-matching database has performance issues.
```sql
BEGIN;
INSERT INTO payment_transactions (trip_id, rider_id, amount, status) VALUES (...);
UPDATE rider_wallets SET balance = balance - amount WHERE rider_id = ...;
COMMIT;
```

### 4. Search/Matching — Elasticsearch (or similar)
Used for more complex matching logic beyond simple geo-radius (e.g., "drivers who accept pets AND have a 4.5+ rating AND are within 5km"), leveraging Elasticsearch's rich, fast filtering capabilities across many simultaneous conditions.

### 5. Analytics — Snowflake/BigQuery (fed by CDC/ETL from the operational databases)
```
PostgreSQL (trips) --CDC (Debezium)--> Kafka --> Spark/dbt transform --> Snowflake
Cassandra (location history) --batch export--> S3 --> Spark aggregation --> Snowflake
```
Business questions like "average trip duration by city this month" or "driver utilization trends" run against this analytical warehouse — never against the live operational databases, which must stay fast and available for actual ride-matching, not compete with heavy analytical queries.

## Why This Multi-Database Architecture (not "just use one database for everything")
```
Using ONLY PostgreSQL for everything would fail at:
  - Driver location updates (write volume far exceeds comfortable B-Tree/row-lock throughput)
  - Real-time nearest-driver geo-queries at scale (not PostgreSQL's core strength, though PostGIS helps)
  - Analytics (heavy aggregation queries would compete with live transactional traffic)

Using ONLY Cassandra/NoSQL for everything would fail at:
  - Payment transactions (needs strong ACID guarantees NoSQL doesn't naturally provide)
  - Complex relational queries needed for operational dashboards (rider/driver/trip joins)

The multi-database approach matches EACH workload's actual access pattern to the
database purpose-built for it — precisely the lesson from file 11's real company examples.
```

## Key Design Decisions & Justifications (interview-ready talking points)
1. **Why isolate payments in its own database instance?** — security/compliance perimeter isolation + protecting payment processing from being affected by trip-matching load spikes.
2. **Why Redis for current location instead of just querying PostgreSQL?** — sub-millisecond in-memory lookups needed for real-time matching; PostgreSQL's disk-backed B-Tree reads, even indexed, can't match this for a query pattern happening continuously for millions of active drivers.
3. **Why not put location HISTORY in Redis too?** — Redis is memory-based and expensive at scale for data you need to retain long-term; Cassandra's disk-based, horizontally-scalable write path is the right tool for high-volume historical data that's queried less frequently and less latency-sensitively.
4. **Why CDC instead of batch-querying the operational database for analytics?** — avoids adding query load to the live operational database, and captures every change in near-real-time rather than large periodic batch pulls (see `01-fundamentals/02-core-concepts.md` on CDC).

## Try It Yourself
Using this same multi-database reasoning, design a database architecture for:
1. A food delivery app (menu browsing, order placement, real-time delivery tracking, restaurant analytics).
2. A social media platform (user profiles, posts/feed, real-time notifications, friend graph, trending content analytics).

For each, identify which access pattern maps to which database TYPE (not necessarily specific product) from files 2-6 of this module, and justify why.
