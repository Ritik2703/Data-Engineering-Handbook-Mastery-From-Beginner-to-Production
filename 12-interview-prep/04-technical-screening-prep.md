# 4. Technical Screening Prep — What's Actually Being Tested

## What a Typical Technical Screen Covers
```
Usually 45-60 minutes, commonly structured as:
- 5-10 min: brief background discussion/resume walkthrough
- 20-30 min: live SQL and/or Python coding
- 10-15 min: possibly a lightweight system design or conceptual
  discussion question
- 5-10 min: your questions for them
```

## What the Interviewer Is ACTUALLY Evaluating (beyond correctness)
```
- Can you translate a WORD PROBLEM into correct SQL/Python without
  extensive hand-holding? (recap the pattern-recognition skill
  emphasized throughout `02-sql/` — "this smells like a window
  function problem")
- Do you communicate your THINKING as you work, or go silent? (silence
  makes it impossible for an interviewer to give you partial credit or
  help redirect you if you're heading down a wrong path)
- How do you handle being STUCK? (asking a clarifying question,
  thinking out loud about approaches, vs freezing or guessing randomly)
- Do you consider EDGE CASES proactively? (nulls, duplicates, empty
  results — recap the production-mindset emphasis throughout this repo)
- Can you EXPLAIN your own solution afterward, including its
  complexity/performance characteristics?
```

## A Concrete Strategy for Live SQL Problems
```
1. RESTATE the problem in your own words first ("So I need to find
   the second-highest salary per department, correct?") — confirms
   understanding AND buys yourself a moment to think

2. Think OUT LOUD about the APPROACH before writing code ("I'm
   thinking I'll use a window function here, DENSE_RANK specifically,
   because...") — recap `02-sql/05`'s pattern-recognition approach

3. Write the query INCREMENTALLY, narrating as you go, rather than
   going silent for 5 minutes and presenting a finished block

4. TEST your own query mentally against a small example BEFORE
   declaring it done ("let me trace through this with a small example...")

5. Proactively mention EDGE CASES even if not explicitly asked
   ("this would need to handle ties in salary — let me make sure
   DENSE_RANK handles that correctly...")
```

## A Concrete Strategy for Live Python/Coding Problems
```
1. Clarify INPUT/OUTPUT format and constraints explicitly before coding
   ("Can this list contain duplicates? Can it be empty?")

2. Discuss your APPROACH and its rough complexity BEFORE writing code
   ("I could do this with a nested loop, O(n²), or use a dictionary
   for O(n) — let me go with the dictionary approach for efficiency")

3. Write clean, reasonably well-named code — even under time pressure,
   avoid single-letter variable names that obscure your own reasoning
   for the interviewer watching

4. Test with a SIMPLE example, then explicitly consider an EDGE CASE
   (empty input, single element, all-duplicate values)

5. If genuinely stuck, narrate your stuck-ness rather than going silent
   ("I'm not immediately seeing the cleanest approach here — let me
   think through a brute-force version first, then see if I can optimize")
```

## What to Do When You Don't Know Something
```
NEVER bluff/pretend confidence about something you don't actually know
— technical interviewers can usually tell, and it erodes trust in
everything ELSE you say. Instead:
  "I haven't worked directly with [X], but based on [related concept
  I DO know], I'd guess it works similarly to... — is that roughly right?"
This demonstrates genuine intellectual honesty AND an ability to reason
from related knowledge — often scores BETTER than a candidate who
happens to know the exact answer but can't explain their reasoning.
```

## Practicing Effectively (not just solving problems silently)
```
The single highest-leverage practice technique: solve problems OUT
LOUD, as if explaining to an interviewer, even when practicing alone —
silent problem-solving builds a DIFFERENT skill than verbalized,
interview-realistic problem-solving, and many otherwise-strong
candidates struggle specifically with the VERBALIZATION skill under
pressure, not the underlying technical knowledge itself.
```

## Interview Traps
- Going completely silent while coding is one of the most common ways technical screens go poorly for genuinely competent candidates — practice narrating your thought process as an explicit, deliberate skill, not an afterthought.
- Don't immediately start typing/writing code the instant a question is given — take the 10-30 seconds to actually think through an approach and communicate it first; rushing to code often leads to a wrong first attempt that costs MORE time than the upfront thinking would have.
- If you make a mistake mid-solution, calmly acknowledge and fix it ("wait, I think I have an off-by-one error here, let me check...") rather than pretending it didn't happen — self-correction is a POSITIVE signal, not a negative one.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Every conversation, even a difficult one, is a chance to learn something about yourself."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
