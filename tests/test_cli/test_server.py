"""Tests for server CLI commands."""
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from gondola.cli.main import app

runner = CliRunner()


@pytest.fixture
def tmp_project():
    """Create a minimal directory with main.py for server tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            (Path(tmpdir) / "main.py").write_text("# FastAPI app")
            yield tmpdir
        finally:
            os.chdir(original_cwd)


def test_server_not_in_project(tmp_project):
    """Test server fails when main.py not found."""
    original_cwd = os.getcwd()
    try:
        os.chdir("/tmp")
        result = runner.invoke(app, ["run", "server"])
        assert result.exit_code == 1
        assert "main.py not found" in result.stdout
    finally:
        os.chdir(original_cwd)


@patch("gondola.cli.server.subprocess.run")
def test_server_success(mock_subprocess, tmp_project):
    """Test successful server start."""
    original_cwd = os.getcwd()
    mock_subprocess.return_value = MagicMock(returncode=0)
    try:
        os.chdir(tmp_project)
        result = runner.invoke(app, ["run", "server", "--port", "8080"])
        assert "Starting server" in result.stdout or result.exit_code == 0
    finally:
        os.chdir(original_cwd)


@patch("gondola.cli.server.subprocess.run")
def test_server_with_options(mock_subprocess, tmp_project):
    """Test server with various options."""
    original_cwd = os.getcwd()
    mock_subprocess.return_value = MagicMock(returncode=0)
    try:
        os.chdir(tmp_project)
        result = runner.invoke(
            app,
            ["run", "server", "--host", "127.0.0.1", "--port", "9000", "--no-reload", "--workers", "2"],
        )
        assert result.exit_code == 0 or "Starting server" in result.stdout
    finally:
        os.chdir(original_cwd)
