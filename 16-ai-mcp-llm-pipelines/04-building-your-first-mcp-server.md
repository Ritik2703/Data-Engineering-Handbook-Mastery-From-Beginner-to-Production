# 4. Building Your First MCP Server — Step by Step, Real Working Code

## Setup
```bash
pip install mcp
```

## Step 1: The Simplest Possible MCP Server (a single tool)
```python
# simple_mcp_server.py
# A minimal, complete, RUNNABLE MCP server exposing one tool: fetching
# the current row count of a table -- deliberately simple so the FULL
# structure is visible end to end before adding complexity in file 5

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("simple-data-server")

# Fake in-memory "database" for this first example -- file 5 replaces
# this with a real database connection
FAKE_TABLES = {
    "orders": 15234,
    "customers": 8921,
    "products": 342,
}

@app.list_tools()
async def list_tools() -> list[Tool]:
    """This is what the AI model sees when it asks 'what can this server do?'"""
    return [
        Tool(
            name="get_row_count",
            description="Returns the current row count for a given table name",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "The name of the table to check",
                    }
                },
                "required": ["table_name"],
            },
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """This is what actually EXECUTES when the AI model decides to call a tool."""
    if name == "get_row_count":
        table_name = arguments["table_name"]
        if table_name not in FAKE_TABLES:
            return [TextContent(type="text", text=f"Error: table '{table_name}' not found")]
        count = FAKE_TABLES[table_name]
        return [TextContent(type="text", text=f"Table '{table_name}' has {count} rows")]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

## Step 2: Connecting This Server to an AI Client (Claude Desktop example)
```json
// claude_desktop_config.json -- tells Claude Desktop how to launch YOUR server
{
  "mcpServers": {
    "simple-data-server": {
      "command": "python",
      "args": ["/path/to/simple_mcp_server.py"]
    }
  }
}
```
Once configured, you can literally ask Claude Desktop "how many rows are in the orders table?" and it will discover your `get_row_count` tool, call it with `table_name="orders"`, and use the returned result in its answer — genuinely working, end to end, from the code above.

## Step 3: Adding a Resource (data the model can READ, not just call)
```python
from mcp.types import Resource

@app.list_resources()
async def list_resources() -> list[Resource]:
    """Exposes a 'schema summary' the model can read directly, without
    needing to explicitly call a tool for it -- useful for context the
    model should generally be AWARE of, not just fetch on demand."""
    return [
        Resource(
            uri="schema://tables/summary",
            name="Table Schema Summary",
            description="A summary of all available tables and their row counts",
            mimeType="text/plain",
        )
    ]

@app.read_resource()
async def read_resource(uri: str) -> str:
    if uri == "schema://tables/summary":
        summary = "\n".join([f"- {name}: {count} rows" for name, count in FAKE_TABLES.items()])
        return f"Available tables:\n{summary}"
    raise ValueError(f"Unknown resource: {uri}")
```

## Step 4: Adding Error Handling (recap `03-python/02` — applies identically here)
```python
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "get_row_count":
            table_name = arguments.get("table_name")
            if not table_name:
                return [TextContent(type="text", text="Error: table_name is required")]
            if table_name not in FAKE_TABLES:
                return [TextContent(
                    type="text",
                    text=f"Error: table '{table_name}' not found. Available tables: {list(FAKE_TABLES.keys())}"
                )]
            return [TextContent(type="text", text=f"Table '{table_name}' has {FAKE_TABLES[table_name]} rows")]
        raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        # NEVER let an unhandled exception crash the server -- always
        # return a clear error message the model can reason about and
        # potentially recover from (e.g., trying a corrected input)
        return [TextContent(type="text", text=f"Tool execution error: {str(e)}")]
```

## What You've Just Built
```
A genuinely complete, minimal MCP server with: tool discovery
(list_tools), tool execution (call_tool), a readable resource
(list_resources/read_resource), and production-grade error handling --
the EXACT same structural pattern every real MCP server follows,
just with more tools, real database connections, and safety guardrails
added in file 5.
```

## Interview Traps
- "Walk through what happens when an AI model calls a tool on your MCP server." — the client sends a tool-call request over the protocol (stdio/HTTP); your `call_tool` handler executes the REAL logic; the result is returned as `TextContent` back to the model, which then continues reasoning/responds to the user with that information incorporated.
- "What's the difference between a Tool and a Resource in MCP?" — Tools are actions the model actively CALLS with specific parameters to perform an action or fetch specific information; Resources are more like readable data the model can be given AWARENESS of more passively (e.g., a schema summary) — recap file 3's primitive definitions.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Progress guided by conscience benefits all; progress without it burdens even its creator."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
