"""Unit tests for GalleriaBuilder."""

import pytest
from pathlib import Path

from build.galleria_builder import GalleriaBuilder
from build.exceptions import GalleriaError


class TestGalleriaBuilder:
    """Test GalleriaBuilder functionality."""

    def test_create_galleria_builder(self):
        """Test creating GalleriaBuilder instance."""
        builder = GalleriaBuilder()
        assert builder is not None

    def test_build_galleria(self, temp_filesystem, file_factory):
        """Test building galleria with valid config."""
        galleria_config = {
            "manifest_path": "manifest.json",
            "output_dir": "galleries",
            "thumbnail_size": 400,
            "photos_per_page": 60,
            "theme": "minimal",
            "quality": 85
        }
        
        # Create a mock manifest file for the test
        manifest_data = {
            "name": "Test Gallery",
            "collection_name": "test-gallery",
            "description": "Test gallery description",
            "pics": []
        }
        manifest_file = file_factory("manifest.json", json_content=manifest_data)
        
        builder = GalleriaBuilder()
        result = builder.build(galleria_config, temp_filesystem)
        
        assert result is True

    def test_build_galleria_missing_manifest_raises_error(self, temp_filesystem):
        """Test that missing manifest file raises GalleriaError."""
        galleria_config = {
            "manifest_path": "missing.json",
            "output_dir": "galleries"
        }
        
        builder = GalleriaBuilder()
        
        with pytest.raises(GalleriaError) as exc_info:
            builder.build(galleria_config, temp_filesystem)
        
        assert "missing.json" in str(exc_info.value) or "not found" in str(exc_info.value)