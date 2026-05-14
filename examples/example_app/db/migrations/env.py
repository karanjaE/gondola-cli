from logging.config import fileConfig
import os
import sys
import asyncio

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

from core.config import get_settings
import importlib
from pathlib import Path

def autodiscover_models():
    """Automatically import all model files so SQLModel tables register."""
    models_dir = Path(__file__).resolve().parents[2] / "api" / "models"
    package = "api.models"
    for py_file in models_dir.glob("*.py"):
        name = py_file.stem
        if name.startswith("__") or name == "base_model":
            continue
        importlib.import_module(f"{package}.{name}")

autodiscover_models()

settings = get_settings()
config = context.config

# Override the sqlalchemy.url from alembic.ini with the app's real DB URL
# (strip the async driver so Alembic can use a sync connection)
sync_url = settings.database_url.replace("+asyncpg", "")
config.set_main_option("sqlalchemy.url", sync_url)

# Standard Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# This is what Alembic compares against the live database
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Emits SQL to stdout instead of executing it.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode with a live connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
