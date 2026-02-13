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


def test_migrate_create_not_in_project(tmp_project):
    """Test migrate create fails when not in a FastAPI project."""
    original_cwd = os.getcwd()
    try:
        os.chdir("/tmp")
        result = runner.invoke(app, ["migrate", "create", "test migration"])
        assert result.exit_code == 1
        assert "Not in a FastAPI project with Alembic" in result.stdout
    finally:
        os.chdir(original_cwd)


@patch("gondola.cli.migrate.subprocess.run")
def test_migrate_create_success(mock_subprocess, tmp_project):
    """Test successful migration creation."""
    original_cwd = os.getcwd()
    mock_subprocess.return_value = MagicMock(returncode=0)
    try:
        os.chdir(tmp_project)
        result = runner.invoke(app, ["migrate", "create", "test migration"])
        assert result.exit_code == 0
        mock_subprocess.assert_called_once()
        assert "Migration created: test migration" in result.stdout
    finally:
        os.chdir(original_cwd)


@patch("gondola.cli.migrate.subprocess.run")
def test_migrate_create_failure(mock_subprocess, tmp_project):
    """Test migration creation failure."""
    original_cwd = os.getcwd()
    from subprocess import CalledProcessError
    mock_subprocess.side_effect = CalledProcessError(1, "alembic")
    try:
        os.chdir(tmp_project)
        result = runner.invoke(app, ["migrate", "create", "test migration"])
        # Should handle the error gracefully
        assert result.exit_code == 1
    finally:
        os.chdir(original_cwd)


def test_migrate_upgrade_not_in_project(tmp_project):
    """Test migrate upgrade fails when not in a FastAPI project."""
    original_cwd = os.getcwd()
    try:
        os.chdir("/tmp")
        result = runner.invoke(app, ["migrate", "upgrade"])
        assert result.exit_code == 1
        assert "Not in a FastAPI project with Alembic" in result.stdout
    finally:
        os.chdir(original_cwd)


@patch("gondola.cli.migrate.subprocess.run")
def test_migrate_upgrade_success(mock_subprocess, tmp_project):
    """Test successful migration upgrade."""
    original_cwd = os.getcwd()
    mock_subprocess.return_value = MagicMock(returncode=0)
    try:
        os.chdir(tmp_project)
        result = runner.invoke(app, ["migrate", "upgrade", "head"])
        assert result.exit_code == 0
        mock_subprocess.assert_called_once()
        assert "Migrations applied successfully" in result.stdout
    finally:
        os.chdir(original_cwd)


def test_migrate_downgrade_not_in_project(tmp_project):
    """Test migrate downgrade fails when not in a FastAPI project."""
    original_cwd = os.getcwd()
    try:
        os.chdir("/tmp")
        result = runner.invoke(app, ["migrate", "downgrade"])
        assert result.exit_code == 1
        assert "Not in a FastAPI project with Alembic" in result.stdout
    finally:
        os.chdir(original_cwd)


@patch("gondola.cli.migrate.subprocess.run")
def test_migrate_downgrade_success(mock_subprocess, tmp_project):
    """Test successful migration downgrade."""
    original_cwd = os.getcwd()
    mock_subprocess.return_value = MagicMock(returncode=0)
    try:
        os.chdir(tmp_project)
        # Use "head" or a specific revision instead of "-1" which might be parsed as an option
        result = runner.invoke(app, ["migrate", "downgrade", "head"])
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
