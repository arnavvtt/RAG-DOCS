# RAG Docs Q&A — Retrieval-Augmented Generation over Technical Documentation

A production-style RAG system that answers questions over technical
documentation using Mistral AI, ChromaDB, and LangChain. Includes
ingestion, chunking, retrieval, grounded generation, source attribution,
evaluation, CLI, and REST API.

## Problem

Large language models have two limitations:
- **Knowledge cutoff** — they don't know recent information
- **No private data** — they can't answer questions about your documents

RAG solves both by retrieving relevant chunks from your own documents
at query time and grounding the LLM's answer in that evidence.

## Architecture
Documents (PDF/MD/TXT)
↓
Loaders → Cleaning → Chunking (Recursive, 800/150)
↓
Mistral Embeddings (1024-dim, unit-normalized)
↓
ChromaDB (persistent, cosine similarity)
↓
Query → Embedding → Top-k Retrieval (k=4) → MMR (optional)
↓
Grounded Prompt (Mistral ministral-8b-2512)
↓
Answer + Source Citations


## Features

- **Multi-format ingestion** — PDF, Markdown, TXT
- **Recursive chunking** with metadata preservation (`source`, `page`, `chunk_id`)
- **Mistral Embeddings** (`mistral-embed`, 1024-dim)
- **ChromaDB** persistent vector store with cosine similarity
- **Grounded generation** with citation support
- **CLI** — `rag-docs ingest`, `rag-docs ask`
- **REST API** — FastAPI with Pydantic validation, Swagger docs
- **MMR retrieval** — diversity-aware chunk selection
- **Evaluation framework** — custom dataset with recall@k and keyword coverage

## Evaluation Results

Tested on 15-question dataset spanning 3 documents:

| Metric | Score |
|---|---|
| **Retrieval Recall@4** | **1.00** |
| **Keyword Coverage** | **0.87** |

Grounding verified with an off-topic query ("capital of France") —
LLM correctly responded "I don't have enough information."

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Mistral (`ministral-8b-2512`) |
| Embeddings | Mistral (`mistral-embed`, 1024-dim) |
| Vector DB | ChromaDB (persistent, cosine) |
| Framework | LangChain (LCEL), langchain-mistralai |
| API | FastAPI, Uvicorn, Pydantic |
| CLI | Typer, Rich |
| Package Mgmt | uv |
| Python | 3.12 |

## Setup

```bash
# 1. Clone and install
git clone <repo-url>
cd rag-docs
uv sync

# 2. Configure
cp .env.example .env
# Edit .env and add MISTRAL_API_KEY

# 3. Add documents to data/raw/

# 4. Ingest
uv run rag-docs ingest

# 5. Ask
uv run rag-docs ask "What is RAG?"