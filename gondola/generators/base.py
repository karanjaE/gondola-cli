from pathlib import Path
from typing import Any, Dict
from jinja2 import Environment, FileSystemLoader, Template
import os

class BaseGenerator:
    """Base class for generators"""

    def __init__(self, template_dir: str):
        templates_path = Path(__file__).parent.parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(templates_path)),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.template_dir = template_dir

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with the given context"""
        template_path = f"{self.template_dir}/{template_name}"
        template = self.env.get_template(template_path)
        return template.render(**context)

    def write_file(self, path: Path, contemt: str) -> None:
        """Write the content to a file, and create the needed directories"""

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contemt)

    def copy_template(
        self,
        template_name: str,
        destination: Path,
        context: Dict[str, Any],
    )-> None:
        """Render and write a template to file"""
        content = self.render_template(template_name, context)
        self.write_file(destination, content)
