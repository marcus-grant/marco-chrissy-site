"""Unit tests for JSON schema validation."""

from pathlib import Path

import pytest

from serializer.json import JsonConfigLoader


class TestConfigSchemas:
    """Test JSON schema validation for all config types."""

    def test_normpic_schema_validation_success(self, temp_filesystem, file_factory):
        """Test normpic schema validates correct config."""
        config_data = {
            "source_dir": "~/Pictures/wedding/full",
            "dest_dir": "output/pics/full",
            "collection_name": "wedding",
            "create_symlinks": True
        }
        config_file = file_factory("config/normpic.json", json_content=config_data)

        # Load schema (this should exist after implementation)
        schema_path = Path("config/schema/normpic.json")
        loader = JsonConfigLoader()
        schema = loader.load_config(schema_path)

        # Test validation
        loader_with_schema = JsonConfigLoader(schema=schema)
        result = loader_with_schema.load_config(config_file)
        assert result == config_data

    def test_normpic_schema_validation_failure(self, temp_filesystem, file_factory):
        """Test normpic schema rejects invalid config."""
        config_data = {
            "invalid_field": "value"
            # Missing required fields
        }
        config_file = file_factory("config/normpic.json", json_content=config_data)

        schema_path = Path("config/schema/normpic.json")
        loader = JsonConfigLoader()
        schema = loader.load_config(schema_path)

        loader_with_schema = JsonConfigLoader(schema=schema)

        with pytest.raises(Exception) as exc_info:
            loader_with_schema.load_config(config_file)

        assert "validation" in str(exc_info.value).lower()

    def test_site_schema_validation(self, temp_filesystem, file_factory):
        """Test site schema validates orchestration config."""
        config_data = {
            "output_dir": "output",
            "cdn": {
                "photos": "https://photos.example.com",
                "site": "https://site.example.com"
            }
        }
        config_file = file_factory("config/site.json", json_content=config_data)

        schema_path = Path("config/schema/site.json")
        loader = JsonConfigLoader()
        schema = loader.load_config(schema_path)

        loader_with_schema = JsonConfigLoader(schema=schema)
        result = loader_with_schema.load_config(config_file)
        assert result == config_data
