"""
gondola db — database management commands.

gondola db init
  1. Reads .env → DATABASE_URL
  2. Creates the database if it does not exist
  3. Enables any configured PostgreSQL extensions
  4. Runs: alembic revision --autogenerate -m "Initial migration"
           alembic upgrade head
"""

import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from urllib.parse import urlparse

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer(help="Database management commands")
console = Console()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _read_dotenv(path: Path) -> dict[str, str]:
    """Minimal .env parser — no external dependencies required."""
    env: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        # Strip optional surrounding quotes
        value = value.strip().strip('"').strip("'")
        env[key.strip()] = value
    return env


def _parse_database_url(url: str) -> dict:
    """
    Parse a SQLAlchemy-style DATABASE_URL into its components.
    Handles async drivers, e.g. postgresql+asyncpg, mysql+asyncmy,
    sqlite+aiosqlite.
    """
    # Strip the async driver portion: postgresql+asyncpg → postgresql
    canonical = re.sub(r"\+\w+", "", url, count=1)
    parsed = urlparse(canonical)
    scheme = parsed.scheme.lower()
    db_name = parsed.path.lstrip("/")

    return {
        "scheme": scheme,
        "host": parsed.hostname or "localhost",
        "port": parsed.port,
        "user": parsed.username or "",
        "password": parsed.password or "",
        "db_name": db_name,
    }


def _venv_python() -> str | None:
    """Return the Poetry venv Python executable for this project, or None."""
    if not shutil.which("poetry"):
        return None
    result = subprocess.run(
        ["poetry", "env", "info", "--executable"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    return None


def _venv_bin(binary: str) -> list[str]:
    """
    Return [path_to_binary] if the binary exists in the poetry venv's bin/,
    else fall back to ["poetry", "run", binary].
    Raises typer.Exit(1) with a helpful message if neither is available.
    """
    python = _venv_python()
    if python:
        bin_path = Path(python).parent / binary
        if bin_path.exists():
            return [str(bin_path)]
        # Venv exists but binary not there → poetry install not run
        console.print(
            f"[red]Error: '{binary}' not found in the project virtual environment.[/red]\n"
            "[yellow]Run [bold]poetry install[/bold] first.[/yellow]"
        )
        raise typer.Exit(1)
    # No poetry — try PATH
    if shutil.which(binary):
        return [binary]
    console.print(
        f"[red]Error: '{binary}' not found. Is poetry installed and has `poetry install` been run?[/red]"
    )
    raise typer.Exit(1)


def _run_python_script(python_bin: str, script: str) -> subprocess.CompletedProcess:
    """Run an inline Python script via the venv interpreter."""
    return subprocess.run(
        [python_bin, "-c", textwrap.dedent(script)],
        capture_output=True,
        text=True,
    )


def _detect_extensions() -> list[str]:
    """
    Detect enabled PostgreSQL extensions from pyproject.toml dependencies.
    geoalchemy2 → postgis,  pgvector → vector
    """
    toml_path = Path("pyproject.toml")
    if not toml_path.exists():
        return []
    content = toml_path.read_text()
    extensions: list[str] = []
    if "geoalchemy2" in content:
        extensions.append("postgis")
    if "pgvector" in content:
        extensions.append("vector")  # SQL extension name for pgvector
    return extensions


# ── Database-specific creation logic ─────────────────────────────────────────

def _create_postgres_db(python_bin: str, info: dict) -> None:
    """Create a PostgreSQL database if it does not already exist."""
    # Double-quote the identifier to handle hyphens / reserved words safely
    safe_db = info["db_name"].replace('"', '""')

    script = f"""\
        import asyncio, sys
        import asyncpg

        async def main():
            try:
                conn = await asyncpg.connect(
                    host={info['host']!r},
                    port={info['port'] or 5432},
                    user={info['user']!r},
                    password={info['password']!r},
                    database="postgres",
                )
            except Exception as e:
                print(f"CONNECT_ERROR: {{e}}", file=sys.stderr)
                sys.exit(1)

            exists = await conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1",
                {info['db_name']!r},
            )
            if exists:
                print("EXISTS")
            else:
                await conn.execute('CREATE DATABASE "{safe_db}"')
                print("CREATED")
            await conn.close()

        asyncio.run(main())
    """
    result = _run_python_script(python_bin, script)
    if result.returncode != 0:
        console.print(f"[red]Error creating database:\n{result.stderr.strip()}[/red]")
        raise typer.Exit(1)

    outcome = result.stdout.strip()
    if outcome == "EXISTS":
        console.print(
            f"[yellow]Database [bold]{info['db_name']}[/bold] already exists — skipping creation.[/yellow]"
        )
    else:
        console.print(f"[green]✓[/green] Database [bold]{info['db_name']}[/bold] created.")


def _create_mysql_db(python_bin: str, info: dict) -> None:
    """Create a MySQL / MariaDB database if it does not already exist."""
    # Backtick-quote the identifier
    safe_db = info["db_name"].replace("`", "``")

    script = f"""\
        import asyncio, sys
        import asyncmy

        async def main():
            try:
                conn = await asyncmy.connect(
                    host={info['host']!r},
                    port={info['port'] or 3306},
                    user={info['user']!r},
                    password={info['password']!r},
                )
            except Exception as e:
                print(f"CONNECT_ERROR: {{e}}", file=sys.stderr)
                sys.exit(1)

            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT SCHEMA_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = %s",
                    ({info['db_name']!r},),
                )
                row = await cursor.fetchone()
                if row:
                    print("EXISTS")
                else:
                    await cursor.execute("CREATE DATABASE `{safe_db}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                    print("CREATED")
            conn.close()

        asyncio.run(main())
    """
    result = _run_python_script(python_bin, script)
    if result.returncode != 0:
        console.print(f"[red]Error creating database:\n{result.stderr.strip()}[/red]")
        raise typer.Exit(1)

    outcome = result.stdout.strip()
    if outcome == "EXISTS":
        console.print(
            f"[yellow]Database [bold]{info['db_name']}[/bold] already exists — skipping creation.[/yellow]"
        )
    else:
        console.print(f"[green]✓[/green] Database [bold]{info['db_name']}[/bold] created.")


def _create_sqlite_db(info: dict) -> None:
    """SQLite databases are created on first connect — just report status."""
    db_file = Path(info["db_name"])
    if db_file.exists():
        console.print(
            f"[yellow]SQLite database [bold]{info['db_name']}[/bold] already exists — skipping creation.[/yellow]"
        )
    else:
        console.print(
            f"[green]✓[/green] SQLite database [bold]{info['db_name']}[/bold] will be created on first migration."
        )


def _enable_pg_extensions(python_bin: str, info: dict, extensions: list[str]) -> None:
    """Create PostgreSQL extensions in the target database."""
    ext_statements = "\n".join(
        f'        await conn.execute("CREATE EXTENSION IF NOT EXISTS \\"{ext}\\"")'
        for ext in extensions
    )

    script = f"""\
        import asyncio, sys
        import asyncpg

        async def main():
            try:
                conn = await asyncpg.connect(
                    host={info['host']!r},
                    port={info['port'] or 5432},
                    user={info['user']!r},
                    password={info['password']!r},
                    database={info['db_name']!r},
                )
            except Exception as e:
                print(f"CONNECT_ERROR: {{e}}", file=sys.stderr)
                sys.exit(1)

{ext_statements}
            await conn.close()
            print("OK")

        asyncio.run(main())
    """
    result = _run_python_script(python_bin, script)
    if result.returncode != 0:
        console.print(f"[red]Error enabling extensions:\n{result.stderr.strip()}[/red]")
        raise typer.Exit(1)
    for ext in extensions:
        console.print(f"[green]✓[/green] Extension [bold]{ext}[/bold] enabled.")


# ── Command ───────────────────────────────────────────────────────────────────

@app.command()
def init() -> None:
    """
    Initialize the database:

    \b
    1. Read .env → DATABASE_URL
    2. Create the database (if it does not exist)
    3. Enable configured extensions (PostgreSQL only)
    4. Run initial Alembic migration (autogenerate + upgrade head)
    """
    # ── Pre-flight checks ──────────────────────────────────────────────────
    if not Path("alembic.ini").exists():
        console.print("[red]Error: alembic.ini not found. Are you in a gondola project directory?[/red]")
        raise typer.Exit(1)

    env_file = Path(".env")
    if not env_file.exists():
        console.print(
            "[red]Error: .env file not found.[/red]\n"
            "[yellow]Copy [bold].env.example[/bold] to [bold].env[/bold] and configure your database credentials.[/yellow]"
        )
        raise typer.Exit(1)

    env = _read_dotenv(env_file)
    db_url = env.get("DATABASE_URL", "").strip()
    if not db_url:
        console.print("[red]Error: DATABASE_URL is not set in .env[/red]")
        raise typer.Exit(1)

    info = _parse_database_url(db_url)
    scheme = info["scheme"]

    console.print(f"\n[dim]DATABASE_URL → [bold]{scheme}[/bold] / [bold]{info['db_name']}[/bold] @ {info['host']}[/dim]\n")

    # ── Resolve Python in the project venv (needed for DB drivers) ─────────
    python_bin = _venv_python()
    if python_bin is None:
        console.print(
            "[red]Error: Could not find the project virtual environment.[/red]\n"
            "[yellow]Run [bold]poetry install[/bold] first.[/yellow]"
        )
        raise typer.Exit(1)

    # ── Step 1: Create database ────────────────────────────────────────────
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as p:
        p.add_task("Checking / creating database...", total=None)
        if scheme in ("postgresql", "postgres"):
            _create_postgres_db(python_bin, info)
        elif scheme == "mysql":
            _create_mysql_db(python_bin, info)
        elif scheme == "sqlite":
            _create_sqlite_db(info)
        else:
            console.print(f"[red]Error: Unsupported database scheme '{scheme}'[/red]")
            raise typer.Exit(1)

    # ── Step 2: Enable extensions (PostgreSQL only) ────────────────────────
    if scheme in ("postgresql", "postgres"):
        extensions = _detect_extensions()
        if extensions:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as p:
                p.add_task(f"Enabling extensions: {', '.join(extensions)}...", total=None)
                _enable_pg_extensions(python_bin, info, extensions)
        else:
            console.print("[dim]No extensions configured — skipping.[/dim]")

    # ── Step 3: Initial migration ──────────────────────────────────────────
    alembic = _venv_bin("alembic")

    console.print("\n[cyan]Running initial migration...[/cyan]")

    # alembic revision --autogenerate -m "Initial migration"
    result = subprocess.run(
        alembic + ["revision", "--autogenerate", "-m", "Initial migration"],
    )
    if result.returncode != 0:
        console.print("[red]Error: alembic revision failed.[/red]")
        raise typer.Exit(1)
    console.print("[green]✓[/green] Migration file created.")

    # alembic upgrade head
    result = subprocess.run(alembic + ["upgrade", "head"])
    if result.returncode != 0:
        console.print("[red]Error: alembic upgrade head failed.[/red]")
        raise typer.Exit(1)
    console.print("[green]✓[/green] Database schema applied.")

    console.print("\n[bold green]✓ Database initialized successfully![/bold green]")
    console.print("[dim]You can now run [bold]gondola start[/bold] to start the server.[/dim]")
