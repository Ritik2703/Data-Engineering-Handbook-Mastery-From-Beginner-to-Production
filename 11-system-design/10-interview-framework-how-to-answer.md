# 10. The Interview Framework — A Repeatable Structure for ANY System Design Question

## Why You Need a Repeatable Structure
Under interview time pressure, even genuinely knowledgeable candidates can freeze or ramble without a structure to lean on. This framework gives you a reliable sequence to work through for ANY data engineering system design prompt — practice it enough that it becomes automatic.

## The Framework — 6 Steps

### Step 1: Clarify Requirements (2-5 minutes — NEVER skip this)
```
Ask explicitly (recap file 2):
- What are the KEY use cases / business questions this must answer?
- What's the expected DATA VOLUME and GROWTH trajectory?
- What LATENCY is actually required (real-time? Minutes? Hours? Nightly?)
- What CONSISTENCY/AVAILABILITY requirements exist?
- Any constraints (existing systems, team skill, budget, compliance)?

Do NOT proceed to design until you have at least ROUGH answers to these —
interviewers are explicitly testing whether you ask, not just whether
you eventually land on a reasonable design.
```

### Step 2: Define the High-Level Data Flow (5 minutes)
```
Sketch (verbally, or on a whiteboard/shared doc):
Source(s) -> Ingestion -> Storage -> Processing -> Serving -> Consumers

Keep this INTENTIONALLY high-level first — resist the urge to jump
straight into "we'll use Kafka" before the overall shape is agreed on.
```

### Step 3: Do Rough Capacity Estimation (3-5 minutes)
```
Apply the back-of-envelope method from file 7 — even rough numbers
("so we're talking about roughly X GB/day, Y events/second at peak")
immediately inform which specific technologies are even reasonable
candidates, and demonstrates quantitative reasoning explicitly.
```

### Step 4: Choose Specific Technologies/Patterns, WITH Justification (10-15 minutes — the bulk of the interview)
```
For EACH major component, state:
- WHAT you're choosing
- WHY, tied EXPLICITLY back to the stated requirements from Step 1
- WHAT tradeoff/cost this choice accepts (recap file 8's structure)

Example: "For ingestion, given the stated ~5,000 events/second peak
(from Step 3) and the requirement for at-least-once processing
guarantees, I'd use Kafka rather than a simpler queue, accepting the
added operational complexity of running/monitoring a Kafka cluster,
because the throughput and replay-ability genuinely justify it here."
```

### Step 5: Address Failure Modes and Scale (5-10 minutes)
```
Proactively raise (recap files 4 and 6):
- "What happens if [specific component] fails?"
- "Where would this design break first under 10x/100x load?"
- At least ONE explicit reliability consideration (retries, idempotency,
  a specific SPOF you've identified and how you'd mitigate it)
```

### Step 6: Summarize and Invite Challenge (2 minutes)
```
"To summarize: given [requirements], I'm proposing [high-level design],
using [key technology choices] because [key reasons], with the main
tradeoff being [explicit cost]. I'd want to validate [specific
assumption] with the team before committing further. What would you
like me to dig into deeper?"

This closing signals: you can synthesize your own reasoning clearly,
you're aware of your own assumptions/uncertainty (genuine intellectual
honesty, valued highly), and you're inviting collaborative discussion
rather than treating the interview as a monologue performance.
```

## What Interviewers Are ACTUALLY Evaluating (beyond "did you get the right answer")
```
- Did you ask clarifying questions BEFORE designing? (Step 1)
- Can you reason quantitatively, even roughly? (Step 3)
- Do you JUSTIFY choices with reasoning tied to requirements, or just
  name-drop tools? (Step 4)
- Do you proactively consider failure/scale, or only when explicitly
  prompted? (Step 5)
- Can you communicate clearly and invite dialogue, or do you monologue
  without checking in? (Step 6)
- How do you respond when the interviewer PUSHES BACK or introduces a
  new constraint mid-discussion? (Genuine flexibility/reasoning vs
  defensively clinging to your first answer — a CRITICAL signal)
```

## Handling the Interviewer's Follow-Up Pushback (a make-or-break skill)
```
Interviewer: "What if the data volume was actually 100x higher than you assumed?"

WEAK response: defending the original design as still fine without
               genuine reconsideration

STRONG response: "That changes things significantly — at that volume,
                  [specific component] would likely become a bottleneck
                  because [reasoning]. I'd reconsider [specific change],
                  accepting [new tradeoff] instead." — demonstrating
                  genuine, on-the-spot re-reasoning, not defensiveness
```

## Interview Traps
- Never skip Step 1 (clarifying requirements) even under time pressure — it's the single most differentiating step between junior and senior-sounding answers.
- Don't silently do capacity math in your head — narrate it OUT LOUD (Step 3) so the interviewer can follow and evaluate your reasoning process, not just your final number.
- When pushed back on, genuinely RECONSIDER rather than defend — this single behavior is one of the strongest signals of true senior-level thinking versus rehearsed answer recitation.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The measure of good judgment is not being right once, but staying humble enough to keep learning."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
