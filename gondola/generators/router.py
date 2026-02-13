from pathlib import Path
from .base import BaseGenerator
from ..utils.string_utils import to_snake_case, to_pascal_case, pluralize

class RouterGenerator(BaseGenerator):
    """Generator for FastAPI routers."""
    
    def __init__(self, name: str, model_name: str = None):
        super().__init__("router")
        self.name = to_pascal_case(name)
        self.file_name = to_snake_case(name)
        self.model_name = to_pascal_case(model_name) if model_name else self.name
        self.plural_name = pluralize(self.file_name)
    
    def generate(self) -> None:
        """Generate router file and integration test."""
        context = {
            "router_name": self.name,
            "file_name": self.file_name,
            "model_name": self.model_name,
            "plural_name": self.plural_name,
        }
        
        # Generate router
        router_path = Path("app/routers") / f"{self.file_name}.py"
        self.copy_template("router.py.jinja", router_path, context)
        
        # Generate integration test
        test_path = Path("test/integration") / f"test_{self.file_name}_routes.py"
        self.copy_template("router_test.py.jinja", test_path, context)
