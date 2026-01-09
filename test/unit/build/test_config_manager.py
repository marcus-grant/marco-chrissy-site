"""Unit tests for ConfigManager."""

import pytest

from build.config_manager import ConfigManager
from build.exceptions import ConfigError


class TestConfigManager:
    """Test ConfigManager functionality."""

    def test_load_site_config(self, temp_filesystem, file_factory):
        """Test loading site configuration."""
        config_data = {
            "output_dir": "output",
            "base_url": "https://site.example.com"
        }
        config_file = file_factory("config/site.json", json_content=config_data)
        
        manager = ConfigManager(config_dir=temp_filesystem / "config")
        result = manager.load_site_config()
        
        assert result == config_data

    def test_load_galleria_config(self, temp_filesystem, file_factory):
        """Test loading galleria configuration."""
        config_data = {
            "manifest_path": "/home/user/Photos/wedding/manifest.json",
            "output_dir": "output/galleries/wedding",
            "thumbnail_size": 400,
            "photos_per_page": 60,
            "theme": "minimal"
        }
        config_file = file_factory("config/galleria.json", json_content=config_data)
        
        manager = ConfigManager(config_dir=temp_filesystem / "config")
        result = manager.load_galleria_config()
        
        assert result == config_data

    def test_load_pelican_config(self, temp_filesystem, file_factory):
        """Test loading pelican configuration."""
        config_data = {
            "sitename": "Marco & Chrissy",
            "author": "Marco & Chrissy",
            "siteurl": "https://example.com",
            "content_path": "content",
            "output_path": "output",
            "theme": "minimal"
        }
        config_file = file_factory("config/pelican.json", json_content=config_data)
        
        manager = ConfigManager(config_dir=temp_filesystem / "config")
        result = manager.load_pelican_config()
        
        assert result == config_data

    def test_load_normpic_config(self, temp_filesystem, file_factory):
        """Test loading normpic configuration."""
        config_data = {
            "source_dir": "~/Pictures/wedding/full",
            "dest_dir": "output/pics/full",
            "collection_name": "wedding",
            "create_symlinks": True
        }
        config_file = file_factory("config/normpic.json", json_content=config_data)
        
        manager = ConfigManager(config_dir=temp_filesystem / "config")
        result = manager.load_normpic_config()
        
        assert result == config_data

    def test_load_config_missing_file_raises_config_error(self, temp_filesystem):
        """Test that missing config file raises ConfigError."""
        manager = ConfigManager(config_dir=temp_filesystem / "config")
        
        with pytest.raises(ConfigError) as exc_info:
            manager.load_site_config()
        
        assert "site.json" in str(exc_info.value)
        assert "not found" in str(exc_info.value)

    def test_load_deploy_config(self, temp_filesystem, file_factory):
        """Test loading deploy configuration with env var names."""
        # Use arbitrary test env var names - NEVER production names in tests
        config_data = {
            "photo_password_env_var": "TEST_PHOTO_PASS",
            "site_password_env_var": "TEST_SITE_PASS",
            "photo_zone_name": "test-photo-zone",
            "site_zone_name": "test-site-zone",
            "region": ""
        }
        config_file = file_factory("config/deploy.json", json_content=config_data)
        
        manager = ConfigManager(config_dir=temp_filesystem / "config")
        result = manager.load_deploy_config()
        
        assert result == config_data
        # Verify config contains arbitrary test names, not production env var names
        assert result["photo_password_env_var"] == "TEST_PHOTO_PASS"
        assert result["site_password_env_var"] == "TEST_SITE_PASS"