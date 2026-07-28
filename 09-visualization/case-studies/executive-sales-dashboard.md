# Case Study: Designing an Executive Sales Dashboard (Full Walkthrough)

## Business Request (as originally stated by a stakeholder — deliberately vague, realistic)
> "We need a dashboard showing our sales performance."

## Step 1: Clarify the ACTUAL Questions (never start building from a vague request)
```
Follow-up questions asked:
- WHO will look at this — executives, regional managers, or analysts?
- WHAT decision will they make FROM this dashboard?
- HOW OFTEN will they check it (daily glance vs deep monthly review)?

Answers gathered:
- Audience: Regional VP + 8 Regional Managers
- Decision: "Which regions/stores need my attention THIS WEEK?"
- Frequency: Quick daily glance, deeper look every Monday morning
```
This directly applies the design principle from file 7 — starting from the ACTUAL question, not the vague initial request.

## Step 2: Design the Data Model (tying back to module 05's design principles)
```sql
-- Star schema underlying this dashboard (see 01-fundamentals/03-data-modeling.md)
fact_daily_sales (date_key, store_key, region_key, revenue, transaction_count, returns_amount)
dim_store (store_key, store_name, region, store_type, opened_date)
dim_region (region_key, region_name, regional_manager)
dim_date (date_key, date, day_of_week, is_weekend, week_number, month, quarter, year)
```
A proper Date dimension table is included deliberately — required for DAX/Tableau time intelligence functions (WoW, MoM comparisons) to work correctly (file 5's warning about needing a marked Date table).

## Step 3: Choose the Right Chart for Each Question

### "How are we doing overall, right now?" — KPI Cards at the Top
```
Big, simple numbers: This Week's Revenue | vs Last Week (%) | vs Same Week Last Year (%)
Color-coded: green if above target/prior period, red if below — following
             file 7's deliberate, meaningful color usage principle
```

### "Which regions need attention?" — A Ranked Bar Chart, Not a Map
```
Decision made: a HORIZONTAL BAR CHART ranking regions by "% vs target,"
sorted worst-to-best, was chosen INSTEAD of a geographic map — because
the actual business question is "WHICH regions are underperforming,
ranked," and a bar chart answers that FASTER and more precisely than a
map (which is better suited to genuinely geographic/spatial questions,
not ranking) — a direct application of file 7's "choose chart type
based on the QUESTION, not visual appeal" principle.
```

### "Why is a specific region underperforming?" — Drill-Down Detail (Analyst Layer)
```
Clicking a region reveals a SECOND, more detailed view: store-level
breakdown within that region, day-by-day trend line, and a returns-rate
comparison — this DEEPER layer is intentionally hidden by default (not
cluttering the executive's first glance) but available on demand —
directly implementing file 7's "different audiences need different
levels of detail" principle within ONE dashboard via drill-down,
rather than forcing every viewer through the same fixed complexity level.
```

## Step 4: The DAX/Calculation Layer (Power BI example)
```dax
Revenue = SUM(fact_daily_sales[revenue])

Revenue Last Week =
CALCULATE([Revenue], DATEADD('dim_date'[date], -7, DAY))

WoW Growth % =
VAR CurrentRevenue = [Revenue]
VAR PriorRevenue = [Revenue Last Week]
RETURN DIVIDE(CurrentRevenue - PriorRevenue, PriorRevenue)

Region Rank =
RANKX(ALL(dim_region[region_name]), [Revenue], , DESC)
```
Using `VAR`/`RETURN` (file 5's readability best practice) and `CALCULATE` with `DATEADD` (proper time intelligence, requiring the marked Date table from Step 2).

## Step 5: Row-Level Security (since Regional Managers should see ONLY their own region)
```dax
// RLS filter applied to the "Regional Manager" role
[Region] = LOOKUPVALUE(dim_region[region_name], dim_region[regional_manager], USERPRINCIPALNAME())
```
The SAME published report serves both the VP (sees everything) and each Regional Manager (sees only their own region automatically) — one governed report, not 9 separate manually-maintained versions, directly applying file 4's RLS concept.

## Step 6: Refresh Scheduling (tying back to orchestration, module 08)
```
The Power BI dataset refresh is triggered programmatically as the FINAL
step of the nightly Airflow DAG that loads fact_daily_sales — via the
Power BI REST API (file 4) — ensuring the dashboard NEVER shows partially-
updated data from a refresh that ran before the warehouse load finished.
```

## Step 7: Iteration After Launch (file 7's "never done once" principle)
```
After 2 weeks of real use, observed via Power BI's own usage analytics:
- Regional Managers were barely using the drill-down store-level detail
  -> investigated why: turned out they wanted it sorted by "days since
  last exceeded target" rather than alphabetically — a small but
  meaningful fix based on real observed usage, not assumption
- The VP asked for a NEW comparison: "vs this same week last MONTH" in
  addition to "vs last year" -> added as an additional Measure, following
  the SAME time-intelligence pattern already established
```

## Why This Case Study Demonstrates Every Module Lesson
```
- Started from the actual business QUESTION, not the vague initial request (file 7)
- Built a proper star schema data model, not a flat denormalized table (file 4, module 05)
- Chose chart types deliberately based on the SPECIFIC question each answers (file 7)
- Applied DAX time intelligence correctly, requiring a marked Date table (file 5)
- Implemented Row-Level Security for proper, scoped multi-user access (file 4)
- Integrated refresh scheduling with the orchestration pipeline, avoiding
  race conditions (file 4, module 08)
- Treated the dashboard as something to OBSERVE and ITERATE on after
  launch, not a one-time deliverable (file 7)
```

## Try It Yourself
Using this same question-first, model-first, audience-aware approach, design a dashboard for:
1. A customer support team lead wanting to know "which agents/ticket categories need attention this week."
2. A supply chain manager wanting to know "which warehouses are at risk of stockouts in the next 7 days."


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"A calm response to chaos is worth more than a hundred anxious reactions."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
