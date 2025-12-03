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


class TestPelicanBuilderURLOverride:
    """Test PelicanBuilder URL override functionality."""

    def test_build_uses_override_url_when_provided(self, mock_site_config, mock_pelican_config, temp_filesystem):
        """Test build uses override URL when provided."""
        from unittest.mock import Mock, patch
        
        override_url = "http://127.0.0.1:8000"
        builder = PelicanBuilder()
        
        with patch('build.pelican_builder.pelican.Pelican') as mock_pelican_class:
            mock_pelican_instance = Mock()
            mock_pelican_class.return_value = mock_pelican_instance
            
            with patch('build.pelican_builder.configure_settings') as mock_configure:
                mock_configure.return_value = {}
                
                result = builder.build(
                    mock_site_config,
                    mock_pelican_config, 
                    temp_filesystem,
                    override_site_url=override_url
                )
                
                # Should call configure_settings with override URL
                mock_configure.assert_called_once()
                settings_dict = mock_configure.call_args[0][0]
                assert settings_dict['SITEURL'] == override_url
                assert result is True