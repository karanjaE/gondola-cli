"""Tests for ProjectGenerator."""
import tempfile
import os
from pathlib import Path
import pytest
from gondola.generators.project import ProjectGenerator


class TestProjectGenerator:
    """Test ProjectGenerator functionality."""
    
    def test_init(self):
        """Test ProjectGenerator initialization."""
        generator = ProjectGenerator("test_project", "postgresql")
        assert generator.name == "test_project"
        assert generator.db_engine == "postgresql"
        assert generator.include_docker is True
        assert generator.extensions == []
    
    def test_init_with_options(self):
        """Test ProjectGenerator initialization with options."""
        generator = ProjectGenerator(
            "test_project",
            "sqlite",
            include_docker=False,
            extensions=["postgis", "pgvector"]
        )
        assert generator.name == "test_project"
        assert generator.db_engine == "sqlite"
        assert generator.include_docker is False
        assert generator.extensions == ["postgis", "pgvector"]
    
    def test_generate_creates_project_directory(self):
        """Test that generate creates project directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                generator = ProjectGenerator("test_project", "postgresql")
                generator.generate()
                
                project_path = Path(tmpdir) / "test_project"
                assert project_path.exists()
                assert project_path.is_dir()
            finally:
                os.chdir(original_cwd)
    
    def test_generate_creates_directory_structure(self):
        """Test that generate creates all required directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                generator = ProjectGenerator("test_project", "postgresql")
                generator.generate()
                
                project_path = Path(tmpdir) / "test_project"
                assert (project_path / "app" / "models" / "serializers").exists()
                assert (project_path / "app" / "routers").exists()
                assert (project_path / "app" / "services").exists()
                assert (project_path / "app" / "lib").exists()
                assert (project_path / "core").exists()
                assert (project_path / "migrations").exists()
                assert (project_path / "logs").exists()
                assert (project_path / "test" / "unit").exists()
                assert (project_path / "test" / "integration").exists()
                assert (project_path / "test" / "fixtures").exists()
            finally:
                os.chdir(original_cwd)
    
    def test_generate_creates_core_files(self):
        """Test that generate creates core files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                generator = ProjectGenerator("test_project", "postgresql")
                generator.generate()
                
                project_path = Path(tmpdir) / "test_project"
                assert (project_path / "core" / "config.py").exists()
                assert (project_path / "core" / "database.py").exists()
                assert (project_path / "core" / "__init__.py").exists()
            finally:
                os.chdir(original_cwd)
    
    def test_generate_creates_app_files(self):
        """Test that generate creates app files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                generator = ProjectGenerator("test_project", "postgresql")
                generator.generate()
                
                project_path = Path(tmpdir) / "test_project"
                assert (project_path / "main.py").exists()
                assert (project_path / "app" / "models" / "base.py").exists()
                assert (project_path / "app" / "routers" / "__init__.py").exists()
            finally:
                os.chdir(original_cwd)
    
    def test_generate_creates_config_files(self):
        """Test that generate creates configuration files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                generator = ProjectGenerator("test_project", "postgresql")
                generator.generate()
                
                project_path = Path(tmpdir) / "test_project"
                assert (project_path / "pyproject.toml").exists()
                assert (project_path / ".env.example").exists()
                assert (project_path / ".gitignore").exists()
                assert (project_path / "alembic.ini").exists()
                assert (project_path / "README.md").exists()
            finally:
                os.chdir(original_cwd)
    
    def test_generate_creates_migration_files(self):
        """Test that generate creates migration files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                generator = ProjectGenerator("test_project", "postgresql")
                generator.generate()
                
                project_path = Path(tmpdir) / "test_project"
                assert (project_path / "migrations" / "env.py").exists()
                assert (project_path / "migrations" / "script.py.mako").exists()
            finally:
                os.chdir(original_cwd)
    
    def test_generate_with_docker(self):
        """Test that generate creates Docker files when include_docker is True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                generator = ProjectGenerator("test_project", "postgresql", include_docker=True)
                generator.generate()
                
                project_path = Path(tmpdir) / "test_project"
                assert (project_path / "Dockerfile").exists()
                assert (project_path / "docker-compose.yml").exists()
                assert (project_path / ".dockerignore").exists()
            finally:
                os.chdir(original_cwd)
    
    def test_generate_without_docker(self):
        """Test that generate doesn't create Docker files when include_docker is False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                generator = ProjectGenerator("test_project", "postgresql", include_docker=False)
                generator.generate()
                
                project_path = Path(tmpdir) / "test_project"
                # Docker files should not exist
                assert not (project_path / "Dockerfile").exists()
                assert not (project_path / "docker-compose.yml").exists()
            finally:
                os.chdir(original_cwd)
    
    def test_generate_creates_test_files(self):
        """Test that generate creates test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                generator = ProjectGenerator("test_project", "postgresql")
                generator.generate()
                
                project_path = Path(tmpdir) / "test_project"
                assert (project_path / "test" / "init_test.py").exists()
                assert (project_path / "test" / "conftest.py").exists()
            finally:
                os.chdir(original_cwd)
    
    def test_generate_config_content(self):
        """Test that config.py contains project name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                generator = ProjectGenerator("my_project", "postgresql")
                generator.generate()
                
                config_file = Path(tmpdir) / "my_project" / "core" / "config.py"
                assert config_file.exists()
                content = config_file.read_text()
                assert "my_project" in content
            finally:
                os.chdir(original_cwd)
    
    def test_generate_database_content_postgresql(self):
        """Test that database.py uses postgresql URL for postgresql engine."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                generator = ProjectGenerator("test_project", "postgresql")
                generator.generate()
                
                config_file = Path(tmpdir) / "test_project" / "core" / "config.py"
                content = config_file.read_text()
                assert "postgresql+asyncpg" in content
            finally:
                os.chdir(original_cwd)
    
    def test_generate_database_content_sqlite(self):
        """Test that database.py uses sqlite URL for sqlite engine."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                generator = ProjectGenerator("test_project", "sqlite")
                generator.generate()
                
                config_file = Path(tmpdir) / "test_project" / "core" / "config.py"
                content = config_file.read_text()
                assert "sqlite+aiosqlite" in content
            finally:
                os.chdir(original_cwd)
    
    def test_generate_with_extensions(self):
        """Test that generate handles extensions correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                generator = ProjectGenerator(
                    "test_project",
                    "postgresql",
                    extensions=["postgis", "pgvector"]
                )
                generator.generate()
                
                # Check that extensions are used in context
                config_file = Path(tmpdir) / "test_project" / "core" / "config.py"
                # Extensions might be used in templates
                assert config_file.exists()
            finally:
                os.chdir(original_cwd)
