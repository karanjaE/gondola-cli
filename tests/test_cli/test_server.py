"""Tests for server CLI commands."""
import os
import pytest
import tempfile
from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from gondola.cli.main import app


runner = CliRunner()


@pytest.fixture
def tmp_project():
    """Create a temporary FastAPI project for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            # Create a minimal FastAPI project structure
            (Path(tmpdir) / "main.py").write_text("# FastAPI app")
            (Path(tmpdir) / "app").mkdir()
            (Path(tmpdir) / "app" / "lib").mkdir(parents=True)
            
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
        # Note: subprocess.run will actually be called, but we mock it
        # The command should construct correctly
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
            ["run", "server", "--host", "127.0.0.1", "--port", "9000", "--no-reload", "--workers", "2"]
        )
        # Should construct command with all options
        assert result.exit_code == 0 or "Starting server" in result.stdout
    finally:
        os.chdir(original_cwd)


def test_celery_worker_not_in_project(tmp_project):
    """Test celery worker fails when not in a FastAPI project."""
    original_cwd = os.getcwd()
    try:
        os.chdir("/tmp")
        result = runner.invoke(app, ["run", "celery-worker"])
        assert result.exit_code == 1
        assert "Not in a FastAPI project directory" in result.stdout
    finally:
        os.chdir(original_cwd)


@patch("gondola.cli.server.subprocess.run")
def test_celery_worker_success(mock_subprocess, tmp_project):
    """Test successful celery worker start."""
    original_cwd = os.getcwd()
    mock_subprocess.return_value = MagicMock(returncode=0)
    try:
        os.chdir(tmp_project)
        result = runner.invoke(app, ["run", "celery-worker"])
        assert "Starting Celery worker" in result.stdout or result.exit_code == 0
    finally:
        os.chdir(original_cwd)


@patch("gondola.cli.server.subprocess.run")
def test_celery_worker_with_loglevel(mock_subprocess, tmp_project):
    """Test celery worker with loglevel option."""
    original_cwd = os.getcwd()
    mock_subprocess.return_value = MagicMock(returncode=0)
    try:
        os.chdir(tmp_project)
        result = runner.invoke(app, ["run", "celery-worker", "--loglevel", "debug"])
        assert result.exit_code == 0 or "Starting Celery worker" in result.stdout
    finally:
        os.chdir(original_cwd)


def test_celery_beat_not_in_project(tmp_project):
    """Test celery beat fails when not in a FastAPI project."""
    original_cwd = os.getcwd()
    try:
        os.chdir("/tmp")
        result = runner.invoke(app, ["run", "celery-beat"])
        assert result.exit_code == 1
        assert "Not in a FastAPI project directory" in result.stdout
    finally:
        os.chdir(original_cwd)


@patch("gondola.cli.server.subprocess.run")
def test_celery_beat_success(mock_subprocess, tmp_project):
    """Test successful celery beat start."""
    original_cwd = os.getcwd()
    mock_subprocess.return_value = MagicMock(returncode=0)
    try:
        os.chdir(tmp_project)
        result = runner.invoke(app, ["run", "celery-beat"])
        assert "Starting Celery beat" in result.stdout or result.exit_code == 0
    finally:
        os.chdir(original_cwd)


@patch("gondola.cli.server.subprocess.run")
def test_celery_beat_with_loglevel(mock_subprocess, tmp_project):
    """Test celery beat with loglevel option."""
    original_cwd = os.getcwd()
    mock_subprocess.return_value = MagicMock(returncode=0)
    try:
        os.chdir(tmp_project)
        result = runner.invoke(app, ["run", "celery-beat", "--loglevel", "warning"])
        assert result.exit_code == 0 or "Starting Celery beat" in result.stdout
    finally:
        os.chdir(original_cwd)
