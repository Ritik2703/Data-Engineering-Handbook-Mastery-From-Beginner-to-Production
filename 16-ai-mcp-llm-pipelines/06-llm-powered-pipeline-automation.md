# 6. LLM-Powered Pipeline Automation — Text-to-SQL & AI-Generated dbt Models

## The Real, Current Use Cases (Not Hype)
By 2026, LLMs are genuinely used across real Data Engineering workflows for: turning a business analyst's plain-English question into SQL, drafting dbt model boilerplate from a schema + a natural-language description, generating data quality test suites automatically, and explaining/documenting existing complex SQL. This file covers each with real, honest context on where AI genuinely helps and where it still needs a human in the loop.

## Text-to-SQL — How It Actually Works in Production
```python
# A production text-to-SQL system needs FAR more than "ask an LLM to write SQL" --
# it needs SCHEMA CONTEXT (via MCP, recap files 3-5) and VALIDATION

def text_to_sql(user_question: str, schema_context: str, dialect: str = "snowflake") -> str:
    prompt = f"""You are a {dialect} SQL expert. Given this schema:

{schema_context}

Write a SQL query to answer: "{user_question}"

Rules:
- Return ONLY the SQL query, no explanation
- Use only tables/columns that exist in the schema above
- Always add a LIMIT clause unless the question requires an aggregate
"""
    generated_sql = call_llm(prompt)
    return generated_sql

def validate_before_execution(sql: str, engine) -> bool:
    """CRITICAL production step -- never execute AI-generated SQL blindly.
    recap the read-only enforcement pattern from file 5."""
    if not is_read_only_query(sql):
        raise ValueError("Generated query is not read-only -- refusing to execute")
    try:
        # EXPLAIN validates the query is syntactically/semantically
        # valid WITHOUT actually running it or returning data
        with engine.connect() as conn:
            conn.execute(text(f"EXPLAIN {sql}"))
        return True
    except Exception as e:
        raise ValueError(f"Generated query failed validation: {e}")
```
**The honest, important caveat**: text-to-SQL genuinely works well for straightforward analytical questions against a WELL-DOCUMENTED schema (recap the catalog/metadata discussion in `15-governance-quality-mlops/02` — the better your data catalog, the better AI-generated queries perform, a genuinely important connection between governance investment and AI capability). It performs meaningfully worse against ambiguous, undocumented, or poorly-named schemas — reinforcing that GOOD DATA MODELING PRACTICE (module 01/05) is a PREREQUISITE for good AI-assisted querying, not a separate concern.

## AI-Assisted dbt Model Generation
```python
# A realistic workflow: an engineer describes a NEW mart model in
# plain English, an LLM drafts the SQL, a human reviews/refines it --
# NOT a fully autonomous "AI writes production dbt models unsupervised" workflow
def draft_dbt_model(description: str, available_staging_models: list[str]) -> str:
    prompt = f"""Given these existing dbt staging models: {available_staging_models}

Draft a dbt SQL model for: "{description}"

Follow these conventions (recap 04-etl-elt/08's dbt patterns):
- Use {{{{ ref() }}}} for referencing other models, never hardcoded table names
- Include a {{{{ config(materialized=...) }}}} block, choosing an
  appropriate materialization
- Add inline comments explaining any non-obvious business logic
"""
    return call_llm(prompt)
```
**Real production workflow this fits into**: the AI-drafted model becomes a STARTING POINT in a Pull Request (recap `10-devops/02`'s PR review discussion), reviewed by a human engineer exactly like any other code contribution — CI still runs `dbt test` (recap `10-devops/08`) regardless of whether a human or an AI drafted the SQL, treating AI-generated code with the SAME rigor as human-written code, not a special exception.

## AI-Generated Data Quality Tests
```python
# Given a table's schema + sample data statistics, an LLM can draft a
# REASONABLE starting set of dbt tests (recap 15-governance-quality-
# mlops/04) -- genuinely useful for bootstrapping test coverage on
# existing, under-tested tables
def suggest_dbt_tests(table_name: str, columns: list[dict], sample_stats: dict) -> str:
    prompt = f"""Given this table '{table_name}' with columns: {columns}
and these sample statistics: {sample_stats}

Suggest a dbt schema.yml tests block covering:
- Appropriate not_null/unique tests based on column names (e.g., ID
  columns should likely be unique/not_null)
- accepted_values tests for columns that look like status/category enums
- Range checks for numeric columns based on the sample statistics provided
"""
    return call_llm(prompt)
```

## Documentation Generation — A Genuinely Low-Risk, High-Value Use Case
```python
# Explaining EXISTING complex SQL is one of the safest, most immediately
# valuable AI use cases -- no risk of the AI producing WRONG results in
# production, since it's purely explanatory
def explain_sql(existing_query: str) -> str:
    prompt = f"""Explain this SQL query in plain English, suitable for a
    non-technical stakeholder. Describe what business question it answers
    and any notable logic (window functions, joins, filters):

{existing_query}
"""
    return call_llm(prompt)
```
This directly supports the documentation practices from `14-internal-tools`'s Confluence discussion — genuinely useful for writing runbooks/documentation for legacy, undocumented SQL inherited from a previous engineer.

## The Honest Line: Where AI Genuinely Helps vs Where Humans Must Stay in the Loop
```
AI genuinely helps with:
- First-draft generation (SQL, dbt models, tests, documentation) --
  accelerating the STARTING point of a task
- Explaining/summarizing existing complex code
- Catching obvious schema mismatches before execution (validation step)

Humans must stay in the loop for:
- Reviewing/approving any AI-generated code before it reaches
  production (the SAME PR review discipline as human-written code,
  recap `10-devops/02`)
- Business logic correctness that requires genuine domain knowledge
  the AI doesn't have (e.g., "does this discount calculation match our
  ACTUAL promotional policy" — the AI can write plausible-LOOKING SQL
  that's subtly wrong about business rules it was never told)
- Final accountability for data quality/correctness -- an AI-authored
  bug is still YOUR team's production incident to own and fix
```

## Interview Traps
- "How would you build a safe text-to-SQL system for business users?" — schema context injection (via MCP/catalog metadata), a validation step (EXPLAIN before execution, read-only enforcement) before EVER running AI-generated SQL against real data, and ideally a human-reviewable output rather than silent auto-execution for anything beyond simple, low-stakes queries.
- "Why does good data modeling/documentation practice directly improve AI-assisted querying quality?" — text-to-SQL and AI-assisted development perform meaningfully better against well-documented, clearly-named, properly-modeled schemas — reinforcing that modules 01/05's data modeling discipline is a genuine PREREQUISITE for effective AI tooling, not a separate concern.
- "Should AI-generated dbt models skip normal code review?" — no; AI-generated code should go through the EXACT same PR review and CI testing discipline as human-written code (recap `10-devops/02` and `10-devops/08`) — treating it as a draft/starting point, not a final, trusted product.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"What is automated without understanding becomes a risk; what is automated with wisdom becomes a gift."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
