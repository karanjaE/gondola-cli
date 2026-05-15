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
- **Multiple Database Support**: PostgreSQL (with PostGIS/pgvector), MySQL, MariaDB, SQLite
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

`gondola init` (alias: `gondola i`) launches an **interactive wizard** to scaffold a new FastAPI project.

```bash
gondola init
# or with alias
gondola i
```

You can also pass a name directly to pre-fill the first prompt:

```bash
gondola init my-api
gondola i my-api
```

#### Interactive session example

```
╭─────────────────────────────────────────────╮
│  gondola init — FastAPI project scaffolding  │
╰─────────────────────────────────────────────╯

  Project name [my-fastapi-project]: my-api

  Database engine
  > 1. PostgreSQL  (asyncpg + SQLModel — recommended)
    2. MySQL       (asyncmy + SQLModel)
    3. MariaDB     (asyncmy + SQLModel)
    4. SQLite      (aiosqlite + SQLModel)
  Enter number [1]:

  Include Docker setup? [Y/n]: Y

  Include PostgreSQL extensions? (postgis, pgvector) [y/N]: y

  Select extensions
    1. postgis
    2. pgvector
  Enter numbers separated by commas (e.g. 1,2), or press Enter to skip
  Selection: 2

╭─ Project configuration ─╮
│  Project     my-api      │
│  Database    postgres    │
│  Docker      Yes         │
│  Extensions  pgvector    │
╰─────────────────────────╯

  Create project? [Y/n]: Y
```

#### Prompts and defaults

| Prompt | Default |
|--------|---------|
| Project name | `my-fastapi-project` |
| Database engine | `postgres` |
| Include Docker? | `Yes` |
| Include extensions? | `No` |
| Extensions | *(none)* |

> **Note**: Project names are automatically normalized to `lowercase-with-hyphens`. Extensions (`postgis`, `pgvector`) are only applicable when using PostgreSQL.

#### Non-interactive (scripted) usage

All prompts can be bypassed by passing flags directly:

```bash
gondola init my-api --db postgres --docker --extensions pgvector
gondola init my-api --db sqlite --no-docker
gondola init my-api --db mysql
```

#### What gets created?

```
my-api/
├── api/
│   ├── models/              # SQLModel tables
│   ├── models/schemas/      # Pydantic schemas (per resource)
│   ├── routers/             # Routers auto-included from *.py (export `router`)
│   ├── services/
│   ├── mailers/
│   └── dependencies/
├── core/                    # Settings (get_settings), database, logging
├── db/
│   └── migrations/          # Alembic (script_location in alembic.ini)
├── test/
│   ├── unit/
│   │   ├── models/          # Model unit tests
│   │   ├── services/        # Service unit tests
│   │   └── mailers/         # Mailer unit tests
│   └── integration/
│       └── routers/         # Router integration tests
├── alembic.ini
├── docker-compose.yml       # Container orchestration (if --docker)
├── Dockerfile               # App container (if --docker)
└── pyproject.toml           # Dependencies
```

A **fresh Git repository** is initialized in the project folder (`git init`).

#### Next steps

```bash
cd my-api
poetry install
# Configure your .env file
gondola db init
gondola start
```

Your API is now running at `http://localhost:8000` with interactive docs at `/docs`.

**API version header (PostgreSQL projects):** clients may send `API-Version: v1`. If the header is missing, the app uses the default from settings (`api_default_version`, usually `v1`). Versioning is header-based, not via URL prefixes.

---

### Starting the Server

`gondola start` (alias: `gondola s`) starts the FastAPI server.

```bash
# Development mode (default)
gondola start
gondola s          # alias

# Custom port and host
gondola start --port 3000 --host 0.0.0.0
gondola start -p 3000 -H 0.0.0.0

# Enable hot-reload in development
gondola start --reload
gondola start -r

# Production mode
gondola start --env production
gondola start -e prod

# Production with multiple workers
gondola start -e prod --workers 4
gondola start -e prod -w 4
```

#### Options

| Option | Alias | Default | Description |
|--------|-------|---------|-------------|
| `--port` | `-p` | `$PORT` or `8000` | Port number |
| `--env` | `-e` | `development` | Runtime mode: `dev`/`development` or `prod`/`production` |
| `--reload` | `-r` | `false` | Hot-reload on code changes (development only) |
| `--host` | `-H` | `127.0.0.1` | Host address |
| `--workers` | `-w` | `1` | Number of workers (production only) |

> **Note**: `--reload` is ignored in production mode. `--workers` is ignored in development mode.

---

### Generators

`gondola generate` (alias: `gondola g`) generates code components. Run these from the **root of a generated project** (where `main.py` lives).

#### Generate a model

```bash
gondola generate model User
gondola g model User           # alias
```

**Creates:**

- `api/models/user.py` — SQLModel table definition
- `api/models/schemas/user.py` — Pydantic schemas (Create, Update, Response)
- `test/unit/models/test_user.py` — Unit tests

**Run migration:**

```bash
gondola generate migration "Create User model"
gondola migrate up
```

#### Generate a router

```bash
gondola generate router users --model=User
gondola g router users --model=User    # alias
```

**Creates:**

- `api/routers/users.py` — CRUD endpoints (list, create, get, update, delete)
- `test/integration/routers/test_users_routes.py` — Integration tests

#### Generate a service

```bash
gondola generate service UserNotification
gondola g service UserNotification     # alias
```

**Creates:**

- `api/services/user_notification.py` — Service class
- `test/unit/services/test_user_notification.py` — Unit tests

#### Generate a mailer

```bash
gondola generate mailer Welcome
gondola g mailer Welcome               # alias
```

**Creates:**

- `api/mailers/welcome.py` — Mailer class with template support
- `test/unit/mailers/test_welcome.py` — Unit tests

---

### Database Commands

#### Initialize the database

`gondola db init` is the one-stop command to get your database ready for the first time:

```bash
gondola db init
```

It performs the following steps in order:

1. **Reads `.env`** and extracts the `DATABASE_URL`
2. **Creates the database** if it doesn't exist yet; if it does, it tells you and moves on
3. **Enables extensions** (PostgreSQL only) — detects `postgis` / `pgvector` from `pyproject.toml` and runs `CREATE EXTENSION IF NOT EXISTS` for each
4. **Runs the initial migration**:
   ```bash
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

> **Prerequisites**: Run `poetry install` first — `gondola db init` uses the project's virtual environment to connect to the database (asyncpg, asyncmy, or aiosqlite must be installed).

**Typical first-time workflow:**

```bash
cd my-api
poetry install
# Edit .env with your real database credentials
gondola db init
gondola start
```

---

### Migration Commands

`gondola migrate` wraps Alembic for easy database migration management.

#### Create a migration

```bash
gondola generate migration "Add user preferences table"
gondola g migration "Add user preferences table"    # alias
```

#### Apply migrations

```bash
# Upgrade to latest (head)
gondola migrate up

# Upgrade to a specific revision
gondola migrate up --revision abc123
gondola migrate up -r abc123
```

#### Rollback migrations

```bash
# Roll back one revision
gondola migrate down

# Roll back to a specific revision
gondola migrate down --revision abc123
gondola migrate down -r abc123
```

#### View migration history

```bash
gondola migrate history
gondola migrate h          # alias
```

#### Check current revision

```bash
gondola migrate current
gondola migrate c          # alias
```

---

### Delete Commands

`gondola delete` (alias: `gondola d`) removes generated code safely with automatic cleanup.

#### Delete a model

```bash
gondola delete model User
gondola d model User          # alias
```

Gondola will:

- List related files (`api/models/user.py`, `api/models/schemas/user.py`, `test/unit/models/test_user.py`)
- Check for simple cross-model references
- Try to point out a related migration revision
- Prompt for confirmation unless `--force`

⚠️ **Migrations**: roll back Alembic revisions yourself when appropriate:

```bash
gondola migrate down
```

#### Delete a router

```bash
gondola delete router users
gondola d router users        # alias
```

Removes `api/routers/users.py` and `test/integration/routers/test_users_routes.py`.

#### Delete a service

```bash
gondola delete service UserNotification
gondola d service UserNotification     # alias
```

Removes `api/services/user_notification.py` and `test/unit/services/test_user_notification.py`.

#### Delete a mailer

```bash
gondola delete mailer Welcome
gondola d mailer Welcome               # alias
```

Removes `api/mailers/welcome.py` and `test/unit/mailers/test_welcome.py`.

---

## Command Reference

| Command | Alias | Description |
|---------|-------|-------------|
| `gondola init [name]` | `gondola i [name]` | Create a new FastAPI project (interactive wizard) |
| `gondola start` | `gondola s` | Start the FastAPI server |
| `gondola db init` | — | Initialize DB: create it, enable extensions, run initial migration |
| `gondola generate model <name>` | `gondola g model <name>` | Generate model + schema + test |
| `gondola generate router <name>` | `gondola g router <name>` | Generate router + integration test |
| `gondola generate service <name>` | `gondola g service <name>` | Generate service + unit test |
| `gondola generate mailer <name>` | `gondola g mailer <name>` | Generate mailer + unit test |
| `gondola generate migration <message>` | `gondola g migration <message>` | Create an Alembic migration |
| `gondola migrate up` | — | Apply migrations (to head) |
| `gondola migrate up -r <hash>` | — | Apply migrations to a revision |
| `gondola migrate down` | — | Roll back one migration |
| `gondola migrate down -r <hash>` | — | Roll back to a revision |
| `gondola migrate history` | `gondola migrate h` | Show migration history |
| `gondola migrate current` | `gondola migrate c` | Show current revision |
| `gondola delete model <name>` | `gondola d model <name>` | Delete model + schema + test |
| `gondola delete router <name>` | `gondola d router <name>` | Delete router + integration test |
| `gondola delete service <name>` | `gondola d service <name>` | Delete service + unit test |
| `gondola delete mailer <name>` | `gondola d mailer <name>` | Delete mailer + unit test |

---

## Development and contributing

We welcome contributions. The CLI renders Jinja templates from:

- **`gondola/templates/default/`** — default output for `gondola init`

**`examples/example_app/`** in this repository is a non-packaged reference layout; update the Jinja trees when you change the example app.

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
- **Gondola / package**: `pip show gondola-cli` (or your install tool's equivalent)
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
