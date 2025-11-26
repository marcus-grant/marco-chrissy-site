"""Unit tests for NormPic integration functionality."""

import json
from unittest.mock import Mock, patch

from organizer.normpic import NormPicOrganizer, OrganizeResult


class TestNormPicOrganizer:
    """Test NormPic orchestration functionality."""

    def test_organizer_initialization(self):
        """Test that NormPicOrganizer can be initialized."""
        organizer = NormPicOrganizer()
        assert organizer is not None

    @patch('organizer.normpic.organize_photos')
    def test_organize_photos_returns_result(self, mock_organize_photos):
        """Test that organize_photos returns an OrganizeResult."""
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
