"""Unit tests for JSON schema validation."""


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

        # Create mock schema instead of loading from filesystem
        mock_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["source_dir", "dest_dir", "collection_name"],
            "properties": {
                "source_dir": {"type": "string"},
                "dest_dir": {"type": "string"},
                "collection_name": {"type": "string"},
                "create_symlinks": {"type": "boolean"}
            }
        }

        # Test validation with mock schema
        loader_with_schema = JsonConfigLoader(schema=mock_schema)
        result = loader_with_schema.load_config(config_file)
        assert result == config_data

    def test_normpic_schema_validation_failure(self, temp_filesystem, file_factory):
        """Test normpic schema rejects invalid config."""
        config_data = {
            "invalid_field": "value"
            # Missing required fields
        }
        config_file = file_factory("config/normpic.json", json_content=config_data)

        # Use same mock schema as success test
        mock_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["source_dir", "dest_dir", "collection_name"],
            "properties": {
                "source_dir": {"type": "string"},
                "dest_dir": {"type": "string"},
                "collection_name": {"type": "string"},
                "create_symlinks": {"type": "boolean"}
            }
        }

        loader_with_schema = JsonConfigLoader(schema=mock_schema)

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

        # Create mock schema instead of loading from filesystem
        mock_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["output_dir", "cdn"],
            "properties": {
                "output_dir": {"type": "string"},
                "cdn": {
                    "type": "object",
                    "required": ["photos", "site"],
                    "properties": {
                        "photos": {"type": "string"},
                        "site": {"type": "string"}
                    }
                }
            }
        }

        loader_with_schema = JsonConfigLoader(schema=mock_schema)
        result = loader_with_schema.load_config(config_file)
        assert result == config_data

    def test_pelican_schema_validation_success(self, temp_filesystem, file_factory):
        """Test pelican schema validates correct config."""
        config_data = {
            "theme": "minimal",
            "site_url": "https://example.com",
            "author": "Test Author",
            "sitename": "Test Site"
        }
        config_file = file_factory("config/pelican.json", json_content=config_data)

        # Create mock schema instead of loading from filesystem
        mock_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["theme", "site_url", "author", "sitename"],
            "properties": {
                "theme": {"type": "string"},
                "site_url": {"type": "string"},
                "author": {"type": "string"},
                "sitename": {"type": "string"}
            }
        }

        loader_with_schema = JsonConfigLoader(schema=mock_schema)
        result = loader_with_schema.load_config(config_file)
        assert result == config_data

    def test_pelican_schema_validation_failure(self, temp_filesystem, file_factory):
        """Test pelican schema rejects invalid config."""
        config_data = {
            "invalid_field": "value"
            # Missing required fields like theme, site_url
        }
        config_file = file_factory("config/pelican.json", json_content=config_data)

        # Use same mock schema as success test
        mock_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["theme", "site_url", "author", "sitename"],
            "properties": {
                "theme": {"type": "string"},
                "site_url": {"type": "string"},
                "author": {"type": "string"},
                "sitename": {"type": "string"}
            }
        }

        loader_with_schema = JsonConfigLoader(schema=mock_schema)

        with pytest.raises(Exception) as exc_info:
            loader_with_schema.load_config(config_file)

        assert "validation" in str(exc_info.value).lower()

    def test_galleria_schema_validation_success(self, temp_filesystem, file_factory):
        """Test galleria schema validates correct config."""
        config_data = {
            "manifest_path": "/home/user/Photos/wedding/manifest.json",
            "output_dir": "output/galleries/wedding",
            "thumbnail_size": 400,
            "photos_per_page": 60,
            "theme": "minimal",
            "quality": 85
        }
        config_file = file_factory("config/galleria.json", json_content=config_data)

        # Create mock schema instead of loading from filesystem
        mock_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["manifest_path", "output_dir"],
            "properties": {
                "manifest_path": {"type": "string"},
                "output_dir": {"type": "string"},
                "thumbnail_size": {"type": "integer"},
                "photos_per_page": {"type": "integer"},
                "theme": {"type": "string"},
                "quality": {"type": "integer"}
            }
        }

        loader_with_schema = JsonConfigLoader(schema=mock_schema)
        result = loader_with_schema.load_config(config_file)
        assert result == config_data

    def test_galleria_schema_validation_failure(self, temp_filesystem, file_factory):
        """Test galleria schema rejects invalid config."""
        config_data = {
            "invalid_field": "value"
            # Missing required fields like manifest_path, output_dir
        }
        config_file = file_factory("config/galleria.json", json_content=config_data)

        # Use same mock schema as success test
        mock_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["manifest_path", "output_dir"],
            "properties": {
                "manifest_path": {"type": "string"},
                "output_dir": {"type": "string"},
                "thumbnail_size": {"type": "integer"},
                "photos_per_page": {"type": "integer"},
                "theme": {"type": "string"},
                "quality": {"type": "integer"}
            }
        }

        loader_with_schema = JsonConfigLoader(schema=mock_schema)

        with pytest.raises(Exception) as exc_info:
            loader_with_schema.load_config(config_file)

        assert "validation" in str(exc_info.value).lower()
