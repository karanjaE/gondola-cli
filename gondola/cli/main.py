import typer
from rich.console import Console

from .create import app as create_app
from .delete import app as delete_app
from .generate import app as generate_app
from .migrate import app as migrate_app
from .server import app as server_app

app = typer.Typer(
    name="gondola",
    help="Console tool for FastAPI",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()

app.add_typer(create_app, name="create")
app.add_typer(generate_app, name="generate")
app.add_typer(delete_app, name="delete")
app.add_typer(migrate_app, name="migrate")
app.add_typer(server_app, name="run")

if __name__ == "__main__":
    app()
