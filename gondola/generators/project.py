import re
import subprocess
import urllib.request
import urllib.error
import json
from pathlib import Path
from typing import List

from .base import BaseGenerator


def _project_slug(name: str) -> str:
    """Sanitized identifier for DB names, image tags, and Poetry package name."""
    s = name.lower().replace("-", "_")
    s = re.sub(r"[^a-z0-9_]", "_", s)
    s = s.strip("_")
    return s or "app"


# Fallback pinned versions — used when PyPI is unreachable
_FALLBACK_VERSIONS: dict[str, str] = {
    "fastapi":          "0.136.1",
    "uvicorn":          "0.46.0",
    "sqlmodel":         "0.0.38",
    "alembic":          "1.18.4",
    "pydantic":         "2.13.3",
    "pydantic-settings": "2.14.1",
    "asyncpg":          "0.31.0",
    "psycopg2-binary":  "2.9.12",
    "asyncmy":          "0.2.9",
    "cryptography":     "42.0.0",
    "aiosqlite":        "0.20.0",
    "greenlet":         "3.5.0",
    "geoalchemy2":      "0.19.0",
    "pgvector":         "0.3.6",
    "pytest":           "9.0.2",
    "pytest-asyncio":   "1.3.0",
    "pytest-cov":       "7.0.0",
    "httpx":            "0.28.1",
    "mypy":             "1.19.1",
    "ruff":             "0.15.0",
}


def _latest_version(package: str) -> str:
    """Return the latest stable version from PyPI, or the fallback pin."""
    try:
        url = f"https://pypi.org/pypi/{package}/json"
        with urllib.request.urlopen(url, timeout=5) as resp:  # noqa: S310
            data = json.loads(resp.read())
        return data["info"]["version"]
    except Exception:
        return _FALLBACK_VERSIONS.get(package, "*")


def _fetch_versions(db_engine: str, extensions: list[str]) -> dict[str, str]:
    """Fetch latest versions for all packages used in the generated project."""
    packages = [
        "fastapi", "uvicorn", "sqlmodel", "alembic",
        "pydantic", "pydantic-settings", "greenlet",
        "pytest", "pytest-asyncio", "pytest-cov", "httpx", "mypy", "ruff",
    ]

    if db_engine == "postgresql":
        packages += ["asyncpg", "psycopg2-binary"]
    elif db_engine == "mysql":
        packages += ["asyncmy", "cryptography"]
    else:
        packages += ["aiosqlite"]

    if "postgis" in extensions:
        packages.append("geoalchemy2")
    if "pgvector" in extensions:
        packages.append("pgvector")

    return {pkg: _latest_version(pkg) for pkg in packages}


class ProjectGenerator(BaseGenerator):
    """Generator for creating a new FastAPI project."""

    def __init__(
        self,
        name: str,
        db_engine: str,
        include_docker: bool = True,
        extensions: List[str] | None = None,
        versions: dict[str, str] | None = None,
    ):
        super().__init__("")
        self.name = name
        self.db_engine = db_engine
        self.include_docker = include_docker
        self.extensions = extensions or []
        self.versions = versions  # None means "fetch at generate() time"
        self.project_path = Path.cwd() / name
        self._tpl_prefix = "default"

    def _tpl(self, relative: str) -> str:
        return f"{self._tpl_prefix}/{relative}"

    def generate(self) -> None:
        versions = self.versions or _fetch_versions(self.db_engine, self.extensions)

        context = {
            "project_name": self.name,
            "project_slug": _project_slug(self.name),
            "db_engine": self.db_engine,
            "include_docker": self.include_docker,
            "extensions": self.extensions,
            "use_postgis": "postgis" in self.extensions,
            "use_pgvector": "pgvector" in self.extensions,
            "versions": versions,
        }

        self._create_directories()
        self._generate_files(context)

        # Automatically create .env from .env.example
        env_example = self.project_path / ".env.example"
        if env_example.exists():
            (self.project_path / ".env").write_text(env_example.read_text())

        self._init_git_repository()

    def _init_git_repository(self) -> None:
        try:
            subprocess.run(
                ["git", "init"],
                cwd=self.project_path,
                check=True,
                capture_output=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Git missing or init failed — project files are still usable.
            pass

    def _create_directories(self) -> None:
        dirs = [
            self.project_path / "api" / "models" / "schemas",
            self.project_path / "api" / "routers",
            self.project_path / "api" / "services",
            self.project_path / "api" / "dependencies",
            self.project_path / "api" / "mailers",
            self.project_path / "core",
            self.project_path / "db" / "migrations" / "versions",
            self.project_path / "db" / "seeds",
            self.project_path / "test" / "unit" / "models",
            self.project_path / "test" / "unit" / "services",
            self.project_path / "test" / "unit" / "mailers",
            self.project_path / "test" / "integration" / "routers",
            self.project_path / "test" / "fixtures",
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            init_file = dir_path / "__init__.py"
            if not init_file.exists():
                init_file.write_text("")

    def _generate_files(self, context: dict) -> None:
        pairs = [
            ("main.py.jinja", self.project_path / "main.py"),
            ("core/config.py.jinja", self.project_path / "core" / "config.py"),
            ("core/database.py.jinja", self.project_path / "core" / "database.py"),
            ("core/logging.py.jinja", self.project_path / "core" / "logging.py"),
            ("core/__init__.py.jinja", self.project_path / "core" / "__init__.py"),
            ("api/__init__.py.jinja", self.project_path / "api" / "__init__.py"),
            ("api/models/__init__.py.jinja", self.project_path / "api" / "models" / "__init__.py"),
            ("api/models/schemas/__init__.py.jinja", self.project_path / "api" / "models" / "schemas" / "__init__.py"),
            ("api/models/base_model.py.jinja", self.project_path / "api" / "models" / "base_model.py"),
            ("api/routers/__init__.py.jinja", self.project_path / "api" / "routers" / "__init__.py"),
            ("api/routers/healthchecks.py.jinja", self.project_path / "api" / "routers" / "healthchecks.py"),
            ("api/dependencies/__init__.py.jinja", self.project_path / "api" / "dependencies" / "__init__.py"),
            ("api/services/__init__.py.jinja", self.project_path / "api" / "services" / "__init__.py"),
            ("db/__init__.py.jinja", self.project_path / "db" / "__init__.py"),
            ("db/seeds/__init__.py.jinja", self.project_path / "db" / "seeds" / "__init__.py"),
            ("db/seeds/base_seed.py.jinja", self.project_path / "db" / "seeds" / "base_seed.py"),
            ("db/seeds/example_seed.py.jinja", self.project_path / "db" / "seeds" / "example_seed.py"),
            ("db/migrations/env.py.jinja", self.project_path / "db" / "migrations" / "env.py"),
            ("db/migrations/script.py.mako.jinja", self.project_path / "db" / "migrations" / "script.py.mako"),
            ("db/migrations/README.jinja", self.project_path / "db" / "migrations" / "README"),
            ("config/pyproject.toml.jinja", self.project_path / "pyproject.toml"),
            ("config/.env.example.jinja", self.project_path / ".env.example"),
            ("config/.gitignore.jinja", self.project_path / ".gitignore"),
            ("config/alembic.ini.jinja", self.project_path / "alembic.ini"),
            ("config/README.md.jinja", self.project_path / "README.md"),
            ("test/conftest.py.jinja", self.project_path / "test" / "conftest.py"),
            ("test/init_test.py.jinja", self.project_path / "test" / "init_test.py"),
        ]
        for rel, dest in pairs:
            self.copy_template(self._tpl(rel), dest, context)

        if self.include_docker:
            self.copy_template(self._tpl("Dockerfile.jinja"), self.project_path / "Dockerfile", context)
            self.copy_template(self._tpl("docker-compose.yml.jinja"), self.project_path / "docker-compose.yml", context)
            self.copy_template(self._tpl("dockerignore.jinja"), self.project_path / ".dockerignore", context)
