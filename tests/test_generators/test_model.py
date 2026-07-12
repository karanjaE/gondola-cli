"""Tests for ModelGenerator."""
import tempfile
import os
from pathlib import Path
from gondola.generators.model import ModelGenerator


class TestModelGenerator:
    """Test ModelGenerator functionality."""
    
    def test_init(self):
        """Test ModelGenerator initialization."""
        generator = ModelGenerator("User", "name:str,email:str")
        assert generator.name == "User"
        assert generator.file_name == "user"
        assert len(generator.fields) == 2
    
    def test_init_pascal_case_conversion(self):
        """Test that names are converted to PascalCase."""
        generator = ModelGenerator("user_profile")
        assert generator.name == "UserProfile"
        assert generator.file_name == "user_profile"
    
    def test_parse_fields_empty(self):
        """Test parsing empty fields string."""
        generator = ModelGenerator("User", "")
        assert generator.fields == []
    
    def test_parse_fields_single(self):
        """Test parsing single field."""
        generator = ModelGenerator("User", "name:str")
        assert len(generator.fields) == 1
        assert generator.fields[0] == ("name", "str")
    
    def test_parse_fields_multiple(self):
        """Test parsing multiple fields."""
        generator = ModelGenerator("User", "name:str,email:str,age:int")
        assert len(generator.fields) == 3
        assert generator.fields[0] == ("name", "str")
        assert generator.fields[1] == ("email", "str")
        assert generator.fields[2] == ("age", "int")
    
    def test_parse_fields_with_spaces(self):
        """Test parsing fields with spaces."""
        generator = ModelGenerator("User", "name: str, email : str")
        assert len(generator.fields) == 2
        assert generator.fields[0] == ("name", "str")
        assert generator.fields[1] == ("email", "str")
    
    def test_generate_creates_files(self):
        """Test that generate creates all required files (legacy app/models layout)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                # Create required directories (legacy app/models layout)
                (Path(tmpdir) / "app" / "models").mkdir(parents=True)
                (Path(tmpdir) / "app" / "models" / "schemas").mkdir(parents=True)
                (Path(tmpdir) / "test" / "unit").mkdir(parents=True)
                
                generator = ModelGenerator("User", "name:str,email:str")
                generator.generate()
                
                # Check model file
                model_file = Path(tmpdir) / "app" / "models" / "user.py"
                assert model_file.exists()
                
                # Check schema file
                schema_file = Path(tmpdir) / "app" / "models" / "schemas" / "user.py"
                assert schema_file.exists()
                
                # Check test file
                test_file = Path(tmpdir) / "test" / "unit" / "models" / "test_user.py"
                assert test_file.exists()
            finally:
                os.chdir(original_cwd)
    
    def test_generate_does_not_update_init(self):
        """generate() must not auto-create app/models/__init__.py (removed in layout consolidation)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                # Create required directories
                (Path(tmpdir) / "app" / "models").mkdir(parents=True)
                (Path(tmpdir) / "app" / "models" / "schemas").mkdir(parents=True)
                (Path(tmpdir) / "test" / "unit").mkdir(parents=True)
                
                generator = ModelGenerator("User")
                generator.generate()
                
                init_file = Path(tmpdir) / "app" / "models" / "__init__.py"
                assert not init_file.exists()
            finally:
                os.chdir(original_cwd)
    
    def test_generate_does_not_modify_existing_init(self):
        """generate() must not append imports to an existing app/models/__init__.py."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                # Create required directories
                (Path(tmpdir) / "app" / "models").mkdir(parents=True)
                (Path(tmpdir) / "app" / "models" / "schemas").mkdir(parents=True)
                (Path(tmpdir) / "test" / "unit").mkdir(parents=True)
                
                # Create existing __init__.py
                init_file = Path(tmpdir) / "app" / "models" / "__init__.py"
                init_file.write_text("from .other import Other\n")
                
                generator = ModelGenerator("User")
                generator.generate()
                
                content = init_file.read_text()
                assert "from .other import Other" in content
                assert "from .user import User" not in content
            finally:
                os.chdir(original_cwd)
    
    def test_generate_does_not_add_init_imports(self):
        """generate() must not add model imports to __init__.py, even when run twice."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                # Create required directories
                (Path(tmpdir) / "app" / "models").mkdir(parents=True)
                (Path(tmpdir) / "app" / "models" / "schemas").mkdir(parents=True)
                (Path(tmpdir) / "test" / "unit").mkdir(parents=True)
                
                # Create existing __init__.py
                init_file = Path(tmpdir) / "app" / "models" / "__init__.py"
                init_file.write_text("from .other import Other\n")
                
                generator = ModelGenerator("User")
                generator.generate()
                content1 = init_file.read_text()
                
                # Generate again
                generator.generate()
                content2 = init_file.read_text()
                
                # Should be untouched and contain no model import
                assert content1 == content2
                assert "from .user import User" not in content1
            finally:
                os.chdir(original_cwd)


class TestModelGeneratorPostgresLayout:
    """ModelGenerator when api/models exists (PostgreSQL-style layout)."""

    def test_generate_creates_model_and_schema(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                (Path(tmpdir) / "api" / "models" / "schemas").mkdir(parents=True)
                (Path(tmpdir) / "api" / "models" / "schemas" / "__init__.py").touch()
                (Path(tmpdir) / "test" / "unit").mkdir(parents=True)

                generator = ModelGenerator("User", "name:str,email:str")
                generator.generate()

                assert (Path(tmpdir) / "api" / "models" / "user.py").exists()
                assert (Path(tmpdir) / "api" / "models" / "schemas" / "user.py").exists()
                assert (Path(tmpdir) / "test" / "unit" / "models" / "test_user.py").exists()
            finally:
                os.chdir(original_cwd)

    def test_generate_does_not_require_models_init(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                (Path(tmpdir) / "api" / "models" / "schemas").mkdir(parents=True)
                (Path(tmpdir) / "test" / "unit").mkdir(parents=True)

                ModelGenerator("Item").generate()

                init_path = Path(tmpdir) / "api" / "models" / "__init__.py"
                if init_path.exists():
                    assert "from .item import Item" not in init_path.read_text()
            finally:
                os.chdir(original_cwd)
