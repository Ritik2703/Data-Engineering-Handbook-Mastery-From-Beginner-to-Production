# Contributing to the Data Engineering Handbook

Thanks for wanting to help grow this repo! To keep 14 modules feeling like ONE coherent handbook rather than a pile of disconnected notes, please follow these guidelines.

## The Core Pattern Every File Follows
```
1. WHAT it is (plain-language definition)
2. WHY it matters (the real production/business reason, not textbook fluff)
3. HOW it works (mechanics, with code/diagrams where relevant)
4. Legacy vs modern context, where relevant (what changed and why)
5. Real company context, where relevant (who uses this and why)
6. Interview traps (common gotchas, questions this topic tends to generate)
```
New contributions should genuinely follow this pattern — a file that's just a syntax reference without the "why" doesn't fit this repo's philosophy.

## Adding a New Topic/File to an Existing Module
1. Check the module's `README.md` to see where it fits in the existing numbered sequence.
2. Follow the exact formatting style of neighboring files (headers, code block style, the "Interview Traps" closing section).
3. Cross-reference other modules where relevant (this repo is intentionally interconnected — e.g., a new SQL pattern should note if it ties back to a system design case study).

## Adding a New Project to Module 13
1. Follow the existing project README structure: Business Scenario → Architecture (as an ASCII/text diagram) → Stage-by-stage walkthrough with real code → "What This Project Demonstrates" closing section.
2. Prefer a genuinely DIFFERENT tech stack combination than existing projects, to keep the module's breadth meaningful.

## Adding a New System Design Case Study to Module 11
1. Follow the 6-step framework from `11-system-design/10-interview-framework-how-to-answer.md` explicitly in your write-up.
2. Every technology choice must include an explicit tradeoff justification tied to stated requirements — this is the module's entire philosophy; a case study without tradeoff reasoning doesn't fit.

## Style Guidelines
- Keep tone practical and direct — avoid marketing language or unnecessary hedging.
- Code examples should be realistic and runnable-style, not toy pseudocode, wherever practical.
- Never present a tool/technology as universally "best" — always frame choices as tradeoffs tied to specific requirements (this repo's core philosophy, especially in modules 11-12).
- Keep the "Interview Traps" section genuinely useful — a real gotcha or commonly-asked follow-up, not a restatement of the file's content.

## Reporting Issues
Found an outdated detail (cloud services/pricing/tool versions change fast), a factual error, or a broken cross-reference? Open an issue or PR — corrections are just as valuable as new content.

## Code of Conduct
Be kind, be constructive, and remember this repo exists to genuinely help people — many of whom are learning this material from zero. Write the explanation you wish you'd had.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"What is practiced with real hands, not just read with tired eyes, becomes true skill."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
