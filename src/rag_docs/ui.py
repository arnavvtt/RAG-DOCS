import os
import zipfile
from pathlib import Path

# Streamlit Cloud: inject secrets as env vars BEFORE importing config.
try:
    import streamlit as st
    if "MISTRAL_API_KEY" in st.secrets:
        os.environ["MISTRAL_API_KEY"] = st.secrets["MISTRAL_API_KEY"]
except Exception:
    pass

import streamlit as st

from rag_docs.core.embeddings import get_embeddings
from rag_docs.services.qa_service import ask
from rag_docs.vectorstore.chroma import load_vectorstore


st.set_page_config(page_title="RAG Docs Q&A", page_icon="📚", layout="wide")
st.title("📚 RAG Docs Q&A")
st.caption("Ask questions over technical documentation using Mistral + ChromaDB")


@st.cache_resource(show_spinner=False)
@st.cache_resource(show_spinner=False)
def get_store():
    """Load ChromaDB — always re-extract from zip on fresh session."""
    chroma_dir = Path("data/chroma")
    zip_path = Path("chroma_db.zip")

    # Force re-extract: if zip exists AND chroma dir exists, wipe and re-extract.
    # This guarantees the deployed app uses the latest pre-built vector store.
    if zip_path.exists():
        if chroma_dir.exists():
            import shutil
            shutil.rmtree(chroma_dir, ignore_errors=True)
        with st.spinner("Extracting pre-built vector store..."):
            chroma_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(chroma_dir)

    return load_vectorstore(get_embeddings())


store = get_store()

if store is None or store._collection.count() == 0:
    st.error("Vector store not found. Run `uv run rag-docs ingest` locally first.")
    st.stop()


with st.sidebar:
    st.header("Settings")
    top_k = st.slider("Top-k chunks", 1, 10, 4)
    st.divider()
    st.metric("Chunks indexed", store._collection.count())
    st.divider()
    st.caption("Built with LangChain, Mistral, ChromaDB")


if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sources" in msg:
            with st.expander("📎 Sources"):
                for s in msg["sources"]:
                    st.write(
                        f"**[{s['ref']}]** {s['filename']} — score `{s['score']}`"
                    )


question = st.chat_input("Ask a question...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = ask(question, vectorstore=store, top_k=top_k)

        st.markdown(result["answer"])

        with st.expander("📎 Sources", expanded=True):
            for s in result["sources"]:
                st.write(
                    f"**[{s['ref']}]** {s['filename']} — score `{s['score']}`"
                )

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result["sources"],
    })