from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..generators.project import ProjectGenerator

app = typer.Typer(help="Create a new FastAPI project")

console = Console()


@app.command()
def project(
    name: str = typer.Argument(..., help="Project name"),
    db: str = typer.Option(
        "postgres",
        "--db",
        "-d",
        help="Database engine (postgres, mysql, mariadb, sqlite)",
    ),
    docker: bool = typer.Option(
        True,
        "--docker/--no-docker",
        "-x",
        help="Include Docker setup",
    ),
    extensions: Optional[str] = typer.Option(
        None,
        "--extensions",
        "-e",
        help="Database extensions (comma-separated: postgis,pgvector)",
    ),
) -> None:
    """Initialize a new FastAPI project"""

    if db not in ["postgres", "postgresql", "mysql", "mariadb", "sqlite"]:
        console.print("[red]Error: Database must be one of: postgres, mysql, mariadb, sqlite[/red]")
        raise typer.Exit(1)
        
    # Map mariadb and postgres to their underlying engine names for the generator
    if db in ["postgres", "postgresql"]:
        db = "postgresql"
    elif db == "mariadb":
        db = "mysql"
        raise typer.Exit(1)

    project_path = Path.cwd() / name

    if project_path.exists():
        console.print(f"[red]Error: Directory '{name}' already exists[/red]")
        raise typer.Exit(1)

    ext_list: list[str] = []
    if extensions:
        ext_list = [ext.strip() for ext in extensions.split(",")]
        valid_extensions = ["postgis", "pgvector"]
        invalid = [ext for ext in ext_list if ext not in valid_extensions]

        if invalid:
            console.print(f"[red]Error: Invalid extensions: {', '.join(invalid)}[/red]")
            raise typer.Exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(description="Generating project structure...", total=None)

        generator = ProjectGenerator(
            name=name,
            db_engine=db,
            include_docker=docker,
            extensions=ext_list,
        )
        generator.generate()

        console.print(f"\n[green]✓[/green] Project '{name}' created successfully!")
        console.print("\n[cyan]Next steps:[/cyan]")
        console.print(f"  cd {name}")
        console.print("  poetry install")
        console.print("  # Configure your .env file")
        console.print("  gondola migrate up")
        console.print("  gondola start")
