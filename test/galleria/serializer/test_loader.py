"""Unit tests for photo collection loader."""

import json

import pytest


class TestLoadPhotoCollection:
    """Unit tests for load_photo_collection function."""

    def test_load_photo_collection_returns_photo_collection_object(self, tmp_path):
        """Test that load_photo_collection returns an object with name property."""
        # Arrange
        manifest_path = tmp_path / "manifest.json"
        manifest_data = {
            "version": "0.1.0",
            "collection_name": "test-collection",
            "generated_at": "2024-10-05T14:00:00Z",
            "pics": [],
        }
        manifest_path.write_text(json.dumps(manifest_data))

        # Act
        from galleria.serializer.loader import load_photo_collection
        collection = load_photo_collection(str(manifest_path))

        # Assert
        assert hasattr(collection, 'name')
        assert collection.name == "test-collection"

    def test_load_photo_collection_handles_missing_file(self, tmp_path):
        """Test that missing file raises appropriate error."""
        from galleria.serializer.exceptions import ManifestNotFoundError
        from galleria.serializer.loader import load_photo_collection

        missing_path = tmp_path / "nonexistent.json"

        with pytest.raises(ManifestNotFoundError):
            load_photo_collection(str(missing_path))

    def test_load_photo_collection_includes_description(self, tmp_path):
        """Test that collection includes description from manifest."""
        # Arrange
        manifest_path = tmp_path / "manifest.json"
        manifest_data = {
            "version": "0.1.0",
            "collection_name": "wedding",
            "generated_at": "2024-10-05T14:00:00Z",
            "collection_description": "John and Jane's wedding photos",
            "pics": [],
        }
        manifest_path.write_text(json.dumps(manifest_data))

        # Act
        from galleria.serializer.loader import load_photo_collection
        collection = load_photo_collection(str(manifest_path))

        # Assert
        assert collection.description == "John and Jane's wedding photos"

    def test_load_photo_collection_includes_photos(self, tmp_path):
        """Test that collection includes photos from manifest pics."""
        # Arrange
        manifest_path = tmp_path / "manifest.json"
        manifest_data = {
            "version": "0.1.0",
            "collection_name": "test",
            "generated_at": "2024-10-05T14:00:00Z",
            "pics": [
                {
                    "source_path": "/photos/IMG_001.jpg",
                    "dest_path": "/organized/img1.jpg",
                    "hash": "abc123",
                    "size_bytes": 1024,
                    "mtime": 1699123456.789,
                }
            ],
        }
        manifest_path.write_text(json.dumps(manifest_data))

        # Act
        from galleria.serializer.loader import load_photo_collection
        collection = load_photo_collection(str(manifest_path))

        # Assert
        assert hasattr(collection, 'photos')
        assert len(collection.photos) == 1

    def test_photo_includes_camera_information(self, tmp_path):
        """Test that photos include camera metadata."""
        # Arrange
        manifest_path = tmp_path / "manifest.json"
        manifest_data = {
            "version": "0.1.0",
            "collection_name": "test",
            "generated_at": "2024-10-05T14:00:00Z",
            "pics": [
                {
                    "source_path": "/photos/IMG_001.jpg",
                    "dest_path": "/organized/img1.jpg",
                    "hash": "abc123",
                    "size_bytes": 1024,
                    "mtime": 1699123456.789,
                    "camera": "Canon EOS R5",
                }
            ],
        }
        manifest_path.write_text(json.dumps(manifest_data))

        # Act
        from galleria.serializer.loader import load_photo_collection
        collection = load_photo_collection(str(manifest_path))

        # Assert
        photo = collection.photos[0]
        assert photo.camera == "Canon EOS R5"

    def test_load_photo_collection_validates_required_fields(self, tmp_path):
        """Test that missing required fields raise validation error."""
        # Arrange
        manifest_path = tmp_path / "invalid.json"
        invalid_manifest = {
            "version": "0.1.0",
            # Missing collection_name
        }
        manifest_path.write_text(json.dumps(invalid_manifest))

        # Act & Assert
        from galleria.serializer.exceptions import ManifestValidationError
        from galleria.serializer.loader import load_photo_collection

        with pytest.raises(ManifestValidationError) as exc_info:
            load_photo_collection(str(manifest_path))

        assert "collection_name" in str(exc_info.value)
