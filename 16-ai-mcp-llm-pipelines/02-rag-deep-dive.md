# 2. RAG (Retrieval-Augmented Generation) — Full Deep Dive

## Recap + Why This Deserves a Full File Now
`05-databases/06-vector-databases-ai-era.md` introduced the RAG pattern conceptually. This file builds the COMPLETE, production-grade pipeline a Data Engineer actually builds and maintains — because RAG pipelines are, at their core, DATA PIPELINES (extraction, transformation/chunking, loading into a vector store), squarely a Data Engineering responsibility, not just a Data Science one.

## The Full RAG Pipeline, Stage by Stage
```
[Source documents: PDFs, Confluence pages, Slack messages, database
 records, SharePoint files -- recap 03-python/10]
        |
   1. EXTRACTION (recap module 03/04's extraction patterns)
        |
   2. CHUNKING (splitting long documents into retrieval-sized pieces)
        |
   3. EMBEDDING (converting each chunk into a vector -- recap
      05-databases/06)
        |
   4. LOADING into a vector store (pgvector / Pinecone / Weaviate)
        |
   [At query time:]
   5. Embed the USER'S QUESTION the same way
        |
   6. RETRIEVE the most similar chunks (vector similarity search)
        |
   7. AUGMENT the LLM prompt with retrieved chunks as context
        |
   8. GENERATE the final answer, grounded in retrieved real data
```

## Stage 2 Deep Dive: Chunking Strategy (the most underrated, highest-impact step)
```python
# Naive chunking (splitting by fixed character count) -- often produces
# POOR retrieval quality by cutting sentences/ideas in half
def naive_chunk(text, chunk_size=500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# Better: chunk by semantic boundaries (paragraphs/sections) with OVERLAP
# -- overlap ensures a concept spanning a chunk boundary isn't lost entirely
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,  # genuinely important -- prevents losing context
                         # at chunk boundaries
    separators=["\n\n", "\n", ". ", " "]  # tries paragraph breaks first,
                                            # falls back to sentences, then words
)
chunks = splitter.split_text(document_text)
```
**Why chunking strategy matters so much**: a chunk that's too large dilutes relevance (the embedding represents an averaged, less-specific meaning across too much content); a chunk that's too small loses necessary context (a sentence fragment without its surrounding paragraph may be meaningless or misleading on its own). This is a genuinely important, often-overlooked DATA ENGINEERING tuning decision, not just an ML concern.

## Stage 4 Deep Dive: Metadata-Enriched Loading (the production-grade practice)
```python
# Never load JUST the text -- always attach metadata enabling filtered retrieval
def load_chunk_to_vector_store(chunk_text, source_document, chunk_index, department):
    embedding = generate_embedding(chunk_text)  # via an embedding model API
    vector_store.upsert(
        id=f"{source_document}_{chunk_index}",
        vector=embedding,
        metadata={
            "text": chunk_text,
            "source": source_document,
            "department": department,      # enables filtered retrieval --
                                             # e.g., only search HR docs
                                             # for an HR question
            "last_updated": datetime.utcnow().isoformat(),
        }
    )
```
This directly connects to the classification/governance discussion in `15-governance-quality-mlops/01` — metadata tagging at load time is what enables filtering retrieval by SENSITIVITY or DEPARTMENT later (e.g., a general employee's RAG query should never retrieve chunks tagged as "Executive-Confidential").

## Stage 6 Deep Dive: Retrieval Strategies (beyond simple top-K similarity)
```python
# Simple top-K -- the baseline approach
results = vector_store.query(query_embedding, top_k=5)

# Hybrid search -- combining vector similarity with traditional keyword/
# metadata filtering, often producing MEANINGFULLY better results than
# vector similarity alone, especially for queries with specific terms
# (product codes, exact names) that pure semantic similarity might miss
results = vector_store.query(
    query_embedding,
    top_k=5,
    filter={"department": "engineering"},  # metadata pre-filter
)

# Re-ranking -- retrieve MORE candidates than needed (e.g., top 20),
# then use a separate, more precise (but slower) re-ranking model to
# re-score and select the TRUE best 5 -- a common production pattern
# balancing the speed of vector search with the precision of a
# heavier-weight relevance model
```

## Stage 7-8 Deep Dive: Prompt Construction and Grounding
```python
def build_rag_prompt(user_question, retrieved_chunks):
    context = "\n\n".join([f"[Source: {c['source']}]\n{c['text']}" for c in retrieved_chunks])
    return f"""Answer the question using ONLY the context provided below.
If the context doesn't contain enough information to answer, say so
explicitly rather than guessing.

CONTEXT:
{context}

QUESTION: {user_question}

ANSWER:"""
```
**The explicit "only use the context provided" instruction is critical** — it's what makes the answer GROUNDED (traceable to real retrieved data) rather than the model falling back on its general training knowledge, which could be outdated or entirely fabricated (hallucinated) for a company-specific question.

## Evaluating RAG Quality (a genuinely important, often-skipped step)
```
Retrieval quality metrics: did the retrieval step actually surface the
  TRUE relevant chunks? (measurable via a labeled test set of
  question->expected-source pairs)

Answer faithfulness: does the generated answer actually reflect ONLY
  what's in the retrieved context, without adding unsupported claims?

Answer relevance: does the final answer actually address the user's question?

A genuinely mature RAG pipeline includes an automated EVALUATION
harness (recap the testing philosophy from `15-governance-quality-
mlops/04`) run whenever the chunking strategy, embedding model, or
retrieval logic changes -- treating RAG quality with the same
rigor as any other data pipeline's quality (file 4 of module 15
directly applies here).
```

## Interview Traps
- "Why does chunking strategy matter so much for RAG quality?" — chunks too large dilute embedding relevance/specificity; chunks too small lose necessary surrounding context — a genuinely important tuning decision, not a minor implementation detail.
- "How would you prevent a RAG system from retrieving/exposing sensitive documents to unauthorized users?" — metadata-tagged loading (classification/department tags, recap module 15) combined with filtered retrieval at query time, enforcing access control BEFORE content ever reaches the LLM prompt.
- "How do you evaluate whether a RAG pipeline is actually working well?" — a labeled test set measuring retrieval accuracy, plus checking answer faithfulness (grounded in retrieved context) and relevance — treated as an ongoing pipeline quality practice, not a one-time check.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Even the newest creation must be held with the same old wisdom of care and responsibility."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
