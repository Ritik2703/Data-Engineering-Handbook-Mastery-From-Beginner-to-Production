# Master Question Bank — Cross-Module Index for Final Revision

A curated pointer to the highest-value questions across the ENTIRE repo, organized for final review in the days before an interview. Not a replacement for each module's own `interview-questions.md` — a MAP to help you prioritize final revision time.

## If You Only Have 1 Day Left — Review These Specifically
```
- 02-sql/interview-questions.md: Q14-18 (window functions — the single
  most commonly tested SQL topic)
- 05-databases/interview-questions.md: Q7-9 (CAP theorem/NoSQL), Q27
  (why Netflix created Iceberg — a great "why" story to have ready)
- 11-system-design/interview-questions.md: work through AT LEAST 2 of
  the numbered design prompts yourself, from a blank page
- 11-system-design/09-senior-de-vs-architect-mindset.md: re-read the
  Q&A at the bottom, be ready to answer this exact question fluently
- 12-interview-prep/03-behavioral-interview-mastery.md: review your
  own story bank against the "real question behind the question" list
```

## If You Have 1 Week Left — A Fuller Review Sequence
```
Day 1: 02-sql/interview-questions.md (all of it) + practice 3-4 problems
       in sql-playground.html
Day 2: 05-databases/interview-questions.md (all of it) — this module's
       breadth (history, NoSQL, NewSQL, vector DBs, company choices) is
       tested surprisingly often in senior-level conversations
Day 3: 06-big-data/interview-questions.md + 07-cloud-platforms/interview-
       questions.md
Day 4: 08-orchestration/interview-questions.md + 10-devops/interview-
       questions.md
Day 5: 11-system-design/interview-questions.md — work through EVERY
       numbered design prompt at least briefly
Day 6: Re-work 3 of the 7 case studies in 11-system-design/case-studies/
       from a blank page yourself
Day 7: 12-interview-prep (this whole module) — resume review, story
       bank finalization, re-read the mock interview case study
```

## Topic-by-Topic Pointer Map (use this to jump to the RIGHT place for a specific weak area)
```
Weak on SQL fundamentals?           -> 02-sql/01-04 + interview-questions.md Q1-13
Weak on window functions?            -> 02-sql/05 + interview-questions.md Q14-18
Weak on query optimization?          -> 02-sql/07 + interview-questions.md Q23-25
Weak on Python for DE specifically?  -> 03-python/01-02 + MASTER_LIBRARY_REFERENCE.py
Weak on cloud service specifics?     -> 07-cloud-platforms/03-05 (pick your target cloud)
Weak on Spark internals?             -> 06-big-data/03-04 + interview-questions.md Q8-15
Weak on database internals?          -> 05-databases/02, 08, 10 + interview-questions.md
Weak on ETL tool history/context?    -> 04-etl-elt/01, 09 + interview-questions.md
Weak on orchestration concepts?      -> 08-orchestration/01-04 + interview-questions.md
Weak on system design structure?     -> 11-system-design/10 (the framework itself)
Weak on articulating tradeoffs?      -> 11-system-design/08 + practice the structure
                                         on 3 case studies yourself
Weak on behavioral stories?          -> 12-interview-prep/03 + build your story bank NOW,
                                         not the night before
```

## The "Why Does X Exist" Question Bank (a recurring interview favorite across this ENTIRE repo)
```
Practice fluently answering "why was [X] created, what problem did it
solve" for EACH of these — this exact question type appears constantly
across modules and interview levels:
- Why was Hadoop created? (06-big-data/01)
- Why did Spark replace MapReduce? (06-big-data/02)
- Why was Kafka created (by LinkedIn)? (06-big-data/09)
- Why was Airflow created (by Airbnb)? (08-orchestration/09)
- Why did Netflix create Iceberg? (06-big-data/06, 09)
- Why did Uber create Hudi? (06-big-data/06, 09)
- Why did dbt's Semantic Layer emerge? (09-visualization/06)
- Why did NoSQL emerge in the mid-2000s? (05-databases/01)
- Why did NewSQL emerge? (05-databases/04)
- Why are vector databases suddenly significant? (05-databases/06)
- Why did cloud migration accelerate industry-wide? (07-cloud-platforms/01)
- Why did DevOps emerge as its own discipline? (10-devops/01)
```

## The "Explain the Tradeoff" Question Bank (practice the structure from `11-system-design/08`)
```
- ETL vs ELT
- Batch vs Streaming
- SQL vs NoSQL (for a specific access pattern)
- Star schema vs Data Vault
- Lambda vs Kappa architecture
- Reserved vs Serverless cloud pricing
- Centralized vs Data Mesh data platform ownership
- Build vs Buy for a data tool
- Simplicity vs Sophistication in a given design

For EACH of these, practice the exact structure from module 11 file 8:
"I'd choose X over Y because [requirement-tied reason], accepting
[explicit cost], though I'd reconsider if [specific condition changed]."
```

## Final Reminder
```
This entire repo — 12 modules, hundreds of files — exists to build ONE
thing: genuine, flexible, articulable JUDGMENT about data engineering
problems. The specific facts/syntax matter less than the ability to
REASON through something you haven't seen exactly before, using the
patterns and frameworks built throughout this repo. Trust the process,
practice articulating your reasoning out loud, and walk into your
interview ready to have a genuine conversation, not recite memorized answers.

Good luck. 🚀
```


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Prepare with sincerity, present with calm, and let the result follow its own course."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
