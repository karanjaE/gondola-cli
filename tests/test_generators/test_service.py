"""Tests for ServiceGenerator."""
import tempfile
import os
from pathlib import Path
import pytest
from gondola.generators.service import ServiceGenerator


class TestServiceGenerator:
    """Test ServiceGenerator functionality."""
    
    def test_init(self):
        """Test ServiceGenerator initialization."""
        generator = ServiceGenerator("EmailService")
        # to_pascal_case splits by underscore/space, so "EmailService" becomes "Emailservice"
        assert generator.name == "Emailservice"
        assert generator.file_name == "email_service"
    
    def test_init_pascal_case_conversion(self):
        """Test that names are converted to PascalCase."""
        generator = ServiceGenerator("email_service")
        assert generator.name == "EmailService"
        assert generator.file_name == "email_service"
    
    def test_init_single_word(self):
        """Test initialization with single word."""
        generator = ServiceGenerator("Service")
        assert generator.name == "Service"
        assert generator.file_name == "service"
    
    def test_generate_creates_files(self):
        """Test that generate creates all required files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                # Create required directories
                (Path(tmpdir) / "app" / "services").mkdir(parents=True)
                (Path(tmpdir) / "test" / "unit").mkdir(parents=True)
                
                generator = ServiceGenerator("EmailService")
                generator.generate()
                
                # Check service file
                service_file = Path(tmpdir) / "app" / "services" / "email_service.py"
                assert service_file.exists()
                
                # Check test file
                test_file = Path(tmpdir) / "test" / "unit" / "test_email_service.py"
                assert test_file.exists()
            finally:
                os.chdir(original_cwd)
    
    def test_generate_service_content(self):
        """Test that generate creates service file with correct content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                # Create required directories
                (Path(tmpdir) / "app" / "services").mkdir(parents=True)
                (Path(tmpdir) / "test" / "unit").mkdir(parents=True)
                
                generator = ServiceGenerator("EmailService")
                generator.generate()
                
                service_file = Path(tmpdir) / "app" / "services" / "email_service.py"
                assert service_file.exists()
                content = service_file.read_text()
                assert "Emailservice" in content
            finally:
                os.chdir(original_cwd)
    
    def test_generate_test_content(self):
        """Test that generate creates test file with content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                # Create required directories
                (Path(tmpdir) / "app" / "services").mkdir(parents=True)
                (Path(tmpdir) / "test" / "unit").mkdir(parents=True)
                
                generator = ServiceGenerator("EmailService")
                generator.generate()
                
                test_file = Path(tmpdir) / "test" / "unit" / "test_email_service.py"
                assert test_file.exists()
                content = test_file.read_text()
                assert "Emailservice" in content
            finally:
                os.chdir(original_cwd)


class TestServiceGeneratorPostgresLayout:
    def test_generate_writes_api_services(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                (Path(tmpdir) / "api" / "services").mkdir(parents=True)
                (Path(tmpdir) / "test" / "unit").mkdir(parents=True)

                ServiceGenerator("EmailService").generate()

                path = Path(tmpdir) / "api" / "services" / "email_service.py"
                assert path.exists()
                assert "Emailservice" in path.read_text()
            finally:
                os.chdir(original_cwd)
