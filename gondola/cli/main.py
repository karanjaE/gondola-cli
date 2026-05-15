import typer
from rich.console import Console

from .create import app as create_app
from .delete import app as delete_app
from .generate import app as generate_app
from .migrate import app as migrate_app
from .server import start as start_command

app = typer.Typer(
    name="gondola",
    help="Console tool for FastAPI",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()

# ── gondola init / gondola i ───────────────────────────────────────────────
app.add_typer(create_app, name="init", help="Create a new FastAPI project")
app.add_typer(create_app, name="i", hidden=True)

# ── gondola generate / gondola g ──────────────────────────────────────────
app.add_typer(generate_app, name="generate", help="Generate code components")
app.add_typer(generate_app, name="g", hidden=True)

# ── gondola delete / gondola d ────────────────────────────────────────────
app.add_typer(delete_app, name="delete", help="Delete generated code")
app.add_typer(delete_app, name="d", hidden=True)

# ── gondola migrate ───────────────────────────────────────────────────────
app.add_typer(migrate_app, name="migrate", help="Database migration commands")

# ── gondola start / gondola s ─────────────────────────────────────────────
app.command(name="start", help="Start the FastAPI server")(start_command)
app.command(name="s", hidden=True)(start_command)


if __name__ == "__main__":
    app()
