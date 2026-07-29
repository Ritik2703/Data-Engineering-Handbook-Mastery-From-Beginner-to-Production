# DevOps Interview Questions — 35+ with Answers

## Fundamentals & History

**Q1. Why did DevOps emerge as its own discipline?**
> The structural Dev/Ops incentive conflict (Dev wants frequent change, Ops wants stability) caused real organizational dysfunction — infrequent, risky deployments and a blame culture when things broke. DevOps culture aligns incentives via shared ownership and heavy automation making frequent change safe.

**Q2. What's the difference between Continuous Delivery and Continuous Deployment?**
> Delivery automates up to release-readiness (built, tested, packaged) but requires a human to approve actual deployment; Deployment automates the entire path to production with no human gate.

**Q3. Why is "ship small, ship often" actually safer than infrequent big releases?**
> Small changes are easier to test, easier to diagnose if something breaks, and have a smaller blast radius than a giant release bundling hundreds of changes at once.

**Q4. What's "immutable infrastructure"?**
> Instead of patching a running server/container in place, you build a new image with the fix and replace the old one entirely — reducing configuration drift over time.

## Git

**Q5. Explain a merge conflict and how you'd resolve one.**
> Occurs when two branches change the same lines of the same file differently; resolved by manually editing to keep the intended combination of changes, removing Git's conflict markers, then committing.

**Q6. GitFlow vs GitHub Flow vs Trunk-Based Development?**
> GitFlow is structured but heavier (multiple long-lived branch types); GitHub Flow is simpler, favoring continuous deployment via short-lived feature branches; Trunk-Based uses very short-lived branches/frequent small merges, often behind feature flags, minimizing long-branch merge pain.

**Q7. Why shouldn't you commit large data files directly to Git?**
> Git's snapshot model isn't designed for large binaries (bloats repo size/clone time); use Git LFS or, better, keep data in appropriate storage (S3/data lake) and version-control only the processing code.

## CI/CD

**Q8. Explain the full pipeline stages from code commit to production.**
> Source (triggered by push/PR) → Build → Test (unit/integration/data quality/security) → Staging deployment → Production deployment → Post-deployment verification → Monitoring.

**Q9. Blue-green vs canary deployment — when would you choose each?**
> Blue-green gives instant, complete rollback via traffic switching, at double infrastructure cost — good for near-zero rollback time needs; canary gradually increases exposure to catch subtle issues before affecting all users, at the cost of a slower full rollout.

**Q10. Why should most automated tests be fast unit tests, not slow E2E tests?**
> CI needs to run frequently (every commit); slow test suites create a bottleneck that discourages this frequency, defeating CI's core purpose of catching problems immediately.

## Docker & Kubernetes

**Q11. Container vs VM — what's the real architectural difference?**
> Containers share the host OS kernel directly (lightweight, fast startup, MBs in size); VMs virtualize entire hardware with a full separate guest OS each (heavier, slower, stronger isolation).

**Q12. Why does Dockerfile instruction order matter for build performance?**
> Docker's layer caching reuses unchanged layers; putting rarely-changing steps (dependency installation) before frequently-changing steps (copying application code) maximizes cache reuse and speeds up builds.

**Q13. What's a multi-stage Docker build and why use one?**
> Separates the build environment (heavy tools/compilers) from the final runtime image, keeping production images small, faster to deploy, with less attack surface.

**Q14. What's the difference between a Pod and a Deployment in Kubernetes?**
> A Pod is the smallest deployable unit (usually one container); a Deployment manages multiple Pod replicas, ensures desired state is maintained (auto-restarting failed Pods), and handles rolling updates.

**Q15. Why do you need a Kubernetes Service if Pods already have IP addresses?**
> Pod IPs are ephemeral, changing whenever a Pod is recreated; a Service provides a stable address automatically routing to whichever Pods are currently healthy.

## Infrastructure & Configuration Management

**Q16. What's the difference between Infrastructure as Code and Configuration Management?**
> IaC provisions the resources themselves (servers, networks, databases — Terraform); Configuration Management configures software running on already-provisioned servers (Ansible/Chef/Puppet).

**Q17. Why did Ansible become popular despite Puppet/Chef's head start?**
> Agentless design (just needs SSH, no persistent agent required on managed servers), dramatically simplifying adoption compared to Puppet/Chef's agent-based model.

**Q18. Why has configuration management become less central to modern deployment than a decade ago?**
> Containers increasingly bake configuration directly into immutable images that get replaced rather than configured in-place, absorbing much of configuration management's traditional job for containerized workloads.

**Q19. What is GitOps and why does it matter for Kubernetes?**
> A philosophy where Git is the single source of truth for infrastructure/deployment state, with a tool (ArgoCD/Flux) continuously syncing the actual running system to match Git — simplifying auditing and reducing configuration drift.

## DevOps for Data Engineers

**Q20. How is testing a data pipeline genuinely different from testing a typical web application?**
> Needs representative, realistic sample data covering real-world messiness (nulls, duplicates, edge cases), not just clean idealized fixtures; often needs a dedicated staging schema/environment for validating transformation logic at real scale before touching production.

**Q21. How would you set up CI/CD for a dbt project?**
> A pipeline running `dbt build`/`dbt test` against a dedicated CI/staging schema on every PR, never directly against production, gating merge on all tests passing.

**Q22. What should and shouldn't live in Git for a data platform?**
> SHOULD: DAGs, dbt models/tests, Python pipeline code, Terraform configs, SQL DDL. SHOULD NOT: the actual data itself (use S3/a data lake) or secrets/credentials (use a secrets manager).

**Q23. How would you validate an Airflow DAG before it reaches production?**
> A CI step loading the DagBag and asserting zero import errors, catching syntax/import mistakes that could otherwise silently prevent the DAG from running or degrade Scheduler performance.

**Q24. What's a "shadow deployment" and when would you use one for a data pipeline?**
> Running a new pipeline version alongside the existing production version temporarily, comparing outputs (e.g., via a FULL OUTER JOIN reconciliation) before fully cutting over — useful for validating significant transformation logic changes at real scale before trusting them fully.

## Monitoring & Observability

**Q25. What are the three pillars of observability, and why do you need all three?**
> Metrics (trends/alerting), logs (detailed event debugging), traces (following a request across services) — complementary, each answering a different diagnostic question.

**Q26. What's the difference between an SLI, SLO, and SLA?**
> SLI is the actual measurement (e.g., 99.2% success rate); SLO is your internal target (e.g., 99.9%); SLA is an external, often contractual commitment, typically looser than your SLO to provide margin.

**Q27. What's an error budget, and how is it used?**
> The allowed amount of unreliability implied by your SLO (e.g., 0.1% for a 99.9% SLO), used to deliberately guide how much deployment/experimentation risk a team can take before needing to prioritize stability over new features.

**Q28. Why should alerting be metric-based rather than single-event-based?**
> A single error doesn't necessarily indicate an incident; alerting on a sustained rate/threshold (e.g., "error rate > 5% for 5 minutes") avoids noise and alert fatigue while still catching genuine problems.

## Real-World / Company Practices

**Q29. What is Chaos Engineering, and why is it valuable despite being counter-intuitive?**
> Deliberately, randomly breaking production infrastructure (Netflix's Chaos Monkey) to continuously verify systems survive real failures — proactively finding weaknesses on your own terms rather than discovering them during an uncontrolled real incident.

**Q30. What does "you build it, you run it" mean, and why does it matter?**
> The same team that builds a service is also responsible for operating it in production, directly embodying DevOps's shared-ownership philosophy rather than a traditional adversarial Dev/Ops split.

**Q31. What is Site Reliability Engineering (SRE)?**
> Google's specific formalization of DevOps principles, treating operations as a software engineering problem (automating away manual toil with code), and popularizing concepts like error budgets/SLOs now used industry-wide.

## Rapid-Fire
32. What's a rollback, and why does its speed matter? *(Reverting to a previous known-good version when a deployment causes problems; fast, reliable rollback is a genuine measure of DevOps maturity.)*
33. What's "blast radius" in a deployment context? *(How much of the system is affected if a specific component/deployment fails; good practice deliberately minimizes it.)*
34. What's a feature flag used for? *(Decoupling deploying code from releasing a feature — merge and deploy inactive code, activate it gradually or instantly without a new deployment.)*
35. Why is a blameless post-mortem culture valuable? *(Focuses on fixing the system/process that allowed a failure rather than punishing an individual, genuinely improving long-term reliability.)*
36. What's the testing pyramid, and why does its shape matter? *(Many fast unit tests at the base, fewer slower integration tests, fewest slow E2E tests at the top; an inverted pyramid makes CI unbearably slow.)*

---

**Practice tip**: For DevOps questions specifically, always ground abstract concepts (blast radius, error budgets, GitOps) in a CONCRETE example — interviewers consistently rate applied reasoning far higher than reciting definitions.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The one who documents clearly today saves a stranger's tomorrow from confusion."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
