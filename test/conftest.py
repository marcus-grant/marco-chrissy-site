"""Shared pytest fixtures for all tests."""

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def temp_filesystem():
    """Create a temporary directory for filesystem tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def file_factory(temp_filesystem):
    """Factory for creating files in temporary filesystem."""
    def _create_file(
        relative_path: str,
        content: str | None = None,
        json_content: dict[str, Any] | None = None
    ) -> Path:
        """Create a file with given content.
        
        Args:
            relative_path: Path relative to temp filesystem
            content: String content for file
            json_content: Dict to serialize as JSON (takes precedence over content)
            
        Returns:
            Path to created file
        """
        file_path = temp_filesystem / relative_path

        # Ensure parent directories exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        if json_content is not None:
            file_path.write_text(json.dumps(json_content, indent=2))
        elif content is not None:
            file_path.write_text(content)
        else:
            file_path.touch()  # Create empty file

        return file_path

    return _create_file


@pytest.fixture
def directory_factory(temp_filesystem):
    """Factory for creating directories in temporary filesystem."""
    def _create_directory(relative_path: str) -> Path:
        """Create a directory structure.
        
        Args:
            relative_path: Path relative to temp filesystem
            
        Returns:
            Path to created directory
        """
        dir_path = temp_filesystem / relative_path
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path

    return _create_directory


@pytest.fixture
def config_file_factory(file_factory):
    """Factory for creating config files with standard content."""
    def _create_config(
        config_name: str,
        custom_content: dict[str, Any] | None = None
    ) -> Path:
        """Create a config file with default or custom content.
        
        Args:
            config_name: Name of config (site, normpic, pelican, galleria)
            custom_content: Custom content dict, otherwise uses defaults
            
        Returns:
            Path to created config file
        """
        defaults = {
            "site": {
                "output_dir": "output",
                "base_url": "https://example.com",
                "cdn": {
                    "photos": "https://photos.example.com",
                    "site": "https://site.example.com"
                }
            },
            "normpic": {
                "input_dir": "photos",
                "output_dir": "organized",
                "manifest_file": "manifest.json"
            },
            "pelican": {
                "theme": "simple",
                "content_dir": "content",
                "output_dir": "output"
            },
            "galleria": {
                "provider": {"plugin": "normpic-provider"},
                "processor": {"plugin": "thumbnail-processor"},
                "transform": {"plugin": "basic-pagination"},
                "template": {"plugin": "basic-template"},
                "css": {"plugin": "basic-css"}
            }
        }

        content = custom_content or defaults.get(config_name, {})
        return file_factory(f"config/{config_name}.json", json_content=content)

    return _create_config


@pytest.fixture
def full_config_setup(config_file_factory, directory_factory):
    """Create a complete config directory setup with all required files."""
    def _setup_configs(custom_configs: dict[str, dict[str, Any]] | None = None):
        """Create all required config files.
        
        Args:
            custom_configs: Dict of {config_name: custom_content} overrides
            
        Returns:
            Dict of {config_name: Path} for all created configs
        """
        custom_configs = custom_configs or {}

        # Ensure config directory exists
        directory_factory("config")

        configs = {}
        for config_name in ["site", "normpic", "pelican", "galleria"]:
            configs[config_name] = config_file_factory(
                config_name,
                custom_configs.get(config_name)
            )

        return configs

    return _setup_configs
