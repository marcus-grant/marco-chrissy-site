"""E2E tests for unified configuration system integration."""

from pathlib import Path

from validator.config import ConfigValidator


class TestConfigIntegration:
    """Test complete config integration workflow across all commands."""

    def test_all_commands_load_configs_correctly(self, temp_filesystem, file_factory):
        """Test that all commands load configs through unified system."""
        import os
        import shutil

        # Copy schema files to temp filesystem
        schema_dir = temp_filesystem / "config" / "schema"
        schema_dir.mkdir(parents=True, exist_ok=True)

        shutil.copy("config/schema/normpic.json", schema_dir / "normpic.json")
        shutil.copy("config/schema/site.json", schema_dir / "site.json")
        shutil.copy("config/schema/pelican.json", schema_dir / "pelican.json")
        shutil.copy("config/schema/galleria.json", schema_dir / "galleria.json")

        # Create valid config files that match our schemas
        file_factory("config/site.json", json_content={
            "output_dir": "output",
            "cdn": {"photos": "photos.example.com", "site": "site.example.com"}
        })

        file_factory("config/normpic.json", json_content={
            "source_dir": "~/Pictures/wedding/full",
            "dest_dir": "output/pics/full",
            "collection_name": "wedding",
            "create_symlinks": True
        })

        file_factory("config/pelican.json", json_content={
            "theme": "minimal",
            "site_url": "https://example.com",
            "author": "Test Author",
            "sitename": "Test Site"
        })

        file_factory("config/galleria.json", json_content={
            "manifest_path": "output/pics/full/manifest.json",
            "output_dir": "output/galleries",
            "thumbnail_size": 400,
            "photos_per_page": 60,
            "theme": "minimal",
            "quality": 85
        })

        # Change to temp directory for tests
        original_cwd = Path.cwd()
        try:
            os.chdir(temp_filesystem)

            # Test validate command loads configs correctly
            validator = ConfigValidator()
            result = validator.validate_config_files()
            assert result.success is True

            # Test organize command loads normpic config correctly
            # (would need mock normpic to avoid real photo processing)

            # Test build command loads all configs correctly
            # (would need mocked dependencies)

        finally:
            os.chdir(original_cwd)

    def test_config_validation_with_schema_errors(self, temp_filesystem, file_factory):
        """Test config validation catches invalid configs with schema validation."""
        import os
        import shutil

        # Copy schema files to temp filesystem
        schema_dir = temp_filesystem / "config" / "schema"
        schema_dir.mkdir(parents=True, exist_ok=True)

        shutil.copy("config/schema/normpic.json", schema_dir / "normpic.json")
        shutil.copy("config/schema/site.json", schema_dir / "site.json")
        shutil.copy("config/schema/pelican.json", schema_dir / "pelican.json")
        shutil.copy("config/schema/galleria.json", schema_dir / "galleria.json")

        # Create invalid normpic config (missing required fields)
        file_factory("config/normpic.json", json_content={
            "invalid_field": "value"  # Missing source_dir, dest_dir, etc.
        })

        original_cwd = Path.cwd()
        try:
            os.chdir(temp_filesystem)

            # Should fail validation with specific schema error messages
            validator = ConfigValidator()
            result = validator.validate_config_files()
            assert result.success is False
            assert any("validation" in error.lower() for error in result.errors)

        finally:
            os.chdir(original_cwd)

    def test_missing_config_file_scenarios(self, temp_filesystem, file_factory):
        """Test missing config file scenarios with meaningful error messages."""
        # Create only some config files, leave others missing
        file_factory("config/site.json", json_content={"output_dir": "output"})
        # normpic.json, pelican.json, galleria.json missing

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(temp_filesystem)

            validator = ConfigValidator()
            result = validator.validate_config_files()
            assert result.success is False
            assert any("normpic.json" in error for error in result.errors)
            assert any("pelican.json" in error for error in result.errors)
            assert any("galleria.json" in error for error in result.errors)

        finally:
            os.chdir(original_cwd)

    def test_config_file_corruption_and_json_parsing_errors(self, temp_filesystem, file_factory):
        """Test config file corruption and JSON parsing errors."""
        # Create corrupted JSON file
        file_factory("config/normpic.json", content="{ invalid json content")

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(temp_filesystem)

            validator = ConfigValidator()
            result = validator.validate_config_files()
            assert result.success is False
            # Check for JSON parsing error in any form
            assert any("json" in error.lower() for error in result.errors)

        finally:
            os.chdir(original_cwd)

