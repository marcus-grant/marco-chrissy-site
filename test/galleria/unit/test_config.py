"""Tests for Galleria configuration loading and validation."""

import json

import click
import pytest

from galleria.config import GalleriaConfig


class TestGalleriaConfig:
    """Test configuration loading and validation."""

    def test_load_valid_config(self, tmp_path):
        """Test loading a valid configuration file."""
        # Arrange
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text('{"version": "0.1.0", "collection_name": "test", "pics": []}')

        config_data = {
            "input": {"manifest_path": str(manifest_path)},
            "output": {"directory": str(tmp_path / "output")},
            "pipeline": {
                "provider": {"plugin": "normpic-provider", "config": {}},
                "processor": {"plugin": "thumbnail-processor", "config": {"size": 400}},
                "transform": {"plugin": "basic-pagination", "config": {"page_size": 10}},
                "template": {"plugin": "basic-template", "config": {"theme": "minimal"}},
                "css": {"plugin": "basic-css", "config": {"responsive": True}}
            }
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_data))

        # Act
        config = GalleriaConfig.from_file(config_path)

        # Assert
        assert config.input_manifest_path == manifest_path
        assert config.output_directory == tmp_path / "output"
        assert config.pipeline.provider.plugin == "normpic-provider"
        assert config.pipeline.processor.config["size"] == 400
        assert config.pipeline.transform.config["page_size"] == 10
        assert config.pipeline.template.config["theme"] == "minimal"
        assert config.pipeline.css.config["responsive"] is True

    def test_load_config_with_output_override(self, tmp_path):
        """Test that CLI output override works correctly."""
        # Arrange
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text('{"version": "0.1.0", "collection_name": "test", "pics": []}')

        config_data = {
            "input": {"manifest_path": str(manifest_path)},
            "output": {"directory": str(tmp_path / "original_output")},
            "pipeline": {
                "provider": {"plugin": "normpic-provider", "config": {}},
                "processor": {"plugin": "thumbnail-processor", "config": {}},
                "transform": {"plugin": "basic-pagination", "config": {}},
                "template": {"plugin": "basic-template", "config": {}},
                "css": {"plugin": "basic-css", "config": {}}
            }
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_data))
        override_output = tmp_path / "override_output"

        # Act
        config = GalleriaConfig.from_file(config_path, override_output)

        # Assert
        assert config.output_directory == override_output

    def test_load_config_missing_file(self, tmp_path):
        """Test error handling for missing config file."""
        nonexistent_config = tmp_path / "missing.json"

        with pytest.raises(click.FileError):
            GalleriaConfig.from_file(nonexistent_config)

    def test_load_config_invalid_json(self, tmp_path):
        """Test error handling for invalid JSON."""
        config_path = tmp_path / "invalid.json"
        config_path.write_text("{ invalid json content }")

        with pytest.raises(click.ClickException, match="Invalid JSON"):
            GalleriaConfig.from_file(config_path)

    def test_load_config_missing_input_section(self, tmp_path):
        """Test error handling for missing input section."""
        config_data = {
            "output": {"directory": "/tmp/output"},
            "pipeline": {}
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_data))

        with pytest.raises(click.ClickException, match="Missing required configuration section"):
            GalleriaConfig.from_file(config_path)

    def test_load_config_missing_manifest_path(self, tmp_path):
        """Test error handling for missing manifest path."""
        config_data = {
            "input": {},  # Missing manifest_path
            "output": {"directory": "/tmp/output"},
            "pipeline": {}
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_data))

        with pytest.raises(click.ClickException, match="input.manifest_path"):
            GalleriaConfig.from_file(config_path)

    def test_load_config_missing_pipeline_stage(self, tmp_path):
        """Test error handling for missing pipeline stage."""
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text('{}')

        config_data = {
            "input": {"manifest_path": str(manifest_path)},
            "output": {"directory": "/tmp/output"},
            "pipeline": {
                "provider": {"plugin": "normpic-provider", "config": {}},
                # Missing processor, transform, template, css
            }
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_data))

        with pytest.raises(click.ClickException, match="Missing required pipeline stage"):
            GalleriaConfig.from_file(config_path)

    def test_load_config_missing_plugin_name(self, tmp_path):
        """Test error handling for missing plugin name."""
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text('{}')

        config_data = {
            "input": {"manifest_path": str(manifest_path)},
            "output": {"directory": "/tmp/output"},
            "pipeline": {
                "provider": {"config": {}},  # Missing plugin name
                "processor": {"plugin": "thumbnail-processor", "config": {}},
                "transform": {"plugin": "basic-pagination", "config": {}},
                "template": {"plugin": "basic-template", "config": {}},
                "css": {"plugin": "basic-css", "config": {}}
            }
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_data))

        with pytest.raises(click.ClickException, match="Missing plugin name"):
            GalleriaConfig.from_file(config_path)

    def test_validate_paths_missing_manifest(self, tmp_path):
        """Test path validation for missing manifest file."""
        nonexistent_manifest = tmp_path / "missing_manifest.json"

        config_data = {
            "input": {"manifest_path": str(nonexistent_manifest)},
            "output": {"directory": str(tmp_path / "output")},
            "pipeline": {
                "provider": {"plugin": "normpic-provider", "config": {}},
                "processor": {"plugin": "thumbnail-processor", "config": {}},
                "transform": {"plugin": "basic-pagination", "config": {}},
                "template": {"plugin": "basic-template", "config": {}},
                "css": {"plugin": "basic-css", "config": {}}
            }
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_data))

        config = GalleriaConfig.from_file(config_path)

        with pytest.raises(click.ClickException, match="Manifest file not found"):
            config.validate_paths()

    def test_to_pipeline_config(self, tmp_path):
        """Test conversion to pipeline manager format."""
        # Arrange
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text('{}')

        config_data = {
            "input": {"manifest_path": str(manifest_path)},
            "output": {"directory": str(tmp_path / "output")},
            "pipeline": {
                "provider": {"plugin": "normpic-provider", "config": {"setting1": "value1"}},
                "processor": {"plugin": "thumbnail-processor", "config": {"size": 400}},
                "transform": {"plugin": "basic-pagination", "config": {"page_size": 10}},
                "template": {"plugin": "basic-template", "config": {"theme": "minimal"}},
                "css": {"plugin": "basic-css", "config": {"responsive": True}}
            }
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_data))

        config = GalleriaConfig.from_file(config_path)

        # Act
        pipeline_config = config.to_pipeline_config()

        # Assert
        assert pipeline_config["provider"]["setting1"] == "value1"
        assert pipeline_config["processor"]["size"] == 400
        assert pipeline_config["transform"]["page_size"] == 10
        assert pipeline_config["template"]["theme"] == "minimal"
        assert pipeline_config["css"]["responsive"] is True
