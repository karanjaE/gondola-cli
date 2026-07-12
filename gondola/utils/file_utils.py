from pathlib import Path
import re


def find_migration_for_model(model_name: str) -> Path | None:
    """Find the migration file that created a model."""
    candidates = [
        Path("db/migrations/versions"),
        Path("migrations/versions"),
    ]
    for migrations_dir in candidates:
        if not migrations_dir.exists():
            continue
        for migration_file in migrations_dir.glob("*.py"):
            content = migration_file.read_text()
            pattern = rf"create_table\(['\"].*{re.escape(model_name.lower())}.*['\"]"
            if re.search(pattern, content, re.IGNORECASE):
                return migration_file
    return None


def remove_file_safely(file_path: Path) -> None:
    """Remove a file if it exists."""
    if file_path.exists():
        file_path.unlink()
