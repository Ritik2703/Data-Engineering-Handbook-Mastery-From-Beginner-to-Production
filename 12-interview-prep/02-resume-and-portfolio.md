# 2. Resume & Portfolio — Getting Past the Screen

## The Brutal Reality of Resume Screening
```
A recruiter/ATS spends SECONDS, not minutes, on an initial resume scan.
Your resume's job is NOT to prove you're qualified in exhaustive detail —
it's to get you to the NEXT stage where a human actually talks to you.
Every design/content decision should serve THAT specific goal.
```

## Structuring a Data Engineering Resume
```
1. Header: name, contact, LinkedIn, GitHub (a real, populated GitHub
   matters more for DE roles than most other fields — see Portfolio below)

2. Summary (optional, 2-3 lines MAX if included): only worth including
   if it adds genuine specific value ("Data Engineer with 4 years
   building cloud-native pipelines processing 10TB+/day on AWS"),
   never generic filler ("hardworking team player passionate about data")

3. Technical Skills: organized by CATEGORY (Languages, Cloud, Big Data,
   Orchestration, Databases) — not just a flat wall of buzzwords;
   matching the categories a job posting/ATS is likely scanning for

4. Experience: REVERSE chronological, each bullet point ideally
   following an IMPACT-focused structure (see below), not a duty-listing structure

5. Projects (especially valuable if experience is limited): real,
   working projects with clear descriptions and GitHub links

6. Education/Certifications: relevant certs (cloud platform certs
   genuinely help for DE roles specifically, more than many other fields)
```

## Writing Impact-Focused Bullet Points (the single highest-leverage resume skill)
```
WEAK (duty-listing, no impact shown):
  "Responsible for building ETL pipelines using Airflow and Spark"

STRONG (impact-focused, quantified where possible):
  "Redesigned a nightly ETL pipeline using Airflow + Spark, reducing
  runtime from 6 hours to 45 minutes and cutting AWS compute costs by 40%"

The STRUCTURE: [Action verb] + [what you built/did] + [quantified
  impact/result] — even if you can't get an exact number, a directional
  claim ("significantly reduced," "enabled the team to X") is far
  stronger than a pure duty description with no outcome mentioned at all.
```

## The GitHub Portfolio — Genuinely Important for Data Engineers Specifically
```
Unlike many roles, Data Engineering hiring managers OFTEN actually look
at a candidate's GitHub — it's concrete, verifiable evidence of real skill.

What a GOOD DE portfolio project looks like:
- A REAL end-to-end pipeline (not just a single Jupyter notebook) —
  ideally touching several skills from this repo: extraction, a proper
  data model, transformation (dbt/Spark), orchestration (Airflow), and
  IDEALLY some cloud component
- A clear, well-written README explaining WHAT it does, WHY you built
  it that way (a mini version of module 11's tradeoff reasoning!), and
  HOW to run it
- Clean, readable code — remember, someone MIGHT actually open these
  files during your interview process
- Evidence of testing/CI (even a simple GitHub Actions workflow, recap
  `10-devops/06`) signals real production-mindset maturity beyond just
  "I can write a script"

What to AVOID:
- A GitHub full of abandoned, half-finished tutorial-following repos
  with no original thought/README
- Copy-pasted boilerplate with no genuine understanding demonstrated
- Committed credentials/secrets (a genuine, embarrassing real mistake —
  recap `10-devops/02`'s .gitignore discussion)
```

## Tailoring Your Resume Per Application (worth the extra effort)
```
A GENERIC resume sent to every job posting performs worse than a
resume LIGHTLY tailored to emphasize the specific skills/tools each
job posting mentions — this doesn't mean fabricating experience, it
means genuinely EMPHASIZING the most relevant parts of your real
experience for THIS specific role (e.g., leading with your Azure
experience for an Azure-heavy job posting, leading with your Spark
experience for a big-data-heavy one).
```

## Common Resume Mistakes That Get Candidates Screened Out
```
- Typos/inconsistent formatting (signals lack of attention to detail —
  a genuinely important DE trait)
- Buzzword soup with no evidence of actual depth ("expert in AI, ML,
  Big Data, Cloud, Blockchain...") — reads as unfocused/inflated
- No quantified impact anywhere — every bullet reads as a duty description
- Resume longer than 1-2 pages for most career stages (recruiters
  genuinely don't read a 4-page resume in the seconds they typically spend)
- Listing every single tool you've ever touched once, rather than the
  tools you're GENUINELY proficient in — this backfires badly if a
  technical interviewer asks a follow-up question about something
  listed but barely known
```

## Interview Traps
- "Walk me through your resume" — practice a CONCISE (60-90 second), well-structured narrative of your background, not a rambling recitation of every bullet point.
- Be ready to speak in DEPTH about literally anything listed on your resume — if you list a tool, expect a follow-up question about it, and never list something you can't discuss genuinely.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The one who walks into any test with a peaceful heart already carries half the victory."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
