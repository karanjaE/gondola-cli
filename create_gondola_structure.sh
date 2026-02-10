#!/bin/bash

# Create Gondola project structure
echo "Creating Gondola project structure..."

# Create main directories
mkdir -p gondola/{cli,templates/{project,model,router,service,mailer,test},generators,utils}
mkdir -p tests/{test_cli,test_generators,fixtures}

# Create __init__.py files
touch gondola/__init__.py
touch gondola/__main__.py
touch gondola/cli/__init__.py
touch gondola/generators/__init__.py
touch gondola/utils/__init__.py
touch tests/__init__.py
touch tests/test_cli/__init__.py
touch tests/test_generators/__init__.py
touch tests/fixtures/__init__.py

# Create CLI files
touch gondola/cli/main.py
touch gondola/cli/create.py
touch gondola/cli/generate.py
touch gondola/cli/delete.py
touch gondola/cli/migrate.py
touch gondola/cli/server.py

# Create generator files
touch gondola/generators/base.py
touch gondola/generators/project.py
touch gondola/generators/model.py
touch gondola/generators/router.py
touch gondola/generators/service.py
touch gondola/generators/mailer.py

# Create utility files
touch gondola/utils/file_utils.py
touch gondola/utils/string_utils.py
touch gondola/utils/validators.py

# Create config file
touch gondola/config.py

# Create root files
touch pyproject.toml
touch README.md
touch LICENSE

echo "✓ Gondola project structure created successfully!"
echo ""
echo "Directory structure:"
tree -L 3 -I '__pycache__'
