"""Tests for ModelGenerator."""
import tempfile
import os
from pathlib import Path
import pytest
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
        """Test that generate creates all required files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                # Create required directories
                (Path(tmpdir) / "app" / "models").mkdir(parents=True)
                (Path(tmpdir) / "app" / "models" / "serializers").mkdir(parents=True)
                (Path(tmpdir) / "test" / "unit").mkdir(parents=True)
                
                generator = ModelGenerator("User", "name:str,email:str")
                generator.generate()
                
                # Check model file
                model_file = Path(tmpdir) / "app" / "models" / "user.py"
                assert model_file.exists()
                
                # Check serializer file
                serializer_file = Path(tmpdir) / "app" / "models" / "serializers" / "user_serializer.py"
                assert serializer_file.exists()
                
                # Check test file
                test_file = Path(tmpdir) / "test" / "unit" / "test_user.py"
                assert test_file.exists()
            finally:
                os.chdir(original_cwd)
    
    def test_generate_updates_init(self):
        """Test that generate updates __init__.py."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                # Create required directories
                (Path(tmpdir) / "app" / "models").mkdir(parents=True)
                (Path(tmpdir) / "app" / "models" / "serializers").mkdir(parents=True)
                (Path(tmpdir) / "test" / "unit").mkdir(parents=True)
                
                generator = ModelGenerator("User")
                generator.generate()
                
                init_file = Path(tmpdir) / "app" / "models" / "__init__.py"
                assert init_file.exists()
                content = init_file.read_text()
                assert "from .user import User" in content
            finally:
                os.chdir(original_cwd)
    
    def test_generate_appends_to_existing_init(self):
        """Test that generate appends to existing __init__.py."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                # Create required directories
                (Path(tmpdir) / "app" / "models").mkdir(parents=True)
                (Path(tmpdir) / "app" / "models" / "serializers").mkdir(parents=True)
                (Path(tmpdir) / "test" / "unit").mkdir(parents=True)
                
                # Create existing __init__.py
                init_file = Path(tmpdir) / "app" / "models" / "__init__.py"
                init_file.write_text("from .other import Other\n")
                
                generator = ModelGenerator("User")
                generator.generate()
                
                content = init_file.read_text()
                assert "from .other import Other" in content
                assert "from .user import User" in content
            finally:
                os.chdir(original_cwd)
    
    def test_generate_no_duplicate_imports(self):
        """Test that generate doesn't add duplicate imports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                # Create required directories
                (Path(tmpdir) / "app" / "models").mkdir(parents=True)
                (Path(tmpdir) / "app" / "models" / "serializers").mkdir(parents=True)
                (Path(tmpdir) / "test" / "unit").mkdir(parents=True)
                
                generator = ModelGenerator("User")
                generator.generate()
                
                init_file = Path(tmpdir) / "app" / "models" / "__init__.py"
                content1 = init_file.read_text()
                
                # Generate again
                generator.generate()
                content2 = init_file.read_text()
                
                # Should not have duplicate imports
                assert content1.count("from .user import User") == 1
                assert content2.count("from .user import User") == 1
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
                assert (Path(tmpdir) / "test" / "unit" / "test_user.py").exists()
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
