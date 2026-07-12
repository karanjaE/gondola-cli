"""Tests for migrate CLI commands."""
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
            (Path(tmpdir) / "alembic.ini").write_text("[alembic]\nscript_location = migrations")
            (Path(tmpdir) / "migrations").mkdir()
            (Path(tmpdir) / "migrations" / "versions").mkdir(parents=True)
            
            yield tmpdir
        finally:
            os.chdir(original_cwd)


def test_migrate_up_not_in_project(tmp_project):
    """Test migrate up fails when not in a FastAPI project."""
    original_cwd = os.getcwd()
    try:
        os.chdir("/tmp")
        result = runner.invoke(app, ["migrate", "up"])
        assert result.exit_code == 1
        assert "Not in a FastAPI project with Alembic" in result.stdout
    finally:
        os.chdir(original_cwd)


@patch("gondola.cli.migrate.subprocess.run")
def test_migrate_up_success(mock_subprocess, tmp_project):
    """Test successful migration upgrade."""
    original_cwd = os.getcwd()
    mock_subprocess.return_value = MagicMock(returncode=0)
    try:
        os.chdir(tmp_project)
        result = runner.invoke(app, ["migrate", "up", "-r", "head"])
        assert result.exit_code == 0
        mock_subprocess.assert_called_once()
        assert "Migrations applied successfully" in result.stdout
    finally:
        os.chdir(original_cwd)


def test_migrate_down_not_in_project(tmp_project):
    """Test migrate down fails when not in a FastAPI project."""
    original_cwd = os.getcwd()
    try:
        os.chdir("/tmp")
        result = runner.invoke(app, ["migrate", "down"])
        assert result.exit_code == 1
        assert "Not in a FastAPI project with Alembic" in result.stdout
    finally:
        os.chdir(original_cwd)


@patch("gondola.cli.migrate.subprocess.run")
def test_migrate_down_success(mock_subprocess, tmp_project):
    """Test successful migration downgrade."""
    original_cwd = os.getcwd()
    mock_subprocess.return_value = MagicMock(returncode=0)
    try:
        os.chdir(tmp_project)
        # Use "-r head" or a specific revision instead of a bare positional,
        # which is no longer accepted (revision is now an option).
        result = runner.invoke(app, ["migrate", "down", "-r", "head"])
        assert result.exit_code == 0
        mock_subprocess.assert_called_once()
        assert "Migration rolled back successfully" in result.stdout
    finally:
        os.chdir(original_cwd)


def test_migrate_history_not_in_project(tmp_project):
    """Test migrate history fails when not in a FastAPI project."""
    original_cwd = os.getcwd()
    try:
        os.chdir("/tmp")
        result = runner.invoke(app, ["migrate", "history"])
        assert result.exit_code == 1
        assert "Not in a FastAPI project with Alembic" in result.stdout
    finally:
        os.chdir(original_cwd)


@patch("gondola.cli.migrate.subprocess.run")
def test_migrate_history_success(mock_subprocess, tmp_project):
    """Test successful migration history."""
    original_cwd = os.getcwd()
    mock_subprocess.return_value = MagicMock(returncode=0)
    try:
        os.chdir(tmp_project)
        result = runner.invoke(app, ["migrate", "history"])
        assert result.exit_code == 0
        mock_subprocess.assert_called_once()
    finally:
        os.chdir(original_cwd)


def test_migrate_current_not_in_project(tmp_project):
    """Test migrate current fails when not in a FastAPI project."""
    original_cwd = os.getcwd()
    try:
        os.chdir("/tmp")
        result = runner.invoke(app, ["migrate", "current"])
        assert result.exit_code == 1
        assert "Not in a FastAPI project with Alembic" in result.stdout
    finally:
        os.chdir(original_cwd)


@patch("gondola.cli.migrate.subprocess.run")
def test_migrate_current_success(mock_subprocess, tmp_project):
    """Test successful migration current."""
    original_cwd = os.getcwd()
    mock_subprocess.return_value = MagicMock(returncode=0)
    try:
        os.chdir(tmp_project)
        result = runner.invoke(app, ["migrate", "current"])
        assert result.exit_code == 0
        mock_subprocess.assert_called_once()
    finally:
        os.chdir(original_cwd)
