import subprocess
from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer(help="Server management commands")
console = Console()


@app.command()
def server(
    port: int = typer.Option(8000, "--port", help="Port number"),
    host: str = typer.Option("0.0.0.0", "--host", help="Host address"),
    reload: bool = typer.Option(True, "--reload/--no-reload", help="Auto-reload on changes"),
    workers: int = typer.Option(1, "--workers", help="Number of workers"),
):
    """Start the FastAPI development server."""
    if not Path("main.py").exists():
        console.print("[red]Error: main.py not found in current directory[/red]")
        raise typer.Exit(1)

    cmd = [
        "uvicorn",
        "main:app",
        "--host",
        host,
        "--port",
        str(port),
    ]

    if reload:
        cmd.append("--reload")

    if workers > 1:
        cmd.extend(["--workers", str(workers)])

    console.print(f"[cyan]Starting server on {host}:{port}...[/cyan]")

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped[/yellow]")
    except Exception as e:
        console.print(f"[red]Error starting server: {e}[/red]")
        raise typer.Exit(1)
