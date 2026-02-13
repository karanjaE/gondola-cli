from pathlib import Path
from typing import List
from .base import BaseGenerator

class ProjectGenerator(BaseGenerator):
    """Generator for creating a new FastAPI project"""

    def __init__(
        self,
        name: str,
        db_engine: str,
        include_docker: bool=True,
        extensions: List[str]=None,
    ):
        super().__init__("")
        self.name = name
        self.db_engine = db_engine
        self.include_docker = include_docker
        self.extensions = extensions or []
        self.project_path = Path.cwd() / name

    def generate(self)-> None:
        """Generate the complete project structure"""
        context = {
            "project_name": self.name,
            "db_engine": self.db_engine,
            "include_docker": self.include_docker,
            "extensions": self.extensions,
            "use_postgis": "postgis" in self.extensions,
            "use_pgvector": "pgvector" in self.extensions,
        }

        # Create directory structure
        self._create_directories()

        # Generate core files
        self._generate_core_files(context)

        # generate_app_files
        self._generate_app_files(context)

        # Generate configuration files
        self._generate_config_files(context)

        # Generate Docker files
        if self.include_docker:
            self._generate_docker_files(context)

        # Generate test files
        self._generate_test_files(context)

    def _create_directories(self)-> None:
        """Create the directory structure for the project"""

        dirs = [
            self.project_path/"app"/"models"/"serializers",
            self.project_path/"app"/"routers",
            self.project_path/"app"/"services",
            self.project_path/"app"/"lib",
            self.project_path/"core",
            self.project_path/"migrations",
            self.project_path/"logs",
            self.project_path/"test"/"unit",
            self.project_path/"test"/"integration",
            self.project_path/"test"/"fixtures",
        ]

        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            # create __init__.py files
            (dir_path/"__init__.py").touch()

    def _generate_core_files(self, context: dict)-> None:
        """Generate core files"""

        # config.py
        self.copy_template(
            "core/config.py.jinja",
            self.project_path/"core"/"config.py",
            context,
        )

        # database.py
        self.copy_template(
            "core/database.py.jinja",
            self.project_path/"core"/"database.py",
            context,
        )

        # __init__.py
        self.copy_template(
            "core/__init__.py.jinja",
            self.project_path/"core"/"__init__.py",
            context,
        )

    def _generate_app_files(self, context: dict)-> None:
        """Generate app files"""

        # main.py
        self.copy_template(
            "app/main.py.jinja",
            self.project_path/"main.py",
            context,
        )

        # models/base.py
        self.copy_template(
            "app/model/base.py.jinja",
            self.project_path/"app"/"models"/"base.py",
            context,
        )

        # routers/__init__.py with health check
        self.copy_template(
            "app/router/init.py.jinja",
            self.project_path/"app"/"routers"/"__init__.py",
            context,
        )

    def _generate_config_files(self, context: dict)-> None:
        """Generate config files"""

        # pyproject.toml
        self.copy_template(
            "config/pyproject.toml.jinja",
            self.project_path/"pyproject.toml",
            context,
        )

        # .env.example
        self.copy_template(
            "config/.env.example.jinja",
            self.project_path/".env.example",
            context,
        )

        # .gitignore
        self.copy_template(
            "config/.gitignore.jinja",
            self.project_path/".gitignore",
            context,
        )

        # alembic.ini
        self.copy_template(
            "config/alembic.ini.jinja",
            self.project_path/"alembic.ini",
            context,
        )

        # migrations/env.py
        self.copy_template(
            "migrations/env.py.jinja",
            self.project_path/"migrations"/"env.py",
            context,
        )

        # migrations/script.py.mako
        self.copy_template(
            "migrations/script.py.mako.jinja",
            self.project_path/"migrations"/"script.py.mako",
            context,
        )

        # README.md
        self.copy_template(
            "config/README.md.jinja",
            self.project_path/"README.md",
            context,
        )

    def _generate_docker_files(self, context: dict)-> None:
        """Generate Docker files"""

        # Dockerfile
        self.copy_template(
            "Dockerfile.jinja",
            self.project_path/"Dockerfile",
            context,
        )

        # docker-compose.yml
        self.copy_template(
            "docker-compose.yml.jinja",
            self.project_path/"docker-compose.yml",
            context,
        )

        # .dockerignore
        self.copy_template(
            "dockerignore.jinja",
            self.project_path/".dockerignore",
            context,
        )

    def _generate_test_files(self, context: dict)-> None:
        """Generate test files"""

        # test/init_test.py
        self.copy_template(
            "test/init_test.py.jinja",
            self.project_path/"test"/"init_test.py",
            context,
        )

        # test/conftest.py
        self.copy_template(
            "test/conftest.py.jinja",
            self.project_path/"test"/"conftest.py",
            context,
        )
