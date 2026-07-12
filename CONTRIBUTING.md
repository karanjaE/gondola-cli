# Development and contributing

We welcome contributions. The CLI renders Jinja templates from:

- **`gondola/templates/default/`** — default output for `gondola init`

**`examples/example_app/`** in this repository is a non-packaged reference layout; update the Jinja trees when you change the example app.

## Setup development environment

```bash
git clone https://github.com/karanjaE/gondola-cli.git
cd gondola-cli
poetry install
```

## Running Tests

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

## Code Quality

```bash
# Type checking with mypy
poetry run mypy gondola

# Linting with ruff
poetry run ruff check gondola

# Format code
poetry run ruff format gondola
```

## Contributing Guidelines

1. **Fork the repository** and create a feature branch
2. **Write tests** for new functionality
3. **Ensure all tests pass** and maintain coverage above 80%
4. **Follow code style** - run mypy and ruff before committing
5. **Write clear commit messages** following conventional commits
6. **Submit a pull request** with a description of changes

## Development Workflow

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
