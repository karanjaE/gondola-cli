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
        "--host", host,
        "--port", str(port),
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


@app.command()
def celery_worker(
    loglevel: str = typer.Option("info", "--loglevel", help="Log level"),
):
    """Start Celery worker."""
    if not Path("app/lib").exists():
        console.print("[red]Error: Not in a FastAPI project directory[/red]")
        raise typer.Exit(1)
    
    console.print("[cyan]Starting Celery worker...[/cyan]")
    
    try:
        subprocess.run([
            "celery",
            "-A", "app.lib.celery_app",
            "worker",
            "--loglevel", loglevel,
        ])
    except KeyboardInterrupt:
        console.print("\n[yellow]Celery worker stopped[/yellow]")


@app.command()
def celery_beat(
    loglevel: str = typer.Option("info", "--loglevel", help="Log level"),
):
    """Start Celery beat scheduler."""
    if not Path("app/lib").exists():
        console.print("[red]Error: Not in a FastAPI project directory[/red]")
        raise typer.Exit(1)
    
    console.print("[cyan]Starting Celery beat...[/cyan]")
    
    try:
        subprocess.run([
            "celery",
            "-A", "app.lib.celery_app",
            "beat",
            "--loglevel", loglevel,
        ])
    except KeyboardInterrupt:
        console.print("\n[yellow]Celery beat stopped[/yellow]")
