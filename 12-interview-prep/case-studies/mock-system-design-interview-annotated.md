# Case Study: A Full Mock System Design Interview, Annotated

*A realistic transcript-style walkthrough showing good technique applied live, with annotations explaining WHY each moment works, tying back to modules 11 and 12.*

**Prompt given by interviewer**: "Design a data pipeline for a company that wants to analyze customer support ticket data to identify trending issues."

---

**Candidate**: "Great, before I dive in, I'd like to ask a few clarifying questions. First, what does 'identify trending issues' actually mean in practice — is this a dashboard the support team checks periodically, or does it need to trigger real-time alerts for a sudden spike in a specific issue type?"

> *Annotation: Immediately clarifying requirements rather than assuming — exactly module 11 file 2 / file 10 Step 1 in action. This is THE single highest-signal opening move.*

**Interviewer**: "Good question — let's say it's mainly a dashboard the support team checks each morning, but they've also mentioned wanting to be alerted if something spikes dramatically during the day."

**Candidate**: "Got it — so we have two distinct needs: a daily/batch dashboard for the regular morning review, and a faster-turnaround anomaly detection for dramatic spikes during the day. That's helpful. A couple more quick questions: roughly what volume of tickets are we talking about, and where does ticket data currently live — a specific support tool like Zendesk, or a custom system?"

> *Annotation: Notice the candidate explicitly SUMMARIZES what they just learned ("so we have two distinct needs") before asking the next question — this demonstrates active listening and synthesis, not just question-firing.*

**Interviewer**: "About 50,000 tickets a month, and yes, it's Zendesk."

**Candidate**: "Okay, let me do some quick rough math. 50,000 tickets a month is roughly 1,700 a day, so under 1 event per second on average — genuinely modest volume. That tells me we don't need heavyweight streaming infrastructure purely for THROUGHPUT reasons — but we DO have that stated need for same-day spike detection, so let me think about how to satisfy that without over-engineering the whole pipeline."

> *Annotation: Explicit capacity estimation, narrated out loud (module 11 file 7 / file 10 Step 3), AND the candidate is already reasoning toward NOT defaulting to full streaming just because "trending/spike" sounds real-time-ish — a genuinely senior instinct (module 11 file 8's simplicity argument).*

**Candidate**: "Here's what I'm thinking at a high level: extract ticket data from Zendesk's API on a schedule — say, every 15 minutes, not truly real-time streaming — land it in a data lake, run it through a classification/categorization step to tag tickets by issue type, and then have two downstream paths: a nightly aggregation feeding the morning dashboard, and a lightweight check after each 15-minute extraction that compares today's issue-type volumes against a rolling baseline, alerting if something's a significant outlier."

> *Annotation: A clean high-level data flow (Step 2), and notice the SPECIFIC tradeoff being made explicit: 15-minute polling instead of true streaming, directly justified by the modest volume and the "same-day, not sub-second" actual latency requirement from Step 1.*

**Interviewer**: "That sounds reasonable. What if I told you the company is expecting to 10x their support volume next year through a big product launch?"

**Candidate**: "That's an important constraint to factor in now rather than after the fact. At 10x, we're looking at roughly 17,000 tickets a day, still under 1 event per second on average even then — so actually, I don't think this specific volume growth changes my core architecture much, since Zendesk's API and a simple lake-based pipeline can comfortably handle that. Where I WOULD want to double check is whether the 15-minute polling frequency against Zendesk's API has any rate-limit concerns at that volume, and whether the classification step — if it's using any kind of ML model — has enough throughput headroom. But I wouldn't jump to full streaming infrastructure just because of a 10x volume number alone, since even at that scale we're still in a genuinely modest range."

> *Annotation: This is THE critical moment (module 11 file 10's pushback-handling). The candidate does NOT panic and switch to "well then we definitely need Kafka" reflexively — they RE-DO the math live, show it still supports the simpler choice, and specifically identify the REAL risk areas (API rate limits, model throughput) worth double-checking instead. This demonstrates genuine reasoning, not a rehearsed answer, and resists the common pull toward reflexive over-engineering.*

**Interviewer**: "Good reasoning. How would you handle a ticket that gets updated multiple times as it moves through different statuses?"

**Candidate**: "That's an idempotency/deduplication concern — I'd want each extraction pull to capture the ticket's CURRENT state, keyed by ticket ID, and use an upsert pattern when landing it — so if the same ticket is pulled in three consecutive 15-minute windows because it's still open and being updated, we don't create three separate conflicting records, we just have the latest state reflected. I'd also keep the RAW extracted snapshots in a separate append-only landing zone specifically so we retain full history if we ever need to reconstruct a ticket's status timeline for analysis, even though the main aggregation table just reflects current state."

> *Annotation: Directly connects to idempotency (recap `01-fundamentals/02` and module 11 file 6) and demonstrates the Bronze/Silver layering instinct (recap module 11 file 3's Medallion discussion) — proactively, without the interviewer needing to explicitly ask "how do you handle historical reconstruction."*

**Candidate (wrapping up)**: "So to summarize — given the modest actual ticket volume and the stated need for same-day (not sub-second) spike detection, I'm proposing a 15-minute batch extraction from Zendesk into a lake, with an idempotent upsert pattern for ticket updates, feeding both a nightly full aggregation for the morning dashboard and a lightweight rolling-baseline comparison for intraday spike alerts. The main tradeoff is NOT building true real-time streaming infrastructure, which I think is justified by the actual requirements and volume here — though if the business's alerting needs tighten toward true real-time in the future, or if we hit real API rate-limit constraints at higher scale, I'd revisit that decision. What would you like me to go deeper on?"

> *Annotation: A clean, structured close (Step 6) — synthesis, explicit tradeoff acknowledgment, and an genuine invitation for the interviewer to direct further depth, rather than assuming the conversation is complete.*

---

## Why This Transcript Demonstrates Strong Performance
```
- Requirements clarified FIRST, with active synthesis, not just question-firing
- Capacity estimation done and NARRATED explicitly
- A deliberate, justified choice AGAINST the "trendier" streaming
  option, with explicit tradeoff reasoning
- Genuine, non-defensive RE-REASONING when the interviewer introduced
  new information (the 10x growth scenario) — the single most
  important moment in the whole interview
- Proactive consideration of idempotency/historical reconstruction
  without being explicitly asked
- A clean, structured summary at the end

Notice that the candidate did NOT need to know some exotic, advanced
technology to perform well here — the STRENGTH of this answer is
entirely in the REASONING PROCESS (modules 11 and 12 combined), not in
name-dropping sophisticated tools.
```


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"What you build with patience and integrity will find its rightful place in time."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
