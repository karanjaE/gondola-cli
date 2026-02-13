# Gondola

A CLI tool for FastAPI projects that brings convention over configuration to the Python async web ecosystem.

---

## Introduction

Gondola is a command-line tool designed to streamline FastAPI development by providing scaffolding, generators, and conventions. Focus on building features, not boilerplate.

### Philosophy

**Convention Over Configuration**: Gondola establishes sensible defaults and project structures so you can start building immediately. Opinionated where it matters, flexible where you need it.

**Developer Happiness**: Reduce cognitive load with intuitive commands, clear project organization, and automatic test generation. If you've used Rails, you'll feel right at home.

**Modern Async-First**: Built for Python 3.11+ with async/await patterns throughout. Native support for SQLModel, PostgreSQL, Redis, and Celery.

**Production Ready**: Generate projects with Docker, testing infrastructure, migrations, and deployment configurations included from day one.

### Features

- **Project Scaffolding**: Create production-ready FastAPI projects in seconds
- **Code Generators**: Auto-generate models, routers, services, mailers, and tests
- **Database Management**: Built-in migration commands powered by Alembic
- **Testing First**: Every generated component includes comprehensive tests
- **Docker Ready**: Optional Docker and docker-compose configuration
- **Multiple Database Support**: PostgreSQL (with PostGIS/pgvector), SQLite
- **Background Jobs**: Celery integration for async task processing
- **Email Support**: Built-in mailer generator with templates
- **Type Safe**: Full mypy support with Pydantic models
- **Migration Rollback**: Reversible database migrations
- **Rich CLI**: Beautiful terminal output with progress indicators

---

## Installation

### Requirements

- **Python**: 3.11 or higher
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

Create a new FastAPI project with PostgreSQL and Docker:

```bash
gondola create project my-api --db=postgresql --docker=true
```

Create a minimal project with SQLite:

```bash
gondola create project my-api --db=sqlite
```

#### What gets created?

```
my-api/
├── app/
│   ├── models/           # Database models
│   ├── routers/          # API endpoints
│   ├── services/         # Business logic
│   ├── mailers/          # Email templates
│   └── core/             # Configuration
├── test/
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── alembic/              # Database migrations
├── docker-compose.yml    # Container orchestration
├── Dockerfile            # App container
└── pyproject.toml        # Dependencies
```

#### Next steps

```bash
cd my-api
poetry install
cp env.example .env
# Configure your .env file
gondola migrate upgrade
gondola run server
```

Your API is now running at `http://localhost:8000` with interactive docs at `/docs`.

---

### Generators

Gondola provides powerful generators to scaffold your application components.

#### Generate a Model

Create a database model with fields, serializers, and tests:

```bash
gondola generate model User name:str email:str age:int is_active:bool
```

**Creates:**
- `app/models/user.py` - SQLModel table definition
- `app/models/serializers/user_serializer.py` - Pydantic schemas (Create, Update, Response)
- `test/unit/test_user.py` - Unit tests

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
- `app/routers/users.py` - CRUD endpoints (list, create, get, update, delete)
- `test/integration/test_users.py` - Integration tests

**Register the router** in `main.py`:
```python
from app.routers import users
app.include_router(users.router)
```

#### Generate a Service

Create a service class for business logic:

```bash
gondola generate service UserNotification
```

**Creates:**
- `app/services/user_notification.py` - Service class with Celery task decorator
- `test/unit/test_user_notification.py` - Unit tests

#### Generate a Mailer

Create an email mailer with templates:

```bash
gondola generate mailer WelcomeMailer
```

**Creates:**
- `app/mailers/welcome_mailer.py` - Mailer class with SMTP configuration
- `app/mailers/templates/welcome.html` - HTML email template
- `test/unit/test_welcome_mailer.py` - Unit tests

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

### Delete Commands

Remove generated code safely with automatic cleanup.

#### Delete a model

```bash
gondola delete model User
```

Gondola will:
- List all related files (model, serializers, tests)
- Check for foreign key dependencies
- Identify the migration that created the table
- Prompt for confirmation
- Remove files and clean up imports

⚠️ **Important**: You must manually rollback the migration:
```bash
gondola migrate downgrade -1
```

#### Delete a router

```bash
gondola delete router users
```

Remember to remove the router registration from `main.py`.

---

### Server Commands

Run your development server and background workers.

#### Start the API server

```bash
# Development mode with auto-reload
gondola run server

# Custom port and host
gondola run server --port=3000 --host=0.0.0.0

# Production mode with multiple workers
gondola run server --workers=4 --no-reload
```

#### Start Celery worker

```bash
gondola run celery-worker

# With custom log level
gondola run celery-worker --log-level=debug
```

#### Start Celery beat scheduler

```bash
gondola run celery-beat
```

---

## Development and Contributing

We welcome contributions! Here's how to get started.

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/karanjaE/gondola-cli.git
cd gondola-cli

# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install
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
- **Gondola version**: Run `pip show gondola`
- **Python version**: Run `python --version`
- **Operating system**: e.g., macOS 14.2, Ubuntu 22.04
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Error messages** or stack traces
- **Code samples** or minimal reproduction

### Security Vulnerabilities

**Do not** open public issues for security vulnerabilities. Instead, email security@gondola.dev with details.

---

## License

Gondola is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2025 E. Karanja Muriithi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

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

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting the project team at conduct@gondola.dev. All complaints will be reviewed and investigated promptly and fairly.

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

- **Documentation**: [https://gondola.dev/docs](https://gondola.dev/docs)
- **PyPI**: [https://pypi.org/project/gondola](https://pypi.org/project/gondola)
- **GitHub**: [https://github.com/karanjaE/gondola-cli](https://github.com/karanjaE/gondola-cli)
- **Discussions**: [https://github.com/karanjaE/gondola-cli/discussions](https://github.com/karanjaE/gondola-cli/discussions)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

---

**Happy building**
