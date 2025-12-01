"""Integration tests for photo collection loading workflow."""

import json

import pytest


class TestPhotoCollectionIntegration:
    """Integration tests for end-to-end photo collection loading."""

    def test_galleria_loads_normpic_manifest_for_gallery_generation(self, tmp_path):
        """E2E: NormPic manifest → Galleria photo collection → Ready for processing.

        This test drives the implementation of the entire serializer module
        by defining the expected end-to-end workflow.
        """
        # Arrange: Create a NormPic manifest.json (like photographer would generate)
        manifest_dir = tmp_path / "wedding-photos"
        manifest_dir.mkdir()
        manifest_path = manifest_dir / "manifest.json"

        normpic_manifest = {
            "version": "0.1.0",
            "collection_name": "wedding",
            "generated_at": "2024-10-05T14:00:00Z",
            "pics": [
                {
                    "source_path": "/photos/IMG_001.jpg",
                    "dest_path": "/organized/wedding-20241005T143045-r5a.jpg",
                    "hash": "abc123def456",
                    "size_bytes": 2048000,
                    "mtime": 1699123456.789,
                    "timestamp": "2024-10-05T14:30:45.123",
                    "timestamp_source": "exif",
                    "camera": "Canon EOS R5",
                    "gps": None,
                    "errors": [],
                },
                {
                    "source_path": "/photos/IMG_002.jpg",
                    "dest_path": "/organized/wedding-20241005T143047-r5b.jpg",
                    "hash": "def456abc789",
                    "size_bytes": 1952000,
                    "mtime": 1699123458.123,
                    "timestamp": "2024-10-05T14:30:47.456",
                    "timestamp_source": "exif",
                    "camera": "Canon EOS R5",
                    "gps": {"lat": 40.7128, "lon": -74.0060},
                    "errors": [],
                },
            ],
            "collection_description": "John and Jane's wedding photos",
            "config": None,
        }

        manifest_path.write_text(json.dumps(normpic_manifest, indent=2))

        # Act: Galleria loads the collection (this will fail initially - that's TDD)
        from galleria.serializer.loader import load_photo_collection

        collection = load_photo_collection(str(manifest_path))

        # Assert: Collection is ready for Galleria processing
        assert collection.name == "wedding"
        assert collection.description == "John and Jane's wedding photos"
        assert len(collection.photos) == 2

        # Check first photo
        photo1 = collection.photos[0]
        assert photo1.source_path == "/photos/IMG_001.jpg"
        assert photo1.dest_path == "/organized/wedding-20241005T143045-r5a.jpg"
        assert photo1.hash == "abc123def456"
        assert photo1.size_bytes == 2048000
        assert photo1.camera == "Canon EOS R5"
        assert photo1.gps is None

        # Check second photo
        photo2 = collection.photos[1]
        assert photo2.source_path == "/photos/IMG_002.jpg"
        assert photo2.gps == {"lat": 40.7128, "lon": -74.0060}

    def test_galleria_handles_invalid_manifest_gracefully(self, tmp_path):
        """E2E: Invalid manifest → Clear error message."""
        # Arrange: Create invalid manifest
        manifest_path = tmp_path / "invalid.json"
        invalid_manifest = {
            "version": "0.1.0",
            # Missing required fields
        }
        manifest_path.write_text(json.dumps(invalid_manifest))

        # Act & Assert: Should raise clear error
        from galleria.serializer.exceptions import ManifestValidationError
        from galleria.serializer.loader import load_photo_collection

        with pytest.raises(ManifestValidationError) as exc_info:
            load_photo_collection(str(manifest_path))

        assert "collection_name" in str(exc_info.value)

    def test_galleria_handles_missing_manifest_file(self, tmp_path):
        """E2E: Missing file → Clear error message."""
        from galleria.serializer.exceptions import ManifestNotFoundError
        from galleria.serializer.loader import load_photo_collection

        missing_path = tmp_path / "nonexistent.json"

        with pytest.raises(ManifestNotFoundError):
            load_photo_collection(str(missing_path))
