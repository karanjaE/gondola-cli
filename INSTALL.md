# Installation

## Requirements

- **Python**: 3.12 or higher (for the `gondola-cli` tool and generated PostgreSQL projects)
- **Poetry**: 1.5+ (recommended) or pip
- **Docker**: Optional, for containerized development

## Installation Guide

### Install via pip

```bash
pip install gondola-cli
```

### Install via pipx (recommended for CLI tools)

```bash
pipx install gondola-cli
```

### Install from source

```bash
git clone https://github.com/karanjaE/gondola-cli.git
cd gondola-cli
poetry install
```

### Verify installation

```bash
gondola --help
```

You should see the Gondola CLI help menu with available commands.
