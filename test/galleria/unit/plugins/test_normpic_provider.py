"""Unit tests for NormPicProviderPlugin implementation."""

import json

from galleria.plugins import PluginContext


class TestNormPicProviderPlugin:
    """Unit tests for NormPicProviderPlugin.load_collection() method."""

    def test_load_collection_returns_success_with_valid_manifest(self, tmp_path):
        """Test that load_collection returns PluginResult with success=True for valid manifest."""
        # This import will FAIL initially - expected for TDD red phase
        from galleria.plugins.providers.normpic import NormPicProviderPlugin

        # Arrange
        manifest_data = {
            "collection_name": "test_collection",
            "pics": [
                {
                    "source_path": "/test/IMG_001.CR3",
                    "dest_path": "test/IMG_001.jpg",
                    "hash": "abc123",
                    "size_bytes": 1000000,
                    "mtime": 1635789012.34
                }
            ]
        }

        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest_data))

        context = PluginContext(
            input_data={"manifest_path": str(manifest_path)},
            config={},
            output_dir=tmp_path / "output"
        )

        # Act
        plugin = NormPicProviderPlugin()
        result = plugin.load_collection(context)

        # Assert
        assert result.success is True
        assert result.errors == []

    def test_load_collection_returns_required_plugin_contract_fields(self, tmp_path):
        """Test that load_collection returns all required ProviderPlugin contract fields."""
        from galleria.plugins.providers.normpic import NormPicProviderPlugin

        # Arrange
        manifest_data = {
            "collection_name": "wedding_photos",
            "collection_description": "Wedding photos",
            "pics": [
                {
                    "source_path": "/photos/IMG_001.CR3",
                    "dest_path": "wedding/IMG_001.jpg",
                    "hash": "hash123",
                    "size_bytes": 2000000,
                    "mtime": 1635789015.67
                }
            ]
        }

        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest_data))

        context = PluginContext(
            input_data={"manifest_path": str(manifest_path)},
            config={},
            output_dir=tmp_path / "output"
        )

        # Act
        plugin = NormPicProviderPlugin()
        result = plugin.load_collection(context)

        # Assert: Required ProviderPlugin contract fields
        assert "photos" in result.output_data
        assert "collection_name" in result.output_data
        assert isinstance(result.output_data["photos"], list)
        assert result.output_data["collection_name"] == "wedding_photos"

    def test_load_collection_converts_normpic_to_plugin_photo_format(self, tmp_path):
        """Test that each pic is converted to ProviderPlugin photo contract format."""
        from galleria.plugins.providers.normpic import NormPicProviderPlugin

        # Arrange
        manifest_data = {
            "collection_name": "test",
            "pics": [
                {
                    "source_path": "/source/IMG_001.CR3",
                    "dest_path": "dest/IMG_001.jpg",
                    "hash": "abc123def456",
                    "size_bytes": 25000000,
                    "mtime": 1635789012.34,
                    "camera": "Canon EOS R5",
                    "gps": {"lat": 40.7128, "lon": -74.0060}
                }
            ]
        }

        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest_data))

        context = PluginContext(
            input_data={"manifest_path": str(manifest_path)},
            config={},
            output_dir=tmp_path / "output"
        )

        # Act
        plugin = NormPicProviderPlugin()
        result = plugin.load_collection(context)

        # Assert: Photo follows ProviderPlugin contract
        photo = result.output_data["photos"][0]
        assert "source_path" in photo
        assert "dest_path" in photo
        assert "metadata" in photo
        assert photo["source_path"] == "/source/IMG_001.CR3"
        assert photo["dest_path"] == "dest/IMG_001.jpg"

        # Assert: NormPic fields moved to metadata
        metadata = photo["metadata"]
        assert metadata["hash"] == "abc123def456"
        assert metadata["size_bytes"] == 25000000
        assert metadata["mtime"] == 1635789012.34
        assert metadata["camera"] == "Canon EOS R5"
        assert metadata["gps"] == {"lat": 40.7128, "lon": -74.0060}

    def test_load_collection_handles_missing_manifest_file(self, tmp_path):
        """Test that missing manifest file returns failure result."""
        from galleria.plugins.providers.normpic import NormPicProviderPlugin

        # Arrange
        nonexistent_path = tmp_path / "nonexistent.json"

        context = PluginContext(
            input_data={"manifest_path": str(nonexistent_path)},
            config={},
            output_dir=tmp_path / "output"
        )

        # Act
        plugin = NormPicProviderPlugin()
        result = plugin.load_collection(context)

        # Assert
        assert result.success is False
        assert len(result.errors) > 0
        assert any("manifest file not found" in error.lower() or "not found" in error.lower() for error in result.errors)

    def test_load_collection_handles_invalid_json(self, tmp_path):
        """Test that invalid JSON returns failure result."""
        from galleria.plugins.providers.normpic import NormPicProviderPlugin

        # Arrange
        manifest_path = tmp_path / "invalid.json"
        manifest_path.write_text("{ invalid json content")

        context = PluginContext(
            input_data={"manifest_path": str(manifest_path)},
            config={},
            output_dir=tmp_path / "output"
        )

        # Act
        plugin = NormPicProviderPlugin()
        result = plugin.load_collection(context)

        # Assert
        assert result.success is False
        assert len(result.errors) > 0

    def test_load_collection_validates_missing_collection_name(self, tmp_path):
        """Test that missing collection_name returns validation failure."""
        from galleria.plugins.providers.normpic import NormPicProviderPlugin

        # Arrange: Manifest without collection_name
        manifest_data = {
            "pics": [
                {
                    "source_path": "/test/IMG_001.jpg",
                    "dest_path": "test/IMG_001.jpg",
                    "hash": "abc123",
                    "size_bytes": 1000000,
                    "mtime": 1635789012.34
                }
            ]
        }

        manifest_path = tmp_path / "invalid.json"
        manifest_path.write_text(json.dumps(manifest_data))

        context = PluginContext(
            input_data={"manifest_path": str(manifest_path)},
            config={},
            output_dir=tmp_path / "output"
        )

        # Act
        plugin = NormPicProviderPlugin()
        result = plugin.load_collection(context)

        # Assert
        assert result.success is False
        assert any("collection_name" in error.lower() for error in result.errors)

    def test_load_collection_handles_missing_pics_field(self, tmp_path):
        """Test that missing pics field defaults to empty photo list."""
        from galleria.plugins.providers.normpic import NormPicProviderPlugin

        # Arrange
        manifest_data = {
            "collection_name": "empty_collection"
            # No pics field
        }

        manifest_path = tmp_path / "empty.json"
        manifest_path.write_text(json.dumps(manifest_data))

        context = PluginContext(
            input_data={"manifest_path": str(manifest_path)},
            config={},
            output_dir=tmp_path / "output"
        )

        # Act
        plugin = NormPicProviderPlugin()
        result = plugin.load_collection(context)

        # Assert
        assert result.success is True
        assert result.output_data["collection_name"] == "empty_collection"
        assert len(result.output_data["photos"]) == 0

    def test_load_collection_handles_malformed_pic_data(self, tmp_path):
        """Test that malformed pic data returns failure result."""
        from galleria.plugins.providers.normpic import NormPicProviderPlugin

        # Arrange: Pic missing required fields
        manifest_data = {
            "collection_name": "test",
            "pics": [
                {
                    "source_path": "/test/IMG_001.jpg"
                    # Missing dest_path, hash, size_bytes, mtime
                }
            ]
        }

        manifest_path = tmp_path / "malformed.json"
        manifest_path.write_text(json.dumps(manifest_data))

        context = PluginContext(
            input_data={"manifest_path": str(manifest_path)},
            config={},
            output_dir=tmp_path / "output"
        )

        # Act
        plugin = NormPicProviderPlugin()
        result = plugin.load_collection(context)

        # Assert
        assert result.success is False
        assert len(result.errors) > 0

    def test_plugin_has_required_properties(self):
        """Test that NormPicProviderPlugin implements required BasePlugin properties."""
        from galleria.plugins.providers.normpic import NormPicProviderPlugin

        # Act
        plugin = NormPicProviderPlugin()

        # Assert: BasePlugin interface requirements
        assert hasattr(plugin, 'name')
        assert hasattr(plugin, 'version')
        assert isinstance(plugin.name, str)
        assert isinstance(plugin.version, str)
        assert len(plugin.name) > 0
        assert len(plugin.version) > 0

    def test_load_collection_preserves_optional_metadata_fields(self, tmp_path):
        """Test that optional metadata fields like camera and gps are preserved."""
        from galleria.plugins.providers.normpic import NormPicProviderPlugin

        # Arrange: Pic with all optional metadata
        manifest_data = {
            "collection_name": "test",
            "pics": [
                {
                    "source_path": "/test/IMG_001.CR3",
                    "dest_path": "test/IMG_001.jpg",
                    "hash": "abc123",
                    "size_bytes": 1000000,
                    "mtime": 1635789012.34,
                    "camera": "Sony A7R IV",
                    "gps": {"lat": 34.0522, "lon": -118.2437},
                    "custom_field": "custom_value"  # Test custom fields
                }
            ]
        }

        manifest_path = tmp_path / "metadata.json"
        manifest_path.write_text(json.dumps(manifest_data))

        context = PluginContext(
            input_data={"manifest_path": str(manifest_path)},
            config={},
            output_dir=tmp_path / "output"
        )

        # Act
        plugin = NormPicProviderPlugin()
        result = plugin.load_collection(context)

        # Assert: All metadata preserved
        metadata = result.output_data["photos"][0]["metadata"]
        assert metadata["camera"] == "Sony A7R IV"
        assert metadata["gps"] == {"lat": 34.0522, "lon": -118.2437}
        assert metadata["custom_field"] == "custom_value"
