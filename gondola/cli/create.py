import re
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..generators.project import ProjectGenerator

app = typer.Typer(help="Create a new FastAPI project")
console = Console()

VALID_DB_ENGINES = ["postgres", "mysql", "mariadb", "sqlite"]
AVAILABLE_EXTENSIONS = ["postgis", "pgvector"]

DB_LABELS = {
    "postgres":  "PostgreSQL  (asyncpg + SQLModel — recommended)",
    "mysql":     "MySQL       (asyncmy + SQLModel)",
    "mariadb":   "MariaDB     (asyncmy + SQLModel)",
    "sqlite":    "SQLite      (aiosqlite + SQLModel)",
}


def _slugify(name: str) -> str:
    """Convert any string to lowercase-with-hyphens."""
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9_-]", "-", name)
    name = re.sub(r"-{2,}", "-", name)
    return name.strip("-")


def _is_valid_name(name: str) -> bool:
    return bool(re.fullmatch(r"[a-z][a-z0-9_-]*", name))


def _select(prompt_text: str, choices: list[str], labels: Optional[dict[str, str]] = None, default_index: int = 0) -> str:
    """Render a numbered menu and return the selected value."""
    console.print(f"\n[bold cyan]{prompt_text}[/bold cyan]")
    for i, choice in enumerate(choices, 1):
        label = labels.get(choice, choice) if labels else choice
        marker = "[bold green]>[/bold green] " if i == default_index + 1 else "  "
        console.print(f"  {marker}[bold]{i}.[/bold] {label}")

    while True:
        raw = Prompt.ask(
            f"  [dim]Enter number[/dim]",
            default=str(default_index + 1),
            console=console,
        )
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
        except ValueError:
            pass
        console.print("  [red]Please enter a valid number from the list.[/red]")


def _multiselect(prompt_text: str, choices: list[str]) -> list[str]:
    """Render a numbered multi-select menu and return selected values."""
    console.print(f"\n[bold cyan]{prompt_text}[/bold cyan]")
    for i, choice in enumerate(choices, 1):
        console.print(f"  [bold]{i}.[/bold] {choice}")
    console.print("  [dim]Enter numbers separated by commas (e.g. 1,2), or press Enter to skip[/dim]")

    raw = Prompt.ask("  Selection", default="", console=console)
    if not raw.strip():
        return []

    selected: list[str] = []
    for part in raw.split(","):
        part = part.strip()
        try:
            idx = int(part) - 1
            if 0 <= idx < len(choices):
                selected.append(choices[idx])
        except ValueError:
            pass
    return list(dict.fromkeys(selected))  # deduplicate, preserve order


@app.command()
def project(
    name: Optional[str] = typer.Argument(None, help="Project name (omit to use interactive mode)"),
    db: Optional[str] = typer.Option(None, "--db", "-d", help="Database engine (postgres, mysql, mariadb, sqlite)"),
    docker: Optional[bool] = typer.Option(None, "--docker/--no-docker", "-x/-X", help="Include Docker setup"),
    extensions: Optional[str] = typer.Option(None, "--extensions", "-e", help="Extensions (comma-separated)"),
) -> None:
    """Initialize a new FastAPI project (interactive by default)."""

    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]gondola init[/bold cyan] — [dim]FastAPI project scaffolding[/dim]",
            border_style="cyan",
        )
    )

    # ── Project name ──────────────────────────────────────────────────────
    if name is None:
        raw_name = Prompt.ask(
            "\n  [bold]Project name[/bold]",
            default="my-fastapi-project",
            console=console,
        )
        name = _slugify(raw_name)
        if name != raw_name:
            console.print(f"  [dim]→ Normalized to:[/dim] [cyan]{name}[/cyan]")
    else:
        name = _slugify(name)

    if not _is_valid_name(name):
        console.print(f"[red]Error: '{name}' is not a valid project name. Use lowercase letters, numbers, hyphens, or underscores.[/red]")
        raise typer.Exit(1)

    project_path = Path.cwd() / name
    if project_path.exists():
        console.print(f"[red]Error: Directory '{name}' already exists[/red]")
        raise typer.Exit(1)

    # ── Database engine ───────────────────────────────────────────────────
    if db is None:
        db = _select("Database engine", VALID_DB_ENGINES, labels=DB_LABELS, default_index=0)
    elif db not in VALID_DB_ENGINES:
        console.print(f"[red]Error: --db must be one of: {', '.join(VALID_DB_ENGINES)}[/red]")
        raise typer.Exit(1)

    # ── Docker ────────────────────────────────────────────────────────────
    if docker is None:
        docker = Confirm.ask("\n  [bold]Include Docker setup?[/bold]", default=True, console=console)

    # ── Extensions ────────────────────────────────────────────────────────
    ext_list: list[str] = []
    if extensions is not None:
        # Non-interactive: parse comma-separated string from CLI flag
        ext_list = [e.strip() for e in extensions.split(",") if e.strip()]
        invalid = [e for e in ext_list if e not in AVAILABLE_EXTENSIONS]
        if invalid:
            console.print(f"[red]Error: Invalid extensions: {', '.join(invalid)}. Available: {', '.join(AVAILABLE_EXTENSIONS)}[/red]")
            raise typer.Exit(1)
    else:
        want_ext = Confirm.ask(
            "\n  [bold]Include PostgreSQL extensions?[/bold] [dim](postgis, pgvector)[/dim]",
            default=False,
            console=console,
        )
        if want_ext:
            ext_list = _multiselect("Select extensions", AVAILABLE_EXTENSIONS)

    # Only extensions make sense for postgres
    if ext_list and db not in ("postgres", "postgresql"):
        console.print("[yellow]Warning: Extensions are only applicable to PostgreSQL. Ignoring extensions.[/yellow]")
        ext_list = []

    # ── Summary ───────────────────────────────────────────────────────────
    console.print()
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="dim", no_wrap=True)
    table.add_column(style="bold")
    table.add_row("Project", name)
    table.add_row("Database", db)
    table.add_row("Docker", "Yes" if docker else "No")
    table.add_row("Extensions", ", ".join(ext_list) if ext_list else "None")
    console.print(Panel(table, title="[bold]Project configuration[/bold]", border_style="cyan", expand=False))

    if not Confirm.ask("\n  [bold]Create project?[/bold]", default=True, console=console):
        console.print("[yellow]Aborted.[/yellow]")
        raise typer.Exit(0)

    # ── Normalise db engine for the generator ─────────────────────────────
    db_engine = "postgresql" if db in ("postgres", "postgresql") else db

    # ── Generate ──────────────────────────────────────────────────────────
    console.print()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(description="Generating project structure...", total=None)
        generator = ProjectGenerator(
            name=name,
            db_engine=db_engine,
            include_docker=docker,
            extensions=ext_list,
        )
        generator.generate()

    console.print(f"\n[green]✓[/green] Project [bold]{name}[/bold] created successfully!")
    console.print("\n[cyan]Next steps:[/cyan]")
    console.print(f"  cd {name}")
    console.print("  poetry install")
    console.print("  # Configure your .env file")
    console.print("  gondola migrate up")
    console.print("  gondola start")
