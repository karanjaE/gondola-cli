from pathlib import Path

from .base import BaseGenerator
from ..utils.string_utils import to_pascal_case, to_snake_case


class SeedGenerator(BaseGenerator):
    """Generator for database seed files."""

    def __init__(self, name: str):
        super().__init__("")
        self.seed_name = to_pascal_case(name)
        self.file_name = to_snake_case(name)

    def generate(self) -> None:
        seeds_dir = Path("db/seeds")
        seeds_dir.mkdir(parents=True, exist_ok=True)

        init_file = seeds_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text("# db/seeds package\n")

        context = {
            "seed_name": self.seed_name,
            "seed_class": f"{self.seed_name}Seed",
            "file_name": self.file_name,
        }

        seed_path = seeds_dir / f"{self.file_name}_seed.py"
        self.copy_template("default/db/seeds/seed.py.jinja", seed_path, context)
