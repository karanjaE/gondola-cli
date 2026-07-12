import subprocess
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

app = typer.Typer(help="Database migration commands")
console = Console()


def _assert_alembic() -> None:
    if not Path("alembic.ini").exists():
        console.print("[red]Error: Not in a FastAPI project with Alembic[/red]")
        raise typer.Exit(1)


@app.command()
def up(
    revision: Optional[str] = typer.Option(
        None,
        "--revision",
        "-r",
        help="Target revision hash (defaults to 'head')",
    ),
) -> None:
    """Apply migrations (upgrade)."""
    _assert_alembic()
    target = revision or "head"
    try:
        subprocess.run(["alembic", "upgrade", target], check=True)
        console.print("[green]✓[/green] Migrations applied successfully")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error running migrations: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def down(
    revision: Optional[str] = typer.Option(
        None,
        "--revision",
        "-r",
        help="Target revision hash (defaults to rolling back one revision)",
    ),
) -> None:
    """Rollback migrations (downgrade)."""
    _assert_alembic()
    target = revision or "-1"
    try:
        subprocess.run(["alembic", "downgrade", target], check=True)
        console.print("[green]✓[/green] Migration rolled back successfully")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error rolling back migration: {e}[/red]")
        raise typer.Exit(1)


@app.command(name="history")
def history() -> None:
    """Show migration history."""
    _assert_alembic()
    try:
        subprocess.run(["alembic", "history"], check=True)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error showing history: {e}[/red]")
        raise typer.Exit(1)


# Alias: gondola migrate h
@app.command(name="h", hidden=True)
def history_alias() -> None:
    """Alias for 'history'."""
    history()


@app.command(name="current")
def current() -> None:
    """Show current migration revision."""
    _assert_alembic()
    try:
        subprocess.run(["alembic", "current"], check=True)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error showing current migration: {e}[/red]")
        raise typer.Exit(1)


# Alias: gondola migrate c
@app.command(name="c", hidden=True)
def current_alias() -> None:
    """Alias for 'current'."""
    current()
