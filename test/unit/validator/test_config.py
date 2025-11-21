"""Unit tests for config validation functionality."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestConfigValidator:
    """Test configuration file validation."""

    def test_config_validator_can_be_imported(self):
        """Test that config validator module can be imported."""
        from validator.config import ConfigValidator
        assert ConfigValidator is not None

    def test_config_validator_checks_required_files(self):
        """Test that config validator checks for required config files."""
        from validator.config import ConfigValidator
        
        validator = ConfigValidator()
        
        # Should check for these config files
        required_files = [
            "config/site.json",
            "config/normpic.json", 
            "config/pelican.json",
            "config/galleria.json"
        ]
        
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            result = validator.validate_config_files()
            
        assert result.success is True
        assert len(result.errors) == 0

    def test_config_validator_fails_on_missing_files(self):
        """Test that config validator fails when required files are missing."""
        from validator.config import ConfigValidator
        
        validator = ConfigValidator()
        
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = False  # All files missing
            result = validator.validate_config_files()
            
        assert result.success is False
        assert len(result.errors) > 0
        assert any("missing" in error.lower() for error in result.errors)

    def test_config_validator_result_has_required_attributes(self):
        """Test that validation result has success and errors attributes."""
        from validator.config import ConfigValidator
        
        validator = ConfigValidator()
        
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            result = validator.validate_config_files()
            
        assert hasattr(result, 'success')
        assert hasattr(result, 'errors')
        assert isinstance(result.success, bool)
        assert isinstance(result.errors, list)