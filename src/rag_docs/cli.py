import logging
from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from rag_docs.services.ingest_service import ingest_directory
from rag_docs.services.qa_service import ask

app = typer.Typer(help="RAG-based Q&A over technical documentation.")
console = Console()

logging.basicConfig(level=logging.INFO, format="%(message)s")


@app.command()
def ingest(
    dir: str = typer.Option("data/raw", "--dir", "-d", help="Folder with raw docs"),
):
    """Ingest documents: load → clean → chunk → embed → store."""
    console.print(f"[bold cyan]Ingesting from:[/] {dir}")
    with console.status("Working..."):
        ingest_directory(raw_dir=dir)
    console.print("[bold green]✓ Ingestion complete.[/]")


@app.command("ask")
def ask_cmd(
    question: str = typer.Argument(..., help="Question to ask"),
    top_k: int = typer.Option(4, "--top-k", "-k", help="Number of chunks to retrieve"),
):
    """Ask a question against the indexed documents."""
    with console.status("Thinking..."):
        result = ask(question, top_k=top_k)

    console.print()
    console.print(Panel(Markdown(result["answer"]), title="Answer", border_style="green"))

    console.print("[bold]Sources:[/]")
    for s in result["sources"]:
        page = f", p.{s['page']}" if s.get("page") else ""
        console.print(
            f"  [{s['ref']}] {s['filename']}{page}  "
            f"[dim](score: {s['score']})[/]"
        )


if __name__ == "__main__":
    app()