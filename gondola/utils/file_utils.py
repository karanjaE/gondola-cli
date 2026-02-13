from pathlib import Path
import re


def find_migration_for_model(model_name: str) -> Path | None:
    """Find the migration file that created a model."""
    migrations_dir = Path("migrations/versions")
    
    if not migrations_dir.exists():
        return None
    
    # Search for migration files mentioning the model
    for migration_file in migrations_dir.glob("*.py"):
        content = migration_file.read_text()
        # Look for table creation with model name
        pattern = rf"create_table\(['\"].*{model_name.lower()}.*['\"]"
        if re.search(pattern, content, re.IGNORECASE):
            return migration_file
    
    return None


def remove_file_safely(file_path: Path) -> None:
    """Remove a file if it exists."""
    if file_path.exists():
        file_path.unlink()
