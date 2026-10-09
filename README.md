# RAG Docs Q&A — Retrieval-Augmented Generation over Technical Documentation

A production-style RAG (Retrieval-Augmented Generation) system that answers questions over technical documentation using Mistral AI, ChromaDB, and LangChain. Features multi-format ingestion, recursive chunking with metadata preservation, grounded generation with source attribution, evaluation, CLI, REST API, and a Streamlit UI.

---

## Problem

Large language models (LLMs) have two key limitations:

- **Knowledge cutoff** — they don't know recent information
- **No private data access** — they can't answer questions about your documents

RAG solves both by retrieving relevant chunks from your own corpus at query time and grounding the LLM's answer in that evidence.

---

## Demo

![RAG Docs Q&A UI](docs/screenshots/ui_demo.png)

Ask a question → grounded answer with citations + source chunks with similarity scores.

---

## Architecture
Documents (PDF / MD / MDX / TXT)
│
▼
Loaders + Cleaning (ingestion/)
│
▼
Recursive Chunking (chunking/) 800 chars / 150 overlap
│
▼
Mistral Embeddings (core/) 1024-dim, normalized
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

## Corpus

The system is tested on **72 official documentation files** (~1361 chunks) pulled from:

| Source | Files | Topics |
|---|---|---|
| FastAPI | 12 | Tutorials, dependencies, metadata, responses |
| ChromaDB | 10 | Collections, querying, cloud, Python client |
| LangChain | 20 | Concepts, integrations, providers |
| Pydantic | 10 | Models, validators, aliases |
| Streamlit | 10 | API reference, tutorials, deployment |
| Typer | 10 | Commands, options, parameters |

Corpus can be rebuilt with `uv run python scripts/download_docs.py`.

---

## Evaluation Results

Custom 15-question evaluation dataset (`data/eval/qa_pairs.json`) spanning the corpus. Each question has an expected source file and expected keywords.

| Metric | Score |
|---|---|
| **Retrieval Recall@4** | **1.000** |
| **Keyword Coverage** | **0.867** |

**Grounding verified** with off-topic queries such as *"What is the capital of France?"* — the LLM correctly responds *"I don't have enough information in the provided documents to answer."* No hallucination from training data.

Run the evaluation:

```bash
uv run python scripts/run_eval.py
Chunking Configuration Analysis
We A/B-tested three RecursiveCharacterTextSplitter configurations on the corpus:

Config	Chunks	Avg Size	Min	Max
Small (500 / 100)	22	349	131	480
Baseline (800 / 150)	14	547	364	794
Large (1200 / 200)	8	959	641	1101
Baseline (800 / 150) chosen because it balances granularity (14 focused chunks per document) with context (avg 547 chars) and respects markdown heading boundaries. Small fragments too aggressively; large produces fewer, coarser chunks.

Custom separators (\n##, \n###) ensure splits occur on markdown structure rather than arbitrary character offsets — the max chunk size of 794 stays under the 800 target without mid-section cuts.

Run the comparison:

bash
uv run python scripts/test_chunking_configs.py
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
Two options:

Option A — Download official docs:

bash
uv run python scripts/download_docs.py
This pulls 40-50 markdown/mdx files from GitHub repos into data/raw/.

Option B — Add your own documents:

Place PDF / Markdown / TXT files in data/raw/. Subdirectories are not recursively scanned.

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
  "answer": "Retrieval-Augmented Generation (RAG) is...",
  "sources": [
    {
      "ref": 1,
      "filename": "langchain__concepts_rag.mdx",
      "chunk_id": "langchain__concepts_rag.mdx::chunk_0002",
      "page": null,
      "score": 0.847
    }
  ]
}
Project Structure
text
rag-docs/
├── src/rag_docs/
│   ├── core/             # config, LLM & embedding factories
│   │   ├── config.py
│   │   ├── embeddings.py
│   │   └── llm.py
│   ├── ingestion/        # loaders, cleaning
│   │   ├── loaders.py
│   │   └── cleaning.py
│   ├── chunking/         # recursive splitter
│   │   └── splitter.py
│   ├── vectorstore/      # ChromaDB build/load/delete
│   │   └── chroma.py
│   ├── retrieval/        # top-k, MMR, formatter
│   │   ├── retriever.py
│   │   ├── mmr_retriever.py
│   │   └── formatter.py
│   ├── generation/       # prompts, LCEL chain
│   │   ├── prompts.py
│   │   └── chain.py
│   ├── evaluation/       # dataset, metrics, evaluator
│   │   ├── dataset.py
│   │   ├── metrics.py
│   │   └── evaluator.py
│   ├── services/         # orchestration
│   │   ├── ingest_service.py
│   │   └── qa_service.py
│   ├── api/              # FastAPI routes
│   │   ├── main.py
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── cli.py            # Typer CLI
│   └── ui.py             # Streamlit UI
├── scripts/              # dev tools & one-off scripts
├── tests/                # pytest tests
├── data/
│   ├── raw/              # source documents
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
Provider isolation — LLM and embeddings live behind factory functions in core/. The pipeline receives interfaces, never concrete provider classes. Swapping Mistral → OpenAI is a one-line change.

Metadata preservation — every chunk keeps source, filename, page, doc_type, and a stable chunk_id ({filename}::chunk_NNNN). This flows through retrieval to citations.

Grounded prompt — strict "answer only from context" rule with an explicit "I don't know" fallback. Verified to prevent hallucination on off-topic queries.

Cosine similarity — Mistral embeddings are unit-normalized (L2 norm = 1.0), so cosine and dot product produce identical rankings. Configured ChromaDB with hnsw:space=cosine.

Extension-aware loader — logs warnings for unsupported file types instead of silently skipping. Discovered during corpus scaling when .mdx files were being dropped.

Service layer — CLI, FastAPI, and Streamlit all call the same services/ functions. No logic duplication.

Testing
bash
uv run pytest tests/ -v
7 tests covering:

Text cleaning (whitespace collapse, unicode normalization)

Directory loading

Chunking (metadata preservation, size bounds)

Retrieval (top-k, score ordering, source relevance)

Limitations
Rate limits — Mistral free tier enforces ~1-3 requests/second. Not suitable for high-concurrency production without retry/backoff or a paid tier.

Single embedding provider — Architecture supports swapping, but only Mistral is implemented.

Lightweight evaluation — Custom keyword-coverage metrics are fast and interpretable, but production systems would benefit from RAGAS with LLM-as-judge for faithfulness scoring.

No authentication — API endpoints are open. Not production-ready without auth.

Local vector store — ChromaDB runs on-disk. Production scale would migrate to Qdrant, Pinecone, or pgvector.

Future Improvements
Hybrid retrieval — combine dense (embedding) + sparse (BM25) for keyword-heavy queries

Cross-encoder reranking — Cohere or BAAI reranker on top-k

Conversational RAG — chat history + query rewriting for follow-up questions

RAGAS evaluation — faithfulness, answer relevance, context precision

LangSmith tracing — step-by-step pipeline inspection

Docker deployment — reproducible container

Incremental indexing — re-embed only changed documents

Acknowledgments
LangChain, ChromaDB, Mistral AI, FastAPI, Streamlit, Typer teams

Documentation sourced from official GitHub repositories

License
MIT