"""Galleria-specific pytest fixtures for comprehensive serve command testing."""

import json
import socket
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest
from PIL import Image

# =============================================================================
# Core Fixtures (Duplicated for Galleria Independence)
# =============================================================================

@pytest.fixture
def galleria_temp_filesystem():
    """Create a temporary directory for galleria filesystem tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def galleria_file_factory(galleria_temp_filesystem):
    """Factory for creating files in galleria temporary filesystem."""
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
        file_path = galleria_temp_filesystem / relative_path

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
def galleria_image_factory(galleria_temp_filesystem):
    """Factory for creating fake images for galleria testing."""
    def _create_fake_image(
        filename: str,
        directory: str = "",
        color: str | tuple[int, int, int] = "red",
        size: tuple[int, int] = (800, 600)
    ) -> Path:
        """Create a fake JPEG image file.

        Args:
            filename: Name of the image file (e.g., "IMG_001.jpg")
            directory: Directory relative to temp filesystem
            color: PIL color name or RGB tuple
            size: Image dimensions as (width, height) tuple

        Returns:
            Path to created image file
        """
        if directory:
            image_dir = galleria_temp_filesystem / directory
            image_dir.mkdir(parents=True, exist_ok=True)
            image_path = image_dir / filename
        else:
            image_path = galleria_temp_filesystem / filename

        # Create PIL-generated JPEG
        img = Image.new('RGB', size, color=color)
        img.save(image_path, 'JPEG')

        return image_path

    return _create_fake_image


# =============================================================================
# Galleria Config Fixtures
# =============================================================================

@pytest.fixture
def galleria_config_factory(galleria_file_factory):
    """Factory for creating galleria config files with defaults."""
    def _create_config(
        config_name: str = "galleria",
        custom_content: dict[str, Any] | None = None
    ) -> Path:
        """Create a galleria config file.

        Args:
            config_name: Name of config file (without .json extension)
            custom_content: Custom content dict, otherwise uses defaults

        Returns:
            Path to created config file
        """
        default_config = {
            "input": {
                "manifest_path": "manifest.json"
            },
            "output": {
                "directory": "gallery_output"
            },
            "pipeline": {
                "provider": {
                    "plugin": "normpic-provider",
                    "config": {}
                },
                "processor": {
                    "plugin": "thumbnail-processor",
                    "config": {
                        "thumbnail_size": 200
                    }
                },
                "transform": {
                    "plugin": "basic-pagination",
                    "config": {
                        "page_size": 10
                    }
                },
                "template": {
                    "plugin": "basic-template",
                    "config": {
                        "theme": "minimal"
                    }
                },
                "css": {
                    "plugin": "basic-css",
                    "config": {
                        "theme": "light"
                    }
                }
            }
        }

        content = custom_content if custom_content is not None else default_config
        return galleria_file_factory(f"config/{config_name}.json", json_content=content)

    return _create_config


# =============================================================================
# Manifest Factory Fixture
# =============================================================================

@pytest.fixture
def manifest_factory(galleria_file_factory):
    """Factory for creating normpic manifests for galleria testing."""
    def _create_manifest(
        collection_name: str = "test_collection",
        photos: list[dict[str, Any]] | None = None,
        filename: str = "manifest.json"
    ) -> Path:
        """Create a normpic manifest file.

        Args:
            collection_name: Name of the photo collection
            photos: List of photo dicts, uses defaults if None
            filename: Name of manifest file

        Returns:
            Path to created manifest file
        """
        if photos is None:
            photos = [
                {
                    "source_path": "source/IMG_001.jpg",
                    "dest_path": "IMG_001.jpg",
                    "hash": "abc123",
                    "size_bytes": 2048000,
                    "mtime": 1234567890
                },
                {
                    "source_path": "source/IMG_002.jpg",
                    "dest_path": "IMG_002.jpg",
                    "hash": "def456",
                    "size_bytes": 1956000,
                    "mtime": 1234567891
                }
            ]

        manifest_data = {
            "version": "0.1.0",
            "collection_name": collection_name,
            "pics": photos
        }

        return galleria_file_factory(filename, json_content=manifest_data)

    return _create_manifest


# =============================================================================
# Gallery Output Factory Fixture
# =============================================================================

@pytest.fixture
def gallery_output_factory(galleria_temp_filesystem, galleria_file_factory, galleria_image_factory):
    """Factory for creating complete gallery output structures."""
    def _create_gallery_output(
        output_dir: str = "gallery_output",
        collection_name: str = "test_gallery",
        num_pages: int = 2,
        photos_per_page: int = 2,
        include_css: bool = True,
        include_thumbnails: bool = True
    ) -> Path:
        """Create a complete gallery output directory structure.

        Args:
            output_dir: Name of output directory
            collection_name: Name of the gallery collection
            num_pages: Number of HTML pages to generate
            photos_per_page: Number of photos per page
            include_css: Whether to include CSS file
            include_thumbnails: Whether to include thumbnail images

        Returns:
            Path to created output directory
        """
        output_path = galleria_temp_filesystem / output_dir
        output_path.mkdir(parents=True, exist_ok=True)

        # Create HTML pages
        for page_num in range(1, num_pages + 1):
            page_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{collection_name} - Page {page_num}</title>
    <link rel="stylesheet" href="gallery.css">
</head>
<body>
    <h1>{collection_name}</h1>
    <div class="gallery">
"""

            # Add photo entries for this page
            start_photo = (page_num - 1) * photos_per_page + 1
            end_photo = min(start_photo + photos_per_page - 1, num_pages * photos_per_page)

            for photo_num in range(start_photo, end_photo + 1):
                page_content += f"""        <div class="photo">
            <img src="thumbnails/photo_{photo_num:03d}.webp"
                 alt="Photo {photo_num}"
                 data-full="photos/photo_{photo_num:03d}.jpg">
        </div>
"""

            page_content += """    </div>
    <nav class="pagination">
"""

            # Add pagination links
            for nav_page in range(1, num_pages + 1):
                if nav_page == page_num:
                    page_content += f'        <span class="current">{nav_page}</span>\n'
                else:
                    page_content += f'        <a href="page_{nav_page}.html">{nav_page}</a>\n'

            page_content += """    </nav>
</body>
</html>"""

            galleria_file_factory(f"{output_dir}/page_{page_num}.html", content=page_content)

        # Create CSS file if requested
        if include_css:
            css_content = """body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
    background-color: #f5f5f5;
}

h1 {
    text-align: center;
    color: #333;
    margin-bottom: 30px;
}

.gallery {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 40px;
}

.photo img {
    width: 100%;
    height: auto;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.pagination {
    text-align: center;
}

.pagination a, .pagination .current {
    display: inline-block;
    padding: 8px 16px;
    margin: 0 4px;
    text-decoration: none;
    border-radius: 4px;
}

.pagination a {
    background-color: #fff;
    color: #007bff;
    border: 1px solid #dee2e6;
}

.pagination .current {
    background-color: #007bff;
    color: white;
}"""
            galleria_file_factory(f"{output_dir}/gallery.css", content=css_content)

        # Create thumbnail images if requested
        if include_thumbnails:
            thumbnails_dir = output_path / "thumbnails"
            thumbnails_dir.mkdir(exist_ok=True)

            total_photos = num_pages * photos_per_page
            for photo_num in range(1, total_photos + 1):
                # Create thumbnail with different colors for visual distinction
                colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FECA57", "#FF9FF3"]
                color = colors[(photo_num - 1) % len(colors)]

                galleria_image_factory(
                    f"photo_{photo_num:03d}.webp",
                    directory=f"{output_dir}/thumbnails",
                    color=color,
                    size=(200, 150)
                )

        return output_path

    return _create_gallery_output


# =============================================================================
# HTTP Server Test Fixtures
# =============================================================================

@pytest.fixture
def free_port():
    """Get a free port number for testing HTTP servers."""
    def _get_free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port

    return _get_free_port


@pytest.fixture
def mock_http_server():
    """Create a mock HTTP server for testing."""
    def _create_mock_server(port: int = 8000):
        """Create a mock HTTP server that tracks requests.

        Args:
            port: Port number for the mock server

        Returns:
            Mock server object with request tracking
        """
        server = Mock()
        server.port = port
        server.host = "127.0.0.1"
        server.requests = []
        server.is_running = False

        def mock_serve_forever():
            server.is_running = True

        def mock_shutdown():
            server.is_running = False

        def mock_handle_request(path: str, method: str = "GET"):
            server.requests.append({"path": path, "method": method})

        server.serve_forever = mock_serve_forever
        server.shutdown = mock_shutdown
        server.handle_request = mock_handle_request

        return server

    return _create_mock_server


# =============================================================================
# Complete Serving Scenario Fixtures
# =============================================================================

@pytest.fixture
def complete_serving_scenario(
    galleria_config_factory,
    manifest_factory,
    gallery_output_factory,
    galleria_image_factory,
    free_port
):
    """Create a complete serving scenario with all required components."""
    def _create_scenario(
        collection_name: str = "wedding_photos",
        num_photos: int = 6,
        photos_per_page: int = 3,
        use_custom_port: bool = True
    ) -> dict[str, Any]:
        """Create complete scenario for serve command testing.

        Args:
            collection_name: Name of the photo collection
            num_photos: Total number of photos to create
            photos_per_page: Photos per gallery page
            use_custom_port: Whether to allocate a custom port

        Returns:
            Dict with all paths and configuration for testing
        """
        # Calculate pages needed
        num_pages = (num_photos + photos_per_page - 1) // photos_per_page

        # Create source images
        source_photos = []
        for i in range(1, num_photos + 1):
            photo_path = galleria_image_factory(
                f"IMG_{i:04d}.jpg",
                directory="source_photos",
                color=(255 - i * 30, i * 40, 100 + i * 20),
                size=(1200, 800)
            )
            source_photos.append({
                "source_path": str(photo_path),
                "dest_path": f"IMG_{i:04d}.jpg",
                "hash": f"hash{i:03d}",
                "size_bytes": 2048000 + i * 1000,
                "mtime": 1234567890 + i
            })

        # Create manifest
        manifest_path = manifest_factory(
            collection_name=collection_name,
            photos=source_photos
        )

        # Create gallery output
        output_path = gallery_output_factory(
            collection_name=collection_name,
            num_pages=num_pages,
            photos_per_page=photos_per_page
        )

        # Create galleria config
        config_content = {
            "input": {"manifest_path": str(manifest_path)},
            "output": {"directory": str(output_path)},
            "pipeline": {
                "provider": {"plugin": "normpic-provider", "config": {}},
                "processor": {"plugin": "thumbnail-processor", "config": {"thumbnail_size": 200}},
                "transform": {"plugin": "basic-pagination", "config": {"page_size": photos_per_page}},
                "template": {"plugin": "basic-template", "config": {"theme": "elegant"}},
                "css": {"plugin": "basic-css", "config": {"theme": "light"}}
            }
        }
        config_path = galleria_config_factory(custom_content=config_content)

        # Allocate port if requested
        port = free_port() if use_custom_port else 8000

        return {
            "collection_name": collection_name,
            "manifest_path": manifest_path,
            "config_path": config_path,
            "output_path": output_path,
            "source_photos": source_photos,
            "num_photos": num_photos,
            "num_pages": num_pages,
            "photos_per_page": photos_per_page,
            "port": port
        }

    return _create_scenario


# =============================================================================
# File Watcher Test Fixtures
# =============================================================================

@pytest.fixture
def file_watcher_scenario(galleria_config_factory, manifest_factory):
    """Create a scenario for testing file watching functionality."""
    def _create_watcher_scenario() -> dict[str, Any]:
        """Create files that can be watched for changes.

        Returns:
            Dict with paths to files that can be modified during tests
        """
        # Create initial config
        initial_config = {
            "input": {"manifest_path": "manifest.json"},
            "output": {"directory": "gallery_output"},
            "pipeline": {
                "template": {"plugin": "basic-template", "config": {"theme": "minimal"}},
                "css": {"plugin": "basic-css", "config": {"theme": "light"}}
            }
        }
        config_path = galleria_config_factory(custom_content=initial_config)

        # Create initial manifest
        initial_photos = [
            {
                "source_path": "source/photo1.jpg",
                "dest_path": "photo1.jpg",
                "hash": "initial_hash",
                "size_bytes": 1000000,
                "mtime": 1234567890
            }
        ]
        manifest_path = manifest_factory(
            collection_name="watch_test",
            photos=initial_photos
        )

        return {
            "config_path": config_path,
            "manifest_path": manifest_path,
            "initial_config": initial_config,
            "initial_photos": initial_photos
        }

    return _create_watcher_scenario
