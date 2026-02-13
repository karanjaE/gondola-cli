from pathlib import Path
from typing import List, Tuple
from .base import BaseGenerator
from ..utils.string_utils import to_snake_case, to_pascal_case

class ModelGenerator(BaseGenerator):
    """Generator for SQLModel models."""
    
    def __init__(self, name: str, fields: str = ""):
        super().__init__("model")
        self.name = to_pascal_case(name)
        self.file_name = to_snake_case(name)
        self.fields = self._parse_fields(fields)
    
    def _parse_fields(self, fields_str: str) -> List[Tuple[str, str]]:
        """Parse field definitions from string."""
        if not fields_str:
            return []
        
        fields = []
        for field in fields_str.split(','):
            if ':' in field:
                name, type_str = field.split(':', 1)
                fields.append((name.strip(), type_str.strip()))
        return fields
    
    def generate(self) -> None:
        """Generate model file, serializer, and test."""
        context = {
            "model_name": self.name,
            "file_name": self.file_name,
            "fields": self.fields,
        }
        
        # Generate model
        model_path = Path("app/models") / f"{self.file_name}.py"
        self.copy_template("model.py.jinja", model_path, context)
        
        # Generate serializer
        serializer_path = Path("app/models/serializers") / f"{self.file_name}_serializer.py"
        self.copy_template("serializer.py.jinja", serializer_path, context)
        
        # Generate test
        test_path = Path("test/unit") / f"test_{self.file_name}.py"
        self.copy_template("model_test.py.jinja", test_path, context)
        
        # Update models __init__.py
        self._update_models_init()
    
    def _update_models_init(self) -> None:
        """Add import to models/__init__.py."""
        init_path = Path("app/models/__init__.py")
        import_line = f"from .{self.file_name} import {self.name}\n"
        
        if init_path.exists():
            content = init_path.read_text()
            if import_line not in content:
                init_path.write_text(content + import_line)
        else:
            init_path.write_text(import_line)
