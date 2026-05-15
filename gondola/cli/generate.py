import subprocess
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ..generators.mailer import MailerGenerator
from ..generators.model import ModelGenerator
from ..generators.router import RouterGenerator
from ..generators.service import ServiceGenerator

app = typer.Typer(help="Generate code components")
console = Console()


def _is_api_layout() -> bool:
    return Path("api/models").exists()


def _assert_alembic() -> None:
    if not Path("alembic.ini").exists():
        console.print("[red]Error: Not in a FastAPI project with Alembic[/red]")
        raise typer.Exit(1)


@app.command()
def model(
    name: str = typer.Argument(..., help="Model name (e.g., User, BlogPost)"),
    fields: str = typer.Option(
        "",
        "--fields",
        help="Fields definition (e.g., 'name:str,email:str,age:int')",
    ),
) -> None:
    """Generate a new model with schema and test."""

    if not Path("main.py").exists():
        console.print("[red]Error: Not in a FastAPI project directory[/red]")
        raise typer.Exit(1)

    generator = ModelGenerator(name=name, fields=fields)
    generator.generate()

    console.print(f"[green]✓[/green] Model '{name}' generated successfully!")
    console.print("\n[cyan]Files created:[/cyan]")
    console.print(f"  - api/models/{generator.file_name}.py")
    console.print(f"  - api/models/schemas/{generator.file_name}.py")
    console.print(f"  - test/unit/models/test_{generator.file_name}.py")
    console.print("\n[cyan]Next steps:[/cyan]")
    console.print(f"  gondola generate migration 'Create {name} model'")
    console.print("  gondola migrate up")


@app.command()
def router(
    name: str = typer.Argument(..., help="Router name (e.g., users, blog-posts)"),
    model: Optional[str] = typer.Option(None, "--model", help="Associated model name"),
) -> None:
    """Generate a new router/endpoint with integration test."""

    if not Path("main.py").exists():
        console.print("[red]Error: Not in a FastAPI project directory[/red]")
        raise typer.Exit(1)

    generator = RouterGenerator(name=name, model_name=model)
    generator.generate()

    console.print(f"[green]✓[/green] Router '{name}' generated successfully!")
    console.print("\n[cyan]Files created:[/cyan]")
    console.print(f"  - api/routers/{generator.file_name}.py")
    console.print(f"  - test/integration/routers/test_{generator.file_name}_routes.py")


@app.command()
def service(
    name: str = typer.Argument(..., help="Service name (e.g., UserNotification)"),
) -> None:
    """Generate a new service for business logic."""

    if not Path("main.py").exists():
        console.print("[red]Error: Not in a FastAPI project directory[/red]")
        raise typer.Exit(1)

    generator = ServiceGenerator(name=name)
    generator.generate()

    console.print(f"[green]✓[/green] Service '{name}' generated successfully!")
    console.print("\n[cyan]Files created:[/cyan]")
    console.print(f"  - api/services/{generator.file_name}.py")
    console.print(f"  - test/unit/services/test_{generator.file_name}.py")


@app.command()
def mailer(
    name: str = typer.Argument(..., help="Mailer name (e.g., Welcome, PasswordReset)"),
) -> None:
    """Generate a new mailer with template and test."""

    if not Path("main.py").exists():
        console.print("[red]Error: Not in a FastAPI project directory[/red]")
        raise typer.Exit(1)

    generator = MailerGenerator(name=name)
    generator.generate()

    console.print(f"[green]✓[/green] Mailer '{name}' generated successfully!")
    console.print("\n[cyan]Files created:[/cyan]")
    console.print(f"  - api/mailers/{generator.file_name}.py")
    console.print(f"  - test/unit/mailers/test_{generator.file_name}.py")


@app.command()
def migration(
    message: str = typer.Argument(..., help="Migration message / description"),
) -> None:
    """Create a new Alembic migration (autogenerate)."""
    _assert_alembic()
    try:
        subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", message],
            check=True,
        )
        console.print(f"[green]✓[/green] Migration created: {message}")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error creating migration: {e}[/red]")
        raise typer.Exit(1)
