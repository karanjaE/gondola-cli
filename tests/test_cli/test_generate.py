"""Tests for generate CLI commands."""
import os
import pytest
from pathlib import Path
from typer.testing import CliRunner
from gondola.cli.main import app
from tests.test_cli.conftest import strip_ansi


runner = CliRunner()


@pytest.fixture
def tmp_project():
    """Create a temporary FastAPI project for testing."""
    import tempfile
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
            (Path(tmpdir) / "app" / "services").mkdir(parents=True)
            (Path(tmpdir) / "app" / "lib").mkdir(parents=True)
            (Path(tmpdir) / "test").mkdir()
            (Path(tmpdir) / "test" / "unit").mkdir(parents=True)
            (Path(tmpdir) / "test" / "integration").mkdir(parents=True)
            
            yield tmpdir
        finally:
            os.chdir(original_cwd)


def test_generate_model_not_in_project(tmp_project):
    """Test generate model fails when not in a FastAPI project."""
    original_cwd = os.getcwd()
    try:
        os.chdir("/tmp")
        result = runner.invoke(app, ["generate", "model", "User"])
        assert result.exit_code == 1
        assert "Not in a FastAPI project directory" in result.stdout
    finally:
        os.chdir(original_cwd)


def test_generate_model(tmp_project):
    """Test generating a model."""
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_project)
        result = runner.invoke(
            app,
            ["generate", "model", "User", "--fields", "name:str,email:str"]
        )
        assert result.exit_code == 0
        assert "Model 'User' generated successfully" in strip_ansi(result.stdout)
        
        # Check files were created
        assert (Path(tmp_project) / "app" / "models" / "user.py").exists()
        assert (Path(tmp_project) / "app" / "models" / "serializers" / "user_serializer.py").exists()
        assert (Path(tmp_project) / "test" / "unit" / "test_user.py").exists()
    finally:
        os.chdir(original_cwd)


def test_generate_model_no_fields(tmp_project):
    """Test generating a model without fields."""
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_project)
        result = runner.invoke(app, ["generate", "model", "Product"])
        assert result.exit_code == 0
        assert "Model 'Product' generated successfully" in strip_ansi(result.stdout)
        assert (Path(tmp_project) / "app" / "models" / "product.py").exists()
    finally:
        os.chdir(original_cwd)


def test_generate_router_not_in_project(tmp_project):
    """Test generate router fails when not in a FastAPI project."""
    original_cwd = os.getcwd()
    try:
        os.chdir("/tmp")
        result = runner.invoke(app, ["generate", "router", "User"])
        assert result.exit_code == 1
        assert "Not in a FastAPI project directory" in result.stdout
    finally:
        os.chdir(original_cwd)


def test_generate_router(tmp_project):
    """Test generating a router."""
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_project)
        result = runner.invoke(app, ["generate", "router", "User"])
        assert result.exit_code == 0
        assert "Router 'User' generated successfully" in strip_ansi(result.stdout)
        assert (Path(tmp_project) / "app" / "routers" / "user.py").exists()
        assert (Path(tmp_project) / "test" / "integration" / "test_user_routes.py").exists()
    finally:
        os.chdir(original_cwd)


def test_generate_router_with_model(tmp_project):
    """Test generating a router with associated model."""
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_project)
        result = runner.invoke(
            app,
            ["generate", "router", "BlogPost", "--model", "BlogPost"]
        )
        assert result.exit_code == 0
        assert "Router 'BlogPost' generated successfully" in strip_ansi(result.stdout)
    finally:
        os.chdir(original_cwd)


def test_generate_service_not_in_project(tmp_project):
    """Test generate service fails when not in a FastAPI project."""
    original_cwd = os.getcwd()
    try:
        os.chdir("/tmp")
        result = runner.invoke(app, ["generate", "service", "EmailService"])
        assert result.exit_code == 1
        assert "Not in a FastAPI project directory" in result.stdout
    finally:
        os.chdir(original_cwd)


def test_generate_service(tmp_project):
    """Test generating a service."""
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_project)
        result = runner.invoke(app, ["generate", "service", "EmailService"])
        assert result.exit_code == 0
        assert "Service 'EmailService' generated successfully" in strip_ansi(result.stdout)
        assert (Path(tmp_project) / "app" / "services" / "email_service.py").exists()
        assert (Path(tmp_project) / "test" / "unit" / "test_email_service.py").exists()
    finally:
        os.chdir(original_cwd)


def test_generate_mailer_not_in_project(tmp_project):
    """Test generate mailer fails when not in a FastAPI project."""
    original_cwd = os.getcwd()
    try:
        os.chdir("/tmp")
        result = runner.invoke(app, ["generate", "mailer", "Welcome"])
        assert result.exit_code == 1
        assert "Not in a FastAPI project directory" in result.stdout
    finally:
        os.chdir(original_cwd)


def test_generate_mailer(tmp_project):
    """Test generating a mailer."""
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_project)
        # Create mailers directory
        (Path(tmp_project) / "app" / "lib" / "mailers").mkdir(parents=True)
        
        result = runner.invoke(app, ["generate", "mailer", "Welcome"])
        assert result.exit_code == 0
        assert "Mailer 'Welcome' generated successfully" in strip_ansi(result.stdout)
        assert (Path(tmp_project) / "app" / "lib" / "mailers" / "welcome.py").exists()
        assert (Path(tmp_project) / "test" / "unit" / "test_welcome.py").exists()
    finally:
        os.chdir(original_cwd)
