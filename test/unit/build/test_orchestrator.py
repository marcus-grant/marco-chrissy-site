"""Unit tests for BuildOrchestrator."""

import pytest
from pathlib import Path

from build.orchestrator import BuildOrchestrator
from build.exceptions import BuildError


class TestBuildOrchestrator:
    """Test BuildOrchestrator functionality."""

    def test_create_build_orchestrator(self):
        """Test creating BuildOrchestrator instance."""
        orchestrator = BuildOrchestrator()
        assert orchestrator is not None

    def test_execute_complete_build(self, temp_filesystem, file_factory):
        """Test executing complete build workflow."""
        # Create config files
        site_config = {
            "output_dir": "output",
            "base_url": "https://site.example.com"
        }
        galleria_config = {
            "manifest_path": "manifest.json",
            "output_dir": "galleries",
            "thumbnail_size": 400
        }
        pelican_config = {
            "author": "Test Author",
            "sitename": "Test Site",
            "content_path": "content"
        }
        
        # Create necessary files
        manifest_data = {
            "name": "Test Gallery",
            "collection_name": "test-gallery",
            "pics": []
        }
        
        config_dir = temp_filesystem / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        file_factory("config/site.json", json_content=site_config)
        file_factory("config/galleria.json", json_content=galleria_config)
        file_factory("config/pelican.json", json_content=pelican_config)
        file_factory("manifest.json", json_content=manifest_data)
        
        # Create content for pelican
        content_dir = temp_filesystem / "content"
        content_dir.mkdir(parents=True, exist_ok=True)
        file_factory("content/test.md", content="Title: Test\n\nTest content")
        
        orchestrator = BuildOrchestrator()
        result = orchestrator.execute(config_dir=config_dir, base_dir=temp_filesystem)
        
        assert result is True

    def test_execute_missing_configs_raises_error(self, temp_filesystem):
        """Test that missing config files raise BuildError."""
        orchestrator = BuildOrchestrator()
        
        with pytest.raises(BuildError) as exc_info:
            orchestrator.execute(config_dir=temp_filesystem / "config", base_dir=temp_filesystem)
        
        assert "Build orchestration failed" in str(exc_info.value)

    def test_execute_passes_build_context_to_galleria_builder(self, temp_filesystem, file_factory):
        """Test that execute creates and passes BuildContext to GalleriaBuilder."""
        # Create config files
        site_config = {
            "output_dir": "output",
            "base_url": "https://site.example.com"
        }
        galleria_config = {
            "manifest_path": "manifest.json",
            "output_dir": "galleries",
            "thumbnail_size": 400
        }
        pelican_config = {
            "author": "Test Author",
            "sitename": "Test Site",
            "content_path": "content"
        }
        
        # Create necessary files
        manifest_data = {
            "name": "Test Gallery",
            "collection_name": "test-gallery",
            "pics": []
        }
        
        config_dir = temp_filesystem / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        file_factory("config/site.json", json_content=site_config)
        file_factory("config/galleria.json", json_content=galleria_config)
        file_factory("config/pelican.json", json_content=pelican_config)
        file_factory("manifest.json", json_content=manifest_data)
        
        # Create content for pelican
        content_dir = temp_filesystem / "content"
        content_dir.mkdir(parents=True, exist_ok=True)
        file_factory("content/test.md", content="Title: Test\n\nTest content")
        
        # Mock the galleria_builder to verify BuildContext is passed
        from unittest.mock import Mock
        orchestrator = BuildOrchestrator()
        mock_galleria_builder = Mock()
        orchestrator.galleria_builder = mock_galleria_builder
        
        result = orchestrator.execute(config_dir=config_dir, base_dir=temp_filesystem)
        
        # Verify that build was called with BuildContext (production=True by default)
        mock_galleria_builder.build.assert_called_once()
        args, kwargs = mock_galleria_builder.build.call_args
        assert len(args) >= 2  # galleria_config, base_dir
        assert "build_context" in kwargs
        assert kwargs["build_context"].production is True

    def test_execute_creates_dev_build_context_when_override_site_url_provided(self, temp_filesystem, file_factory):
        """Test that execute creates development BuildContext when override_site_url is provided."""
        # Create config files
        site_config = {
            "output_dir": "output",
            "base_url": "https://site.example.com"
        }
        galleria_config = {
            "manifest_path": "manifest.json",
            "output_dir": "galleries",
            "thumbnail_size": 400
        }
        pelican_config = {
            "author": "Test Author",
            "sitename": "Test Site",
            "content_path": "content"
        }
        
        # Create necessary files
        manifest_data = {
            "name": "Test Gallery",
            "collection_name": "test-gallery",
            "pics": []
        }
        
        config_dir = temp_filesystem / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        file_factory("config/site.json", json_content=site_config)
        file_factory("config/galleria.json", json_content=galleria_config)
        file_factory("config/pelican.json", json_content=pelican_config)
        file_factory("manifest.json", json_content=manifest_data)
        
        # Create content for pelican
        content_dir = temp_filesystem / "content"
        content_dir.mkdir(parents=True, exist_ok=True)
        file_factory("content/test.md", content="Title: Test\n\nTest content")
        
        # Mock the galleria_builder to verify BuildContext is passed
        from unittest.mock import Mock
        orchestrator = BuildOrchestrator()
        mock_galleria_builder = Mock()
        orchestrator.galleria_builder = mock_galleria_builder
        
        result = orchestrator.execute(
            config_dir=config_dir, 
            base_dir=temp_filesystem,
            override_site_url="http://localhost:8000"
        )
        
        # Verify that build was called with development BuildContext
        mock_galleria_builder.build.assert_called_once()
        args, kwargs = mock_galleria_builder.build.call_args
        assert len(args) >= 2  # galleria_config, base_dir
        assert "build_context" in kwargs
        assert kwargs["build_context"].production is False
        assert "site_url" in kwargs
        assert kwargs["site_url"] == "http://localhost:8000"