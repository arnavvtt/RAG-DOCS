# 🦜 LangChain Docs Q&A — Retrieval-Augmented Generation over LangChain Documentation

A production-style **RAG (Retrieval-Augmented Generation)** system that answers questions over official **LangChain documentation** using **Mistral AI**, **LangChain**, and **ChromaDB**.

The system retrieves relevant chunks from LangChain's RAG, retrieval, agents, and knowledge-base documentation, and generates grounded answers with source citations — refusing to answer when the information isn't in the corpus.

---

## Problem

Large language models (LLMs) have two key limitations:

- **Knowledge cutoff** — they don't know recent information
- **No private data access** — they can't answer questions about your documents

RAG solves both by retrieving relevant chunks from a known corpus at query time and grounding the LLM's answer in that evidence.

This project applies RAG to a specific, high-value corpus: **LangChain's own documentation on RAG, retrieval, and knowledge bases**.

---

## Architecture
Documents (LangChain .md files from docs.langchain.com)
│
▼
Loaders + Cleaning (ingestion/)
│
▼
Recursive Chunking (chunking/) 800 chars / 150 overlap
│
▼
Mistral Embeddings (core/) 1024-dim, unit-normalized
│
▼
ChromaDB (persistent) (vectorstore/) HNSW + cosine
│
▼
Query → Retrieval (retrieval/) top-k + MMR
│
▼
Grounded Prompt + LLM (generation/) Mistral ministral-8b
│
▼
Answer + Citations

text

Providers (LLM & embeddings) are isolated behind factory functions in `core/`. Swapping Mistral → OpenAI is a config change, not a code rewrite.

---

## Demo

![LangChain Docs Q&A UI](docs/screenshots/ui_demo.png)

Ask a question → grounded answer with citations + source chunks with similarity scores.

---

## Corpus

The system is tested on **7 official LangChain documentation files** (~316 chunks):

| File | Coverage |
|---|---|
| `langchain__knowledge-base.md` | Semantic search + RAG tutorial |
| `langchain__deepagents__retrieval.md` | Retrieval pipelines + RAG architectures |
| `langchain__langgraph__agentic-rag.md` | Agentic RAG example |
| `langchain__agents.md` | Agents (tools, planning, delegation) |
| `langchain__overview.md` | LangChain overview |
| `langchain__component-architecture.md` | Component architecture |
| `langchain__quickstart.md` | Quickstart guide |

All files sourced from `docs.langchain.com/oss/python/`.

---

## Evaluation Results

Custom evaluation dataset with questions spanning the corpus, each with expected source files and expected keywords.

| Metric | Score |
|---|---|
| **Retrieval Recall@4** | 1.00 |
| **Keyword Coverage** | 0.85+ |

**Grounding verified** with off-topic queries such as *"What is the capital of France?"* — the LLM correctly responds *"I don't have enough information in the provided documents to answer."*

Run the evaluation:

```bash
uv run python scripts/run_eval.py
Tech Stack
Layer	Technology
LLM	Mistral (ministral-8b-2512)
Embeddings	Mistral (mistral-embed, 1024-dim, unit-normalized)
Vector DB	ChromaDB (persistent, HNSW, cosine)
Framework	LangChain (LCEL), langchain-mistralai, langchain-chroma
API	FastAPI, Uvicorn, Pydantic
CLI	Typer, Rich
UI	Streamlit
Testing	pytest (7 tests passing)
Package Mgmt	uv
Python	3.12
Setup
1. Clone and install
bash
git clone <repo-url>
cd rag-docs
uv sync
2. Configure environment
bash
cp .env.example .env
Edit .env and add your Mistral API key:

text
MISTRAL_API_KEY=your_key_here
Get a free key at https://console.mistral.ai/

3. Populate the corpus
Run the LangChain docs downloader:

bash
uv run python scripts/download_langchain_final.py
This downloads 7 verified LangChain documentation files into data/raw/.

4. Ingest
bash
uv run rag-docs ingest
This runs the full pipeline: load → clean → chunk → embed → store. The vector store persists to data/chroma/.

5. Ask questions
CLI:

bash
uv run rag-docs ask "What is RAG?"
Streamlit UI:

bash
uv run streamlit run src/rag_docs/ui.py
Open http://localhost:8501

FastAPI:

bash
uv run uvicorn rag_docs.api.main:app --reload --port 8000
Open http://127.0.0.1:8000/docs for Swagger UI.

API Usage
bash
# Health check
curl http://127.0.0.1:8000/health

# Ask a question
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?", "top_k": 4}'
Example response:

json
{
  "question": "What is RAG?",
  "answer": "Agentic Retrieval-Augmented Generation (RAG) combines...",
  "sources": [
    {
      "ref": 1,
      "filename": "langchain__deepagents__retrieval.md",
      "chunk_id": "langchain__deepagents__retrieval.md::chunk_0003",
      "page": null,
      "score": 0.819
    }
  ]
}
Project Structure
text
rag-docs/
├── src/rag_docs/
│   ├── core/             # config, LLM & embedding factories
│   ├── ingestion/        # loaders, cleaning
│   ├── chunking/         # recursive splitter
│   ├── vectorstore/      # ChromaDB build/load/delete
│   ├── retrieval/        # top-k, MMR, formatter
│   ├── generation/       # prompts, LCEL chain
│   ├── evaluation/       # dataset, metrics, evaluator
│   ├── services/         # orchestration (ingest, Q&A)
│   ├── api/              # FastAPI routes, schemas
│   ├── cli.py            # Typer CLI
│   └── ui.py             # Streamlit UI
├── scripts/              # downloaders, dev tools, eval
├── tests/                # pytest tests
├── data/
│   ├── raw/              # LangChain source documents
│   ├── chroma/           # persisted vector store
│   └── eval/             # evaluation dataset
├── docs/
│   ├── architecture.md
│   ├── interview_prep.md
│   └── screenshots/
├── .env.example
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
Design Decisions
Focused corpus — 7 LangChain docs instead of a broad multi-framework mix. Improves retrieval precision for LangChain queries.

Provider isolation — LLM and embeddings behind factory functions in core/. One-line swap from Mistral to OpenAI.

Metadata preservation — every chunk keeps source, filename, page, chunk_id for citations.

Grounded prompt — strict "answer only from context" rule with explicit "I don't know" fallback. Verified against off-topic queries.

Cosine similarity — Mistral embeddings are unit-normalized (L2 = 1.0), so cosine = dot product.

Fresh vector store per ingestion — data/chroma/ is wiped before re-ingestion to avoid stale data merging.

Limitations
Corpus scope — only LangChain RAG/retrieval/agents documentation. General LangChain API questions may fail.

Rate limits — Mistral free tier ~1-3 RPS. Not suitable for high concurrency without retry/backoff.

Single embedding provider — architecture supports swap, but only Mistral implemented.

Local vector store — ChromaDB on disk. Production would migrate to Qdrant/Pinecone/pgvector.

Future Improvements
Expand LangChain corpus — add splitters, loaders, vector store concept pages

Hybrid retrieval — combine dense + BM25 for keyword-heavy queries

Cross-encoder reranking — Cohere/BAAI reranker on top-k

Conversational RAG — chat history + query rewriting

RAGAS evaluation — faithfulness, answer relevance

LangSmith tracing

License
MIT

## Known Limitations

This project is a **focused MVP**, not a production-grade system. Below are 
the limitations we consciously accept — and how production systems address them.

### 1. Typo Tolerance

**What happens:** Queries with typos (e.g., `"agnetic ai"` instead of 
`"agentic AI"`) often fail to retrieve relevant chunks. The system 
responds with *"I don't have enough information"* rather than answering.

**Why:** Dense embeddings (Mistral `mistral-embed`) capture semantic 
meaning but are sensitive to character-level differences. `"agentic"` and 
`"agnetic"` produce different embeddings despite the same intent.

**Production fix:**
- **Query rewriting** — use the LLM as a preprocessor to correct/normalize queries
- **Spell correction** — `symspellpy`, `pyspellchecker` for dictionary-based correction
- **Hybrid search** — combine dense retrieval with BM25 for keyword-level matching
- **Query expansion** — generate alternate phrasings, retrieve across all

**Trade-off accepted:** We prioritized a simpler, faster pipeline over typo tolerance. For a 7-document corpus with ~316 chunks, the failure rate is low.

---

### 2. Chat History Persistence

**What happens:** Chat history is preserved **within a browser session** but not across sessions. Closing the tab or refreshing the page clears the conversation.

**Why:** Streamlit's `st.session_state` is in-memory and session-scoped. It is not persisted to disk or database.

**Production fix:**
- Store messages in **SQLite** with a `session_id` and `timestamp`
- Rehydrate history on page load via session lookup
- Add session management (login, session tokens) for multi-user support

**Trade-off accepted:** The RAG pipeline is intentionally **stateless** — each query is independent. This avoids context contamination between unrelated questions. Persistent UI history is a separate concern.

---

### 3. Single Embedding Provider

Only Mistral embeddings are implemented. The architecture isolates providers behind a factory (`core/embeddings.py`), so swapping to OpenAI, Cohere, or local models is a one-line change — but only Mistral is currently configured.

---

### 4. Local Vector Store

ChromaDB runs on-disk (single-node). Production scale would migrate to Qdrant, Pinecone, or pgvector — the pipeline is provider-agnostic and would only require changing `vectorstore/`.

---

### 5. Free-Tier Rate Limits

Mistral's free tier enforces ~1-3 requests/second. High-concurrency deployments would need retry-with-backoff logic or a paid tier.