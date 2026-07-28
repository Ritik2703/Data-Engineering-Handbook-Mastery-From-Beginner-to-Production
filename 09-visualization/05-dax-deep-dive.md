# 5. DAX (Data Analysis Expressions) — Deep Dive

## Why DAX Feels Familiar Yet Behaves Differently
DAX deliberately LOOKS like Excel formulas (`SUM()`, `IF()`, `CALCULATE()`) — but it operates on an entirely different underlying model (relational tables with relationships, not a single flat grid of cells), and introduces a genuinely new concept that trips up even experienced Excel users: **Context**.

## Calculated Columns vs Measures — The First Critical Distinction
```dax
// Calculated Column: computed ONCE per row, stored physically in the table,
// takes up memory, recalculated only on data refresh
Total Price = Orders[Quantity] * Orders[Unit Price]

// Measure: computed DYNAMICALLY at QUERY TIME, based on whatever
// filter/grouping context is currently active — NOT stored, computed on the fly
Total Sales = SUM(Orders[Total Price])
```
**Real guidance**: prefer Measures over Calculated Columns whenever possible — Measures are more memory-efficient (not physically stored) and automatically adapt to whatever context they're viewed in (a table broken down by region, by date, by product — the SAME measure definition works correctly in all of them).

## Row Context vs Filter Context — THE Core DAX Concept
```
ROW CONTEXT: exists when DAX is evaluating a formula ROW BY ROW
             (calculated columns always have row context; certain
             functions like SUMX explicitly create it)

FILTER CONTEXT: exists based on whatever slicers/rows/columns/filters
                are currently applied in the report — a Measure like
                SUM(Sales[Amount]) automatically respects whatever
                filter context is active (e.g., if the visual is
                filtered to Region = "North", the SUM only includes
                North's rows)
```
```dax
// A Measure automatically adapts to filter context — the SAME formula
// gives different results depending on what's filtered/grouped in the visual
Total Sales = SUM(Sales[Amount])
// Shown in a table broken down by Region: automatically shows PER-REGION totals
// Shown as a single card with no breakdown: shows the GRAND total
// Shown with a "Region = North" slicer applied: shows ONLY North's total
```

## CALCULATE — The Most Important (and Most Confusing) DAX Function
```dax
// CALCULATE lets you MODIFY the filter context for an expression —
// the foundation of nearly every advanced DAX pattern
Sales Last Year = CALCULATE(
    SUM(Sales[Amount]),
    SAMEPERIODLASTYEAR('Date'[Date])
)

// Real business example: "sales excluding a specific region, regardless
// of what the user has currently filtered/selected"
Sales Excluding Test Region = CALCULATE(
    SUM(Sales[Amount]),
    Sales[Region] <> "Test"
)
```
**Why CALCULATE is central**: almost every advanced DAX calculation — year-over-year comparisons, "% of total" calculations, exceptions/overrides to normal filtering — is built by using CALCULATE to deliberately MODIFY the filter context away from whatever the user currently has selected, in a specific, controlled way.

## Time Intelligence — DAX's Killer Feature for Business Reporting
```dax
Sales YTD = TOTALYTD(SUM(Sales[Amount]), 'Date'[Date])

Sales Prior Month = CALCULATE(SUM(Sales[Amount]), DATEADD('Date'[Date], -1, MONTH))

YoY Growth % =
    DIVIDE(
        [Total Sales] - CALCULATE([Total Sales], SAMEPERIODLASTYEAR('Date'[Date])),
        CALCULATE([Total Sales], SAMEPERIODLASTYEAR('Date'[Date]))
    )
```
**Critical prerequisite**: DAX time intelligence functions REQUIRE a proper, marked **Date table** in your data model (a dedicated table with one row per calendar date, marked as a "Date Table" in Power BI) — without this, time intelligence functions won't work correctly. This is a very common real production gotcha for beginners who forget to create/mark a proper date dimension table.

## Iterator Functions (X-Suffix Functions) — Row-by-Row Calculations
```dax
// SUMX iterates row-by-row, evaluating an expression for EACH row, then sums the results —
// needed when the calculation itself can't be expressed as a simple column reference
Total Revenue = SUMX(Sales, Sales[Quantity] * Sales[Unit Price])

// Why not just SUM(Sales[Quantity] * Sales[Unit Price])? — DAX doesn't allow
// arithmetic directly between two columns inside a simple aggregation like
// that; SUMX explicitly creates the row context needed to evaluate this
// row-by-row before summing.
```

## VAR — Making Complex DAX Readable (and More Efficient)
```dax
YoY Growth % =
VAR CurrentSales = [Total Sales]
VAR PriorYearSales = CALCULATE([Total Sales], SAMEPERIODLASTYEAR('Date'[Date]))
RETURN
    DIVIDE(CurrentSales - PriorYearSales, PriorYearSales)
```
`VAR`/`RETURN` blocks make complex DAX dramatically more readable (naming intermediate results) AND more efficient (the expression is evaluated ONCE and reused, rather than potentially being recalculated multiple times if referenced repeatedly without a variable) — a real production best practice for any non-trivial measure.

## ALL / ALLEXCEPT — Removing Filters Deliberately
```dax
// "% of Total" pattern — a VERY common real business request
Pct of Total Sales =
DIVIDE(
    [Total Sales],
    CALCULATE([Total Sales], ALL(Sales))  -- ALL() removes ALL filters from
                                            -- the Sales table, giving the
                                            -- TRUE grand total regardless
                                            -- of what's currently filtered
)
```

## Interview Traps
- "What's the difference between a calculated column and a measure?" — a calculated column is computed once per row and physically stored; a measure is computed dynamically at query time based on the current filter context — measures are generally preferred for their memory efficiency and context-awareness.
- "Explain row context vs filter context with an example." — row context is DAX evaluating something row-by-row (as in a calculated column or inside SUMX); filter context is whatever slicers/groupings are currently active in the report, automatically respected by measures like `SUM()`.
- "Why is CALCULATE considered the most important DAX function?" — it's the mechanism for deliberately modifying filter context, underlying nearly every advanced pattern (time intelligence, exceptions, percent-of-total calculations).
- "Why do DAX time intelligence functions require a marked Date table?" — they rely on specific date-continuity and relationship assumptions that only a proper, complete calendar Date table (marked as such in the model) satisfies correctly.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"A grateful mind finds lessons even in setbacks that a proud mind would only resent."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
