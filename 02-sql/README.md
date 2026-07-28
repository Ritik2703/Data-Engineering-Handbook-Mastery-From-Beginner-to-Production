# 02 — SQL: Beginner to Production-Level Mastery

Complete SQL module written for **zero-to-hero** — even if you've never written a `SELECT` before, by the end of this module you should be able to reason about real production queries used at product-based companies (Amazon, Uber, Swiggy, Netflix, Spotify style problems).

> 🎮 Try the **[Interactive SQL Playground](./sql-playground.html)** — runs real SQL in your browser against a sample e-commerce database. No install needed, just open the HTML file.

## 📖 Learning Path

| # | File | Level | Covers |
|---|---|---|---|
| 1 | [`01-sql-basics.md`](./01-sql-basics.md) | Beginner | SELECT, WHERE, ORDER BY, data types, filtering |
| 2 | [`02-joins.md`](./02-joins.md) | Beginner-Intermediate | All join types, real examples, common mistakes |
| 3 | [`03-aggregation-grouping.md`](./03-aggregation-grouping.md) | Intermediate | GROUP BY, HAVING, aggregate functions |
| 4 | [`04-subqueries-ctes.md`](./04-subqueries-ctes.md) | Intermediate | Subqueries, CTEs, recursive CTEs |
| 5 | [`05-window-functions.md`](./05-window-functions.md) | Advanced | ROW_NUMBER, RANK, LAG/LEAD, running totals |
| 6 | [`06-advanced-sql-patterns.md`](./06-advanced-sql-patterns.md) | Advanced | Dedup, SCD2, gaps & islands, pivot, sessionization |
| 7 | [`07-query-optimization-indexing.md`](./07-query-optimization-indexing.md) | Advanced | EXPLAIN plans, indexing strategy, query tuning |
| 8 | [`08-transactions-concurrency.md`](./08-transactions-concurrency.md) | Advanced | ACID, isolation levels, locking, deadlocks |
| 9 | [`09-sql-in-production.md`](./09-sql-in-production.md) | Production | dbt/warehouse SQL, dialect differences, style guide |
| 10 | [`case-studies/`](./case-studies/) | Production | Real company-style schemas + queries (Amazon, Uber, Swiggy, Netflix, Spotify, Bank) |
| 11 | [`interview-questions.md`](./interview-questions.md) | All levels | 40+ questions with solutions and explanations |
| 12 | [`sql-playground.html`](./sql-playground.html) | Interactive | Runs SQL in-browser (SQLite via sql.js), sample schema pre-loaded |

## 🧠 How to use this module (if SQL is totally new to you)
```
Day 1-2:   01-sql-basics.md          -> practice every query in the playground
Day 3-4:   02-joins.md               -> this is where most beginners get stuck, go slow
Day 5:     03-aggregation-grouping.md
Day 6-7:   04-subqueries-ctes.md
Day 8-10:  05-window-functions.md    -> THE most-asked interview topic, don't rush
Day 11-12: 06-advanced-sql-patterns.md
Day 13:    07-query-optimization-indexing.md + 08-transactions-concurrency.md
Day 14+:   case-studies/ + interview-questions.md  -> apply everything to real scenarios
```

## 🏢 Why "real industry examples" matter
Textbook SQL problems ("find the second highest salary") teach syntax but not **judgment** — knowing *which* concept to reach for and *why*. Every file in this module pairs each concept with a **real business scenario** a product company actually solves with it, so you build the instinct: "this smells like a window function problem" or "this needs a self-join."


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Let go of the need to be right, and you will finally hear what the data is actually saying."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
