# 7. AI Agents for Data Engineering — Self-Healing Pipelines & Autonomous Workflows

## What Makes Something an "Agent" (vs Just an LLM Call)
An AI Agent is an LLM given TOOLS (recap file 1/3) PLUS the ability to operate in a LOOP — observe a situation, decide on an action, execute it (via tool calls), observe the RESULT, and decide the NEXT action, repeating until the task is genuinely complete — rather than a single one-shot prompt-response. This loop is what enables an agent to handle a multi-step, GENUINELY uncertain task (like "figure out why this pipeline failed and fix it") rather than just answering a single well-defined question.

## The Agent Loop, Concretely
```
1. OBSERVE: gather current state (e.g., read the Airflow task failure
   log via an MCP tool, recap files 4-5)
2. THINK/REASON: the LLM reasons about what this observation means and
   what to do next
3. ACT: call a tool to take an action (e.g., query the source table to
   check if the data actually arrived, or check the source API's status page)
4. OBSERVE the RESULT of that action
5. Repeat steps 2-4 until the agent decides the task is complete or it
   needs to escalate to a human
```

## A Concrete Example: An Autonomous Pipeline-Failure-Triage Agent
```python
# A conceptual agent loop for triaging an Airflow task failure --
# built on the SAME MCP tool-calling foundation from files 3-5
import anthropic

client = anthropic.Anthropic()

tools = [
    {"name": "get_airflow_task_log", "description": "Fetches the failure log for a given Airflow task instance", ...},
    {"name": "check_source_api_status", "description": "Checks if the upstream source API is currently healthy", ...},
    {"name": "query_warehouse", "description": "Runs a read-only diagnostic query", ...},  # recap file 5
    {"name": "post_to_slack", "description": "Posts a message to the on-call Slack channel", ...},
    {"name": "trigger_airflow_retry", "description": "Triggers a retry of a specific failed task", ...},
]

def run_triage_agent(failed_dag_id: str, failed_task_id: str):
    messages = [{
        "role": "user",
        "content": f"""The task '{failed_task_id}' in DAG '{failed_dag_id}' just
        failed. Investigate the root cause using the available tools, and:
        - If it's a transient issue (e.g., a temporary API timeout), retry it
          and post a brief Slack summary
        - If it's a genuine data issue (e.g., the source sent malformed data),
          do NOT retry -- post a detailed Slack summary for a human to investigate
        - If you're not confident about the root cause after investigating,
          escalate to Slack rather than guessing"""
    }]

    for _ in range(10):  # a genuinely important safety bound -- NEVER
                          # let an agent loop indefinitely (recap the
                          # "designing for failure" mindset from
                          # 11-system-design/06)
        response = client.messages.create(
            model="claude-sonnet-4-5", max_tokens=2048, tools=tools, messages=messages
        )
        messages.append({"role": "assistant", "content": response.content})

        tool_calls = [b for b in response.content if b.type == "tool_use"]
        if not tool_calls:
            break  # agent has produced a final text response, done

        tool_results = []
        for call in tool_calls:
            result = execute_tool_safely(call.name, call.input)  # YOUR real execution
            tool_results.append({"type": "tool_result", "tool_use_id": call.id, "content": result})
        messages.append({"role": "user", "content": tool_results})
```

## Why the "Never Retry, Only Escalate for Genuine Data Issues" Instruction Matters
This directly encodes the SAME judgment taught in `08-orchestration/04`'s idempotency discussion and `11-system-design/06`'s reliability patterns — an agent that BLINDLY retries every failure risks retrying something that will NEVER succeed (a genuine data quality problem) repeatedly, wasting compute and delaying the REAL fix, or worse, silently "succeeding" on a retry that actually just reprocesses corrupted data. The agent's PROMPT must encode the same operational judgment a senior engineer would apply manually.

## Guardrails for Autonomous Agents — Non-Negotiable Production Requirements
```
1. BOUNDED ACTIONS: an agent should have access ONLY to the SPECIFIC
   tools it genuinely needs (recap the least-privilege principle,
   `07-cloud-platforms/09`) -- an agent triaging pipeline failures does
   NOT need "delete production table" as an available tool, full stop.

2. BOUNDED ITERATIONS: a maximum loop count (shown as `for _ in
   range(10)` above) prevents a genuinely stuck/confused agent from
   looping forever, burning cost and potentially taking repeated
   unintended actions.

3. HUMAN ESCALATION PATH: an agent should be explicitly instructed
   (and structurally ABLE) to say "I'm not confident, escalating to a
   human" rather than being forced to always take SOME action --
   recap the alert-severity discipline from `08-orchestration/08`.

4. FULL AUDIT LOGGING: every tool call an agent makes should be logged
   (recap file 5's audit_log_query pattern) -- if an agent takes an
   unexpected action, you need to be able to trace EXACTLY what it did
   and why, after the fact.

5. DESTRUCTIVE ACTIONS REQUIRE HUMAN APPROVAL: for anything genuinely
   risky (deleting data, modifying production schemas, spending real
   money), a mature agent design REQUIRES a human-in-the-loop
   confirmation step before executing, rather than full autonomy --
   directly mirroring the "Continuous Delivery vs Continuous
   Deployment" human-gate distinction from `10-devops/01`.
```

## Real-World Agentic Data Engineering Use Cases (2025-2026)
```
- Autonomous data quality investigation: an agent that, upon a data
  observability alert (recap `15-governance-quality-mlops/05`),
  automatically investigates likely causes (checking upstream source
  health, recent schema changes, recent code deploys) and produces a
  human-readable root-cause hypothesis BEFORE a human even starts looking

- Automated pipeline documentation maintenance: an agent that detects
  a dbt model's logic changed and drafts an updated description/
  documentation, flagged for human review rather than auto-published

- Cost anomaly investigation: an agent that, given a FinOps cost
  spike alert (recap `07-cloud-platforms/08`), investigates recent
  query history to identify the specific expensive query/job, exactly
  the investigation loop described in that module's FinOps discussion,
  now AUTOMATED as a first-pass investigation rather than manual
```

## Interview Traps
- "What makes something an 'agent' rather than just an LLM API call?" — the LOOP: observing, reasoning, acting via tools, observing results, and repeating across MULTIPLE steps toward a goal, rather than a single one-shot response.
- "What guardrails are non-negotiable for a production autonomous data agent?" — bounded/least-privilege tool access, bounded iteration counts, explicit human-escalation capability, full audit logging, and human approval gates for genuinely destructive actions — never full unbounded autonomy for high-stakes operations.
- "How would you prevent an agent from retrying a failure that will never succeed?" — encode the SAME operational judgment a senior engineer applies (distinguishing transient vs genuine data issues) directly into the agent's instructions/prompt, and bound total retry attempts regardless.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Curiosity about the new, balanced with respect for the old, is the mark of a truly growing mind."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
