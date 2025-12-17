"""Shared pytest fixtures for all tests."""

import json
import socket
import tempfile
from pathlib import Path
from typing import Any

import pytest
from PIL import Image


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
        json_content: dict[str, Any] | None = None,
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
        config_name: str, custom_content: dict[str, Any] | None = None
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
                    "site": "https://site.example.com",
                },
            },
            "normpic": {
                "input_dir": "photos",
                "output_dir": "organized",
                "manifest_file": "manifest.json",
            },
            "pelican": {
                "theme": "simple",
                "content_dir": "content",
                "output_dir": "output",
            },
            "galleria": {
                "provider": {"plugin": "normpic-provider"},
                "processor": {"plugin": "thumbnail-processor"},
                "transform": {"plugin": "basic-pagination"},
                "template": {"plugin": "basic-template"},
                "css": {"plugin": "basic-css"},
                "output_dir": "output/galleries/test",
                "manifest_path": "output/pics/full/manifest.json",
            },
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
                config_name, custom_configs.get(config_name)
            )

        return configs

    return _setup_configs


@pytest.fixture
def fake_image_factory(temp_filesystem):
    """Factory for creating fake JPEG images for testing."""

    def _create_fake_image(
        filename: str,
        directory: str = "",
        color: str = "red",
        size: tuple[int, int] = (800, 600),
        use_raw_bytes: bool = False,
    ) -> Path:
        """Create a fake JPEG image file.

        Args:
            filename: Name of the image file (e.g., "IMG_001.jpg")
            directory: Directory relative to temp filesystem (default: root)
            color: PIL color name or RGB tuple for PIL images (default: "red")
            size: Image dimensions as (width, height) tuple (default: 800x600)
            use_raw_bytes: If True, create minimal JPEG bytes with fake EXIF
                          If False, create PIL-generated JPEG (default: False)

        Returns:
            Path to created image file
        """
        if directory:
            image_dir = temp_filesystem / directory
            image_dir.mkdir(parents=True, exist_ok=True)
            image_path = image_dir / filename
        else:
            image_path = temp_filesystem / filename

        if use_raw_bytes:
            # Create minimal JPEG bytes with fake EXIF (for NormPic tests)
            fake_jpeg_with_exif = (
                b"\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00"
                b"\xff\xe1\x00\x16Exif\x00\x00II*\x00\x08\x00\x00\x00"  # Fake EXIF header
                b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f"
                b"\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01"
                b"\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08"
                b"\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xd2\xcf \xff\xd9"  # End of Image
            )
            image_path.write_bytes(fake_jpeg_with_exif)
        else:
            # Create PIL-generated JPEG (for Galleria tests)
            img = Image.new("RGB", size, color=color)
            img.save(image_path, "JPEG")

        return image_path

    return _create_fake_image


@pytest.fixture
def free_port():
    """Get a free port number for testing HTTP servers."""

    def _get_free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port

    return _get_free_port


@pytest.fixture
def mock_pelican_config():
    """Mock pelican configuration for URL testing."""
    return {
        "author": "Test Author",
        "sitename": "Test Site",
        "site_url": "https://marco-chrissy.com",
        "timezone": "UTC",
        "default_lang": "en"
    }


@pytest.fixture
def mock_site_config():
    """Mock site configuration for build testing."""
    return {
        "output_dir": "output"
    }


@pytest.fixture
def shared_theme_dirs(directory_factory):
    """Create standard shared theme directory structure for testing.

    Returns:
        Dict with 'shared_templates' and 'galleria_templates' Path objects
    """
    def _create_theme_dirs():
        """Create theme directories and return paths."""
        shared_templates = directory_factory("themes/shared/templates")
        galleria_templates = directory_factory("galleria/themes/minimal/templates")

        return {
            "shared_templates": shared_templates,
            "galleria_templates": galleria_templates
        }

    return _create_theme_dirs
