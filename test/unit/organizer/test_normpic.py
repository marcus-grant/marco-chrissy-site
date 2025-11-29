"""Unit tests for NormPic integration functionality."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from organizer.normpic import NormPicOrganizer, OrganizeResult
from serializer.exceptions import ConfigLoadError


class TestNormPicOrganizer:
    """Test NormPic orchestration functionality."""

    def test_organizer_initialization(self):
        """Test that NormPicOrganizer can be initialized."""
        organizer = NormPicOrganizer()
        assert organizer is not None

    @patch('organizer.normpic.organize_photos')
    def test_organize_photos_returns_result(self, mock_organize_photos):
        """Test that organize_photos returns an OrganizeResult."""
        # Ensure output directory exists (may be missing due to test contamination)
        # Handle case where working directory was changed/deleted by other tests
        import tempfile
        from pathlib import Path

        try:
            current_dir = Path.cwd()
        except FileNotFoundError:
            # Working directory was deleted by another test, use temp directory
            current_dir = Path(tempfile.gettempdir())

        output_dir = current_dir / "output"
        output_dir.mkdir(exist_ok=True)

        # Mock the heavy NormPic function
        mock_manifest = Mock()
        mock_manifest.pics = [Mock(), Mock()]  # 2 pics
        mock_manifest.errors = []
        mock_organize_photos.return_value = mock_manifest

        organizer = NormPicOrganizer()
        result = organizer.organize_photos()

        assert isinstance(result, OrganizeResult)
        assert hasattr(result, 'success')
        assert hasattr(result, 'errors')
        assert result.success is True
        assert result.pics_processed == 2

    def test_organize_result_dataclass(self):
        """Test OrganizeResult dataclass creation."""
        result = OrganizeResult(success=True, errors=[])
        assert result.success is True
        assert result.errors == []

        result_with_errors = OrganizeResult(success=False, errors=["test error"])
        assert result_with_errors.success is False
        assert result_with_errors.errors == ["test error"]

    def test_is_already_organized_no_manifest(self, temp_filesystem):
        """Test is_already_organized returns False when no manifest exists."""
        dest_dir = temp_filesystem / "output" / "pics"
        organizer = NormPicOrganizer(dest_dir=dest_dir)

        assert not organizer.is_already_organized()

    def test_is_already_organized_valid_manifest(self, temp_filesystem, file_factory):
        """Test is_already_organized returns True with valid manifest and symlinks."""
        dest_dir = temp_filesystem / "output" / "pics"
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Create a source file
        source_dir = temp_filesystem / "source"
        source_dir.mkdir(parents=True, exist_ok=True)
        source_file = source_dir / "test.jpg"
        source_file.write_text("fake image")

        # Create a symlink
        symlink_file = dest_dir / "wedding_123.jpg"
        symlink_file.symlink_to(source_file)

        # Create valid manifest
        manifest_data = {
            "collection_name": "wedding",
            "pics": [
                {
                    "source_path": str(source_file),
                    "dest_path": "wedding_123.jpg",
                    "hash": "abc123",
                    "size_bytes": 1000
                }
            ]
        }

        manifest_path = dest_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest_data, f)

        organizer = NormPicOrganizer(dest_dir=dest_dir, collection_name="wedding")
        assert organizer.is_already_organized()

    def test_is_already_organized_wrong_collection_name(self, temp_filesystem):
        """Test is_already_organized returns False with wrong collection name."""
        dest_dir = temp_filesystem / "output" / "pics"
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Create manifest with different collection name
        manifest_data = {
            "collection_name": "vacation",
            "pics": []
        }

        manifest_path = dest_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest_data, f)

        organizer = NormPicOrganizer(dest_dir=dest_dir, collection_name="wedding")
        assert not organizer.is_already_organized()

    @patch('organizer.normpic.JsonConfigLoader')
    def test_unified_config_loading_success(self, mock_loader_class, temp_filesystem):
        """Test NormPicOrganizer uses unified config system successfully."""
        # Mock the JsonConfigLoader and its behavior
        mock_loader_instance = Mock()
        mock_loader_class.return_value = mock_loader_instance

        # Mock successful config loading with schema validation
        mock_config_data = {
            "source_dir": "~/Pictures/wedding/full",
            "dest_dir": "output/pics/full",
            "collection_name": "wedding",
            "create_symlinks": True
        }
        mock_loader_instance.load_config.return_value = mock_config_data

        organizer = NormPicOrganizer()

        # Verify organizer was created successfully
        assert organizer is not None

        # Verify JsonConfigLoader was called for both schema and config loading
        assert mock_loader_class.call_count == 2

        # Verify config was loaded twice (schema + actual config)
        assert mock_loader_instance.load_config.call_count == 2

    @patch('organizer.normpic.JsonConfigLoader')
    def test_unified_config_loading_missing_file(self, mock_loader_class):
        """Test NormPicOrganizer handles missing config file gracefully."""
        mock_loader_instance = Mock()
        mock_loader_class.return_value = mock_loader_instance

        # Mock config file not found
        mock_loader_instance.load_config.side_effect = ConfigLoadError(
            Path("config/normpic.json"),
            "Configuration file not found"
        )

        # Should fall back to defaults without crashing
        organizer = NormPicOrganizer()
        assert organizer is not None

    @patch('organizer.normpic.JsonConfigLoader')
    def test_unified_config_validation_failure(self, mock_loader_class):
        """Test NormPicOrganizer handles schema validation failures."""
        from serializer.exceptions import ConfigValidationError

        mock_loader_instance = Mock()
        mock_loader_class.return_value = mock_loader_instance

        # Mock schema validation failure
        mock_loader_instance.load_config.side_effect = ConfigValidationError(
            Path("config/normpic.json"),
            "Missing required field: source_dir"
        )

        # Should raise the validation error to caller
        with pytest.raises(ConfigValidationError) as exc_info:
            NormPicOrganizer()

        assert "source_dir" in str(exc_info.value)

    def test_is_already_organized_missing_symlinks(self, temp_filesystem):
        """Test is_already_organized returns False when symlinks are missing."""
        dest_dir = temp_filesystem / "output" / "pics"
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Create manifest with symlink that doesn't exist
        manifest_data = {
            "collection_name": "wedding",
            "pics": [
                {
                    "dest_path": "missing_symlink.jpg",
                    "hash": "abc123"
                }
            ]
        }

        manifest_path = dest_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest_data, f)

        organizer = NormPicOrganizer(dest_dir=dest_dir, collection_name="wedding")
        assert not organizer.is_already_organized()
