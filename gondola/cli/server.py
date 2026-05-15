import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

console = Console()


def _fastapi_runner() -> list[str]:
    """
    Resolve the fastapi CLI binary to use, in priority order:

    1. Exact binary in the Poetry-managed venv for this project
       (found via `poetry env info --executable`).
    2. fastapi binary sitting next to the currently-running Python
       (covers activated venvs and pipx installs where fastapi is co-installed).
    3. fastapi anywhere on PATH.

    Raises typer.Exit(1) with a helpful message if fastapi cannot be found
    and we know the project venv exists but hasn't had `poetry install` run.
    """
    # ── 1. Resolve from the Poetry venv for this project ──────────────────
    if Path("pyproject.toml").exists() and shutil.which("poetry"):
        try:
            result = subprocess.run(
                ["poetry", "env", "info", "--executable"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                venv_python = Path(result.stdout.strip())
                fastapi_bin = venv_python.parent / "fastapi"
                if fastapi_bin.exists():
                    return [str(fastapi_bin)]
                # Venv exists but fastapi binary is missing → deps not installed
                console.print(
                    "[red]Error: fastapi is not installed in the project virtual environment.[/red]\n"
                    "[yellow]Run [bold]poetry install[/bold] first, then try again.[/yellow]"
                )
                raise typer.Exit(1)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass  # poetry not usable here — fall through

    # ── 2. Same venv as the running Python ────────────────────────────────
    venv_fastapi = Path(sys.executable).parent / "fastapi"
    if venv_fastapi.exists():
        return [str(venv_fastapi)]

    # ── 3. PATH fallback ──────────────────────────────────────────────────
    if shutil.which("fastapi"):
        return ["fastapi"]

    console.print(
        "[red]Error: fastapi CLI not found.[/red]\n"
        "[yellow]Make sure fastapi[standard] is installed: [bold]poetry install[/bold][/yellow]"
    )
    raise typer.Exit(1)


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

    runner = _fastapi_runner()

    if is_production:
        cmd = runner + ["run", "main.py", "--host", host, "--port", str(port)]
        if workers > 1:
            cmd.extend(["--workers", str(workers)])
        mode_label = "production"
    else:
        cmd = runner + ["dev", "main.py", "--host", host, "--port", str(port)]
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

