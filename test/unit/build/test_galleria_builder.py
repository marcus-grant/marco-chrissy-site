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

    def test_build_galleria_accepts_build_context_parameters(self, temp_filesystem, file_factory):
        """Test that GalleriaBuilder can accept BuildContext and site_url parameters."""
        from build.context import BuildContext

        galleria_config = {
            "manifest_path": "manifest.json",
            "output_dir": "galleries",
        }
        
        # Create a mock manifest file
        manifest_data = {
            "name": "Test Gallery", 
            "collection_name": "test-gallery",
            "description": "Test gallery description",
            "pics": [
                {
                    "source_path": "photo1.jpg",
                    "dest_path": str(temp_filesystem / "pics" / "photo1.jpg"),
                    "hash": "abcd1234"
                }
            ]
        }
        manifest_file = file_factory("manifest.json", json_content=manifest_data)
        
        builder = GalleriaBuilder()
        build_context = BuildContext(production=False)
        site_url = "http://127.0.0.1:8000"
        
        # This should not raise an error - method should accept these parameters
        result = builder.build(
            galleria_config, 
            temp_filesystem, 
            build_context=build_context, 
            site_url=site_url
        )
        
        assert result is True

    def test_build_galleria_passes_build_context_in_plugin_metadata(self, temp_filesystem, file_factory):
        """Test that GalleriaBuilder passes BuildContext via PluginContext metadata to plugins."""
        from build.context import BuildContext
        from unittest.mock import patch, MagicMock

        galleria_config = {
            "manifest_path": "manifest.json",
            "output_dir": "galleries",
        }
        
        # Create a mock manifest file
        manifest_data = {
            "name": "Test Gallery",
            "collection_name": "test-gallery", 
            "description": "Test gallery description",
            "pics": [
                {
                    "source_path": "photo1.jpg",
                    "dest_path": str(temp_filesystem / "pics" / "photo1.jpg"),
                    "hash": "abcd1234"
                }
            ]
        }
        manifest_file = file_factory("manifest.json", json_content=manifest_data)
        
        builder = GalleriaBuilder()
        build_context = BuildContext(production=True)
        site_url = "https://cdn.example.com"
        
        # Mock the pipeline to capture the context passed to plugins
        captured_context = None
        
        def capture_context(stages, context):
            nonlocal captured_context
            captured_context = context
            # Return a mock successful result
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.output_data = {"html_files": [], "css_files": []}
            return mock_result
        
        with patch('galleria.manager.pipeline.PipelineManager.execute_stages', side_effect=capture_context):
            result = builder.build(
                galleria_config,
                temp_filesystem,
                build_context=build_context,
                site_url=site_url
            )
        
        # Verify that BuildContext was passed in metadata
        assert captured_context is not None
        assert captured_context.metadata["build_context"] == build_context
        assert captured_context.metadata["site_url"] == site_url
        assert result is True

    def test_build_galleria_includes_shared_templates(self, temp_filesystem, file_factory, directory_factory):
        """Test that Galleria includes shared templates in generated HTML."""
        # Create shared template
        directory_factory("themes/shared/templates")
        file_factory(
            "themes/shared/templates/navbar.html",
            '<nav id="test-shared-navbar"><a href="/">Home</a></nav>'
        )
        
        galleria_config = {
            "manifest_path": "manifest.json",
            "output_dir": "galleries/test",
            "theme": "minimal",
            "SHARED_THEME_PATH": "themes/shared"
        }
        
        # Create manifest with one photo
        manifest_data = {
            "name": "Test Gallery",
            "collection_name": "test-gallery",
            "description": "Test gallery", 
            "pics": [
                {
                    "source_path": "photo1.jpg",
                    "dest_path": "photo1.jpg",
                    "hash": "abcd1234"
                }
            ]
        }
        file_factory("manifest.json", json_content=manifest_data)
        
        builder = GalleriaBuilder()
        result = builder.build(galleria_config, temp_filesystem)
        assert result, "Galleria build should succeed"
        
        # Check generated HTML contains shared navbar
        output_html = temp_filesystem / "galleries" / "test" / "page_1.html"
        if output_html.exists():
            html_content = output_html.read_text()
            assert 'id="test-shared-navbar"' in html_content, "Generated HTML should contain shared navbar"

    def test_build_galleria_includes_shared_css(self, temp_filesystem, file_factory, directory_factory):
        """Test that Galleria copies and links shared CSS files."""
        # Create shared CSS file
        directory_factory("themes/shared/static/css")
        file_factory(
            "themes/shared/static/css/shared.css",
            '.shared-nav { background: #ff00ff; color: #00ff00; }'
        )
        
        galleria_config = {
            "manifest_path": "manifest.json",
            "output_dir": "galleries/test",
            "theme": "minimal",
            "SHARED_THEME_PATH": "themes/shared"
        }
        
        # Create manifest with one photo
        manifest_data = {
            "name": "Test Gallery",
            "collection_name": "test-gallery",
            "pics": [{"source_path": "photo1.jpg", "dest_path": "photo1.jpg", "hash": "abcd1234"}]
        }
        file_factory("manifest.json", json_content=manifest_data)
        
        builder = GalleriaBuilder()
        result = builder.build(galleria_config, temp_filesystem)
        assert result, "Galleria build should succeed"
        
        # Check CSS file was copied to output
        output_css = temp_filesystem / "galleries" / "test" / "shared.css"
        assert output_css.exists(), f"Shared CSS should be copied to {output_css}"
        
        css_content = output_css.read_text()
        assert 'background: #ff00ff' in css_content, "CSS content should be preserved"
        
        # Check HTML references shared CSS
        output_html = temp_filesystem / "galleries" / "test" / "page_1.html"
        if output_html.exists():
            html_content = output_html.read_text()
            assert 'shared.css' in html_content, "Generated HTML should reference shared.css"