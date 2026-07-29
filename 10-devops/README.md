# 10 — DevOps: The Bridge Between Local Development and Production

DevOps is the discipline (and culture) that connects "it works on my laptop" to "it works reliably in production, for everyone, every time." This module takes you from zero — what even is DevOps, why did it need to become its own discipline — through Git, CI/CD, Docker, Kubernetes, all the way to what a Data Engineer specifically needs from DevOps in 2026.

## 📖 Learning Path

| # | File | Level | Covers |
|---|---|---|---|
| 1 | [`01-what-is-devops.md`](./01-what-is-devops.md) | Beginner | The Dev vs Ops divide, why DevOps emerged, culture + tools, history |
| 2 | [`02-git-version-control-deep-dive.md`](./02-git-version-control-deep-dive.md) | Beginner-Intermediate | Git internals, branching strategies, real workflows |
| 3 | [`03-cicd-fundamentals.md`](./03-cicd-fundamentals.md) | Intermediate | CI vs CD vs Continuous Deployment, pipeline stages explained deeply |
| 4 | [`04-docker-containers-deep-dive.md`](./04-docker-containers-deep-dive.md) | Intermediate | Why containers, images vs containers, Dockerfile best practices |
| 5 | [`05-kubernetes-deep-dive.md`](./05-kubernetes-deep-dive.md) | Advanced | Pods, Deployments, Services — orchestrating containers at scale |
| 6 | [`06-cicd-tools-evolution.md`](./06-cicd-tools-evolution.md) | Intermediate-Advanced | Jenkins → GitHub Actions/GitLab CI/CircleCI — what changed and why |
| 7 | [`07-infrastructure-as-code-config-management.md`](./07-infrastructure-as-code-config-management.md) | Advanced | Terraform recap + Ansible/Chef/Puppet, the full IaC landscape |
| 8 | [`08-devops-for-data-engineers.md`](./08-devops-for-data-engineers.md) | Production | The SPECIFIC DevOps practices a Data Engineer actually needs |
| 9 | [`09-monitoring-observability.md`](./09-monitoring-observability.md) | Production | Prometheus, Grafana, logging — knowing when something's wrong |
| 10 | [`10-what-companies-use.md`](./10-what-companies-use.md) | Production | Real company DevOps stacks and the history behind them |
| — | [`case-studies/`](./case-studies/) | Production | Full CI/CD pipeline design for a real data platform |
| — | [`interview-questions.md`](./interview-questions.md) | All levels | 35+ Q&A across the whole module |

## 🎯 The Core Question This Module Answers
```
Why can't a Data Engineer just "write the pipeline and run it"?
Because between writing code on YOUR laptop and it running reliably in
PRODUCTION for the whole company, there's a chasm: different environments,
manual deployment mistakes, no repeatability, no safety net when something
breaks. DevOps is the entire discipline of closing that chasm — reliably,
repeatably, and fast.
```

## 🗺️ Suggested Path
```
Total beginner:       01 -> 02 -> 03
Building pipelines:   04 -> 05 (containers are foundational to nearly everything else)
CI/CD in practice:    06 -> 07
DE-specific:           08 (this is the file that ties everything back to YOUR job)
Production reality:    09 + case-studies/
Interview prep:        10 + interview-questions.md
```


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"A pipeline built with patience rarely needs to be rebuilt in panic."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
