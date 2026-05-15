import os
import subprocess
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

console = Console()


def start(
    port: Optional[int] = typer.Option(
        None,
        "--port",
        "-p",
        help="Port number (defaults to PORT env var or 8000)",
    ),
    env: str = typer.Option(
        "development",
        "--env",
        "-e",
        help="Runtime mode: dev/development or prod/production",
    ),
    reload: bool = typer.Option(
        False,
        "--reload/--no-reload",
        "-r/-R",
        help="Reload app on code changes (development only)",
    ),
    host: str = typer.Option(
        "127.0.0.1",
        "--host",
        "-H",
        help="Host address",
    ),
    workers: int = typer.Option(
        1,
        "--workers",
        "-w",
        help="Number of workers (production only)",
    ),
) -> None:
    """Start the FastAPI server."""
    if not Path("main.py").exists():
        console.print("[red]Error: main.py not found in current directory[/red]")
        raise typer.Exit(1)

    # Normalise env
    env_lower = env.lower()
    if env_lower in ("dev", "development"):
        is_production = False
    elif env_lower in ("prod", "production"):
        is_production = True
    else:
        console.print(
            "[red]Error: --env must be one of: dev, development, prod, production[/red]"
        )
        raise typer.Exit(1)

    # Resolve port: CLI flag → PORT env var → 8000
    if port is None:
        port = int(os.environ.get("PORT", 8000))

    if is_production:
        cmd = ["fastapi", "run", "main.py", "--host", host, "--port", str(port)]
        if workers > 1:
            cmd.extend(["--workers", str(workers)])
        mode_label = "production"
    else:
        cmd = ["fastapi", "dev", "main.py", "--host", host, "--port", str(port)]
        if reload:
            cmd.append("--reload")
        mode_label = "development"

    console.print(
        f"[cyan]Starting FastAPI server ({mode_label}) on {host}:{port}...[/cyan]"
    )

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped[/yellow]")
    except Exception as e:
        console.print(f"[red]Error starting server: {e}[/red]")
        raise typer.Exit(1)
