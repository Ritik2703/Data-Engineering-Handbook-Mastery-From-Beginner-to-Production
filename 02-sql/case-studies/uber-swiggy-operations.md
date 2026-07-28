# Case Study: Uber-style Ride Analytics & Swiggy-style Food Delivery Analytics

## Schema (Uber-style)
```sql
drivers (driver_id, name, city, signup_date, vehicle_type)
riders  (rider_id, name, city, signup_date)
trips   (trip_id, driver_id, rider_id, city, trip_start_time, trip_end_time, fare, status)
-- status: completed, cancelled_by_rider, cancelled_by_driver
```

## Business Question 1: "Driver utilization — what % of a driver's online hours are spent on active trips?"
```sql
WITH driver_trip_time AS (
    SELECT
        driver_id,
        DATE(trip_start_time) AS trip_date,
        SUM(EXTRACT(EPOCH FROM (trip_end_time - trip_start_time)) / 3600.0) AS hours_on_trips
    FROM trips
    WHERE status = 'completed'
    GROUP BY driver_id, DATE(trip_start_time)
)
SELECT
    d.driver_id,
    dtt.trip_date,
    dtt.hours_on_trips,
    ROUND(100.0 * dtt.hours_on_trips / 8, 1) AS utilization_pct_assuming_8hr_shift
FROM driver_trip_time dtt
JOIN drivers d ON dtt.driver_id = d.driver_id;
```
**Concept used**: Date/time arithmetic + aggregation — a core "operations efficiency" metric at any ride-hailing/logistics company.

## Business Question 2: "Idle time between consecutive trips per driver (positioning/dispatch efficiency signal)"
```sql
SELECT
    driver_id, trip_id, trip_start_time,
    LAG(trip_end_time) OVER (PARTITION BY driver_id ORDER BY trip_start_time) AS prev_trip_end,
    trip_start_time - LAG(trip_end_time) OVER (PARTITION BY driver_id ORDER BY trip_start_time) AS idle_time
FROM trips
WHERE status = 'completed'
ORDER BY driver_id, trip_start_time;
```
**Concept used**: `LAG()` window function — the canonical "time since previous event" pattern.

## Business Question 3: "Cancellation rate by city — where is the marketplace experience worst?"
```sql
SELECT
    city,
    COUNT(*) AS total_requests,
    SUM(CASE WHEN status LIKE 'cancelled%' THEN 1 ELSE 0 END) AS cancelled,
    ROUND(100.0 * SUM(CASE WHEN status LIKE 'cancelled%' THEN 1 ELSE 0 END) / COUNT(*), 2) AS cancel_rate_pct
FROM trips
GROUP BY city
ORDER BY cancel_rate_pct DESC;
```

## Business Question 4: "Surge pricing candidate windows — hours with highest demand-to-driver ratio"
```sql
WITH hourly_demand AS (
    SELECT city, DATE_TRUNC('hour', trip_start_time) AS hour_bucket, COUNT(*) AS ride_requests
    FROM trips
    GROUP BY city, DATE_TRUNC('hour', trip_start_time)
),
hourly_supply AS (
    SELECT city, DATE_TRUNC('hour', trip_start_time) AS hour_bucket, COUNT(DISTINCT driver_id) AS active_drivers
    FROM trips
    WHERE status = 'completed'
    GROUP BY city, DATE_TRUNC('hour', trip_start_time)
)
SELECT
    d.city, d.hour_bucket, d.ride_requests, s.active_drivers,
    ROUND(1.0 * d.ride_requests / NULLIF(s.active_drivers, 0), 2) AS demand_supply_ratio
FROM hourly_demand d
JOIN hourly_supply s ON d.city = s.city AND d.hour_bucket = s.hour_bucket
ORDER BY demand_supply_ratio DESC
LIMIT 10;
```
**Concept used**: Two separate aggregations joined together — very common "combine two metrics computed at different grains" pattern; `NULLIF` prevents divide-by-zero errors.

---

## Schema (Swiggy/Zomato-style)
```sql
restaurants (restaurant_id, name, city, cuisine_type)
menu_items  (item_id, restaurant_id, item_name, price)
orders      (order_id, customer_id, restaurant_id, order_time, delivery_time, status, total_amount)
```

## Business Question 5: "Average delivery time by city — operations SLA monitoring"
```sql
SELECT
    r.city,
    AVG(EXTRACT(EPOCH FROM (o.delivery_time - o.order_time)) / 60.0) AS avg_delivery_minutes,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (o.delivery_time - o.order_time)) / 60.0) AS p95_delivery_minutes
FROM orders o
JOIN restaurants r ON o.restaurant_id = r.restaurant_id
WHERE o.status = 'delivered'
GROUP BY r.city
ORDER BY avg_delivery_minutes DESC;
```
**Concept used**: `PERCENTILE_CONT` — averages hide outliers; P95 delivery time is what operations teams actually monitor for SLA breaches (a few very late orders matter more than the average suggests).

## Business Question 6: "Restaurant order streak — restaurants with 7+ consecutive days of at least one order (engagement health check)"
```sql
WITH daily_orders AS (
    SELECT DISTINCT restaurant_id, DATE(order_time) AS order_date
    FROM orders
),
numbered AS (
    SELECT restaurant_id, order_date,
           order_date - (ROW_NUMBER() OVER (PARTITION BY restaurant_id ORDER BY order_date))::int AS grp
    FROM daily_orders
)
SELECT restaurant_id, MIN(order_date) AS streak_start, MAX(order_date) AS streak_end, COUNT(*) AS streak_days
FROM numbered
GROUP BY restaurant_id, grp
HAVING COUNT(*) >= 7
ORDER BY streak_days DESC;
```
**Concept used**: Gaps & islands pattern (see `06-advanced-sql-patterns.md`) — directly reused for a different business context, showing the pattern's versatility.

## Takeaway
Notice how the **same handful of SQL patterns** (window functions, conditional aggregation, gaps & islands, joining differently-grained aggregates) solve completely different business problems across completely different companies. Master the patterns once, apply them everywhere — that's the real skill product companies test for.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Stay rooted in your values even when the shortcuts look tempting."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
