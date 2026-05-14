from pathlib import Path
from typing import List, Tuple

from .base import BaseGenerator
from ..utils.string_utils import to_pascal_case, to_snake_case


class ModelGenerator(BaseGenerator):
    """Generator for SQLModel models."""

    def __init__(self, name: str, fields: str = ""):
        super().__init__("")
        self.name = to_pascal_case(name)
        self.file_name = to_snake_case(name)
        self.fields = self._parse_fields(fields)

    def _parse_fields(self, fields_str: str) -> List[Tuple[str, str]]:
        if not fields_str:
            return []
        fields: List[Tuple[str, str]] = []
        for field in fields_str.split(","):
            if ":" in field:
                name, type_str = field.split(":", 1)
                fields.append((name.strip(), type_str.strip()))
        return fields

    @staticmethod
    def _is_api_layout() -> bool:
        return Path("api/models").exists()

    def generate(self) -> None:
        context = {
            "model_name": self.name,
            "file_name": self.file_name,
            "fields": self.fields,
        }

        if self._is_api_layout():
            self.copy_template(
                "postgres/api/models/model.py.jinja",
                Path("api/models") / f"{self.file_name}.py",
                context,
            )
            self.copy_template(
                "postgres/api/models/schemas/schema.py.jinja",
                Path("api/models/schemas") / f"{self.file_name}.py",
                context,
            )
        else:
            self.copy_template(
                "legacy/app/model/model.py.jinja",
                Path("app/models") / f"{self.file_name}.py",
                context,
            )
            self.copy_template(
                "legacy/app/model/serializer.py.jinja",
                Path("app/models/serializers") / f"{self.file_name}_serializer.py",
                context,
            )
            self._update_models_init()

        test_path = Path("test/unit") / f"test_{self.file_name}.py"
        if self._is_api_layout():
            self.copy_template("postgres/api/models/model_test.py.jinja", test_path, context)
        else:
            self.copy_template("legacy/app/model/model_test.py.jinja", test_path, context)

    def _update_models_init(self) -> None:
        init_path = Path("app/models/__init__.py")
        import_line = f"from .{self.file_name} import {self.name}\n"
        if init_path.exists():
            content = init_path.read_text()
            if import_line not in content:
                init_path.write_text(content + import_line)
        else:
            init_path.write_text(import_line)
