# Case Study: Netflix/Spotify-style Content & Streaming Analytics

## Schema
```sql
users        (user_id, name, country, signup_date, subscription_plan)
content      (content_id, title, genre, content_type, release_date)  -- content_type: movie, series, song, podcast
watch_history (watch_id, user_id, content_id, watch_date, watch_duration_minutes, content_total_minutes)
```

## Business Question 1: "Content engagement score — % of content actually watched, per genre"
```sql
SELECT
    c.genre,
    COUNT(*) AS total_views,
    AVG(1.0 * w.watch_duration_minutes / c.content_total_minutes) AS avg_completion_rate
FROM watch_history w
JOIN content c ON w.content_id = c.content_id
GROUP BY c.genre
ORDER BY avg_completion_rate DESC;
```
**Concept used**: Row-level calculated ratio inside an aggregate — a classic "engagement quality" metric more meaningful than raw view counts.

## Business Question 2: "Monthly retention cohort — of users who signed up in a given month, what % watched something in each following month?"
```sql
WITH signup_cohort AS (
    SELECT user_id, DATE_TRUNC('month', signup_date) AS cohort_month
    FROM users
),
monthly_activity AS (
    SELECT DISTINCT user_id, DATE_TRUNC('month', watch_date) AS activity_month
    FROM watch_history
),
cohort_activity AS (
    SELECT
        sc.cohort_month,
        ma.activity_month,
        COUNT(DISTINCT ma.user_id) AS active_users
    FROM signup_cohort sc
    JOIN monthly_activity ma ON sc.user_id = ma.user_id
    GROUP BY sc.cohort_month, ma.activity_month
),
cohort_size AS (
    SELECT cohort_month, COUNT(*) AS total_users
    FROM signup_cohort
    GROUP BY cohort_month
)
SELECT
    ca.cohort_month,
    ca.activity_month,
    ca.active_users,
    cs.total_users,
    ROUND(100.0 * ca.active_users / cs.total_users, 1) AS retention_pct
FROM cohort_activity ca
JOIN cohort_size cs ON ca.cohort_month = cs.cohort_month
ORDER BY ca.cohort_month, ca.activity_month;
```
**Concept used**: Cohort analysis — the single most-asked "growth/product analytics" SQL question at subscription-based companies.

## Business Question 3: "Top 3 trending songs/shows per genre this week (leaderboard)"
```sql
WITH weekly_views AS (
    SELECT c.genre, c.content_id, c.title, COUNT(*) AS view_count
    FROM watch_history w
    JOIN content c ON w.content_id = c.content_id
    WHERE w.watch_date >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY c.genre, c.content_id, c.title
),
ranked AS (
    SELECT *, DENSE_RANK() OVER (PARTITION BY genre ORDER BY view_count DESC) AS rnk
    FROM weekly_views
)
SELECT genre, title, view_count
FROM ranked
WHERE rnk <= 3
ORDER BY genre, rnk;
```
**Concept used**: `DENSE_RANK()` partitioned per genre — reused from `05-window-functions.md`, applied to a "top-N per group" leaderboard, one of the most common production reporting needs.

## Business Question 4: "Binge-watching sessionization — group a user's watch events into sessions (30-min gap = new session)"
```sql
WITH events_with_gap AS (
    SELECT user_id, content_id, watch_date,
           LAG(watch_date) OVER (PARTITION BY user_id ORDER BY watch_date) AS prev_watch_time
    FROM watch_history
),
session_flags AS (
    SELECT *,
           CASE WHEN prev_watch_time IS NULL 
                     OR watch_date - prev_watch_time > INTERVAL '30 minutes'
                THEN 1 ELSE 0 END AS is_new_session
    FROM events_with_gap
),
sessions AS (
    SELECT *, SUM(is_new_session) OVER (PARTITION BY user_id ORDER BY watch_date) AS session_id
    FROM session_flags
)
SELECT user_id, session_id, COUNT(*) AS items_watched_in_session, MIN(watch_date) AS session_start, MAX(watch_date) AS session_end
FROM sessions
GROUP BY user_id, session_id
HAVING COUNT(*) >= 3   -- 3+ items in one sitting = a "binge session"
ORDER BY items_watched_in_session DESC;
```
**Concept used**: Sessionization pattern (reused directly from `06-advanced-sql-patterns.md`) — this exact query structure powers "binge-watching" features/insights at Netflix-scale companies.

## Business Question 5: "Recommend content — users who watched X also watched Y (collaborative filtering seed query)"
```sql
SELECT
    w1.content_id AS watched_content,
    w2.content_id AS also_watched,
    COUNT(DISTINCT w1.user_id) AS co_watch_count
FROM watch_history w1
JOIN watch_history w2 
    ON w1.user_id = w2.user_id 
    AND w1.content_id < w2.content_id
GROUP BY w1.content_id, w2.content_id
HAVING COUNT(DISTINCT w1.user_id) > 20
ORDER BY co_watch_count DESC
LIMIT 20;
```
**Concept used**: Same self-join "bought together" pattern from the Amazon case study, applied here as the SQL-level seed for a recommendation engine — real production ML systems often start with exactly this kind of SQL co-occurrence query before layering a proper model on top.

## Takeaway
Streaming companies live and die by **engagement and retention metrics** — cohort analysis, sessionization, and leaderboard/ranking queries are asked constantly in interviews for these companies specifically because they map directly to real dashboards their data teams maintain daily.
