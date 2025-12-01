"""Unit tests for JSON config loader with schema validation."""

import pytest

from serializer.exceptions import ConfigLoadError, ConfigValidationError
from serializer.json import JsonConfigLoader


class TestJsonConfigLoader:
    """Test JSON config loader functionality."""

    def test_load_valid_json_config(self, temp_filesystem, file_factory):
        """Test loading valid JSON config file."""
        config_data = {
            "source_dir": "~/Pictures/wedding/full",
            "dest_dir": "output/pics/full",
            "collection_name": "wedding",
            "create_symlinks": True,
        }
        config_file = file_factory("config/normpic.json", json_content=config_data)

        loader = JsonConfigLoader()
        result = loader.load_config(config_file)

        assert result == config_data

    def test_load_config_with_schema_validation(self, temp_filesystem, file_factory):
        """Test loading config with schema validation enabled."""
        config_data = {
            "source_dir": "~/Pictures/wedding/full",
            "dest_dir": "output/pics/full",
            "collection_name": "wedding",
            "create_symlinks": True,
        }
        config_file = file_factory("config/normpic.json", json_content=config_data)

        # Mock schema that validates our config structure
        schema = {
            "type": "object",
            "properties": {
                "source_dir": {"type": "string"},
                "dest_dir": {"type": "string"},
                "collection_name": {"type": "string"},
                "create_symlinks": {"type": "boolean"},
            },
            "required": ["source_dir", "dest_dir", "collection_name"],
        }

        loader = JsonConfigLoader(schema=schema)
        result = loader.load_config(config_file)

        assert result == config_data

    def test_config_file_not_found(self, temp_filesystem):
        """Test loading non-existent config file raises appropriate error."""
        non_existent_file = temp_filesystem / "config" / "missing.json"

        loader = JsonConfigLoader()

        with pytest.raises(ConfigLoadError) as exc_info:
            loader.load_config(non_existent_file)

        assert "not found" in str(exc_info.value).lower()
        assert str(non_existent_file) in str(exc_info.value)

    def test_malformed_json_file(self, temp_filesystem, file_factory):
        """Test loading malformed JSON file raises appropriate error."""
        config_file = file_factory(
            "config/invalid.json", content="{ invalid json content"
        )

        loader = JsonConfigLoader()

        with pytest.raises(ConfigLoadError) as exc_info:
            loader.load_config(config_file)

        assert "json" in str(exc_info.value).lower()
        assert (
            "parse" in str(exc_info.value).lower()
            or "decode" in str(exc_info.value).lower()
        )

    def test_schema_validation_failure_missing_required_field(
        self, temp_filesystem, file_factory
    ):
        """Test schema validation fails with missing required fields."""
        config_data = {
            "collection_name": "wedding"
            # Missing required source_dir and dest_dir
        }
        config_file = file_factory("config/normpic.json", json_content=config_data)

        schema = {
            "type": "object",
            "properties": {
                "source_dir": {"type": "string"},
                "dest_dir": {"type": "string"},
                "collection_name": {"type": "string"},
                "create_symlinks": {"type": "boolean"},
            },
            "required": ["source_dir", "dest_dir", "collection_name"],
        }

        loader = JsonConfigLoader(schema=schema)

        with pytest.raises(ConfigValidationError) as exc_info:
            loader.load_config(config_file)

        error_msg = str(exc_info.value).lower()
        assert "validation" in error_msg
        assert "source_dir" in error_msg or "dest_dir" in error_msg

    def test_schema_validation_failure_wrong_type(self, temp_filesystem, file_factory):
        """Test schema validation fails with wrong field types."""
        config_data = {
            "source_dir": "~/Pictures/wedding/full",
            "dest_dir": "output/pics/full",
            "collection_name": "wedding",
            "create_symlinks": "invalid_boolean",  # Should be boolean
        }
        config_file = file_factory("config/normpic.json", json_content=config_data)

        schema = {
            "type": "object",
            "properties": {
                "source_dir": {"type": "string"},
                "dest_dir": {"type": "string"},
                "collection_name": {"type": "string"},
                "create_symlinks": {"type": "boolean"},
            },
            "required": ["source_dir", "dest_dir", "collection_name"],
        }

        loader = JsonConfigLoader(schema=schema)

        with pytest.raises(ConfigValidationError) as exc_info:
            loader.load_config(config_file)

        error_msg = str(exc_info.value).lower()
        assert "validation" in error_msg
        assert "create_symlinks" in error_msg

    def test_load_without_schema_validation(self, temp_filesystem, file_factory):
        """Test loading config without schema validation allows invalid data."""
        config_data = {"invalid_field": "value", "create_symlinks": "invalid_boolean"}
        config_file = file_factory("config/normpic.json", json_content=config_data)

        loader = JsonConfigLoader()  # No schema provided
        result = loader.load_config(config_file)

        assert result == config_data

    def test_schema_validation_provides_meaningful_error_messages(
        self, temp_filesystem, file_factory
    ):
        """Test that schema validation errors contain meaningful context."""
        config_data = {
            "source_dir": 123,  # Wrong type
            "dest_dir": "output/pics/full",
            # Missing collection_name
            "create_symlinks": "not_a_boolean",  # Wrong type
        }
        config_file = file_factory("config/normpic.json", json_content=config_data)

        schema = {
            "type": "object",
            "properties": {
                "source_dir": {"type": "string"},
                "dest_dir": {"type": "string"},
                "collection_name": {"type": "string"},
                "create_symlinks": {"type": "boolean"},
            },
            "required": ["source_dir", "dest_dir", "collection_name"],
        }

        loader = JsonConfigLoader(schema=schema)

        with pytest.raises(ConfigValidationError) as exc_info:
            loader.load_config(config_file)

        error_msg = str(exc_info.value)
        # Should contain file path for context
        assert str(config_file) in error_msg
        # Should reference the validation issue
        assert "validation" in error_msg.lower()

    def test_empty_json_file(self, temp_filesystem, file_factory):
        """Test loading empty JSON file."""
        config_file = file_factory("config/empty.json", content="")

        loader = JsonConfigLoader()

        with pytest.raises(ConfigLoadError) as exc_info:
            loader.load_config(config_file)

        assert "json" in str(exc_info.value).lower()

    def test_null_json_content(self, temp_filesystem, file_factory):
        """Test loading JSON file with null content."""
        config_file = file_factory("config/null.json", content="null")

        loader = JsonConfigLoader()
        result = loader.load_config(config_file)

        assert result is None
