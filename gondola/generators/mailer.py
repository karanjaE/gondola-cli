from pathlib import Path
from .base import BaseGenerator
from ..utils.string_utils import to_snake_case, to_pascal_case

class MailerGenerator(BaseGenerator):
    """Generator for mailer classes."""
    
    def __init__(self, name: str):
        super().__init__("")
        self.name = to_pascal_case(name)
        self.file_name = to_snake_case(name)
    
    def generate(self) -> None:
        """Generate mailer file and test."""
        # Create lib/mailers directory if it doesn't exist
        mailers_dir = Path("app/lib/mailers")
        mailers_dir.mkdir(parents=True, exist_ok=True)
        (mailers_dir / "__init__.py").touch()
        
        context = {
            "mailer_name": self.name,
            "file_name": self.file_name,
        }
        
        # Generate mailer
        mailer_path = mailers_dir / f"{self.file_name}.py"
        self.copy_template("app/mailer/mailer.py.jinja", mailer_path, context)
        
        # Generate test
        test_path = Path("test/unit") / f"test_{self.file_name}.py"
        test_path.parent.mkdir(parents=True, exist_ok=True)
        test_path.write_text(f"# Test for {self.name} mailer\n")
