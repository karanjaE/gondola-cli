"""Tests for delete CLI commands."""
import os
import pytest
import tempfile
from pathlib import Path
from typer.testing import CliRunner
from gondola.cli.main import app
from tests.test_cli.conftest import strip_ansi


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
            (Path(tmpdir) / "app" / "__init__.py").touch()
            (Path(tmpdir) / "app" / "models").mkdir(parents=True)
            (Path(tmpdir) / "app" / "models" / "__init__.py").touch()
            (Path(tmpdir) / "app" / "models" / "serializers").mkdir(parents=True)
            (Path(tmpdir) / "app" / "routers").mkdir(parents=True)
            (Path(tmpdir) / "test").mkdir()
            (Path(tmpdir) / "test" / "unit").mkdir(parents=True)
            (Path(tmpdir) / "test" / "unit" / "models").mkdir(parents=True)
            (Path(tmpdir) / "test" / "integration").mkdir(parents=True)
            (Path(tmpdir) / "test" / "integration" / "routers").mkdir(parents=True)

            yield tmpdir
        finally:
            os.chdir(original_cwd)


def test_delete_model_not_in_project(tmp_project):
    """Test delete model fails when not in a FastAPI project."""
    original_cwd = os.getcwd()
    try:
        os.chdir("/tmp")
        result = runner.invoke(app, ["delete", "model", "User", "--force"])
        assert result.exit_code == 1
        assert "Not in a FastAPI project directory" in result.stdout
    finally:
        os.chdir(original_cwd)


def test_delete_model_no_files(tmp_project):
    """Test delete model when no files exist."""
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_project)
        result = runner.invoke(app, ["delete", "model", "NonExistent", "--force"])
        assert result.exit_code == 0
        assert "No files found for model 'NonExistent'" in strip_ansi(result.stdout)
    finally:
        os.chdir(original_cwd)


def test_delete_model_with_files(tmp_project):
    """Test deleting a model with existing files."""
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_project)
        # Create model files
        model_file = Path(tmp_project) / "app" / "models" / "user.py"
        serializer_file = Path(tmp_project) / "app" / "models" / "serializers" / "user_serializer.py"
        test_file = Path(tmp_project) / "test" / "unit" / "models" / "test_user.py"

        model_file.write_text("# User model")
        serializer_file.write_text("# User serializer")
        test_file.write_text("# User tests")

        # Create __init__.py with import
        init_file = Path(tmp_project) / "app" / "models" / "__init__.py"
        init_file.write_text("from .user import User\n")

        result = runner.invoke(app, ["delete", "model", "User", "--force"])
        assert result.exit_code == 0
        assert "Model 'User' deleted successfully" in strip_ansi(result.stdout)

        # Check files were deleted
        assert not model_file.exists()
        assert not serializer_file.exists()
        assert not test_file.exists()

        # Check import was removed
        assert "from .user import User" not in init_file.read_text()
    finally:
        os.chdir(original_cwd)


def test_delete_model_with_dependencies(tmp_project):
    """Test delete model fails when model has dependencies."""
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_project)
        # Create model files
        user_file = Path(tmp_project) / "app" / "models" / "user.py"
        user_file.write_text("# User model")
        
        # Create another model that references User
        post_file = Path(tmp_project) / "app" / "models" / "post.py"
        post_file.write_text('Relationship("User"')
        
        result = runner.invoke(app, ["delete", "model", "User", "--force"])
        assert result.exit_code == 1
        assert "This model is referenced by" in result.stdout
        assert user_file.exists()  # File should not be deleted
    finally:
        os.chdir(original_cwd)


def test_delete_router_not_in_project(tmp_project):
    """Test delete router fails when not in a FastAPI project."""
    original_cwd = os.getcwd()
    try:
        os.chdir("/tmp")
        result = runner.invoke(app, ["delete", "router", "User", "--force"])
        assert result.exit_code == 1
        assert "Not in a FastAPI project directory" in result.stdout
    finally:
        os.chdir(original_cwd)


def test_delete_router_no_files(tmp_project):
    """Test delete router when no files exist."""
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_project)
        result = runner.invoke(app, ["delete", "router", "NonExistent", "--force"])
        assert result.exit_code == 0
        assert "No files found for router 'NonExistent'" in strip_ansi(result.stdout)
    finally:
        os.chdir(original_cwd)


def test_delete_router_with_files(tmp_project):
    """Test deleting a router with existing files."""
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_project)
        # Create router files
        router_file = Path(tmp_project) / "app" / "routers" / "user.py"
        test_file = Path(tmp_project) / "test" / "integration" / "routers" / "test_user_routes.py"

        router_file.write_text("# User router")
        test_file.write_text("# User router tests")

        result = runner.invoke(app, ["delete", "router", "User", "--force"])
        assert result.exit_code == 0
        assert "Router 'User' deleted successfully" in strip_ansi(result.stdout)

        # Check files were deleted
        assert not router_file.exists()
        assert not test_file.exists()
    finally:
        os.chdir(original_cwd)
