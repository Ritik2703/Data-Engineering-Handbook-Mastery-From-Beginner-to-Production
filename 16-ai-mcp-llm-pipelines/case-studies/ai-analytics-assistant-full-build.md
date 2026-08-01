# Case Study: Building a Complete AI-Powered Analytics Assistant (MCP + Agent + BI Integration)

## Business Scenario
A mid-size retail company (recap the recurring retail scenario from modules 04/13) wants their business analysts to ask plain-English questions about sales data and get answers — either as quick text, an inline chart, or pushed into their existing Power BI dashboards — while a separate autonomous agent monitors and triages nightly pipeline failures.

## Architecture — Everything in This Module, Combined
```
[Business Analyst types: "Which regions underperformed target last week?"]
        |
        v
[Claude (MCP Client) <--MCP Protocol--> Retail Data MCP Server]
        |                                        |
        |                             (recap files 3-5: tools for
        |                              query_warehouse, get_table_schema,
        |                              list_available_tables -- read-only,
        |                              row-capped, audited, schema-restricted)
        |
        v
[Validated SQL generated (recap file 6) -> executed safely -> results
 returned to Claude]
        |
        v
[Claude selects chart_type + generates chart spec (recap file 8) OR
 pushes results into an existing Power BI dataset via REST API,
 based on the analyst's stated preference]

--- SEPARATELY, running on a schedule ---

[Airflow nightly pipeline fails] --triggers--> [Triage Agent (recap
 file 7) investigates via: get_airflow_task_log, check_source_api_status,
 query_warehouse tools] --> [Decides: transient (auto-retry + Slack
 summary) OR genuine data issue (escalate to on-call, no retry)]
```

## Stage 1: The MCP Server (recap file 5's production pattern directly)
```python
# retail_mcp_server.py -- reuses the EXACT structure from file 5,
# scoped specifically to this company's retail schema
ALLOWED_SCHEMAS = {"retail_analytics"}
MAX_ROWS_RETURNED = 500

# Tools: query_warehouse, get_table_schema, list_available_tables --
# identical implementation to file 5, connected to THIS company's
# actual Snowflake warehouse via their own connection string/credentials
```

## Stage 2: The Analyst-Facing Query Flow (recap files 6 and 8)
```python
def handle_analyst_question(question: str, output_preference: str):
    schema_context = get_schema_context_via_mcp()  # recap file 5's
                                                      # get_table_schema
                                                      # and list_available_tables

    sql = generate_validated_sql(question, schema_context, dialect="snowflake")
    # recap file 6's validate_before_execution -- EXPLAIN check before running

    results = execute_readonly_query(sql)  # recap file 5's audited,
                                             # row-capped execution

    return deliver_answer_by_preference(question, results, sql, output_preference)
    # recap file 8's branching: quick_answer / inline_chart / power_bi_dashboard
```
**A real interaction**: "Which regions underperformed target last week?" → SQL joining `fct_sales` and `dim_region` with a target comparison → analyst chose `power_bi_dashboard` preference → results pushed to an "AI Ad-Hoc Queries" Power BI dataset via the REST API (recap `09-visualization/04`), analyst gets a link to explore the LIVE Power BI report interactively, with full drill-down capability the custom chart alone wouldn't offer.

## Stage 3: The Autonomous Triage Agent (recap file 7)
```python
# Triggered by an Airflow on_failure_callback (recap 08-orchestration/04)
def on_pipeline_failure(context):
    dag_id = context["dag"].dag_id
    task_id = context["task_instance"].task_id
    run_triage_agent(dag_id, task_id)  # recap file 7's full agent loop
```
**A real scenario**: the nightly `load_daily_sales` DAG fails. The agent calls `get_airflow_task_log`, sees a connection timeout error. It calls `check_source_api_status` and finds the POS vendor's API status page reports a known ongoing outage. It concludes this is TRANSIENT, calls `trigger_airflow_retry`, and posts to Slack: *"load_daily_sales failed due to a confirmed POS vendor API outage (their status page shows ongoing incident). Triggered automatic retry. Will re-alert if the retry also fails."* — genuinely useful, correctly-scoped autonomous behavior, with full audit logging (recap file 5) of every tool call it made.

## Stage 4: Security & Governance Applied (recap file 10, tying to module 15)
```
- The MCP server's database credential is a genuinely READ-ONLY
  database role (recap file 5's defense-in-depth principle) -- even
  if somehow tricked, it structurally CANNOT modify data
- The triage agent's tools are scoped to READ logs/status + Slack
  posting + a SPECIFIC retry action -- it has NO access to delete
  DAGs, modify production code, or access unrelated systems
- Every query (both analyst-facing and agent-triggered) is audit-logged
  (recap file 5's audit_log_query), with the underlying SQL always
  shown back to the analyst for transparency (recap file 8's
  "always show the SQL" principle)
- The retail_analytics schema is EXPLICITLY allowlisted (recap file 5) --
  neither the analyst-facing assistant nor the triage agent can
  accidentally wander into an unrelated HR or finance schema
```

## Why This Case Study Demonstrates the Whole Module
```
Every file appears here, working together on one coherent, realistic
system: MCP fundamentals and server-building (files 3-5), validated
text-to-SQL (file 6), an autonomous agent with proper guardrails
(file 7), multi-format BI delivery giving the analyst real choice
(file 8), and security/governance applied throughout (file 10) --
exactly the kind of "AI genuinely integrated into a real data
platform, safely" system that represents the current, honest state
of the art in 2026, neither underselling AI's real usefulness nor
overselling it as fully autonomous magic.
```

## Try It Yourself
1. Extend the triage agent to also check recent Git commits to the DAG's own code (recap `10-devops/02`) as a possible root cause candidate, alongside source API health.
2. Design the classification/access-control scoping (recap module 15) needed if this same assistant needed to answer questions touching PII-classified customer data, not just aggregate sales figures.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"May whatever you build with this knowledge serve others faithfully, and may your own heart stay humble."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
