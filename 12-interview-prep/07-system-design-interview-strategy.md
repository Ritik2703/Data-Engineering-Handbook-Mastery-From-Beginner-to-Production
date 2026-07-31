# 7. System Design Interview Strategy — Applying Module 11, Live

## This File's Purpose
Module 11 taught you the REASONING (requirements, tradeoffs, capacity estimation, the 6-step framework). This file is specifically about the INTERVIEW PERFORMANCE layer on top of that reasoning — time management, whiteboard/communication mechanics, and handling the live, interactive nature of this specific round.

## Time Management in a 45-Minute System Design Round
```
Roughly:
5 min:  Requirements clarification (module 11 file 2) — don't rush this,
        but don't spend 20 minutes here either
5 min:  High-level data flow sketch (module 11 file 10, step 2)
5 min:  Capacity estimation (module 11 file 7) — narrate the math
20 min: Deep dive on specific components, WITH explicit tradeoff
        justification (module 11 files 3, 4, 8) — this is where MOST
        of your talking should happen
5 min:  Failure modes/scale discussion (module 11 file 6)
5 min:  Summary + inviting questions (module 11 file 10, step 6)

If the interviewer steers you toward spending MORE time on a specific
area (they often will, deliberately, to see how deep your knowledge
goes there), FOLLOW their lead — this isn't you failing to stick to a
plan, it's the interviewer actively probing where THEY want more depth.
```

## Whiteboard/Diagram Communication (mechanics matter, not just content)
```
- Use CONSISTENT, simple shapes (boxes for services/components, arrows
  for data flow) — don't worry about making it visually beautiful,
  worry about making it CLEAR
- Label arrows with WHAT'S flowing ("order events," not just an
  unlabeled arrow) — this small habit dramatically improves clarity
- Leave VISUAL SPACE to add detail as the conversation goes deeper —
  don't cram your initial sketch so tightly that there's no room to
  annotate/extend it as the interviewer asks follow-ups
- If working in a shared doc/virtual whiteboard, keep your sketch
  visible/shared throughout — don't switch away from it while
  continuing to talk about it
```

## Handling "What If This Requirement Changed?" Follow-Ups
```
This is one of the MOST COMMON and MOST IMPORTANT moments in a system
design interview — recap module 11 file 10's "handling pushback" guidance.

The interviewer changing a requirement mid-discussion ("what if this
needed to be real-time instead of daily batch?") is DELIBERATELY testing
whether you can genuinely RE-REASON, not just defend your original
design. Practice, explicitly:
"That changes [specific component] significantly, because [reasoning].
I'd now consider [specific alternative], accepting [new tradeoff]
instead of [old tradeoff]."
```

## Common System Design Interview Formats (know which one you're in)
```
Open-ended prompt ("design a data platform for X"): most common,
  most similar to module 11's case studies — apply the full 6-step
  framework.

A more NARROW, specific prompt ("how would you design the incremental
  loading logic for this specific table"): requires LESS requirements-
  gathering ceremony and MORE immediate technical depth — read the
  scope of the question correctly and calibrate your depth-vs-breadth
  balance accordingly.

A "critique this existing design" prompt (less common, but does
  happen): requires you to identify SPECIFIC weaknesses/risks in a
  GIVEN design (recap module 11 file 4's "where will this break first"
  exercise) rather than designing from scratch.
```

## What a Strong Closing Sounds Like
```
"So to summarize, given [key requirements], I've proposed [core
architecture], with [key technology choices] justified by [reasoning],
accepting [explicit tradeoff]. If I had more time, I'd want to dig
deeper into [specific area] — what would be most useful for you to
explore further?"

This demonstrates: synthesis ability, genuine tradeoff awareness, AND
appropriate humility about the depth achievable in 45 minutes — all
strong signals.
```

## Interview Traps
- Don't treat a system design interview as a monologue — genuinely PAUSE periodically and invite the interviewer's input/questions; the BEST system design interviews feel like a collaborative discussion, not a one-person presentation.
- If the interviewer seems to want you to move faster through a section you're spending too long on, take that cue and move on — reading the room/interviewer's signals is itself part of what's being evaluated.
- Never present your FIRST idea as if it's obviously correct with no alternatives considered — even briefly mentioning "I considered X, but chose Y because..." demonstrates the tradeoff-awareness that module 11 emphasizes throughout.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Patience during rejection is the seed of readiness for the door that opens next."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
