"""Unit tests for PelicanBuilder."""

import pytest
from pathlib import Path

from build.pelican_builder import PelicanBuilder
from build.exceptions import PelicanError


class TestPelicanBuilder:
    """Test PelicanBuilder functionality."""

    def test_create_pelican_builder(self):
        """Test creating PelicanBuilder instance."""
        builder = PelicanBuilder()
        assert builder is not None

    def test_build_pelican_site(self, temp_filesystem, file_factory):
        """Test building pelican site with valid configs."""
        site_config = {
            "output_dir": "output"
        }
        pelican_config = {
            "author": "Test Author",
            "sitename": "Test Site",
            "content_path": "content",
            "theme": "notmyidea"
        }
        
        # Create content directory and a sample page
        content_dir = temp_filesystem / "content"
        content_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a simple markdown page
        page_content = """Title: Test Page
Date: 2023-01-01
Category: test

This is a test page.
"""
        page_file = file_factory("content/test.md", content=page_content)
        
        builder = PelicanBuilder()
        result = builder.build(site_config, pelican_config, temp_filesystem)
        
        assert result is True

    def test_build_pelican_invalid_config_raises_error(self, temp_filesystem):
        """Test that invalid pelican config raises PelicanError."""
        site_config = {"output_dir": "output"}
        pelican_config = {
            "author": "Test Author",
            "sitename": "Test Site",
            "content_path": "/invalid/path/that/cannot/be/created",  # This should cause an error
            "theme": "invalid-theme-name"
        }
        
        builder = PelicanBuilder()
        
        with pytest.raises(PelicanError) as exc_info:
            builder.build(site_config, pelican_config, temp_filesystem)
        
        assert "Pelican generation failed" in str(exc_info.value)