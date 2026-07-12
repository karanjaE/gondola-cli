import tempfile
import os
from pathlib import Path
from typer.testing import CliRunner
from gondola.cli.main import app

runner = CliRunner()

def test_create_project():
    """Test project creation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Change to the temporary directory for the test
        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            result = runner.invoke(
                app,
                ["init", "test-project", "--db", "sqlite", "--no-docker", "--extensions", "", "--no-fetch"],
                input="y\n",
            )
        finally:
            os.chdir(original_cwd)

        assert result.exit_code == 0
        project_path = Path(tmpdir) / "test-project"
        assert project_path.exists()
        assert (project_path / "main.py").exists()
        assert (project_path / "pyproject.toml").exists()
