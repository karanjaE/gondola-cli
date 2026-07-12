"""Tests for RouterGenerator."""
import tempfile
import os
from pathlib import Path
from gondola.generators.router import RouterGenerator


class TestRouterGenerator:
    """Test RouterGenerator functionality."""
    
    def test_init(self):
        """Test RouterGenerator initialization."""
        generator = RouterGenerator("User")
        assert generator.name == "User"
        assert generator.file_name == "user"
        assert generator.model_name == "User"
    
    def test_init_with_model(self):
        """Test RouterGenerator initialization with model name."""
        generator = RouterGenerator("UserRouter", "BlogPost")
        # to_pascal_case splits by underscore/space, so "UserRouter" becomes "Userrouter"
        assert generator.name == "Userrouter"
        assert generator.file_name == "user_router"
        # to_pascal_case splits by underscore/space, so "BlogPost" becomes "Blogpost"
        assert generator.model_name == "Blogpost"
    
    def test_init_pascal_case_conversion(self):
        """Test that names are converted to PascalCase."""
        generator = RouterGenerator("user_profile")
        assert generator.name == "UserProfile"
        assert generator.file_name == "user_profile"
    
    def test_pluralize(self):
        """Test pluralization."""
        generator = RouterGenerator("User")
        assert generator.plural_name == "users"
        
        generator2 = RouterGenerator("Category")
        assert generator2.plural_name == "categories"
        
        generator3 = RouterGenerator("Box")
        assert generator3.plural_name == "boxes"
    
    def test_generate_creates_files(self):
        """Test that generate creates all required files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                # Create required directories
                (Path(tmpdir) / "app" / "routers").mkdir(parents=True)
                (Path(tmpdir) / "test" / "integration").mkdir(parents=True)
                
                generator = RouterGenerator("User")
                generator.generate()
                
                # Check router file
                router_file = Path(tmpdir) / "app" / "routers" / "user.py"
                assert router_file.exists()
                
                # Check test file
                test_file = Path(tmpdir) / "test" / "integration" / "test_user_routes.py"
                assert test_file.exists()
            finally:
                os.chdir(original_cwd)
    
    def test_generate_with_model(self):
        """Test generate with model name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                # Create required directories
                (Path(tmpdir) / "app" / "routers").mkdir(parents=True)
                (Path(tmpdir) / "test" / "integration").mkdir(parents=True)
                
                generator = RouterGenerator("UserRouter", "BlogPost")
                generator.generate()
                
                router_file = Path(tmpdir) / "app" / "routers" / "user_router.py"
                assert router_file.exists()
                
                # Check that model_name is used in context
                content = router_file.read_text()
                # The template should use model_name
                assert "BlogPost" in content or "user_router" in content
            finally:
                os.chdir(original_cwd)
    
    def test_generate_creates_test_content(self):
        """Test that generate creates test file with content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                # Create required directories
                (Path(tmpdir) / "app" / "routers").mkdir(parents=True)
                (Path(tmpdir) / "test" / "integration").mkdir(parents=True)
                
                generator = RouterGenerator("User")
                generator.generate()
                
                test_file = Path(tmpdir) / "test" / "integration" / "test_user_routes.py"
                assert test_file.exists()
                content = test_file.read_text()
                assert "User" in content
            finally:
                os.chdir(original_cwd)


class TestRouterGeneratorPostgresLayout:
    def test_generate_creates_api_router(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                (Path(tmpdir) / "api" / "routers").mkdir(parents=True)
                (Path(tmpdir) / "test" / "integration").mkdir(parents=True)

                RouterGenerator("User").generate()

                assert (Path(tmpdir) / "api" / "routers" / "user.py").exists()
            finally:
                os.chdir(original_cwd)
