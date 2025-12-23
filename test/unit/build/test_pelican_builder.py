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

    def test_build_configures_shared_theme_paths(self, shared_theme_dirs, file_factory, mock_site_config, config_file_factory):
        """Test that build configures Pelican to use shared theme paths when SHARED_THEME_PATH is provided."""
        from unittest.mock import patch
        
        # Use shared_theme_dirs fixture to create standard shared theme structure
        theme_dirs = shared_theme_dirs()
        shared_templates = theme_dirs["shared_templates"]
        
        # Create shared navbar using file_factory
        navbar_template = file_factory(
            "themes/shared/templates/navbar.html",
            '<nav class="shared-nav">Test Navbar</nav>'
        )
        
        # Create pelican config with shared theme path using config_file_factory
        pelican_config_path = config_file_factory("pelican", {
            "author": "Test Author", 
            "sitename": "Test Site",
            "content_path": "content",
            "SHARED_THEME_PATH": str(shared_templates.parent)  # Point to themes/shared dir
        })
        
        # Load the config for the test
        import json
        with open(pelican_config_path) as f:
            pelican_config = json.load(f)
        
        # Create content with shared template include using file_factory
        page_content = """Title: Test Page
Date: 2023-01-01

Test content with navbar: {% include 'navbar.html' %}
"""
        file_factory("content/test.md", content=page_content)
        
        builder = PelicanBuilder()
        
        with patch('build.pelican_builder.pelican.Pelican') as mock_pelican_class:
            with patch('build.pelican_builder.configure_settings') as mock_configure:
                mock_configure.return_value = {}
                mock_pelican_class.return_value.run.return_value = None
                
                # Get temp filesystem from fixture (available via shared_theme_dirs)
                temp_dir = shared_templates.parents[1]  # Go up to get base temp dir
                
                result = builder.build(mock_site_config, pelican_config, temp_dir)
                
                # Verify configure_settings was called with shared template paths
                mock_configure.assert_called_once()
                settings_dict = mock_configure.call_args[0][0]
                
                # Should include shared template paths in JINJA_ENVIRONMENT settings
                assert 'JINJA_ENVIRONMENT' in settings_dict, "JINJA_ENVIRONMENT should be configured for shared templates"
                jinja_env = settings_dict['JINJA_ENVIRONMENT']
                
                # Check that shared templates directory is in the loader search paths
                loader_search_paths = jinja_env['loader'].searchpath
                assert str(shared_templates) in loader_search_paths, "Shared template path should be in Jinja loader search paths"
                assert result is True

    def test_build_uses_proper_template_loader_configuration(self, shared_theme_dirs, file_factory, mock_site_config, config_file_factory):
        """Test that build uses configure_pelican_shared_templates for proper template precedence."""
        from unittest.mock import patch, Mock
        
        # Use shared_theme_dirs fixture to create standard shared theme structure
        theme_dirs = shared_theme_dirs()
        shared_templates = theme_dirs["shared_templates"]
        
        # Create pelican config with shared theme path
        pelican_config_path = config_file_factory("pelican", {
            "author": "Test Author", 
            "sitename": "Test Site",
            "content_path": "content",
            "theme": "minimal",  # Add theme config
            "SHARED_THEME_PATH": str(shared_templates.parent)  # Point to themes/shared dir
        })
        
        # Load the config for the test
        import json
        with open(pelican_config_path) as f:
            pelican_config = json.load(f)
        
        builder = PelicanBuilder()
        temp_dir = shared_templates.parents[1]  # Go up to get base temp dir
        
        # Mock configure_pelican_shared_templates to verify it's called
        with patch('build.pelican_builder.configure_pelican_shared_templates') as mock_configure_shared:
            with patch('build.pelican_builder.pelican.Pelican') as mock_pelican_class:
                with patch('build.pelican_builder.configure_settings') as mock_configure:
                    # Mock configure_pelican_shared_templates to return expected paths
                    mock_configure_shared.return_value = [str(shared_templates), "themes/minimal/templates"]
                    mock_configure.return_value = {}
                    mock_pelican_class.return_value.run.return_value = None
                    
                    result = builder.build(mock_site_config, pelican_config, temp_dir)
                    
                    # Verify configure_pelican_shared_templates was called
                    mock_configure_shared.assert_called_once()
                    # Should be called with a config file path (can be temporary file)
                    call_args = mock_configure_shared.call_args[0]
                    assert call_args[0].endswith('.json'), "Should be called with a JSON config file"
                    assert result is True

    def test_build_copies_shared_css_files_to_theme_output(self, temp_filesystem, file_factory, directory_factory):
        """Test that Pelican copies shared CSS files from themes/shared/static/css/ to output/theme/css/."""
        # Create shared CSS file
        directory_factory("themes/shared/static/css")
        file_factory(
            "themes/shared/static/css/shared.css",
            '.shared-nav { background: #ff00ff; color: #00ff00; }'
        )
        
        # Create minimal content
        directory_factory("content")
        file_factory("content/test.md", """Title: Test CSS
Date: 2023-01-01

# Test Page
Test content.
""")
        
        site_config = {"output_dir": "output"}
        pelican_config = {
            "author": "Test Author",
            "sitename": "Test Site", 
            "content_path": "content",
            "SHARED_THEME_PATH": "themes/shared",
            "theme": "notmyidea"
        }
        
        builder = PelicanBuilder()
        result = builder.build(site_config, pelican_config, temp_filesystem)
        assert result, "Pelican build should succeed"
        
        # Check that shared CSS file was copied to theme output
        output_css = temp_filesystem / "output" / "theme" / "css" / "shared.css"
        assert output_css.exists(), f"Shared CSS should be copied to {output_css}"
        
        css_content = output_css.read_text()
        assert 'background: #ff00ff' in css_content, "CSS content should be preserved"


    def test_build_configures_css_file_for_shared_css(self, temp_filesystem, file_factory, directory_factory, theme_factory):
        """Test that Pelican configures CSS_FILE when shared CSS exists."""
        # Create main theme (required for Pelican to work)
        theme_factory("notmyidea")
        
        # Create shared theme with CSS  
        theme_factory("shared", css_files={"shared.css": ".shared-nav { background: #ff00ff; }"})
        
        # Create content
        directory_factory("content")
        file_factory("content/test.md", """Title: Test
Date: 2023-01-01

Test content.""")
        
        site_config = {"output_dir": "output"}
        pelican_config = {
            "author": "Test Author",
            "sitename": "Test Site", 
            "content_path": "content",
            "theme": "themes/notmyidea",
            "THEME_TEMPLATES_OVERRIDES": "themes/shared"
        }
        
        builder = PelicanBuilder()
        result = builder.build(site_config, pelican_config, temp_filesystem)
        assert result, "Build should succeed"
        
        # Check generated HTML contains CSS reference
        output_html = temp_filesystem / "output" / "test.html"
        if output_html.exists():
            html_content = output_html.read_text()
            assert 'shared.css' in html_content, "HTML should reference shared.css"

