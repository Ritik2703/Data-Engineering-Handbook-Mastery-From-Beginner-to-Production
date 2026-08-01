# AI, MCP & LLM Pipelines Interview Questions — 30+ with Answers

## Fundamentals

**Q1. Why can't you just paste an entire database schema into every LLM prompt?**
> Context window limits and per-token cost make this impractical at scale, especially for large schemas — motivating retrieval-based approaches (RAG, MCP tools) that fetch only relevant context per request.

**Q2. What's the difference between an LLM 'chatting' and an LLM 'using tools'?**
> Chatting only produces text; tool use lets the model request that external code execute a real action (a query, an API call) and feed the result back, enabling interaction with real systems.

## RAG

**Q3. Why does chunking strategy matter so much for RAG quality?**
> Chunks too large dilute embedding relevance/specificity; chunks too small lose necessary surrounding context — a genuinely important tuning decision.

**Q4. How would you prevent a RAG system from exposing sensitive documents to unauthorized users?**
> Metadata-tagged loading (classification/department tags) combined with filtered retrieval at query time, enforcing access control before content reaches the LLM prompt.

**Q5. How do you evaluate whether a RAG pipeline is actually working well?**
> A labeled test set measuring retrieval accuracy, plus checking answer faithfulness (grounded in retrieved context) and relevance — an ongoing quality practice, not a one-time check.

## MCP

**Q6. What problem does MCP solve that function calling alone didn't?**
> Standardization and reusability — a single MCP server can serve multiple different AI client applications without rebuilding the integration for each, solving the "N systems × M AI apps" combinatorial problem.

**Q7. What are the three core MCP primitives?**
> Tools (actions the model can call), Resources (data the model can read), Prompts (reusable prompt templates).

**Q8. Who typically builds an MCP server vs an MCP client?**
> Data Engineers/backend teams typically build servers (bridging AI models to systems they own); the client is usually an existing AI application you connect to, unless building a custom agent application.

**Q9. stdio vs HTTP+SSE transport — when would you use each?**
> stdio for local development/desktop AI applications running the server as a local process; HTTP+SSE for production, network-accessible deployments serving multiple users/applications.

## Building MCP Servers

**Q10. How would you prevent an AI model from modifying data through an MCP server?**
> Defense-in-depth: SQL keyword blocking at the application layer AND a genuinely read-only database role/credential at the connection level — never rely on just one layer.

**Q11. Why cap the number of rows an MCP tool returns?**
> Protects against context window blowup and excessive token cost if a query unexpectedly returns a huge result set.

**Q12. Why include schema-discovery tools rather than just a query tool?**
> Prevents the model from guessing/hallucinating column names, which would otherwise produce failed or subtly incorrect queries.

## LLM-Powered Pipeline Automation

**Q13. How would you build a safe text-to-SQL system for business users?**
> Schema context injection via a catalog/MCP server, a validation step (EXPLAIN before execution, read-only enforcement) before running any AI-generated SQL, and ideally human review for anything beyond simple, low-stakes queries.

**Q14. Why does good data modeling/documentation directly improve AI-assisted querying quality?**
> Text-to-SQL performs meaningfully better against well-documented, clearly-named, properly-modeled schemas — good data modeling is a prerequisite for good AI tooling, not a separate concern.

**Q15. Should AI-generated dbt models skip normal code review?**
> No — AI-generated code should go through the exact same PR review and CI testing discipline as human-written code, treated as a draft/starting point, not a final trusted product.

## AI Agents

**Q16. What makes something an "agent" rather than just an LLM API call?**
> The loop: observing, reasoning, acting via tools, observing results, and repeating across multiple steps toward a goal, rather than a single one-shot response.

**Q17. What guardrails are non-negotiable for a production autonomous data agent?**
> Bounded/least-privilege tool access, bounded iteration counts, explicit human-escalation capability, full audit logging, and human approval gates for genuinely destructive actions.

**Q18. How would you prevent an agent from retrying a failure that will never succeed?**
> Encode the same operational judgment a senior engineer applies (distinguishing transient vs genuine data issues) directly into the agent's instructions, and bound total retry attempts regardless.

## AI-Powered BI

**Q19. Would you always build a custom natural-language-to-dashboard layer instead of using Power BI Copilot/Tableau Pulse?**
> No — weigh native features (less engineering effort, vendor-maintained) against custom builds (full control over data access/security, multi-tool unification, embeddability); the right choice depends on organizational constraints.

**Q20. Why always show the underlying SQL alongside an AI-generated chart?**
> Transparency and trust — lets a technical user/analyst verify the AI didn't misinterpret the question.

**Q21. How would you let users choose between a quick text answer, an inline chart, or a full BI dashboard for the same question?**
> Separate the expensive, safety-critical step (validated query generation + execution, done once) from the cheap presentation-format branch based on user preference.

## Security & Governance

**Q22. What's prompt injection, and how does it differ from SQL injection?**
> Similar defensive mindset (never fully trust external/untrusted content), but the injected payload is natural language instructions rather than SQL syntax — the primary defense is tool-access scoping (least privilege) rather than input sanitization alone.

**Q23. How would you prevent an AI agent from being tricked into leaking data via a malicious support ticket it's asked to summarize?**
> Least-privilege tool access (the agent shouldn't have a data-export/email tool if that's not its job) combined with clearly separating untrusted content from instructions in the prompt structure.

**Q24. Is a vector database exempt from normal data governance policies?**
> No — it's still a database containing potentially sensitive information and must be classified, access-controlled, and governed identically to any other data store.

**Q25. What are the key risks of sending data to a third-party LLM API?**
> Understanding the provider's data retention/training policies (verified, not assumed), preventing sensitive retrieved content from reaching unauthorized users, and ensuring vector-stored embeddings of sensitive documents are governed like any other sensitive data store.

## Real-World Context

**Q26. Is fully autonomous AI pipeline management already standard industry practice?**
> An honest answer: no, this remains an early-stage capability at most companies in 2026 — foundational integration (MCP servers, RAG, validated text-to-SQL, Copilot-style assistants) is far more common than fully autonomous, unsupervised agents.

**Q27. Why might a company build a custom MCP server rather than rely on their warehouse's native AI features (Snowflake Cortex, Databricks Mosaic)?**
> Need for custom security/access control granularity, multi-platform unification, or proprietary internal systems vendor-native features don't cover.

## Rapid-Fire
28. What's the difference between a Tool and a Resource in MCP? *(Tools are actions the model actively calls with parameters; Resources are more passively-read data the model can be given awareness of.)*
29. Why is embedding overlap important in chunking? *(Prevents losing context/concepts that span a chunk boundary.)*
30. What's hybrid search in RAG? *(Combining vector similarity with keyword/metadata filtering, often outperforming vector similarity alone for queries with specific terms.)*
31. What's the honest limit of text-to-SQL against a poorly-documented schema? *(Meaningfully worse performance — ambiguous/undocumented schemas produce less reliable AI-generated queries.)*
32. Why bound an agent's maximum loop iterations? *(Prevents a stuck/confused agent from looping indefinitely, burning cost and potentially taking repeated unintended actions.)*

---

**Practice tip**: This is the newest, fastest-evolving module in the repo — verify specific tool/protocol details against current documentation when interviewing, since this space changes genuinely quickly; focus your interview preparation on the underlying PRINCIPLES (least privilege, validation before execution, human-in-the-loop for destructive actions) which remain stable even as specific tools evolve.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Go now, build with courage, govern with conscience, and share what you learn freely with the world."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
