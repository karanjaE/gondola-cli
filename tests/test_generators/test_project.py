"""Tests for ProjectGenerator."""
import os
import shutil
import tempfile
from pathlib import Path

import pytest

import gondola.generators.project as project_module
from gondola.generators.project import ProjectGenerator, _FALLBACK_VERSIONS


@pytest.fixture(autouse=True)
def _patched_versions(monkeypatch):
    """Avoid slow/flaky network calls to PyPI during project generation tests.

    Real version lookups happen in the CLI (`gondola init`); these tests only
    need deterministic generated output, so we substitute the bundled fallback
    version pins instead of hitting the network for every package.
    """
    monkeypatch.setattr(
        project_module,
        "_fetch_versions",
        lambda db_engine, extensions: dict(_FALLBACK_VERSIONS),
    )


class TestProjectGenerator:
    """Test ProjectGenerator functionality."""

    def test_init(self):
        generator = ProjectGenerator("test_project", "postgresql")
        assert generator.name == "test_project"
        assert generator.db_engine == "postgresql"
        assert generator.include_docker is True
        assert generator.extensions == []

    def test_init_with_options(self):
        generator = ProjectGenerator(
            "test_project",
            "sqlite",
            include_docker=False,
            extensions=["postgis", "pgvector"],
        )
        assert generator.name == "test_project"
        assert generator.db_engine == "sqlite"
        assert generator.include_docker is False
        assert generator.extensions == ["postgis", "pgvector"]

    def test_generate_creates_project_directory(self):
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

    def test_generate_postgres_directory_structure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                generator = ProjectGenerator("test_project", "postgresql")
                generator.generate()

                project_path = Path(tmpdir) / "test_project"
                assert (project_path / "api" / "models" / "schemas").exists()
                assert (project_path / "api" / "routers").exists()
                assert (project_path / "api" / "services").exists()
                assert (project_path / "core").exists()
                assert (project_path / "db" / "migrations" / "versions").exists()
                assert (project_path / "test" / "unit").exists()
                assert (project_path / "test" / "integration").exists()
                assert (project_path / "test" / "fixtures").exists()
            finally:
                os.chdir(original_cwd)

    def test_generate_sqlite_directory_structure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                generator = ProjectGenerator("test_project", "sqlite")
                generator.generate()

                project_path = Path(tmpdir) / "test_project"
                # SQLite projects share the same modern layout as other engines.
                assert (project_path / "api" / "models" / "schemas").exists()
                assert (project_path / "api" / "routers").exists()
                assert (project_path / "api" / "services").exists()
                assert (project_path / "core").exists()
                assert (project_path / "db" / "migrations" / "versions").exists()
                assert (project_path / "test" / "unit").exists()
                assert (project_path / "test" / "integration").exists()
                assert (project_path / "test" / "fixtures").exists()

                # The SQLite-specific dependency is recorded in pyproject.toml.
                text = (project_path / "pyproject.toml").read_text()
                assert "aiosqlite" in text
            finally:
                os.chdir(original_cwd)

    def test_generate_postgres_core_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                generator = ProjectGenerator("test_project", "postgresql")
                generator.generate()

                project_path = Path(tmpdir) / "test_project"
                assert (project_path / "core" / "config.py").exists()
                assert (project_path / "core" / "database.py").exists()
                assert (project_path / "core" / "logging.py").exists()
                assert (project_path / "core" / "__init__.py").exists()
            finally:
                os.chdir(original_cwd)

    def test_generate_postgres_app_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                generator = ProjectGenerator("test_project", "postgresql")
                generator.generate()

                project_path = Path(tmpdir) / "test_project"
                assert (project_path / "main.py").exists()
                assert (project_path / "api" / "models" / "base_model.py").exists()
                assert (project_path / "api" / "routers" / "__init__.py").exists()
            finally:
                os.chdir(original_cwd)

    def test_generate_creates_config_files(self):
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
                assert not (project_path / "poetry.lock").exists()
            finally:
                os.chdir(original_cwd)

    def test_generate_postgres_migration_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                generator = ProjectGenerator("test_project", "postgresql")
                generator.generate()

                project_path = Path(tmpdir) / "test_project"
                assert (project_path / "db" / "migrations" / "env.py").exists()
                assert (project_path / "db" / "migrations" / "script.py.mako").exists()
            finally:
                os.chdir(original_cwd)

    def test_generate_with_docker(self):
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
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                generator = ProjectGenerator("test_project", "postgresql", include_docker=False)
                generator.generate()

                project_path = Path(tmpdir) / "test_project"
                assert not (project_path / "Dockerfile").exists()
                assert not (project_path / "docker-compose.yml").exists()
            finally:
                os.chdir(original_cwd)

    def test_generate_creates_test_files(self):
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
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                generator = ProjectGenerator("test_project", "sqlite")
                generator.generate()

                # The SQLite driver is declared in pyproject.toml (config.py is
                # engine-agnostic and validates the URL at runtime).
                pyproject = Path(tmpdir) / "test_project" / "pyproject.toml"
                content = pyproject.read_text()
                assert "aiosqlite" in content
                assert "asyncpg" not in content
            finally:
                os.chdir(original_cwd)

    def test_generate_with_extensions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                generator = ProjectGenerator(
                    "test_project",
                    "postgresql",
                    extensions=["postgis", "pgvector"],
                )
                generator.generate()

                pyproject = Path(tmpdir) / "test_project" / "pyproject.toml"
                text = pyproject.read_text()
                assert "geoalchemy2" in text
                assert "pgvector" in text
            finally:
                os.chdir(original_cwd)

    @pytest.mark.skipif(not shutil.which("git"), reason="git not available")
    def test_generate_initializes_git_repository(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                generator = ProjectGenerator("git_project", "postgresql")
                generator.generate()

                project_path = Path(tmpdir) / "git_project"
                assert (project_path / ".git").exists()
            finally:
                os.chdir(original_cwd)
