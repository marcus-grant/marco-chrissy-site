"""Unit tests for config validation functionality."""



class TestConfigValidator:
    """Test configuration file validation."""

    def test_config_validator_can_be_imported(self):
        """Test that config validator module can be imported."""
        from validator.config import ConfigValidator
        assert ConfigValidator is not None

    def test_config_validator_checks_required_files(self, temp_filesystem, full_config_setup):
        """Test that config validator checks for required config files."""
        import os

        from validator.config import ConfigValidator

        # Set up all required config files
        full_config_setup()

        # Change to temp directory so validator finds the configs
        original_cwd = os.getcwd()
        try:
            os.chdir(str(temp_filesystem))
            validator = ConfigValidator()
            result = validator.validate_config_files()
        finally:
            os.chdir(original_cwd)

        assert result.success is True
        assert len(result.errors) == 0

    def test_config_validator_fails_on_missing_files(self, temp_filesystem):
        """Test that config validator fails when required files are missing."""
        import os

        from validator.config import ConfigValidator

        # Don't create any config files - use empty temp filesystem
        original_cwd = os.getcwd()
        try:
            os.chdir(str(temp_filesystem))
            validator = ConfigValidator()
            result = validator.validate_config_files()
        finally:
            os.chdir(original_cwd)

        assert result.success is False
        assert len(result.errors) > 0
        assert any("missing" in error.lower() for error in result.errors)

    def test_config_validator_result_has_required_attributes(self, temp_filesystem, full_config_setup):
        """Test that validation result has success and errors attributes."""
        import os

        from validator.config import ConfigValidator

        # Set up config files
        full_config_setup()

        original_cwd = os.getcwd()
        try:
            os.chdir(str(temp_filesystem))
            validator = ConfigValidator()
            result = validator.validate_config_files()
        finally:
            os.chdir(original_cwd)

        assert hasattr(result, 'success')
        assert hasattr(result, 'errors')
        assert isinstance(result.success, bool)
        assert isinstance(result.errors, list)

    def test_config_validator_validates_schema_content(self, temp_filesystem, file_factory):
        """Test that config validator validates config content against schemas."""
        import os
        import shutil

        from validator.config import ConfigValidator

        # Copy schema files to temp filesystem
        schema_dir = temp_filesystem / "config" / "schema"
        schema_dir.mkdir(parents=True, exist_ok=True)

        # Copy actual schema files using absolute paths
        import pathlib
        project_root = pathlib.Path(__file__).parent.parent.parent.parent
        shutil.copy(project_root / "config/schema/normpic.json", schema_dir / "normpic.json")
        shutil.copy(project_root / "config/schema/site.json", schema_dir / "site.json")
        shutil.copy(project_root / "config/schema/pelican.json", schema_dir / "pelican.json")
        shutil.copy(project_root / "config/schema/galleria.json", schema_dir / "galleria.json")

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

        original_cwd = os.getcwd()
        try:
            os.chdir(str(temp_filesystem))
            validator = ConfigValidator()
            result = validator.validate_config_files()
        finally:
            os.chdir(original_cwd)

        assert result.success is False
        assert len(result.errors) > 0
        assert any("validation" in error.lower() for error in result.errors)

    def test_config_validator_passes_valid_schema_content(self, temp_filesystem, file_factory):
        """Test that config validator passes valid config content."""
        import os
        import shutil

        from validator.config import ConfigValidator

        # Copy schema files to temp filesystem
        schema_dir = temp_filesystem / "config" / "schema"
        schema_dir.mkdir(parents=True, exist_ok=True)

        # Copy actual schema files using absolute paths
        import pathlib
        project_root = pathlib.Path(__file__).parent.parent.parent.parent
        shutil.copy(project_root / "config/schema/normpic.json", schema_dir / "normpic.json")
        shutil.copy(project_root / "config/schema/site.json", schema_dir / "site.json")
        shutil.copy(project_root / "config/schema/pelican.json", schema_dir / "pelican.json")
        shutil.copy(project_root / "config/schema/galleria.json", schema_dir / "galleria.json")

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

        original_cwd = os.getcwd()
        try:
            os.chdir(str(temp_filesystem))
            validator = ConfigValidator()
            result = validator.validate_config_files()
        finally:
            os.chdir(original_cwd)

        assert result.success is True
        assert len(result.errors) == 0
