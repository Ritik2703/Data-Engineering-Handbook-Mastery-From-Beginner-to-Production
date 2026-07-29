# 2. Git & Version Control — Deep Dive

## Why Version Control Is Non-Negotiable
Before Git-style version control, teams shared code via emailed zip files, shared network drives with "final_v2_FINAL.py," or no coordination at all — leading to overwritten work, no history of WHY a change was made, and no safe way to experiment without risking the working version. Version control solves this by tracking every change, who made it, why (via commit messages), and letting multiple people work in parallel safely.

## Git's Core Model — Snapshots, Not Diffs (a common misconception)
```
Many people assume Git stores a series of "diffs" (what changed between
versions) — it actually stores a series of full SNAPSHOTS of your entire
project at each commit (though it cleverly stores unchanged files as
references to avoid duplication) — this snapshot model is why Git can
do things like checking out any historical version so efficiently.
```

## Core Commands (know these cold)
```bash
git init                        # start tracking a new project
git clone <url>                  # copy an existing remote repository locally
git add <file>                   # stage changes for the next commit
git commit -m "message"          # save a snapshot with a description
git push                         # upload local commits to the remote (e.g., GitHub)
git pull                         # download and merge remote changes into local
git branch <name>                 # create a new branch
git checkout <branch>             # switch to a branch (or `git switch` in modern Git)
git merge <branch>                 # combine another branch's changes into current branch
git log                           # view commit history
git diff                          # see uncommitted changes
```

## Branching — Working in Parallel Safely
```
main/master branch: the stable, deployable version of the code

feature branches: created FROM main, where a specific feature/fix is
                   developed in isolation, without risking main's stability
   git checkout -b feature/add-retry-logic

Once the feature is complete and reviewed (via a Pull Request, see below),
it's merged BACK into main.
```

## Merge Conflicts — Why They Happen and How to Resolve Them
```
A merge conflict occurs when TWO branches have changed the SAME lines of
the SAME file differently — Git can't automatically decide which version
is "correct," so it asks a human to resolve it.

<<<<<<< HEAD
retry_count = 3
=======
retry_count = 5
>>>>>>> feature/add-retry-logic
```
The developer manually edits the file to keep the correct resolution (perhaps `retry_count = 5`, or something combining both intentions), removes the conflict markers, then commits the resolution.

## Pull Requests (PRs) / Merge Requests — The Code Review Gateway
```
A PR is a REQUEST to merge one branch into another, opened on GitHub/
GitLab/Bitbucket, that:
- Shows a clear DIFF of exactly what's changing
- Allows TEAMMATES to review, comment, and request changes before merging
- Can be configured to REQUIRE passing automated tests (CI, see file 3)
  before merging is even allowed
- Creates a permanent, searchable RECORD of why a change was made,
  who approved it, and what discussion happened around it
```
This code review gate is a core DevOps practice — catching bugs/design issues BEFORE they reach production, and spreading knowledge across the team (reviewers learn what changed, authors get feedback).

## Branching Strategies — Real Team Workflows
```
GitFlow (older, more structured, more overhead):
  main (production) + develop (integration) + feature branches +
  release branches + hotfix branches — a rigid, multi-branch model,
  once very popular, now considered heavyweight for most modern teams

GitHub Flow (simpler, more common for continuous deployment):
  main (always deployable) + short-lived feature branches merged directly
  back to main via PR, deployed immediately after merge — much simpler,
  favored by teams practicing frequent, continuous deployment

Trunk-Based Development (favored by high-velocity teams, e.g., Google):
  Very short-lived branches (hours, not days/weeks), frequent small
  merges directly to main/trunk, often behind FEATURE FLAGS (see below)
  rather than long-lived feature branches — minimizes painful merge
  conflicts from long-diverging branches
```

## Feature Flags — Deploying Code Without "Releasing" It Yet
```python
if feature_flags.is_enabled("new_recommendation_algorithm", user_id):
    return new_algorithm(user_id)
else:
    return old_algorithm(user_id)
```
Feature flags let you MERGE and DEPLOY code to production while keeping it INACTIVE (or active only for a small test group) — decoupling "deploying code" from "releasing a feature to users," a genuinely powerful modern practice enabling trunk-based development and safer rollouts (turn a flag off instantly if something's wrong, without needing a code rollback/redeploy).

## .gitignore — What NOT to Track
```
__pycache__/
*.pyc
.env
venv/
*.log
credentials.json
```
Critical for keeping secrets, generated files, and environment-specific junk OUT of version control — a leaked credential committed to Git history is a genuine, common, serious security incident (and simply deleting the file in a LATER commit does NOT remove it from Git's history — it requires actively rewriting history, a much more involved and disruptive fix).

## Git for Data Engineers Specifically
```
- SQL files (dbt models), Python pipeline code, Airflow DAGs, Terraform
  configs — ALL of this should live in Git, exactly like application code
- Data files themselves (large CSVs/Parquet) should generally NOT be
  committed to Git directly — Git isn't designed for large binary files;
  use Git LFS (Large File Storage) if genuinely needed, or better, keep
  actual data in S3/a data lake and only version-control the CODE that
  processes it
```

## Interview Traps
- "Explain a merge conflict and how you'd resolve one." — happens when two branches change the same lines differently; resolved by manually editing to keep the intended combination of changes, removing Git's conflict markers, then committing.
- "GitFlow vs GitHub Flow vs Trunk-Based Development — what's the real tradeoff?" — GitFlow is more structured but heavier overhead; GitHub Flow is simpler for continuous deployment; Trunk-Based minimizes long-branch merge pain via very short-lived branches and feature flags, favored by high-velocity teams.
- "Why shouldn't you commit large data files directly to Git?" — Git's snapshot model isn't designed for large binary files (bloats repository size/clone time); use Git LFS or, better, keep data in appropriate storage (S3/data lake) and version-control only the processing code.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"A team that shares both credit and blame equally will always outlast one that shares neither."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
