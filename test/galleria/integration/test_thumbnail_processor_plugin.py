"""Integration tests for ThumbnailProcessorPlugin implementation.

This module tests the conversion of the existing processor to a proper
ProcessorPlugin implementation following TDD methodology.
"""

import json
from pathlib import Path

from PIL import Image

from galleria.plugins import PluginContext


class TestThumbnailProcessorPlugin:
    """Integration tests for ThumbnailProcessorPlugin implementation."""

    def test_thumbnail_processor_processes_real_provider_data(self, tmp_path):
        """ThumbnailProcessorPlugin should process actual ProviderPlugin output and generate thumbnails.

        This is the E2E integration test that will initially FAIL since
        ThumbnailProcessorPlugin doesn't exist yet. This test defines:

        1. Input: Real ProviderPlugin output format with photo collection
        2. Expected output: ProcessorPlugin contract format with thumbnail_path
        3. File generation: Actual thumbnail files created on disk
        4. Error handling: Missing files, corrupted images

        This test will drive the implementation of ThumbnailProcessorPlugin.
        """
        # This import will FAIL initially - that's expected for TDD red phase
        from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin

        # Arrange: Create test source images
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        output_dir = tmp_path / "output"

        # Create test images (simple colored squares)
        img1_path = source_dir / "IMG_001.jpg"
        img2_path = source_dir / "IMG_002.jpg"

        # Create test JPEG images
        img1 = Image.new('RGB', (800, 600), color='red')
        img1.save(img1_path, 'JPEG')
        img2 = Image.new('RGB', (1200, 800), color='blue')
        img2.save(img2_path, 'JPEG')

        # Arrange: Create ProviderPlugin output format as input
        provider_output = {
            "photos": [
                {
                    "source_path": str(img1_path),
                    "dest_path": "wedding/IMG_001.jpg",
                    "metadata": {
                        "hash": "abc123def456",
                        "size_bytes": 25000000,
                        "mtime": 1635789012.34,
                        "camera": "Canon EOS R5"
                    }
                },
                {
                    "source_path": str(img2_path),
                    "dest_path": "wedding/IMG_002.jpg",
                    "metadata": {
                        "hash": "def456ghi789",
                        "size_bytes": 26500000,
                        "mtime": 1635789015.67,
                        "camera": "Canon EOS R5"
                    }
                }
            ],
            "collection_name": "wedding_photos",
            "collection_description": "Wedding photos"
        }

        # Arrange: Create plugin context
        context = PluginContext(
            input_data=provider_output,
            config={
                "thumbnail_size": 300,
                "quality": 80,
                "output_format": "webp"
            },
            output_dir=output_dir
        )

        # Act: Process thumbnails through plugin interface
        plugin = ThumbnailProcessorPlugin()
        result = plugin.process_thumbnails(context)

        # Assert: Plugin follows ProcessorPlugin contract
        assert result.success is True
        assert isinstance(result.output_data, dict)

        # Assert: Required ProcessorPlugin output format
        assert "photos" in result.output_data
        assert "collection_name" in result.output_data
        assert "thumbnail_count" in result.output_data
        assert result.output_data["collection_name"] == "wedding_photos"
        assert result.output_data["thumbnail_count"] == 2

        # Assert: Photo data follows ProcessorPlugin contract
        photos = result.output_data["photos"]
        assert len(photos) == 2

        photo1 = photos[0]
        # Original provider data preserved
        assert photo1["source_path"] == str(img1_path)
        assert photo1["dest_path"] == "wedding/IMG_001.jpg"
        assert photo1["metadata"]["camera"] == "Canon EOS R5"

        # New processor data added
        assert "thumbnail_path" in photo1
        assert "thumbnail_size" in photo1
        assert photo1["thumbnail_size"] == (300, 300)  # Square thumbnails

        # Assert: Actual thumbnail files created
        thumbnail1_path = Path(photo1["thumbnail_path"])
        assert thumbnail1_path.exists()
        assert thumbnail1_path.suffix == ".webp"

        # Verify thumbnail is correct size
        with Image.open(thumbnail1_path) as thumb:
            assert thumb.size == (300, 300)
            assert thumb.format == "WEBP"

    def test_thumbnail_processor_handles_missing_source_files(self, tmp_path):
        """ThumbnailProcessorPlugin should handle missing source files gracefully."""
        # This import will FAIL initially - that's expected for TDD red phase
        from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin

        # Arrange: Provider output with non-existent source files
        provider_output = {
            "photos": [
                {
                    "source_path": "/nonexistent/IMG_001.jpg",
                    "dest_path": "wedding/IMG_001.jpg",
                    "metadata": {"hash": "abc123"}
                }
            ],
            "collection_name": "test_collection"
        }

        context = PluginContext(
            input_data=provider_output,
            config={"thumbnail_size": 300},
            output_dir=tmp_path / "output"
        )

        # Act: Process thumbnails with missing files
        plugin = ThumbnailProcessorPlugin()
        result = plugin.process_thumbnails(context)

        # Assert: Plugin handles errors gracefully
        assert result.success is True  # Plugin should continue processing other photos
        photos = result.output_data["photos"]
        photo1 = photos[0]

        # Photo should have error information but preserve original data
        assert "error" in photo1
        assert "source_path" in photo1  # Original data preserved
        assert "does not exist" in photo1["error"].lower() or "missing" in photo1["error"].lower() or "not found" in photo1["error"].lower()

    def test_thumbnail_processor_handles_corrupted_images(self, tmp_path):
        """ThumbnailProcessorPlugin should handle corrupted image files gracefully."""
        # This import will FAIL initially - that's expected for TDD red phase
        from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin

        # Arrange: Create corrupted image file
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        corrupted_img = source_dir / "corrupted.jpg"
        corrupted_img.write_text("This is not an image file")

        provider_output = {
            "photos": [
                {
                    "source_path": str(corrupted_img),
                    "dest_path": "test/corrupted.jpg",
                    "metadata": {"hash": "corrupted123"}
                }
            ],
            "collection_name": "test_collection"
        }

        context = PluginContext(
            input_data=provider_output,
            config={"thumbnail_size": 300},
            output_dir=tmp_path / "output"
        )

        # Act: Process corrupted image
        plugin = ThumbnailProcessorPlugin()
        result = plugin.process_thumbnails(context)

        # Assert: Plugin handles corruption gracefully
        assert result.success is True
        photo1 = result.output_data["photos"][0]
        assert "error" in photo1
        assert "source_path" in photo1  # Original data preserved

    def test_thumbnail_processor_implements_caching(self, tmp_path):
        """ThumbnailProcessorPlugin should implement caching to skip existing thumbnails."""
        # This import will FAIL initially - that's expected for TDD red phase
        from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin

        # Arrange: Create test source image
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        output_dir = tmp_path / "output"
        thumbnails_dir = output_dir / "thumbnails"
        thumbnails_dir.mkdir(parents=True)

        img_path = source_dir / "IMG_001.jpg"
        img = Image.new('RGB', (800, 600), color='green')
        img.save(img_path, 'JPEG')

        # Create existing thumbnail file (simulate previous processing)
        existing_thumb = thumbnails_dir / "IMG_001.webp"
        thumb = Image.new('RGB', (300, 300), color='green')
        thumb.save(existing_thumb, 'WEBP')

        provider_output = {
            "photos": [
                {
                    "source_path": str(img_path),
                    "dest_path": "test/IMG_001.jpg",
                    "metadata": {"hash": "cache123"}
                }
            ],
            "collection_name": "test_collection"
        }

        context = PluginContext(
            input_data=provider_output,
            config={"thumbnail_size": 300, "use_cache": True},
            output_dir=output_dir
        )

        # Act: Process with existing thumbnail
        plugin = ThumbnailProcessorPlugin()
        result = plugin.process_thumbnails(context)

        # Assert: Plugin should use cached thumbnail
        assert result.success is True
        photo1 = result.output_data["photos"][0]
        assert "thumbnail_path" in photo1
        assert "cached" in photo1
        assert photo1["cached"] is True

    def test_thumbnail_processor_integration_with_provider_output(self, tmp_path):
        """ThumbnailProcessorPlugin should work seamlessly with NormPicProviderPlugin output.

        This test ensures full integration between Provider → Processor pipeline.
        """
        # These imports will FAIL initially - that's expected for TDD red phase
        from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin
        from galleria.plugins.providers.normpic import NormPicProviderPlugin

        # Arrange: Create real manifest and source images
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        output_dir = tmp_path / "output"

        # Create test images
        img1_path = source_dir / "IMG_001.jpg"
        img2_path = source_dir / "IMG_002.jpg"
        img1 = Image.new('RGB', (1000, 750), color='purple')
        img1.save(img1_path, 'JPEG')
        img2 = Image.new('RGB', (800, 1200), color='orange')
        img2.save(img2_path, 'JPEG')

        # Create NormPic manifest
        manifest_data = {
            "collection_name": "integration_test",
            "pics": [
                {
                    "source_path": str(img1_path),
                    "dest_path": "test/IMG_001.jpg",
                    "hash": "integration123",
                    "size_bytes": 1000000,
                    "mtime": 1635789012.34
                },
                {
                    "source_path": str(img2_path),
                    "dest_path": "test/IMG_002.jpg",
                    "hash": "integration456",
                    "size_bytes": 1200000,
                    "mtime": 1635789015.67
                }
            ]
        }

        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest_data))

        # Act: Run Provider → Processor pipeline
        # Stage 1: Provider loads collection
        provider = NormPicProviderPlugin()
        provider_context = PluginContext(
            input_data={"manifest_path": str(manifest_path)},
            config={},
            output_dir=output_dir
        )
        provider_result = provider.load_collection(provider_context)

        # Stage 2: Processor processes provider output
        processor = ThumbnailProcessorPlugin()
        processor_context = PluginContext(
            input_data=provider_result.output_data,
            config={"thumbnail_size": 400, "quality": 90},
            output_dir=output_dir
        )
        processor_result = processor.process_thumbnails(processor_context)

        # Assert: End-to-end pipeline success
        assert provider_result.success is True
        assert processor_result.success is True

        # Assert: Data flow through pipeline
        assert provider_result.output_data["collection_name"] == "integration_test"
        assert processor_result.output_data["collection_name"] == "integration_test"
        assert processor_result.output_data["thumbnail_count"] == 2

        # Assert: Thumbnail generation with provider data preservation
        photos = processor_result.output_data["photos"]
        photo1 = photos[0]

        # Provider data preserved
        assert photo1["source_path"] == str(img1_path)
        assert photo1["dest_path"] == "test/IMG_001.jpg"
        assert photo1["metadata"]["hash"] == "integration123"

        # Processor data added
        assert "thumbnail_path" in photo1
        assert "thumbnail_size" in photo1
        thumbnail_path = Path(photo1["thumbnail_path"])
        assert thumbnail_path.exists()

        # Verify actual thumbnail
        with Image.open(thumbnail_path) as thumb:
            assert thumb.size == (400, 400)
            assert thumb.format == "WEBP"
