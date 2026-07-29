# 3. CI/CD Fundamentals — Deep Dive

## Continuous Integration (CI) — Automatically Build & Test Every Change
```
Every time code is pushed/a PR is opened, a CI system automatically:
1. Checks out the code
2. Installs dependencies
3. Runs linters (style/syntax checks)
4. Runs automated tests (unit tests, integration tests)
5. Reports PASS/FAIL back to the PR — often BLOCKING merge if it fails
```
**Why "Integration" specifically**: the name comes from catching problems when different developers' changes are INTEGRATED (merged) together — running tests on every small change, constantly, catches integration bugs immediately, rather than discovering them weeks later when a large batch of changes is finally combined (the classic pre-CI "integration hell" problem).

## Continuous Delivery vs Continuous Deployment — The Critical Distinction (recap + depth)
```
Continuous Delivery: code is automatically built, tested, and packaged
                       into a deployable artifact — ALWAYS ready to release
                       — but an actual human clicks "deploy" when they
                       decide it's the right time (common in regulated
                       industries, or when releases are deliberately
                       synchronized with business events)

Continuous Deployment: EVERY change that passes automated tests is
                         AUTOMATICALLY deployed to production, no human
                         approval needed — the most aggressive automation
                         level, common at companies like Amazon/Netflix
                         deploying hundreds/thousands of times per day
```

## A Full Pipeline, Stage by Stage
```
1. SOURCE: triggered by a git push/PR
2. BUILD: compile code, build a Docker image, package a dbt project
3. TEST: unit tests, integration tests, data quality tests (dbt test!),
         security scans (checking for known vulnerabilities in dependencies)
4. STAGING DEPLOYMENT: deploy to a staging/pre-production environment that
         mirrors production, run further validation there
5. PRODUCTION DEPLOYMENT: deploy to production (manually approved, or
         fully automatic, depending on CD maturity)
6. POST-DEPLOYMENT VERIFICATION: automated smoke tests confirming the
         deployment actually works correctly in production
7. MONITORING: ongoing observation (file 9) for any issues the deployment introduced
```

## Deployment Strategies — Minimizing Blast Radius
```
Blue-Green Deployment: run TWO complete, identical production environments
  ("blue" = currently live, "green" = new version) — deploy the new
  version to green, test it, then switch ALL traffic to green instantly.
  If something's wrong, switch back to blue instantly — a very fast,
  low-risk rollback mechanism, at the cost of running double infrastructure
  temporarily.

Canary Deployment: roll out the new version to a SMALL percentage of
  traffic/servers first (e.g., 5%), monitor closely for errors, then
  gradually increase to 25%, 50%, 100% if all looks healthy — limits
  blast radius by catching problems while only a small fraction of users
  are affected.

Rolling Deployment: gradually replace OLD instances with NEW ones, one
  (or a few) at a time, rather than all at once — balances safety and
  resource efficiency, a common default in Kubernetes deployments (file 5).

Feature Flags (recap from file 2): decouple DEPLOYING code from RELEASING
  a feature — deploy inactive code, activate it gradually/instantly
  without needing a new deployment at all.
```

## Rollback — The Safety Net
```
A mature CI/CD pipeline makes rolling back to a PREVIOUS known-good
version FAST and RELIABLE — ideally a single command/button, not a
manual, error-prone, multi-hour process. The SPEED and RELIABILITY of
rollback is a genuine measure of DevOps/CI-CD maturity — "how confident
are we that if this deployment goes wrong, we can undo it in minutes, not hours."
```

## Testing Pyramid — What Gets Tested at Each Stage
```
                    /\
                   /  \      Few, SLOW, expensive — full end-to-end
                  / E2E \     tests simulating real user/system behavior
                 /--------\
                / Integr-  \   Moderate number — testing how components
               /  ation     \  work TOGETHER (e.g., a pipeline actually
              /--------------\ writing to a real test database)
             /   Unit Tests    \ MANY, FAST, cheap — testing individual
            /--------------------\ functions in isolation (see
                                    `03-python/13-production-best-practices.md`)
```
**Real guidance**: most of your automated tests should be FAST unit tests (run on every single commit); fewer, slower integration/E2E tests run less frequently (e.g., only before production deployment) — an inverted pyramid (mostly slow E2E tests) makes CI unbearably slow and discourages developers from running tests frequently.

## CI/CD for Infrastructure (tying to Terraform, `07-cloud-platforms/10`)
```
The EXACT same CI/CD discipline applies to infrastructure changes:
  PR with Terraform changes -> CI runs `terraform plan`, posts the plan
  as a PR comment for review -> human approves -> CI runs `terraform apply`
  upon merge — treating infrastructure changes with the same rigor as
  application code changes, not manual console clicks.
```

## Interview Traps
- "What's the real difference between Continuous Delivery and Continuous Deployment?" — Delivery automates up to release-readiness with a human deployment gate; Deployment automates the ENTIRE path to production with no human gate.
- "Explain blue-green vs canary deployment — when would you choose each?" — blue-green gives instant, complete rollback capability at double infrastructure cost, good for critical systems needing near-zero rollback time; canary limits blast radius by gradually increasing exposure, better for catching subtle issues before they affect all users, at the cost of a slower full rollout.
- "Why should most of your automated tests be fast unit tests, not slow E2E tests?" — CI needs to run FREQUENTLY (every commit); slow test suites discourage this frequency and create a bottleneck, defeating CI's core purpose of catching problems immediately and often.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"To automate a task with care is to free the mind for the tasks that truly need it."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
