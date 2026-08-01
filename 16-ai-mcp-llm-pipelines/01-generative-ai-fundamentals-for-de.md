# 1. Generative AI Fundamentals for Data Engineers (Zero Assumed Knowledge)

## What Is a Large Language Model (LLM), In Plain Terms
An LLM (like Claude, GPT, Gemini, or Llama) is a model trained on enormous amounts of text that learns to predict "what word/token comes next" given everything before it — repeated at massive scale, this simple prediction task produces a model that can write code, answer questions, summarize documents, and reason through problems. For a Data Engineer, the crucial thing to understand isn't the deep neural network math — it's how to feed an LLM the RIGHT information and CONNECT it to real systems, which is exactly what this module teaches.

## Tokens — The Actual Unit LLMs Process
```
LLMs don't read "words" — they read TOKENS, which are often sub-word
chunks (e.g., "unbelievable" might split into "un", "believ", "able").
Practical implications for a Data Engineer:
  - API costs are billed PER TOKEN (both input and output) — a genuinely
    real cost consideration when building AI-powered pipelines at scale
  - Every model has a CONTEXT WINDOW limit (the max tokens it can
    process in one request, e.g., 200K tokens) — this directly drives
    WHY you can't just paste your entire 500-table warehouse schema
    into a prompt and expect it to work well, motivating retrieval
    strategies (file 2) instead of "paste everything"
```

## Embeddings — Recap + Why They Matter Here Specifically
Recap `05-databases/06-vector-databases-ai-era.md` in full — an embedding is a list of numbers representing a piece of text's MEANING, such that semantically similar text produces mathematically close vectors. This module builds directly on that foundation: RAG (file 2) and MCP-connected tools (files 3-5) both fundamentally rely on finding the RIGHT relevant information to give an LLM, and embeddings are the primary technical mechanism for that "finding" step.

## Prompt Engineering — The Practical Skill (a quick primer)
```
A well-structured prompt for a DATA task typically includes:
1. Clear ROLE/CONTEXT ("You are a SQL expert working with a Snowflake warehouse")
2. The SPECIFIC TASK ("Write a query to find the top 10 customers by revenue")
3. RELEVANT CONTEXT the model needs (the actual table schema — this is
   exactly what MCP/RAG automate the retrieval of, rather than a human
   manually copy-pasting schema into every prompt)
4. OUTPUT FORMAT constraints ("Return only the SQL query, no explanation")
5. Constraints/guardrails ("Never use DELETE or DROP statements")
```

## Function Calling / Tool Use — The Concept That Makes Everything in This Module Possible
```
Modern LLMs can be given a list of AVAILABLE TOOLS (e.g., "run_sql_query",
"read_file", "search_database_schema") with descriptions of what each
does and what parameters they need. The model then decides, based on
the user's request, WHICH tool to call and WITH WHAT parameters —
the model itself doesn't execute anything; YOUR CODE receives the
model's tool-call request, actually runs it, and returns the result
back to the model to continue reasoning.

This "tool use" / "function calling" capability is the SINGLE
foundational concept underlying MCP (file 3), AI agents (file 7), and
every "AI that can actually DO things, not just talk" system covered
in this module.
```
```python
# A simplified illustration of the tool-calling loop (conceptual,
# using the Anthropic API structure)
import anthropic

client = anthropic.Anthropic()

tools = [{
    "name": "run_sql_query",
    "description": "Executes a read-only SQL query against the warehouse and returns results",
    "input_schema": {
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"]
    }
}]

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "What were our top 5 products by revenue last month?"}]
)

# The model responds with a TOOL USE request (not the final answer yet) --
# YOUR code must detect this, actually run the SQL, and send the result BACK
for block in response.content:
    if block.type == "tool_use" and block.name == "run_sql_query":
        actual_query = block.input["query"]
        result = execute_sql_safely(actual_query)  # YOUR real execution logic
        # ... send result back to the model in a follow-up message ...
```

## Why This Matters More Than Ever for Data Engineers in 2026
```
Every AI system that can "look at your data and answer a real business
question" or "fix a broken pipeline" is built on this exact tool-calling
foundation, connected to REAL systems (databases, APIs, orchestrators)
that a Data Engineer builds and maintains. The AI doesn't replace the
Data Engineer's role here — it creates a NEW category of system
(MCP servers, AI agents) that Data Engineers are increasingly
responsible for building, securing, and operating.
```

## Interview Traps
- "What's the difference between an LLM just 'chatting' and an LLM 'using tools'?" — chatting only produces text; tool use lets the model request that YOUR code execute a real action (a query, an API call) and feed the result back, enabling the model to interact with real systems rather than just generate text about them.
- "Why can't you just paste an entire database schema into every prompt?" — context window limits and per-token cost make this impractical at scale, especially for large schemas — motivating retrieval-based approaches (RAG, file 2) that fetch only the RELEVANT subset of context for a given request.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"New tools will keep arriving, but the seeker who understands first principles adapts to any of them."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
