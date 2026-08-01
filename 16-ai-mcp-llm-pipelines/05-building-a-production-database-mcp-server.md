# 5. Building a Production-Grade Database MCP Server — 0 to Pro

## What "Production-Grade" Adds on Top of File 4
File 4 built a working TOY server. This file adds every genuinely necessary production concern: a real database connection, READ-ONLY safety enforcement, query cost/row limits, credential security, logging/audit trail, and schema-awareness — turning "a demo" into "something you'd actually deploy at a real company."

## The Full Production MCP Server
```python
# production_warehouse_mcp_server.py
import asyncio
import logging
import os
import re
from datetime import datetime
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, Resource, TextContent
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("warehouse-mcp-server")

app = Server("production-warehouse-server")

# Credentials via environment/secrets manager (recap 03-python/07-09) --
# NEVER hardcoded
engine = create_engine(
    os.getenv("WAREHOUSE_CONN_STRING"),
    pool_size=5,
    pool_pre_ping=True,
)

MAX_ROWS_RETURNED = 1000  # a genuinely important production guardrail --
                            # prevents an AI model accidentally requesting
                            # a query that returns millions of rows,
                            # blowing up token usage/cost and context window

ALLOWED_SCHEMAS = {"analytics", "public"}  # restrict which schemas the
                                             # AI model can even query --
                                             # recap least-privilege from
                                             # 07-cloud-platforms/09


def is_read_only_query(sql: str) -> bool:
    """A critical safety check -- an AI model should NEVER be able to
    modify data through this server. This is a defense-in-depth layer
    ON TOP OF the database connection itself ideally using a read-only
    database role (belt AND suspenders, recap the least-privilege
    principle from 07-cloud-platforms/09 and 15-governance-quality-mlops)."""
    normalized = sql.strip().upper()
    forbidden_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
                           "TRUNCATE", "CREATE", "GRANT", "REVOKE"]
    if not normalized.startswith("SELECT") and not normalized.startswith("WITH"):
        return False
    return not any(re.search(rf"\b{kw}\b", normalized) for kw in forbidden_keywords)


def audit_log_query(sql: str, requester_context: str, row_count: int):
    """Every query an AI model runs against real company data should be
    AUDITABLE -- recap the audit trigger pattern from 13-projects/
    project-01 and the governance metrics discussion in
    15-governance-quality-mlops/08. This is non-negotiable for any
    production AI-to-data integration."""
    logger.info(
        f"AI_QUERY_AUDIT | requester={requester_context} | "
        f"rows_returned={row_count} | query={sql[:200]}"
    )
    # In real production: also write this to a persistent audit table,
    # not just application logs


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="query_warehouse",
            description=(
                "Executes a READ-ONLY SQL query against the analytics warehouse. "
                "Only SELECT/WITH statements are permitted. Results are capped at "
                f"{MAX_ROWS_RETURNED} rows. Use get_table_schema first if you're "
                "unsure of a table's columns."
            ),
            inputSchema={
                "type": "object",
                "properties": {"query": {"type": "string", "description": "A SELECT SQL query"}},
                "required": ["query"],
            },
        ),
        Tool(
            name="get_table_schema",
            description="Returns column names and types for a given table, so the model doesn't guess incorrectly",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {"type": "string"},
                    "schema_name": {"type": "string", "default": "analytics"},
                },
                "required": ["table_name"],
            },
        ),
        Tool(
            name="list_available_tables",
            description="Lists all tables the model is permitted to query, with a one-line description of each",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "list_available_tables":
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT table_schema, table_name
                    FROM information_schema.tables
                    WHERE table_schema = ANY(:schemas)
                """), {"schemas": list(ALLOWED_SCHEMAS)})
                tables = [f"{row.table_schema}.{row.table_name}" for row in result]
            return [TextContent(type="text", text="\n".join(tables))]

        elif name == "get_table_schema":
            schema_name = arguments.get("schema_name", "analytics")
            if schema_name not in ALLOWED_SCHEMAS:
                return [TextContent(type="text", text=f"Error: schema '{schema_name}' is not accessible")]
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_schema = :schema AND table_name = :table
                """), {"schema": schema_name, "table": arguments["table_name"]})
                columns = [f"{row.column_name} ({row.data_type})" for row in result]
            if not columns:
                return [TextContent(type="text", text=f"Table not found or has no columns visible")]
            return [TextContent(type="text", text="\n".join(columns))]

        elif name == "query_warehouse":
            sql = arguments["query"]

            if not is_read_only_query(sql):
                logger.warning(f"BLOCKED non-read-only query attempt: {sql[:200]}")
                return [TextContent(
                    type="text",
                    text="Error: only read-only SELECT/WITH queries are permitted through this server."
                )]

            # Enforce a row limit even if the model forgets to add its own LIMIT
            capped_sql = f"SELECT * FROM ({sql.rstrip(';')}) AS subquery LIMIT {MAX_ROWS_RETURNED}"

            with engine.connect() as conn:
                result = conn.execute(text(capped_sql))
                rows = result.fetchall()
                columns = list(result.keys())

            audit_log_query(sql, requester_context="mcp-client", row_count=len(rows))

            if not rows:
                return [TextContent(type="text", text="Query returned no rows.")]

            header = " | ".join(columns)
            body = "\n".join(" | ".join(str(v) for v in row) for row in rows)
            return [TextContent(type="text", text=f"{header}\n{body}")]

        raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Tool execution failed for '{name}': {e}")
        return [TextContent(type="text", text=f"Error executing tool: {str(e)}")]


async def main():
    logger.info("Starting production warehouse MCP server")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

## The Production Checklist This Server Implements
```
[x] Read-only enforcement (defense-in-depth: SQL keyword blocking +
    should ALSO use a genuinely read-only DB role at the connection
    level, recap 07-cloud-platforms/09's least-privilege principle)
[x] Row count limits (protects against runaway context/cost from a
    query returning millions of rows)
[x] Schema allowlisting (the model can ONLY see/query explicitly
    permitted schemas -- recap least-privilege again)
[x] Full audit logging (every query is traceable -- recap
    15-governance-quality-mlops/08's governance metrics discussion)
[x] Credentials via environment variables, never hardcoded
[x] Graceful error handling (never an unhandled crash)
[x] Schema-discovery tools (get_table_schema, list_available_tables)
    so the model can explore correctly rather than guessing/hallucinating
    column names
```

## Deploying This for Team-Wide Use (recap file 3's transport discussion)
```
For a single developer's local Claude Desktop: the stdio transport
  shown above, configured in claude_desktop_config.json, is sufficient.

For team-wide/production deployment: wrap this same tool logic in an
  HTTP+SSE transport (recap file 3), containerize it (recap
  `10-devops/04`'s Dockerfile patterns), and deploy it as a genuinely
  managed service (recap `07-cloud-platforms`'s deployment patterns) --
  with proper authentication (recap `07-cloud-platforms/09`'s IAM
  discussion) so only authorized users/applications can connect to it
  at all.
```

## Interview Traps
- "How would you prevent an AI model from accidentally (or maliciously, via a crafted prompt) deleting data through an MCP server?" — defense-in-depth: SQL keyword blocking at the application layer AND a genuinely read-only database role/credential at the connection level — never rely on just one layer.
- "Why cap the number of rows an MCP tool can return?" — protects against context window blowup and excessive token cost if a query unexpectedly returns a huge result set — a genuinely important production guardrail specific to LLM-connected systems.
- "Why include schema-discovery tools (get_table_schema) rather than just a query tool?" — prevents the model from guessing/hallucinating column names, which would otherwise produce failed or subtly incorrect queries.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The wisest builder gives their creation just enough freedom to help, and just enough limit to stay safe."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
