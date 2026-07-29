# 10. What Real Companies Use — DevOps Stacks

## Netflix — Chaos Engineering Pioneer
As covered in `07-cloud-platforms/11-real-company-cloud-journeys.md`, Netflix's "Chaos Monkey" (and the broader "Simian Army" family of tools) deliberately, randomly breaks production infrastructure to CONTINUOUSLY verify systems survive real failures — a genuinely radical, proactive DevOps philosophy (test resilience constantly, don't just hope for it) that has since inspired the broader "Chaos Engineering" discipline adopted well beyond Netflix itself.

## Google — Site Reliability Engineering (SRE), Its Own DevOps Philosophy
Google developed (and extensively published on, via their influential "Site Reliability Engineering" book) their own specific flavor of DevOps culture — **SRE** — treating operations as fundamentally a SOFTWARE ENGINEERING problem (automate operational toil away with code, rather than growing an ever-larger manual-operations team), and formalizing concepts like error budgets and SLOs (file 9) that have since become industry-standard vocabulary well beyond Google.

## Amazon — "You Build It, You Run It"
Amazon is widely credited with popularizing the principle that the SAME team that builds a service is responsible for OPERATING it in production (rather than throwing it over the wall to a separate Ops team) — directly embodying DevOps's core "shared ownership" philosophy (file 1) at genuine organizational scale, and a major influence on how many companies have since structured their own engineering teams.

## Etsy — Continuous Deployment Pioneer, Blameless Post-Mortems
Etsy was an early, influential public advocate for BOTH extremely frequent continuous deployment (at one point publicly known for deploying to production dozens of times per DAY) AND a genuinely blameless post-mortem culture — publishing openly about both practices in ways that significantly influenced broader industry DevOps culture beyond their own engineering org.

## Enterprises on Microsoft Stack — Azure DevOps as the Integrated Default
Similar to the Power BI pattern in module 09, enterprises already standardized on Microsoft/Azure commonly default to Azure DevOps (which bundles source control, CI/CD pipelines, work item tracking, and artifact management in one integrated Microsoft product) rather than assembling GitHub Actions + a separate project management tool + separate artifact registry — an ecosystem-fit decision matching the same pattern seen throughout this repo.

## Startups & GitHub-Native Companies — GitHub Actions as the Default
Companies already using GitHub for source control (an enormous majority of modern startups/tech companies) overwhelmingly default to GitHub Actions for CI/CD specifically because of its zero-setup-friction, built-directly-into-where-your-code-already-lives advantage (file 6) — genuinely the path of least resistance for a huge share of newer companies.

## The Recurring Pattern (once more, holding true across every module)
```
DevOps tool/culture choices, exactly like databases (module 05),
orchestrators (module 08), and BI tools (module 09), are driven by:
1. Existing ecosystem investment (Microsoft shops -> Azure DevOps;
   GitHub-native companies -> GitHub Actions)
2. Organizational philosophy/culture (Google's SRE, Etsy's blameless
   post-mortems, Amazon's "you build it you run it")
3. Scale forcing genuinely novel practices at the largest companies
   (Netflix's Chaos Engineering) that later influence the entire industry

There is no single "correct" DevOps stack — the RIGHT choice (and the
RIGHT cultural practices) depend on your organization's existing
investments, culture, and specific reliability/velocity needs.
```

## Interview Traps
- "What is Site Reliability Engineering (SRE) and how does it relate to DevOps?" — Google's specific formalization of DevOps principles, treating operations as a software engineering problem (automating away manual toil), and popularizing concepts like error budgets/SLOs now used industry-wide.
- "What does 'you build it, you run it' mean, and why does it matter?" — the same team that builds a service also operates it in production, directly embodying DevOps's shared-ownership philosophy rather than the traditional adversarial Dev/Ops split (file 1).
- Be ready to explain WHY Chaos Engineering (deliberately breaking production to test resilience) is a genuinely counter-intuitive but valuable practice — proactively finding weaknesses on your own terms, rather than discovering them during a real, uncontrolled incident.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The discipline to pause and reflect after a mistake is worth more than the mistake itself."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
