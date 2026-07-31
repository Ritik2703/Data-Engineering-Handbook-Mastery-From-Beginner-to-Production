# 5. Live Coding Strategy — SQL & Python, Deep Practice Approach

## The Pattern-Recognition Skill (the real thing being tested, recap module 02)
The single biggest jump in live SQL interview performance comes from recognizing WHICH pattern a problem needs, quickly:
```
"Find the Nth highest/per-group X" -> window function (DENSE_RANK), recap `02-sql/05`
"Remove duplicates, keep latest" -> ROW_NUMBER + PARTITION, recap `02-sql/06`
"Find records in A but not B" -> LEFT JOIN + IS NULL, or NOT EXISTS, recap `02-sql/02` and `04`
"Consecutive streak/gaps" -> the row-number-minus-date trick, recap `02-sql/06`
"Compare to previous row" -> LAG/LEAD, recap `02-sql/05`
"Running total" -> SUM() OVER, recap `02-sql/05`
```
Practicing enough PROBLEMS that you recognize these patterns INSTANTLY (rather than re-deriving the approach from scratch each time) is the single highest-leverage SQL interview prep activity.

## A Structured SQL Practice Routine
```
Week 1-2: Drill the FUNDAMENTALS until automatic — joins, aggregation,
          subqueries (recap `02-sql/01-04`) — speed and confidence here
          frees up mental bandwidth for harder problems later

Week 3-4: Drill WINDOW FUNCTIONS specifically — this is consistently
          the single most-tested SQL topic at product companies
          (recap `02-sql/05`) — practice until RANK vs DENSE_RANK vs
          ROW_NUMBER differences are completely automatic

Week 5-6: Drill the ADVANCED PATTERNS — dedup, gaps/islands,
          sessionization, cohort analysis (recap `02-sql/06`) —
          these show up constantly at product companies specifically
          (recap the case studies in `02-sql/case-studies/`)

Ongoing: mix in the REAL COMPANY CASE STUDIES from `02-sql/case-studies/`
         specifically — practicing recognizing "this is a funnel
         analysis problem" or "this is a cohort retention problem" from
         a business scenario description, not just a pre-labeled SQL exercise
```

## Python Live Coding — What Actually Gets Asked for DE Roles (different from a typical SWE algorithm interview)
```
DE-specific Python interviews commonly focus on:
- Data manipulation problems (often solvable with EITHER plain Python
  OR pandas — being ready to discuss both approaches is valuable)
- Parsing/transforming semi-structured data (nested JSON/dicts — recap
  `03-python/01`'s dict/list manipulation fluency)
- Writing a function with proper error handling (recap `03-python/02`)
  — some interviewers SPECIFICALLY check whether you handle errors
  gracefully without being explicitly told to
- Less commonly (but sometimes): a classic algorithm problem (sorting,
  searching, basic data structures) — worth SOME practice, but usually
  less central to DE-specific interviews than pure SWE interviews
```

## A Genuinely Useful Practice Habit: the "Explain It to a Rubber Duck" Technique
```
Before writing ANY code in practice, say OUT LOUD (or write in a
comment) your full plan: "First I'll do X, then Y, then handle the Z
edge case" — this single habit, practiced repeatedly, is what builds
the narration skill that live coding interviews specifically reward,
far more than just solving MORE problems silently ever will.
```

## Handling Interviewer Hints (a skill in itself)
```
If an interviewer gives you a hint ("have you considered using a
window function here?"), respond with genuine engagement, not
defensiveness: "Ah, good point — let me think about how that would
apply here..." and actually incorporate it, rather than stubbornly
continuing your original approach. Interviewers give hints SPECIFICALLY
to see how you respond to new information mid-problem — handling this
gracefully is itself a positive signal (directly connects to module 11's
"genuinely reconsider when pushed back on" lesson).
```

## Interview Traps
- Practicing ONLY in a silent, no-pressure environment builds a different skill than what's tested live — practice with a timer, and ideally practice explaining solutions to another person (or recording yourself) at least a few times before a real interview.
- Don't memorize exact solutions to specific practice problems — memorize the PATTERNS (window function scenarios, join scenarios) so you can adapt to a NEW problem phrased differently, which is what real interviews actually present.
- If asked "what's the time complexity of this?" for a SQL query, be ready to reason about it in terms of indexes/scans (recap `02-sql/07`), not just Big-O notation from a pure algorithms context.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The right opportunity finds the one who keeps preparing quietly, without losing hope."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
