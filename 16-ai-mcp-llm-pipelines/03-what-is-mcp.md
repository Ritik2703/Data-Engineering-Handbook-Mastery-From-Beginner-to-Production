# 3. What Is MCP (Model Context Protocol)? — History & Architecture

## The Problem MCP Solves (the exact same "why" pattern from every module in this repo)
Before MCP, if a company wanted an AI assistant to query their Snowflake warehouse, ALSO read their Jira tickets, ALSO check their Salesforce data, they needed to build a SEPARATE, custom integration for EACH tool, for EACH AI application — the classic "N systems × M AI applications = N×M custom integrations" combinatorial explosion problem. This is EXACTLY the same class of problem that motivated Kafka (module 06, one integration point for many consumers) and the Data Catalog (module 15, one metadata layer for many query engines) — MCP applies that same "build the connector once, reuse everywhere" principle specifically to AI-model-to-data-system connections.

## MCP's Origin
Anthropic introduced the Model Context Protocol in November 2024 as an OPEN STANDARD (not a proprietary, Anthropic-only technology) specifically to solve this integration explosion — allowing ANY MCP-compatible AI application (Claude, and increasingly other AI tools that have adopted the open protocol) to connect to ANY MCP server, without custom one-off integration code for each pairing.

## The Core Architecture — Client, Server, and the Protocol Between Them
```
┌─────────────────┐         MCP Protocol          ┌─────────────────┐
│   MCP CLIENT      │◄─────(JSON-RPC over stdio /────►│   MCP SERVER      │
│  (an AI app --     │       HTTP/SSE)                │  (YOUR code --     │
│   Claude Desktop,  │                                │   connects to a   │
│   Claude Code,      │                                │   REAL system:    │
│   a custom agent)   │                                │   database, API,   │
│                     │                                │   file system)     │
└─────────────────┘                                └─────────────────┘
```
**The genuinely important architectural insight**: the MCP SERVER is what a Data Engineer builds and owns — it's the bridge between an AI model and YOUR actual data infrastructure (a warehouse, an API, a file system). The MCP CLIENT (the AI application itself) is typically something you CONNECT TO, not something you build yourself, unless you're building a custom agent application.

## The Three Core MCP Primitives
```
1. TOOLS: functions the AI model can CALL to perform an action or
   retrieve information (e.g., "run_sql_query", "search_customer_by_id")
   -- directly extends the tool-calling concept from file 1

2. RESOURCES: data the AI model can READ, similar to files (e.g., "the
   current schema of the orders table", "this week's data quality
   report") -- think of these as things the model can look AT, versus
   Tools which are things the model can DO

3. PROMPTS: pre-defined, reusable prompt TEMPLATES the server can
   expose (e.g., a standardized "investigate this pipeline failure"
   prompt template) -- ensuring consistent, well-crafted prompts for
   common tasks rather than every user/agent inventing their own
   phrasing each time
```

## A Minimal Conceptual MCP Server Definition
```python
# Conceptual structure (using the Python MCP SDK) -- full working code in file 4
from mcp.server import Server
from mcp.server.models import Tool, Resource

server = Server("my-data-warehouse-server")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="run_sql_query",
            description="Executes a READ-ONLY SQL query against the analytics warehouse",
            inputSchema={
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        )
    ]

@server.call_tool()
async def call_tool(name, arguments):
    if name == "run_sql_query":
        return execute_readonly_query(arguments["query"])
```

## Why MCP Specifically (Not Just "Custom Function Calling," Which Already Existed)
```
Function calling (file 1) ALREADY let a single AI application call
custom tools -- what MCP adds is STANDARDIZATION and REUSABILITY:
  - A SINGLE MCP server you build ONCE can be used by MULTIPLE
    different AI clients/applications (Claude Desktop, Claude Code,
    a custom internal agent) without rebuilding the integration each time
  - A GROWING ECOSYSTEM of pre-built MCP servers exists for common
    systems (GitHub, Slack, Google Drive, Postgres, and many more) --
    meaning a Data Engineer often doesn't need to build EVERYTHING
    from scratch, only the genuinely custom/proprietary systems
  - Consistent security/permission models across servers (recap the
    IAM/least-privilege discussion in `07-cloud-platforms/09`, now
    applied specifically to what an AI model is allowed to touch)
```

## MCP Transport Mechanisms (the technical connection layer)
```
stdio (standard input/output): the MCP server runs as a LOCAL process,
  communicating via stdin/stdout -- simplest, common for local
  development tools and desktop AI applications

HTTP + SSE (Server-Sent Events) / Streamable HTTP: the MCP server runs
  as a REMOTE, network-accessible service -- necessary for production
  deployments where the server needs to be reachable by multiple users/
  applications over a network, exactly the deployment pattern a Data
  Engineer would use for a genuinely production, team-wide MCP server
  (recap the API deployment patterns from `07-cloud-platforms` and
  `10-devops`)
```

## Interview Traps
- "What problem does MCP solve that function calling alone didn't?" — standardization and reusability — a single MCP server can serve MULTIPLE different AI client applications without rebuilding the integration for each, solving the "N systems × M AI apps" combinatorial integration problem.
- "What are the three core MCP primitives?" — Tools (actions the model can perform), Resources (data the model can read), Prompts (reusable prompt templates) — be ready to give an example of each in a data engineering context.
- "Who typically builds an MCP SERVER vs an MCP CLIENT?" — Data Engineers/backend teams typically build SERVERS (bridging AI models to real systems they own); the CLIENT is usually an existing AI application you connect TO, unless you're specifically building a custom agent application.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"To build a mind that serves without overstepping its bounds is a modern form of ancient discipline."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
