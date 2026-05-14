import typer
from pathlib import Path
from rich.console import Console

from ..generators.mailer import MailerGenerator
from ..generators.model import ModelGenerator
from ..generators.router import RouterGenerator
from ..generators.service import ServiceGenerator

app = typer.Typer(help="Generate code components")
console = Console()


def _is_api_layout() -> bool:
    return Path("api/models").exists()


@app.command()
def model(
    name: str = typer.Argument(..., help="Model name (e.g., User, BlogPost)"),
    fields: str = typer.Option(
        "",
        "--fields",
        help="Fields definition (e.g., 'name:str,email:str,age:int')",
    ),
) -> None:
    """Generate a new model with migration."""

    if not Path("main.py").exists():
        console.print("[red]Error: Not in a FastAPI project directory[/red]")
        raise typer.Exit(1)

    generator = ModelGenerator(name=name, fields=fields)
    generator.generate()

    console.print(f"[green]✓[/green] Model '{name}' generated successfully!")
    console.print("\n[cyan]Files created:[/cyan]")
    if _is_api_layout():
        console.print(f"  - api/models/{generator.file_name}.py")
        console.print(f"  - api/models/schemas/{generator.file_name}.py")
    else:
        console.print(f"  - app/models/{generator.file_name}.py")
        console.print(f"  - app/models/serializers/{generator.file_name}_serializer.py")
    console.print(f"  - test/unit/test_{generator.file_name}.py")
    console.print("\n[cyan]Next steps:[/cyan]")
    console.print(f"  gondola migrate create 'Create {name} model'")
    console.print("  gondola migrate upgrade")


@app.command()
def router(
    name: str = typer.Argument(..., help="Router name (e.g., User, BlogPost)"),
    model: str = typer.Option(None, "--model", help="Associated model name"),
) -> None:
    """Generate a new router/endpoint."""

    if not Path("main.py").exists():
        console.print("[red]Error: Not in a FastAPI project directory[/red]")
        raise typer.Exit(1)

    generator = RouterGenerator(name=name, model_name=model)
    generator.generate()

    console.print(f"[green]✓[/green] Router '{name}' generated successfully!")
    console.print("\n[cyan]Files created:[/cyan]")
    if _is_api_layout():
        console.print(f"  - api/routers/{generator.file_name}.py")
    else:
        console.print(f"  - app/routers/{generator.file_name}.py")
    console.print(f"  - test/integration/test_{generator.file_name}_routes.py")


@app.command()
def service(
    name: str = typer.Argument(..., help="Service name (e.g., UserService, EmailService)"),
) -> None:
    """Generate a new service for business logic."""

    if not Path("main.py").exists():
        console.print("[red]Error: Not in a FastAPI project directory[/red]")
        raise typer.Exit(1)

    generator = ServiceGenerator(name=name)
    generator.generate()

    console.print(f"[green]✓[/green] Service '{name}' generated successfully!")
    console.print("\n[cyan]Files created:[/cyan]")
    if _is_api_layout():
        console.print(f"  - api/services/{generator.file_name}.py")
    else:
        console.print(f"  - app/services/{generator.file_name}.py")
    console.print(f"  - test/unit/test_{generator.file_name}.py")


@app.command()
def mailer(
    name: str = typer.Argument(..., help="Mailer name (e.g., Welcome, PasswordReset)"),
) -> None:
    """Generate a new mailer."""

    if not Path("main.py").exists():
        console.print("[red]Error: Not in a FastAPI project directory[/red]")
        raise typer.Exit(1)

    generator = MailerGenerator(name=name)
    generator.generate()

    console.print(f"[green]✓[/green] Mailer '{name}' generated successfully!")
    console.print("\n[cyan]Files created:[/cyan]")
    console.print(f"  - app/lib/mailers/{generator.file_name}.py")
    console.print(f"  - test/unit/test_{generator.file_name}.py")
