from pathlib import Path

from .base import BaseGenerator
from ..utils.string_utils import pluralize, to_pascal_case, to_snake_case


class RouterGenerator(BaseGenerator):
    """Generator for FastAPI routers."""

    def __init__(self, name: str, model_name: str | None = None):
        super().__init__("")
        self.name = to_pascal_case(name)
        self.file_name = to_snake_case(name)
        self.model_name = to_pascal_case(model_name) if model_name else self.name
        self.plural_name = pluralize(self.file_name)

    @staticmethod
    def _is_api_layout() -> bool:
        return Path("api/routers").exists()

    def generate(self) -> None:
        context = {
            "router_name": self.name,
            "file_name": self.file_name,
            "model_name": self.model_name,
            "plural_name": self.plural_name,
        }

        if self._is_api_layout():
            router_path = Path("api/routers") / f"{self.file_name}.py"
            self.copy_template("postgres/api/routers/router.py.jinja", router_path, context)
        else:
            router_path = Path("app/routers") / f"{self.file_name}.py"
            self.copy_template("legacy/app/router/router.py.jinja", router_path, context)

        test_path = Path("test/integration") / f"test_{self.file_name}_routes.py"
        test_path.parent.mkdir(parents=True, exist_ok=True)
        test_path.write_text(f"# Integration tests for {self.name} router\n")
