"""Unit tests for config validation functionality."""

import pytest
from pathlib import Path


class TestConfigValidator:
    """Test configuration file validation."""

    def test_config_validator_can_be_imported(self):
        """Test that config validator module can be imported."""
        from validator.config import ConfigValidator
        assert ConfigValidator is not None

    def test_config_validator_checks_required_files(self, temp_filesystem, full_config_setup):
        """Test that config validator checks for required config files."""
        from validator.config import ConfigValidator
        import os
        
        # Set up all required config files
        full_config_setup()
        
        # Change to temp directory so validator finds the configs
        original_cwd = os.getcwd()
        try:
            os.chdir(str(temp_filesystem))
            validator = ConfigValidator()
            result = validator.validate_config_files()
        finally:
            os.chdir(original_cwd)
            
        assert result.success is True
        assert len(result.errors) == 0

    def test_config_validator_fails_on_missing_files(self, temp_filesystem):
        """Test that config validator fails when required files are missing."""
        from validator.config import ConfigValidator
        import os
        
        # Don't create any config files - use empty temp filesystem
        original_cwd = os.getcwd()
        try:
            os.chdir(str(temp_filesystem))
            validator = ConfigValidator()
            result = validator.validate_config_files()
        finally:
            os.chdir(original_cwd)
            
        assert result.success is False
        assert len(result.errors) > 0
        assert any("missing" in error.lower() for error in result.errors)

    def test_config_validator_result_has_required_attributes(self, temp_filesystem, full_config_setup):
        """Test that validation result has success and errors attributes."""
        from validator.config import ConfigValidator
        import os
        
        # Set up config files
        full_config_setup()
        
        original_cwd = os.getcwd()
        try:
            os.chdir(str(temp_filesystem))
            validator = ConfigValidator()
            result = validator.validate_config_files()
        finally:
            os.chdir(original_cwd)
            
        assert hasattr(result, 'success')
        assert hasattr(result, 'errors')
        assert isinstance(result.success, bool)
        assert isinstance(result.errors, list)