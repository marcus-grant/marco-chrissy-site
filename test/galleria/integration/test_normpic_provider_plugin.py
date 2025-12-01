"""Integration tests for NormPicProviderPlugin implementation.

This module tests the conversion of the existing serializer to a proper
ProviderPlugin implementation following TDD methodology.
"""

import json

from galleria.plugins import PluginContext


class TestNormPicProviderPlugin:
    """Integration tests for NormPicProviderPlugin implementation."""

    def test_normpic_provider_loads_real_manifest_data(self, tmp_path):
        """NormPicProviderPlugin should load actual NormPic manifest and convert to plugin contract.

        This is the E2E integration test that will initially FAIL since
        NormPicProviderPlugin doesn't exist yet. This test defines:

        1. Input: Real NormPic manifest.json format
        2. Expected output: ProviderPlugin contract format
        3. Error handling: Missing files, invalid JSON

        This test will drive the implementation of NormPicProviderPlugin.
        """
        # This import will FAIL initially - that's expected for TDD red phase
        from galleria.plugins.providers.normpic import NormPicProviderPlugin

        # Arrange: Create a real NormPic manifest file
        manifest_data = {
            "collection_name": "wedding_photos",
            "collection_description": "Marcus and Chrissy's wedding photos",
            "manifest_version": "0.1.0",
            "pics": [
                {
                    "source_path": "/photos/wedding/IMG_001.CR3",
                    "dest_path": "wedding/IMG_001.jpg",
                    "hash": "abc123def456",
                    "size_bytes": 25000000,
                    "mtime": 1635789012.34,
                    "camera": "Canon EOS R5",
                    "gps": {"lat": 40.7128, "lon": -74.0060},
                },
                {
                    "source_path": "/photos/wedding/IMG_002.CR3",
                    "dest_path": "wedding/IMG_002.jpg",
                    "hash": "def456ghi789",
                    "size_bytes": 26500000,
                    "mtime": 1635789015.67,
                    "camera": "Canon EOS R5",
                    "gps": {"lat": 40.7130, "lon": -74.0058},
                },
            ],
        }

        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest_data, indent=2))

        # Arrange: Create plugin context
        context = PluginContext(
            input_data={"manifest_path": str(manifest_path)},
            config={"validate_files": False},  # Skip file validation for test
            output_dir=tmp_path / "output",
        )

        # Act: Load collection through plugin interface
        plugin = NormPicProviderPlugin()
        result = plugin.load_collection(context)

        # Assert: Plugin follows ProviderPlugin contract
        assert result.success is True
        assert isinstance(result.output_data, dict)

        # Assert: Required ProviderPlugin output format
        assert "photos" in result.output_data
        assert "collection_name" in result.output_data
        assert result.output_data["collection_name"] == "wedding_photos"

        # Assert: Photo data follows ProviderPlugin contract
        photos = result.output_data["photos"]
        assert len(photos) == 2

        photo1 = photos[0]
        assert "source_path" in photo1
        assert "dest_path" in photo1
        assert "metadata" in photo1
        assert photo1["source_path"] == "/photos/wedding/IMG_001.CR3"
        assert photo1["dest_path"] == "wedding/IMG_001.jpg"

        # Assert: Metadata includes original NormPic fields
        metadata = photo1["metadata"]
        assert metadata["hash"] == "abc123def456"
        assert metadata["size_bytes"] == 25000000
        assert metadata["mtime"] == 1635789012.34
        assert metadata["camera"] == "Canon EOS R5"
        assert metadata["gps"] == {"lat": 40.7128, "lon": -74.0060}

    def test_normpic_provider_handles_missing_manifest(self, tmp_path):
        """NormPicProviderPlugin should raise appropriate error for missing manifest."""
        # This import will FAIL initially - that's expected for TDD red phase
        from galleria.plugins.providers.normpic import NormPicProviderPlugin

        # Arrange: Non-existent manifest path
        manifest_path = tmp_path / "nonexistent.json"

        context = PluginContext(
            input_data={"manifest_path": str(manifest_path)},
            config={},
            output_dir=tmp_path / "output",
        )

        # Act & Assert: Should raise PluginExecutionError
        plugin = NormPicProviderPlugin()
        result = plugin.load_collection(context)

        assert result.success is False
        assert any(
            "manifest file not found" in error.lower() for error in result.errors
        )

    def test_normpic_provider_handles_invalid_manifest_json(self, tmp_path):
        """NormPicProviderPlugin should handle invalid JSON gracefully."""
        # This import will FAIL initially - that's expected for TDD red phase
        from galleria.plugins.providers.normpic import NormPicProviderPlugin

        # Arrange: Create invalid JSON file
        manifest_path = tmp_path / "invalid.json"
        manifest_path.write_text("{ invalid json ")

        context = PluginContext(
            input_data={"manifest_path": str(manifest_path)},
            config={},
            output_dir=tmp_path / "output",
        )

        # Act & Assert: Should handle invalid JSON
        plugin = NormPicProviderPlugin()
        result = plugin.load_collection(context)

        assert result.success is False
        assert any(
            "invalid json" in error.lower() or "json" in error.lower()
            for error in result.errors
        )

    def test_normpic_provider_handles_missing_required_fields(self, tmp_path):
        """NormPicProviderPlugin should validate required manifest fields."""
        # This import will FAIL initially - that's expected for TDD red phase
        from galleria.plugins.providers.normpic import NormPicProviderPlugin

        # Arrange: Create manifest missing collection_name
        manifest_data = {
            "pics": [
                {
                    "source_path": "/photos/wedding/IMG_001.CR3",
                    "dest_path": "wedding/IMG_001.jpg",
                    "hash": "abc123def456",
                    "size_bytes": 25000000,
                    "mtime": 1635789012.34,
                }
            ]
        }

        manifest_path = tmp_path / "incomplete.json"
        manifest_path.write_text(json.dumps(manifest_data))

        context = PluginContext(
            input_data={"manifest_path": str(manifest_path)},
            config={},
            output_dir=tmp_path / "output",
        )

        # Act & Assert: Should validate required fields
        plugin = NormPicProviderPlugin()
        result = plugin.load_collection(context)

        assert result.success is False
        assert any("collection_name" in error.lower() for error in result.errors)

    def test_normpic_provider_integration_with_existing_serializer_data(self, tmp_path):
        """NormPicProviderPlugin should produce same results as existing serializer.

        This test ensures backward compatibility by comparing plugin output
        with existing serializer.load_photo_collection() output.
        """
        # This import will FAIL initially - that's expected for TDD red phase
        from galleria.plugins.providers.normpic import NormPicProviderPlugin

        # Also test against existing serializer for compatibility
        from galleria.serializer.loader import load_photo_collection

        # Arrange: Create manifest that works with both systems
        manifest_data = {
            "collection_name": "test_collection",
            "collection_description": "Test description",
            "pics": [
                {
                    "source_path": "/test/IMG_001.CR3",
                    "dest_path": "test/IMG_001.jpg",
                    "hash": "test123",
                    "size_bytes": 1000000,
                    "mtime": 1635789012.34,
                    "camera": "Test Camera",
                }
            ],
        }

        manifest_path = tmp_path / "test_manifest.json"
        manifest_path.write_text(json.dumps(manifest_data))

        # Act: Load with both systems
        # Existing serializer
        collection = load_photo_collection(str(manifest_path))

        # New plugin system
        context = PluginContext(
            input_data={"manifest_path": str(manifest_path)},
            config={},
            output_dir=tmp_path / "output",
        )
        plugin = NormPicProviderPlugin()
        result = plugin.load_collection(context)

        # Assert: Both systems produce compatible data
        assert result.success is True

        # Compare collection data
        assert result.output_data["collection_name"] == collection.name
        assert len(result.output_data["photos"]) == len(collection.photos)

        # Compare photo data (plugin should contain all serializer data)
        plugin_photo = result.output_data["photos"][0]
        serializer_photo = collection.photos[0]

        assert plugin_photo["source_path"] == serializer_photo.source_path
        assert plugin_photo["dest_path"] == serializer_photo.dest_path
        assert plugin_photo["metadata"]["hash"] == serializer_photo.hash
        assert plugin_photo["metadata"]["size_bytes"] == serializer_photo.size_bytes
        assert plugin_photo["metadata"]["mtime"] == serializer_photo.mtime
        assert plugin_photo["metadata"]["camera"] == serializer_photo.camera
