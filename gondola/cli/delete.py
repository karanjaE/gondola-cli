import typer
from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm

from ..utils.file_utils import find_migration_for_model

app = typer.Typer(help="Delete/rollback generated code")
console = Console()

@app.command()
def model(
    name: str = typer.Argument(..., help="Model name to delete"),
    force: bool = typer.Option(False, "--force", help="Skip confirmation"),
):
    """Delete a model and its related files."""
    if not Path("main.py").exists():
        console.print("[red]Error: Not in a FastAPI project directory[/red]")
        raise typer.Exit(1)
    
    from ..utils.string_utils import to_snake_case, to_pascal_case
    
    file_name = to_snake_case(name)
    model_name = to_pascal_case(name)
    
    files_to_delete = [
        Path("app/models") / f"{file_name}.py",
        Path("app/models/serializers") / f"{file_name}_serializer.py",
        Path("test/unit") / f"test_{file_name}.py",
    ]
    
    # Check which files exist
    existing_files = [f for f in files_to_delete if f.exists()]
    
    if not existing_files:
        console.print(f"[yellow]No files found for model '{name}'[/yellow]")
        raise typer.Exit(0)
    
    # Show files to be deleted
    console.print("\n[yellow]The following files will be deleted:[/yellow]")
    for file in existing_files:
        console.print(f"  - {file}")
    
    # Find related migration
    migration_file = find_migration_for_model(model_name)
    if migration_file:
        console.print("\n[yellow]Related migration found:[/yellow]")
        console.print(f"  - {migration_file}")
        console.print("\n[red]Warning: You'll need to manually rollback this migration[/red]")
    
    # Check for dependencies
    dependencies = check_model_dependencies(model_name)
    if dependencies:
        console.print("\n[red]Warning: This model is referenced by:[/red]")
        for dep in dependencies:
            console.print(f"  - {dep}")
        console.print("\n[yellow]Please remove these dependencies first[/yellow]")
        raise typer.Exit(1)
    
    # Confirm deletion
    if not force:
        if not Confirm.ask("\nDo you want to proceed?"):
            console.print("[yellow]Deletion cancelled[/yellow]")
            raise typer.Exit(0)
    
    # Delete files
    for file in existing_files:
        file.unlink()
        console.print(f"[green]✓[/green] Deleted {file}")
    
    # Remove from __init__.py
    remove_model_import(file_name, model_name)
    
    console.print(f"\n[green]✓[/green] Model '{name}' deleted successfully!")
    
    if migration_file:
        console.print("\n[cyan]Next steps:[/cyan]")
        console.print("  gondola migrate downgrade -1")

def check_model_dependencies(model_name: str) -> list:
    """Check if model is referenced in other models."""
    # This is a simplified version - you'd need to parse Python files
    # to detect actual relationships
    dependencies = []
    models_dir = Path("app/models")
    
    if not models_dir.exists():
        return dependencies
    
    for model_file in models_dir.glob("*.py"):
        if model_file.name == "__init__.py":
            continue
        
        content = model_file.read_text()
        if f'Relationship("{model_name}"' in content or f"ForeignKey('{model_name}" in content:
            dependencies.append(model_file.stem)
    
    return dependencies

def remove_model_import(file_name: str, model_name: str) -> None:
    """Remove model import from __init__.py."""
    init_path = Path("app/models/__init__.py")
    
    if not init_path.exists():
        return
    
    content = init_path.read_text()
    import_line = f"from .{file_name} import {model_name}\n"
    
    if import_line in content:
        content = content.replace(import_line, "")
        init_path.write_text(content)

@app.command()
def router(
    name: str = typer.Argument(..., help="Router name to delete"),
    force: bool = typer.Option(False, "--force", help="Skip confirmation"),
):
    """Delete a router and its test."""
    if not Path("main.py").exists():
        console.print("[red]Error: Not in a FastAPI project directory[/red]")
        raise typer.Exit(1)
    
    from ..utils.string_utils import to_snake_case
    
    file_name = to_snake_case(name)
    
    files_to_delete = [
        Path("app/routers") / f"{file_name}.py",
        Path("test/integration") / f"test_{file_name}_routes.py",
    ]
    
    existing_files = [f for f in files_to_delete if f.exists()]
    
    if not existing_files:
        console.print(f"[yellow]No files found for router '{name}'[/yellow]")
        raise typer.Exit(0)
    
    console.print("\n[yellow]The following files will be deleted:[/yellow]")
    for file in existing_files:
        console.print(f"  - {file}")
    
    if not force:
        if not Confirm.ask("\nDo you want to proceed?"):
            console.print("[yellow]Deletion cancelled[/yellow]")
            raise typer.Exit(0)
    
    for file in existing_files:
        file.unlink()
        console.print(f"[green]✓[/green] Deleted {file}")
    
    console.print(f"\n[green]✓[/green] Router '{name}' deleted successfully!")
    console.print("\n[yellow]Remember to remove the router from main.py[/yellow]")
