"""Typer CLI interface for tokenization inspection and dataset management."""

import typer
from rich.console import Console
from rich.table import Table
from src.core.tokenizer_service import TokenizerService
from src.core.data_generator import export_all_datasets, RAW_LANGUAGE_SAMPLES

app = typer.Typer(help="LLM Tokenizer Inspection & Language Equity CLI")
console = Console()


@app.command()
def tokenize(
    text: str = typer.Argument(..., help="Text to tokenize"),
    encoding: str = typer.Option(
        "cl100k_base", help="Tokenizer encoding (cl100k_base, o200k_base, r50k_base)"
    ),
) -> None:
    """Tokenize a string and display token chips, IDs, and byte breakdown."""
    svc = TokenizerService()
    res = svc.tokenize(text, encoding=encoding)

    console.print(f"[bold cyan]Input text:[/bold cyan] {res.text}")
    console.print(f"[bold green]Encoding:[/bold green] {res.encoding}")
    console.print(
        f"[bold yellow]Tokens:[/bold yellow] {res.token_count} | "
        f"[bold yellow]Chars:[/bold yellow] {res.char_count} | "
        f"[bold yellow]Words:[/bold yellow] {res.word_count} | "
        f"[bold yellow]Tokens/Word:[/bold yellow] {res.tokens_per_word}"
    )

    table = Table(title="Token Breakdown", show_header=True, header_style="bold magenta")
    table.add_column("Idx", justify="right", style="cyan")
    table.add_column("Token ID", justify="right", style="green")
    table.add_column("Text Piece", style="white")
    table.add_column("Bytes (Hex)", style="dim")
    table.add_column("Length", justify="right")
    table.add_column("Fallback", justify="center")

    for idx, p in enumerate(res.pieces):
        table.add_row(
            str(idx),
            str(p.token_id),
            repr(p.text),
            p.bytes_hex,
            str(p.byte_length),
            "⚠️ Yes" if p.is_byte_fallback else "No",
        )

    console.print(table)


@app.command()
def compare(
    text: str = typer.Argument(..., help="Text to compare across tokenizers"),
) -> None:
    """Compare a text across GPT-4 (cl100k), GPT-4o (o200k), and GPT-3 (r50k)."""
    svc = TokenizerService()
    results = svc.compare_encodings(text)

    table = Table(title=f"Tokenizer Comparison for '{text}'", header_style="bold blue")
    table.add_column("Model / Encoding", style="cyan")
    table.add_column("Tokens", justify="right", style="green")
    table.add_column("Token IDs", style="white")
    table.add_column("Tokens/Word", justify="right", style="yellow")

    for enc_name, res in results.items():
        table.add_row(
            enc_name,
            str(res.token_count),
            str(res.token_ids[:10]) + ("..." if len(res.token_ids) > 10 else ""),
            str(res.tokens_per_word),
        )

    console.print(table)


@app.command()
def languages() -> None:
    """Display the multi-language token inequality benchmark."""
    svc = TokenizerService()
    en_sample = next(s for s in RAW_LANGUAGE_SAMPLES if s["code"] == "en")
    en_tokens = svc.tokenize(en_sample["text"], "cl100k_base").token_count

    table = Table(title="Language Equity: The Token Tax Benchmark", header_style="bold green")
    table.add_column("Language", style="cyan")
    table.add_column("Script", style="dim")
    table.add_column("Words", justify="right")
    table.add_column("GPT-4 (cl100k)", justify="right", style="yellow")
    table.add_column("Tokens/Word", justify="right", style="magenta")
    table.add_column("Cost Multiplier vs EN", justify="right", style="red")

    for s in RAW_LANGUAGE_SAMPLES:
        res = svc.tokenize(s["text"], "cl100k_base")
        words = s.get("word_count") or len(s["text"].split()) or 1
        tpw = round(res.token_count / words, 2)
        mult = round(res.token_count / en_tokens, 2)
        table.add_row(
            s["name"],
            s["script"],
            str(words),
            str(res.token_count),
            f"{tpw} t/w",
            f"{mult}x",
        )

    console.print(table)


@app.command()
def generate_data() -> None:
    """Regenerate all JSON datasets for the web application."""
    export_all_datasets()
    console.print("[bold green]Datasets successfully regenerated in data/![/bold green]")


if __name__ == "__main__":
    app()
