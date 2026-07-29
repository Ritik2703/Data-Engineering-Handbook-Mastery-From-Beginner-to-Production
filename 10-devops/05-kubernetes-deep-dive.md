# 5. Kubernetes — Deep Dive

## The Problem Kubernetes Solves — Managing Containers at Scale
Docker packages ONE application into a container beautifully — but a real production system might run HUNDREDS of containers across MANY machines: how do you decide which container runs on which machine? What happens when a container crashes — who restarts it? How do you roll out an update to 50 running containers safely? How does one container find and talk to another? **Kubernetes (K8s) is the system that answers all of these questions automatically**, born from Google's internal container-orchestration system ("Borg") and open-sourced in 2014.

## Core Concepts — The Building Blocks

### Pod — The Smallest Deployable Unit
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: orders-etl-pod
spec:
  containers:
    - name: orders-etl
      image: my-registry/orders-etl:v1.2
```
A Pod usually wraps ONE container (sometimes a few tightly-coupled ones sharing resources) — it's the basic unit Kubernetes schedules onto a machine, NOT the container directly.

### Deployment — Managing Multiple Replicas & Rolling Updates
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orders-api
spec:
  replicas: 3                # run 3 identical copies for availability/load
  selector:
    matchLabels: {app: orders-api}
  template:
    metadata:
      labels: {app: orders-api}
    spec:
      containers:
        - name: orders-api
          image: my-registry/orders-api:v2.0
  strategy:
    type: RollingUpdate       # gradually replace old pods with new ones
                                # (recap from file 3's deployment strategies)
```
A Deployment ensures the DESIRED state (e.g., "3 replicas always running") is continuously maintained — if a Pod crashes, Kubernetes automatically starts a replacement, without any human intervention.

### Service — Stable Networking for Pods That Come and Go
```yaml
apiVersion: v1
kind: Service
metadata:
  name: orders-api-service
spec:
  selector: {app: orders-api}
  ports:
    - port: 80
      targetPort: 8080
```
Pods are EPHEMERAL — they get created/destroyed/replaced constantly (crashes, rolling updates, scaling), each getting a NEW internal IP address each time. A Service provides a STABLE, unchanging address/DNS name that automatically routes traffic to WHICHEVER Pods are currently healthy and running — solving the "how do other components find this constantly-changing set of Pods" problem.

### ConfigMaps & Secrets — Externalizing Configuration
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
data:
  password: cGFzc3dvcmQ=   # base64-encoded — NOT truly encrypted at rest by
                             # default; real production secrets typically
                             # integrate with a proper secrets manager
                             # (Vault, AWS Secrets Manager) instead
```
ConfigMaps hold non-sensitive configuration; Secrets hold sensitive values — both let you change configuration WITHOUT rebuilding the container image itself, following the same "never hardcode config/credentials" principle from `03-python/07-09`.

## Namespaces — Logical Isolation Within a Cluster
```
Namespaces let you partition ONE physical Kubernetes cluster into
multiple logical environments (e.g., "development," "staging,"
"production," or per-team) — providing organizational isolation and
access control boundaries without needing entirely SEPARATE physical clusters.
```

## Horizontal Pod Autoscaler (HPA) — Automatic Scaling
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: orders-api-hpa
spec:
  scaleTargetRef: {apiVersion: apps/v1, kind: Deployment, name: orders-api}
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource: {name: cpu, target: {type: Utilization, averageUtilization: 70}}
```
Automatically adds/removes Pod replicas based on real-time load (e.g., CPU utilization) — directly implementing the elasticity concept from `07-cloud-platforms/02-cloud-fundamentals-deep.md` at the application/container level.

## Kubernetes for Data Engineering Specifically
```
- KubernetesExecutor for Airflow (`08-orchestration/02`): each task gets
  its own isolated Pod, spun up and torn down per task run
- Running Spark on Kubernetes (`06-big-data/07`): Kubernetes has become
  a genuine alternative to YARN as a Spark cluster manager
- Running dbt/Python transformation jobs as scheduled Kubernetes Jobs
  (a Kubernetes resource type specifically for run-to-completion tasks,
  as opposed to Deployments which run continuously)
- Self-hosted data tools (a self-managed Airflow, Superset, or JupyterHub
  instance) commonly run ON Kubernetes for the same scaling/reliability
  benefits any other application gets from it
```

## Helm — Kubernetes' "Package Manager"
```bash
helm install my-airflow apache-airflow/airflow --set executor=KubernetesExecutor
```
Helm packages a complex set of Kubernetes YAML files (a full Airflow deployment might need dozens of interrelated resource definitions) into a single, configurable, reusable "Chart" — similar in spirit to how `pip install` or `apt install` package complex software for easier reuse, rather than hand-writing every YAML file from scratch each time.

## Interview Traps
- "What's the difference between a Pod and a Container?" — a Pod is Kubernetes' smallest deployable/schedulable unit, usually wrapping one (sometimes a few tightly-coupled) container(s); you don't schedule containers directly, you schedule Pods.
- "Why do you need a Service if Pods already have IP addresses?" — Pod IPs are EPHEMERAL, changing every time a Pod is recreated (crash, rolling update, scaling); a Service provides a stable address automatically routing to whichever Pods are currently healthy.
- "How does Kubernetes relate to Airflow's KubernetesExecutor?" — each Airflow task run gets spun up as its OWN isolated Pod (independent dependency environment) and torn down after completion, giving genuine per-task isolation and elastic resource usage.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Small, honest steps taken daily outpace grand plans announced but never walked."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
