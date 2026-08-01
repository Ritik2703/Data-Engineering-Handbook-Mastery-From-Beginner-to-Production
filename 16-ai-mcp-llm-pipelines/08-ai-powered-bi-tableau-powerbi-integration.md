# 8. AI-Powered BI — Tableau/Power BI Native Features PLUS Building Your Own

## Part A: The Native AI Features Already Built Into Tableau & Power BI (recap + depth)

### Power BI Copilot
```
Recap the mention in 09-visualization/08 -- Copilot lets a business
user type a plain-English request ("summarize this quarter's sales
trends and create a visual") directly inside Power BI, and it
generates DAX measures, visuals, and narrative summaries automatically.

Real production consideration: Copilot's quality depends HEAVILY on
your semantic model being well-structured (recap 09-visualization/04's
star schema recommendation, and file 6's "good data modeling is a
prerequisite for good AI" principle) -- a messy, undocumented Power BI
model produces noticeably worse Copilot results than a clean, properly
labeled one with clear measure/column descriptions.
```

### Tableau Pulse / Tableau Einstein (via Salesforce's Tableau acquisition)
```
Tableau Pulse takes a more PROACTIVE approach than a chat interface --
it automatically surfaces "this metric moved significantly, here's a
likely explanation" insights to users' feeds, rather than requiring
them to actively ask a question -- recap the mention in
09-visualization/08. This proactive-insight model is a genuinely
different UX philosophy than the "ask a question, get an answer"
pattern of Copilot/most chat-based AI-BI tools.
```

## Part B: Building Your OWN Natural-Language-to-Dashboard Layer (The Practical Example)

### Why You'd Build This Instead of Just Using Native Copilot/Pulse
```
- Your organization uses an OLDER version of Tableau/Power BI without
  the native AI features (licensing/version constraints)
- You want a UNIFIED natural-language interface across MULTIPLE BI
  tools/data sources, not locked into one vendor's specific AI feature
- You want FULL CONTROL over what data/tables the AI can access (recap
  the least-privilege MCP server design from file 5) -- native
  vendor AI features may have less granular control than a custom-built layer
- You want to embed this INSIDE your own product (recap
  09-visualization/08's embedded analytics discussion), not just
  inside the standalone BI tool's own UI
```

### The Architecture — Natural Language Question to Rendered Chart
```
[User asks in plain English: "Show me revenue by region for the last
 6 months as a bar chart"]
        |
        v
[LLM + your MCP server (recap files 3-5) -- has access to warehouse
 schema via get_table_schema, generates a validated SQL query]
        |
        v
[Query executes against the warehouse -- recap file 5's read-only,
 row-capped, audited execution]
        |
        v
[LLM receives the QUERY RESULTS, decides an appropriate chart type
 (recap 09-visualization/07's chart-selection principles), and
 generates a chart SPECIFICATION (not raw pixels -- structured JSON
 describing chart type, axes, data)]
        |
        v
[Your frontend renders the chart spec using a charting library
 (e.g., Vega-Lite, Chart.js, or triggering an actual Tableau/Power BI
 embedded visual via their respective embedding APIs]
```

### A Working Implementation
```python
# nl_to_dashboard.py -- ties together files 5 (MCP/SQL execution) and
# 09-visualization's chart-selection principles into one pipeline
import json
import anthropic

client = anthropic.Anthropic()

CHART_SELECTION_GUIDANCE = """
When choosing a chart type for the result, follow these rules (recap
09-visualization/07):
- Comparing values across categories -> bar chart
- A trend over time -> line chart
- Part-to-whole composition -> stacked bar (avoid pie charts beyond 3-4 slices)
- A single important number -> a KPI card, not a chart
"""

def natural_language_to_dashboard(user_question: str, schema_context: str):
    # Step 1: generate and validate SQL (recap file 6's text-to-SQL pattern)
    sql = generate_validated_sql(user_question, schema_context)

    # Step 2: execute safely (recap file 5's guardrails)
    results = execute_readonly_query(sql)

    # Step 3: ask the LLM to pick the right chart AND structure the spec
    chart_prompt = f"""Given this query result: {json.dumps(results[:20])}
    (showing first 20 rows) and the original question: "{user_question}"

    {CHART_SELECTION_GUIDANCE}

    Return a JSON chart specification with: chart_type, x_field, y_field,
    title, and a one-sentence insight summary. Return ONLY valid JSON."""

    response = client.messages.create(
        model="claude-sonnet-4-5", max_tokens=1024,
        messages=[{"role": "user", "content": chart_prompt}]
    )
    chart_spec = json.loads(response.content[0].text)

    return {
        "sql_used": sql,           # ALWAYS show the underlying SQL --
                                     # transparency builds trust and lets
                                     # a user/analyst verify correctness
        "chart_spec": chart_spec,
        "raw_data": results,
    }
```
```javascript
// frontend_render.js -- rendering the chart_spec using Vega-Lite
// (a genuinely good choice for AI-generated chart specs, since its
// JSON-based grammar maps cleanly onto what an LLM can reliably generate)
import vegaEmbed from "vega-embed";

function renderAIChart(chartSpec, rawData) {
  const vegaLiteSpec = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "title": chartSpec.title,
    "data": { "values": rawData },
    "mark": chartSpec.chart_type,  // "bar", "line", etc.
    "encoding": {
      "x": { "field": chartSpec.x_field, "type": "nominal" },
      "y": { "field": chartSpec.y_field, "type": "quantitative" }
    }
  };
  vegaEmbed("#chart-container", vegaLiteSpec);
}
```

### Giving Users Real Choice — Multiple Output Options (exactly what was asked for)
```python
# A genuinely useful pattern: don't force ONE output format -- let the
# user (or your product) choose HOW they want the answer delivered,
# reusing the SAME underlying validated query + result
def deliver_answer(user_question: str, schema_context: str, output_preference: str):
    sql = generate_validated_sql(user_question, schema_context)
    results = execute_readonly_query(sql)

    if output_preference == "quick_answer":
        # Just a plain-English answer, no chart -- fastest, for a
        # simple single-number question ("what was last month's revenue?")
        return summarize_as_text(results, user_question)

    elif output_preference == "inline_chart":
        # The custom Vega-Lite chart pipeline shown above -- fast,
        # embedded directly in YOUR app's chat/interface
        return natural_language_to_dashboard(user_question, schema_context)

    elif output_preference == "power_bi_dashboard":
        # Push the result into an EXISTING Power BI dataset via the
        # REST API (recap 09-visualization/04's Power BI REST API
        # pattern) and return a link to the LIVE Power BI report --
        # best when the user wants to keep exploring interactively in
        # a full BI tool rather than a one-off chart
        push_to_powerbi_dataset(results, dataset_id="ai_adhoc_queries")
        return {"powerbi_report_link": get_powerbi_embed_url()}

    elif output_preference == "tableau_workbook":
        # Similarly, write results to a staging table Tableau is
        # already connected to (recap 09-visualization/03's extract/
        # live connection discussion), then trigger an extract refresh
        # via the Tableau REST API
        write_to_tableau_staging_table(results)
        trigger_tableau_extract_refresh(workbook_id="ai_adhoc_analysis")
        return {"tableau_workbook_link": get_tableau_view_url()}
```
**This is the genuinely practical "give users options" pattern**: the EXPENSIVE, safety-critical part (validated SQL generation + safe execution, files 5-6) happens ONCE, and the CHEAP part (how to visually present/deliver it) is a simple branch based on user preference — quick text answer for simple questions, an inline AI-generated chart for fast exploration, or pushing into the full Tableau/Power BI tool for users who want to keep digging interactively.

## Interview Traps
- "Would you always build a custom natural-language-to-dashboard layer instead of using Power BI Copilot/Tableau Pulse?" — no; a nuanced answer weighs native features (less engineering effort, vendor-maintained) against custom builds (full control over data access/security, multi-tool unification, embeddability) — the right choice depends on the organization's specific constraints (recap module 11's tradeoff-framing discipline).
- "Why always show the underlying SQL alongside an AI-generated chart?" — transparency and trust — lets a technical user/analyst verify the AI didn't misinterpret the question, and is a genuinely important practice for any AI-generated data output in production.
- "How would you let users choose between a quick text answer, an inline chart, or a full Tableau/Power BI dashboard for the same question?" — separate the EXPENSIVE, safety-critical step (validated query generation + execution, done once) from the CHEAP presentation-format branch (text summary vs custom chart vs pushing to an existing BI tool via its REST API) — exactly the pattern shown above.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Every powerful tool asks the same question of its maker: will you wield it with humility?"*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
