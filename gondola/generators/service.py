# gondola/generators/service.py
from pathlib import Path
from .base import BaseGenerator
from ..utils.string_utils import to_snake_case, to_pascal_case


class ServiceGenerator(BaseGenerator):
    """Generator for service classes."""
    
    def __init__(self, name: str):
        super().__init__("")
        self.name = to_pascal_case(name)
        self.file_name = to_snake_case(name)
    
    def generate(self) -> None:
        """Generate service file and test."""
        context = {
            "service_name": self.name,
            "file_name": self.file_name,
        }
        
        # Generate service
        service_path = Path("app/services") / f"{self.file_name}.py"
        self.copy_template("app/service/service.py.jinja", service_path, context)
        
        # Generate test
        test_path = Path("test/unit") / f"test_{self.file_name}.py"
        test_path.parent.mkdir(parents=True, exist_ok=True)
        test_path.write_text(f"# Test for {self.name} service\n")
