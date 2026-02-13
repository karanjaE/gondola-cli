"""Test fixtures for CLI tests."""
import tempfile
import os
import re
from pathlib import Path
import pytest
from typer.testing import CliRunner
from gondola.cli.main import app


def strip_ansi(text: str) -> str:
    """Strip ANSI color codes from text."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


@pytest.fixture
def runner():
    """CLI runner fixture."""
    return CliRunner()


@pytest.fixture
def temp_project():
    """Create a temporary FastAPI project for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            # Create a minimal FastAPI project structure
            (Path(tmpdir) / "main.py").write_text("# FastAPI app")
            (Path(tmpdir) / "alembic.ini").write_text("[alembic]\nscript_location = migrations")
            (Path(tmpdir) / "app").mkdir()
            (Path(tmpdir) / "app" / "__init__.py").touch()
            (Path(tmpdir) / "app" / "models").mkdir(parents=True)
            (Path(tmpdir) / "app" / "models" / "__init__.py").touch()
            (Path(tmpdir) / "app" / "models" / "serializers").mkdir(parents=True)
            (Path(tmpdir) / "app" / "routers").mkdir(parents=True)
            (Path(tmpdir) / "app" / "services").mkdir(parents=True)
            (Path(tmpdir) / "app" / "lib").mkdir(parents=True)
            (Path(tmpdir) / "test").mkdir()
            (Path(tmpdir) / "test" / "unit").mkdir(parents=True)
            (Path(tmpdir) / "test" / "integration").mkdir(parents=True)
            (Path(tmpdir) / "migrations").mkdir()
            (Path(tmpdir) / "migrations" / "versions").mkdir(parents=True)
            
            yield tmpdir
        finally:
            os.chdir(original_cwd)
