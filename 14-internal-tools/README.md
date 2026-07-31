# 14 — Internal Company Tools (Bonus Module — The "Nobody Tells You This" Guide)

Nobody teaches you these in a course, but you'll use them every single day at any real job. This is the adhoc, practical guide to the non-technical (or semi-technical) tools every Data Engineer works inside daily — project tracking, documentation, communication, and incident management.

## Jira — Project & Task Tracking
```
What it is: Atlassian's issue/project tracking tool — the de facto
  standard at most tech companies for tracking work.

Core concepts:
  Epic: a large body of work (e.g., "Migrate reporting warehouse to Snowflake")
  Story: a specific piece of user-facing or engineering value within an Epic
  Task/Sub-task: smaller, concrete units of work within a Story
  Sprint: a fixed time-box (commonly 2 weeks) during which a team commits
    to completing a set of tickets (Agile/Scrum methodology)
  Backlog: all not-yet-scheduled work, prioritized and groomed regularly
  Board (Kanban/Scrum): visual columns (To Do / In Progress / In Review
    / Done) tracking ticket status

What a Data Engineer actually does in Jira daily:
- Move tickets across the board as work progresses (update status
  honestly and promptly — this is how your manager/team knows what's
  actually happening without asking you directly)
- Write clear ticket descriptions when creating your OWN tickets
  (bug reports, technical debt items) — a vague ticket ("fix the
  pipeline") wastes everyone's time later; a good one includes
  context, reproduction steps, and expected outcome
- Link related tickets (a bug ticket linked to the Epic it affects) —
  helps anyone later understand the full picture
- Attend Sprint Planning/Standup/Retro ceremonies (if the team runs Scrum)

Real practical tip: get comfortable with JQL (Jira Query Language) —
  e.g., `project = DATA AND status = "In Progress" AND assignee = currentUser()`
  — genuinely useful for building your own custom views of relevant work.
```

## Confluence — Documentation & Knowledge Base
```
What it is: Atlassian's wiki/documentation tool, commonly paired with Jira.

What Data Engineers actually document here:
- Pipeline/system architecture documentation (a written companion to
  the diagrams from module 11 — "here's how the orders pipeline works,
  here's who to contact if it breaks")
- Runbooks for on-call (recap `08-orchestration/08`'s on-call/runbook
  discussion) — step-by-step guides for diagnosing/fixing common failures
- Design documents (RFCs — "Request for Comments") — before building
  something significant, write up the proposed design, requirements,
  and tradeoffs (directly applying module 11's reasoning IN WRITING)
  and share for team feedback before committing engineering time

Real practical tip: a genuinely underrated career-growth habit is
  writing clear, well-organized Confluence docs — it's highly visible
  evidence of the "designing for others' comprehension" skill discussed
  in `11-system-design/09` as a senior/architect differentiator.
```

## Slack / Microsoft Teams — Team Communication
```
Real practical DE-specific patterns:
- Dedicated alert channels (e.g., #data-eng-alerts) where automated
  pipeline failure notifications post (recap the alerting patterns
  from `08-orchestration/08` and `10-devops/09`) — genuinely learn to
  triage these without alert fatigue causing you to ignore the channel
- Threading replies (keeping a channel readable, not a wall of
  unthreaded messages) — a small habit that genuinely affects how
  your team perceives your communication clarity
- Status updates in a team channel during an active incident — clear,
  frequent, honest updates ("still investigating, next update in 15
  min") build trust even when you don't yet have the full answer
```

## ServiceNow / Jira Service Management — IT Ticketing
```
What it is: used for formal IT service requests — e.g., requesting new
  cloud access/permissions, provisioning a new database, requesting a
  new tool license.

Real practical DE relevance: in larger, more governed enterprises,
  even simple infrastructure requests (like getting IAM permissions
  for a new S3 bucket) often go through a formal ServiceNow ticket and
  approval workflow — genuinely different from a startup's "just ask
  in Slack" culture, and worth understanding the difference exists
  before joining a larger enterprise expecting startup-speed informality.
```

## PagerDuty / Opsgenie — On-Call & Incident Management
```
What it is: tools that route alerts (from monitoring systems, recap
  `10-devops/09`) to the currently on-call engineer via phone call/SMS/
  push notification, with escalation policies if the first person
  doesn't acknowledge within a set time.

Real practical DE relevance: if you're on a data platform on-call
  rotation, this is the tool that actually pages YOU at 2 AM — learn
  your team's specific escalation policy, acknowledgment process, and
  how to properly hand off/schedule around your on-call shifts BEFORE
  you're actually on one.
```

## Notion / Miro — Modern Alternatives Increasingly Seen
```
Notion: increasingly used as an alternative (or complement) to
  Confluence at newer/smaller companies — same core purpose
  (documentation/knowledge base), different tool, more flexible
  formatting.

Miro: a collaborative whiteboarding tool — genuinely useful for the
  EXACT system design sketching discussed in `11-system-design` and
  `12-interview-prep/07`, but used for REAL architecture discussions
  with your team, not just interviews.
```

## Git Hosting Platforms — GitHub/GitLab/Bitbucket (recap, but as a "tool" specifically)
```
Beyond the Git concepts covered in `10-devops/02`, the PLATFORM itself
(GitHub/GitLab/Bitbucket) has its own genuinely important features:
- Project boards (some teams use GitHub Projects INSTEAD of Jira for
  smaller teams)
- Code owners files (automatically requesting review from the right
  people based on which files changed)
- Branch protection rules (enforcing CI passing + review approval
  before merge is even possible — recap `10-devops/03`'s CI gating discussion)
```

## The Meta-Skill: Tool-Agnostic Habits That Transfer Everywhere
```
Regardless of the SPECIFIC tools your company uses (and they genuinely
vary company to company), these habits transfer universally:
- Write clear, context-rich tickets/documentation — assume the reader
  has LESS context than you currently do
- Update status/progress PROACTIVELY, don't make people chase you for updates
- Document decisions and their REASONING (not just the final choice) —
  directly applying module 11's tradeoff-articulation skill, in writing,
  for your future self and teammates
- Keep a personal record of what you've worked on (genuinely useful
  both for performance reviews AND for building your `12-interview-prep/03`
  behavioral story bank over time, rather than trying to remember
  specific situations months later)
```

## Interview Traps
- "What project management tools have you used?" — a completely normal, low-stakes question; be honest about your actual experience level with specific tools (most are genuinely easy to pick up quickly) rather than overstating familiarity.
- Some interviews (especially for more senior/lead roles) may ask about your DOCUMENTATION habits or how you handle on-call — having a genuine, specific answer (not just "I'd use whatever tool the team uses") signals real production-environment experience.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"To finish what you started, even imperfectly, teaches more than endless planning ever could."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
