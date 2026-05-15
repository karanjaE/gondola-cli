# Gondola

A CLI tool for FastAPI projects that brings convention over configuration to the Python async web ecosystem.

---

## Introduction

Gondola is a command-line tool designed to streamline FastAPI development by providing scaffolding, generators, and conventions. Focus on building features, not boilerplate.

### Philosophy

**Convention Over Configuration**: Gondola establishes sensible defaults and project structures so you can start building immediately. Opinionated where it matters, flexible where you need it.

**Developer Happiness**: Reduce cognitive load with intuitive commands, clear project organization, and automatic test generation. If you've used Rails, you'll feel right at home.

**Modern Async-First**: Built for Python 3.12+ with async/await patterns. The default PostgreSQL stack uses SQLModel, **asyncpg**, and Alembic.

**Production Ready**: Optional Docker Compose (API, Postgres, Redis), pytest layout, and migrations from day one.

### Features

- **Project Scaffolding**: Create production-ready FastAPI projects in seconds
- **Code Generators**: Auto-generate models, routers, services, mailers, and tests
- **Database Management**: Built-in migration commands powered by Alembic
- **Testing First**: Every generated component includes comprehensive tests
- **Docker Ready**: Optional Docker and docker-compose configuration
- **Multiple Database Support**: PostgreSQL (with PostGIS/pgvector), SQLite
- **Email Support**: Built-in mailer generator with templates
- **Type Safe**: Full mypy support with Pydantic models
- **Migration Rollback**: Reversible database migrations
- **Rich CLI**: Beautiful terminal output with progress indicators

---

## Installation

### Requirements

- **Python**: 3.12 or higher (for the `gondola-cli` tool and generated PostgreSQL projects)
- **Poetry**: 1.5+ (recommended) or pip
- **Docker**: Optional, for containerized development

### Installation Guide

#### Install via pip

```bash
pip install gondola-cli
```

#### Install via pipx (recommended for CLI tools)

```bash
pipx install gondola-cli
```

#### Install from source

```bash
git clone https://github.com/karanjaE/gondola-cli.git
cd gondola-cli
poetry install
```

#### Verify installation

```bash
gondola --help
```

You should see the Gondola CLI help menu with available commands.

---

## Usage

### Start a New Project

Create a new FastAPI project with PostgreSQL and Docker (defaults):

```bash
gondola create project my-api
# same as:
gondola create project my-api --db=postgresql --docker
```

Skip Docker files:

```bash
gondola create project my-api --no-docker
```

Create a minimal project with SQLite (legacy layout):

```bash
gondola create project my-api --db=sqlite
```

Optional Postgres extensions when using `--db=postgresql`:

```bash
gondola create project my-api --extensions postgis,pgvector
```

#### What gets created?

**PostgreSQL (default: `--db=postgresql`)** — async SQLModel + asyncpg, neutral naming in config and Docker metadata:

```
my-api/
├── api/
│   ├── models/              # SQLModel tables (e.g. base_model.py)
│   ├── models/schemas/      # Pydantic schemas (per resource)
│   ├── routers/             # Routers auto-included from *.py (export `router`)
│   ├── services/
│   └── dependencies/
├── core/                    # Settings (get_settings), database, logging
├── db/
│   └── migrations/          # Alembic (script_location in alembic.ini)
├── test/
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── alembic/              # Database migrations
├── docker-compose.yml    # Container orchestration
├── Dockerfile            # App container
└── pyproject.toml        # Dependencies
```

A **fresh Git repository** is initialized in the project folder (`git init`).

**SQLite / MySQL (`--db=sqlite` or `--db=mysql`)** — Use the exact same directory structure and generators as PostgreSQL, but configure `alembic.ini`, `core/database.py`, and `pyproject.toml` with the appropriate async drivers (aiosqlite or asyncmy).

#### Next steps

```bash
cd my-api
poetry install
# Configure your .env file
gondola migrate upgrade
gondola run server
```

Your API is now running at `http://localhost:8000` with interactive docs at `/docs`.

**API version header (PostgreSQL projects):** clients may send `API-Version: v1`. If the header is missing, the app uses the default from settings (`api_default_version`, usually `v1`). Versioning is header-based, not via URL prefixes.

---

### Generators

Run these from the **root of a generated project** (where `main.py` lives).

#### Generate a model

```bash
gondola generate model User name:str email:str age:int is_active:bool
```

**Creates:**

- `api/models/user.py` - SQLModel table definition
- `api/models/schemas/user.py` - Pydantic schemas (Create, Update, Response)
- `test/unit/models/test_user.py` - Unit tests

**Run migration:**

```bash
gondola migrate create "Create User model"
gondola migrate upgrade
```

#### Generate a Router

Create RESTful API endpoints:

```bash
gondola generate router users --model=User
```

**Creates:**

- `api/routers/users.py` - CRUD endpoints (list, create, get, update, delete)
- `test/integration/routers/test_users_routes.py` - Integration tests

**Register the router** in `main.py`:

```python
from api.routers import users
app.include_router(users.router)
```

#### Generate a Service

Create a service class for business logic:

```bash
gondola generate service UserNotification
```

**Creates:**

- `api/services/user_notification.py` - Service class with Celery task decorator
- `test/unit/services/test_user_notification.py` - Unit tests

#### Generate a Mailer

Create an email mailer with templates:

```bash
gondola generate mailer Welcome
```

Creates **`api/mailers/welcome.py`** (and `__init__.py` if needed) plus `test/unit/mailers/test_welcome.py`.

---

### Migration Commands

Gondola wraps Alembic for easy database migration management.

#### Create a migration

```bash
gondola migrate create "Add user preferences table"
```

#### Apply migrations

```bash
# Upgrade to latest
gondola migrate upgrade

# Upgrade to specific revision
gondola migrate upgrade abc123
```

#### Rollback migrations

```bash
# Downgrade one revision
gondola migrate downgrade -1

# Downgrade to specific revision
gondola migrate downgrade abc123
```

#### View migration history

```bash
gondola migrate history
```

#### Check current revision

```bash
gondola migrate current
```

---

### Delete commands

Remove generated code safely with automatic cleanup.

#### Delete a model

```bash
gondola delete model User
```

Gondola will:

- List related files
- Try to point out a related migration revision (under `db/migrations/versions`)
- Prompt for confirmation unless `--force`

Deleting a model removes `api/models/<name>.py` and `api/models/schemas/<name>.py`.

⚠️ **Migrations**: you still need to roll back or edit Alembic revisions yourself when appropriate:

```bash
gondola migrate downgrade -1
```

#### Delete a router

```bash
gondola delete router users
```

Removes `api/routers/users.py` and the matching integration test stub.

---

### Server commands

Start the development ASGI server (wraps **uvicorn**):

```bash
# Default: reload on, host 0.0.0.0, port 8000
gondola run server

gondola run server --port=3000 --host=127.0.0.1
gondola run server --workers=4 --no-reload
```

Celery helpers are **not** part of the CLI anymore; add background workers in your own codebase if you need them.

---

## Development and contributing

We welcome contributions. The CLI renders Jinja templates from:

- **`gondola/templates/default/`** — output for `gondola create project`

**`examples/example_app/`** in this repository is a non-packaged reference layout aligned with the PostgreSQL template; update the Jinja trees when you change the example app.

### Setup development environment

```bash
git clone https://github.com/karanjaE/gondola-cli.git
cd gondola-cli
poetry install
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=gondola --cov-report=html

# Run specific test file
poetry run pytest tests/test_generators/test_model.py

# Run with verbose output
poetry run pytest -v
```

### Code Quality

```bash
# Type checking with mypy
poetry run mypy gondola

# Linting with ruff
poetry run ruff check gondola

# Format code
poetry run ruff format gondola
```

### Contributing Guidelines

1. **Fork the repository** and create a feature branch
2. **Write tests** for new functionality
3. **Ensure all tests pass** and maintain coverage above 80%
4. **Follow code style** - run mypy and ruff before committing
5. **Write clear commit messages** following conventional commits
6. **Submit a pull request** with a description of changes

### Development Workflow

```bash
# Create a feature branch
git checkout -b feature/amazing-feature

# Make your changes and write tests
# ...

# Run quality checks
poetry run pytest
poetry run mypy gondola
poetry run ruff check gondola

# Commit your changes
git commit -m "feat: add amazing feature"

# Push to your fork
git push origin feature/amazing-feature

# Open a pull request on GitHub
```

---

## Reporting Bugs

Found a bug? We'd love to hear about it!

### Before Reporting

1. **Search existing issues** to avoid duplicates
2. **Update to the latest version** - the bug may be fixed
3. **Prepare a minimal reproduction** if possible

### Creating an Issue

Open an issue on [GitHub Issues](https://github.com/karanjaE/gondola-cli/issues) with:

- **Clear title** describing the problem
- **Gondola / package**: `pip show gondola-cli` (or your install tool’s equivalent)
- **Python version**: Run `python --version`
- **Operating system**: e.g., macOS 14.2, Ubuntu 22.04
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Error messages** or stack traces
- **Code samples** or minimal reproduction

### Security vulnerabilities

Please use **GitHub private vulnerability reporting** for this repository (or contact the maintainers through a channel they publish on the repo) instead of filing public issues for undisclosed security problems.

---

## License

Gondola is licensed under the **MIT License**.

See [LICENSE](LICENSE) file for full text.

---

## Code of Conduct

### Our Pledge

Just be nice.

### Our Standards

**Positive behavior includes:**

- Using welcoming and inclusive language
- Respecting differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what's best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**

- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate

### Enforcement

Project maintainers are responsible for clarifying standards and will take appropriate and fair corrective action in response to unacceptable behavior.

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported to the maintainers via **GitHub Issues** or **Discussions** on this repository.

### Attribution

This Code of Conduct is adapted from the [Contributor Covenant](https://www.contributor-covenant.org), version 2.1.

---

## Acknowledgments

Gondola is inspired by:

- **FastAPI** - For bringing async Python to the mainstream
- **Django** - For showing the power of conventions

Special thanks to all our [contributors](https://github.com/karanjaE/gondola-cli/graphs/contributors)!

---

## Links

- **PyPI**: [https://pypi.org/project/gondola-cli/](https://pypi.org/project/gondola-cli/)
- **GitHub**: [https://github.com/karanjaE/gondola-cli](https://github.com/karanjaE/gondola-cli)
- **Discussions**: [https://github.com/karanjaE/gondola-cli/discussions](https://github.com/karanjaE/gondola-cli/discussions)

---

**Happy building**
