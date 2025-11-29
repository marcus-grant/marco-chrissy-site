"""Unit tests for config validation functionality."""



class TestConfigValidator:
    """Test configuration file validation."""

    def test_config_validator_can_be_imported(self):
        """Test that config validator module can be imported."""
        from validator.config import ConfigValidator
        assert ConfigValidator is not None

    def test_config_validator_checks_required_files(self, temp_filesystem, full_config_setup):
        """Test that config validator checks for required config files."""

        from validator.config import ConfigValidator

        # Set up all required config files
        full_config_setup()

        # Use base_path parameter instead of changing working directory
        validator = ConfigValidator(base_path=temp_filesystem)
        result = validator.validate_config_files()

        assert result.success is True
        assert len(result.errors) == 0

    def test_config_validator_fails_on_missing_files(self, temp_filesystem):
        """Test that config validator fails when required files are missing."""

        from validator.config import ConfigValidator

        # Don't create any config files - use empty temp filesystem
        # Use base_path parameter instead of changing working directory
        validator = ConfigValidator(base_path=temp_filesystem)
        result = validator.validate_config_files()

        assert result.success is False
        assert len(result.errors) > 0
        assert any("missing" in error.lower() for error in result.errors)

    def test_config_validator_result_has_required_attributes(self, temp_filesystem, full_config_setup):
        """Test that validation result has success and errors attributes."""

        from validator.config import ConfigValidator

        # Set up config files
        full_config_setup()

        # Use base_path parameter instead of changing working directory
        validator = ConfigValidator(base_path=temp_filesystem)
        result = validator.validate_config_files()

        assert hasattr(result, 'success')
        assert hasattr(result, 'errors')
        assert isinstance(result.success, bool)
        assert isinstance(result.errors, list)

    def test_config_validator_validates_schema_content(self, temp_filesystem, file_factory):
        """Test that config validator validates config content against schemas."""

        from validator.config import ConfigValidator

        # Create mock schema files instead of copying real ones
        schema_dir = temp_filesystem / "config" / "schema"
        schema_dir.mkdir(parents=True, exist_ok=True)

        # Create mock schemas with required fields for validation
        file_factory("config/schema/normpic.json", json_content={
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["source_dir", "dest_dir", "collection_name"],
            "properties": {
                "source_dir": {"type": "string"},
                "dest_dir": {"type": "string"},
                "collection_name": {"type": "string"},
                "create_symlinks": {"type": "boolean"}
            }
        })
        file_factory("config/schema/site.json", json_content={
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["output_dir", "cdn"],
            "properties": {
                "output_dir": {"type": "string"},
                "cdn": {
                    "type": "object",
                    "required": ["photos", "site"],
                    "properties": {
                        "photos": {"type": "string"},
                        "site": {"type": "string"}
                    }
                }
            }
        })
        file_factory("config/schema/pelican.json", json_content={
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["theme", "site_url", "author", "sitename"],
            "properties": {
                "theme": {"type": "string"},
                "site_url": {"type": "string"},
                "author": {"type": "string"},
                "sitename": {"type": "string"}
            }
        })
        file_factory("config/schema/galleria.json", json_content={
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["manifest_path", "output_dir"],
            "properties": {
                "manifest_path": {"type": "string"},
                "output_dir": {"type": "string"},
                "thumbnail_size": {"type": "integer"},
                "photos_per_page": {"type": "integer"},
                "theme": {"type": "string"},
                "quality": {"type": "integer"}
            }
        })

        # Create invalid config files that exist but have bad content
        file_factory("config/normpic.json", json_content={
            "invalid_field": "value"
            # Missing required fields
        })
        file_factory("config/site.json", json_content={
            "output_dir": "output",
            "cdn": {
                "photos": "https://photos.example.com",
                "site": "https://site.example.com"
            }
        })
        file_factory("config/pelican.json", json_content={
            "invalid_field": "value"
            # Missing required fields
        })
        file_factory("config/galleria.json", json_content={
            "invalid_field": "value"
            # Missing required fields
        })

        # Use base_path parameter instead of changing working directory
        validator = ConfigValidator(base_path=temp_filesystem)
        result = validator.validate_config_files()

        assert result.success is False
        assert len(result.errors) > 0
        assert any("validation" in error.lower() for error in result.errors)

    def test_config_validator_passes_valid_schema_content(self, temp_filesystem, file_factory):
        """Test that config validator passes valid config content."""

        from validator.config import ConfigValidator

        # Create mock schema files instead of copying real ones
        schema_dir = temp_filesystem / "config" / "schema"
        schema_dir.mkdir(parents=True, exist_ok=True)

        # Create mock schemas with required fields for validation
        file_factory("config/schema/normpic.json", json_content={
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["source_dir", "dest_dir", "collection_name"],
            "properties": {
                "source_dir": {"type": "string"},
                "dest_dir": {"type": "string"},
                "collection_name": {"type": "string"},
                "create_symlinks": {"type": "boolean"}
            }
        })
        file_factory("config/schema/site.json", json_content={
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["output_dir", "cdn"],
            "properties": {
                "output_dir": {"type": "string"},
                "cdn": {
                    "type": "object",
                    "required": ["photos", "site"],
                    "properties": {
                        "photos": {"type": "string"},
                        "site": {"type": "string"}
                    }
                }
            }
        })
        file_factory("config/schema/pelican.json", json_content={
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["theme", "site_url", "author", "sitename"],
            "properties": {
                "theme": {"type": "string"},
                "site_url": {"type": "string"},
                "author": {"type": "string"},
                "sitename": {"type": "string"}
            }
        })
        file_factory("config/schema/galleria.json", json_content={
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["manifest_path", "output_dir"],
            "properties": {
                "manifest_path": {"type": "string"},
                "output_dir": {"type": "string"},
                "thumbnail_size": {"type": "integer"},
                "photos_per_page": {"type": "integer"},
                "theme": {"type": "string"},
                "quality": {"type": "integer"}
            }
        })

        # Create valid config files
        file_factory("config/normpic.json", json_content={
            "source_dir": "~/Pictures/wedding/full",
            "dest_dir": "output/pics/full",
            "collection_name": "wedding",
            "create_symlinks": True
        })
        file_factory("config/site.json", json_content={
            "output_dir": "output",
            "cdn": {
                "photos": "https://photos.example.com",
                "site": "https://site.example.com"
            }
        })
        file_factory("config/pelican.json", json_content={
            "theme": "minimal",
            "site_url": "https://example.com",
            "author": "Test Author",
            "sitename": "Test Site"
        })
        file_factory("config/galleria.json", json_content={
            "manifest_path": "/home/user/Photos/wedding/manifest.json",
            "output_dir": "output/galleries/wedding",
            "thumbnail_size": 400,
            "photos_per_page": 60,
            "theme": "minimal",
            "quality": 85
        })

        # Use base_path parameter instead of changing working directory
        validator = ConfigValidator(base_path=temp_filesystem)
        result = validator.validate_config_files()

        assert result.success is True
        assert len(result.errors) == 0
