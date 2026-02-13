import subprocess
from pathlib import Path
import typer
from rich.console import Console

app = typer.Typer(help="Database migration commands")
console = Console()


@app.command()
def create(
    message: str = typer.Argument(..., help="Migration message"),
):
    """Create a new migration."""
    if not Path("alembic.ini").exists():
        console.print("[red]Error: Not in a FastAPI project with Alembic[/red]")
        raise typer.Exit(1)
    
    try:
        subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", message],
            check=True,
        )
        console.print(f"[green]✓[/green] Migration created: {message}")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error creating migration: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def upgrade(
    revision: str = typer.Argument("head", help="Target revision"),
):
    """Run migrations."""
    if not Path("alembic.ini").exists():
        console.print("[red]Error: Not in a FastAPI project with Alembic[/red]")
        raise typer.Exit(1)
    
    try:
        subprocess.run(["alembic", "upgrade", revision], check=True)
        console.print(f"[green]✓[/green] Migrations applied successfully")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error running migrations: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def downgrade(
    revision: str = typer.Argument("-1", help="Target revision"),
):
    """Rollback migrations."""
    if not Path("alembic.ini").exists():
        console.print("[red]Error: Not in a FastAPI project with Alembic[/red]")
        raise typer.Exit(1)
    
    try:
        subprocess.run(["alembic", "downgrade", revision], check=True)
        console.print(f"[green]✓[/green] Migration rolled back successfully")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error rolling back migration: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def history():
    """Show migration history."""
    if not Path("alembic.ini").exists():
        console.print("[red]Error: Not in a FastAPI project with Alembic[/red]")
        raise typer.Exit(1)
    
    try:
        subprocess.run(["alembic", "history"], check=True)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error showing history: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def current():
    """Show current migration."""
    if not Path("alembic.ini").exists():
        console.print("[red]Error: Not in a FastAPI project with Alembic[/red]")
        raise typer.Exit(1)
    
    try:
        subprocess.run(["alembic", "current"], check=True)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error showing current migration: {e}[/red]")
        raise typer.Exit(1)
