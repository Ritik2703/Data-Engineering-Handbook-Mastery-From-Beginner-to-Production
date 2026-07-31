# 6. Take-Home Assignment Strategy — What Separates Good From Great

## Why Companies Use Take-Homes
Take-home assignments let candidates demonstrate REALISTIC work quality (proper testing, documentation, thoughtful design) that's hard to show under live-interview time pressure — but they also genuinely evaluate whether you can work INDEPENDENTLY and make reasonable judgment calls without someone available to immediately clarify every ambiguity.

## The #1 Mistake: Treating It as "Just Get the Right Answer"
```
A take-home asking you to "build a pipeline to process this sample
data" is testing MUCH more than whether your final output is correct:
- Did you handle edge cases (nulls, malformed rows, duplicates)
  PROACTIVELY, or does your code crash on anything not perfectly clean?
- Is your code STRUCTURED sensibly (functions, not one giant script —
  recap `03-python/13`'s production best practices), or a stream-of-
  consciousness script?
- Did you include ANY tests? (Even a few basic unit tests signal real
  production maturity, recap `10-devops/08`'s DE-specific testing discussion)
- Is there a README explaining your APPROACH and REASONING (recap
  module 11's tradeoff-articulation skill, applied in writing this time)?
- Did you handle ERRORS gracefully (recap `03-python/02`), or does an
  API timeout crash the whole thing with an ugly traceback?
```

## A Genuinely Strong Take-Home Structure
```
project/
├── README.md          # approach, assumptions made, how to run it,
│                         and IMPORTANTLY, what you'd do differently
│                         with more time (shows self-awareness of
│                         tradeoffs, recap module 11's file 8)
├── src/
│   ├── extract.py
│   ├── transform.py
│   └── load.py
├── tests/
│   └── test_transform.py   # even 3-4 meaningful tests genuinely help
├── requirements.txt
└── sample_output/      # (if applicable) a small sample of your
                          actual output, so reviewers don't need to
                          run your code just to see what it produces
```

## Handling Ambiguity in the Assignment (a real, deliberate test)
```
Take-home instructions are OFTEN deliberately somewhat ambiguous
(mirroring real work, where requirements are rarely perfectly specified)
— the RIGHT response is:
1. If a clarifying question is genuinely blocking, ask it (most
   companies welcome this, and it demonstrates good judgment about
   when to ask vs when to proceed)
2. For everything else, make a REASONABLE assumption, and EXPLICITLY
   DOCUMENT it in your README ("I assumed 'active user' means logged
   in within 30 days, since this wasn't specified") — this demonstrates
   EXACTLY the requirements-gathering instinct from module 11, applied
   independently without someone there to ask directly.
```

## Time Management — Don't Over-Invest, But Don't Under-Invest Either
```
Most take-homes state an expected time budget (e.g., "should take
2-4 hours") — WILDLY exceeding this (spending 15 hours perfecting
something meant to take 3) can actually be viewed NEGATIVELY (poor
time-management judgment, or over-engineering relative to the actual
ask) — aim to deliver something GENUINELY solid within roughly the
stated budget, with your README explicitly noting what you'd add
with more time if relevant, rather than silently over-investing.
```

## What to Do If You Genuinely Can't Finish Everything
```
A PARTIAL, well-documented, working solution with a clear README
explaining what's done, what's not, and WHY you prioritized what you
did, is almost always viewed better than a rushed, broken attempt at
the FULL scope — explicit, honest communication about scope tradeoffs
under time constraints is itself a positive signal (recap module 11's
emphasis on transparent reasoning).
```

## Interview Traps
- Submitting code with ZERO tests, zero README, and zero error handling — even if the core logic is technically correct, this reads as "doesn't operate with production maturity," a genuine red flag for a DE role specifically.
- Wildly over-engineering a simple ask (e.g., setting up a full Kubernetes deployment for a take-home explicitly asking for "a simple script") — signals poor judgment about matching solution complexity to the actual ask (recap module 11 file 8's simplicity-argument instinct).
- Not reading the instructions carefully enough to catch an explicitly stated constraint (e.g., "must run without any paid API keys") — a surprisingly common, easily avoidable way to lose points regardless of code quality.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Speak your truth plainly; a sincere answer outshines a clever performance."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
