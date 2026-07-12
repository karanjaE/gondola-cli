from pathlib import Path

from .base import BaseGenerator
from ..utils.string_utils import to_pascal_case, to_snake_case


class ServiceGenerator(BaseGenerator):
    """Generator for service classes."""

    def __init__(self, name: str):
        super().__init__("")
        self.name = to_pascal_case(name)
        self.file_name = to_snake_case(name)

    @staticmethod
    def _is_api_layout() -> bool:
        return Path("api/services").exists()

    def generate(self) -> None:
        context = {
            "service_name": self.name,
            "file_name": self.file_name,
        }
        if self._is_api_layout():
            service_path = Path("api/services") / f"{self.file_name}.py"
        else:
            service_path = Path("app/services") / f"{self.file_name}.py"
        
        tpl = "default/api/services/service.py.jinja"
        self.copy_template(tpl, service_path, context)

        test_dir = Path("test/unit/services")
        test_dir.mkdir(parents=True, exist_ok=True)
        test_path = test_dir / f"test_{self.file_name}.py"
        test_path.write_text(f"# Test for {self.name} service\n")
