"""Integration tests for parallel thumbnail processing."""

from pathlib import Path

from PIL import Image

from galleria.plugins import PluginContext
from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin


class TestParallelThumbnailProcessing:
    """Integration tests for parallel thumbnail processing with ProcessPoolExecutor."""

    def test_parallel_processing_generates_all_thumbnails(self, tmp_path):
        """Test that parallel processing generates thumbnails for all photos."""
        # Arrange: Create multiple test source images
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        num_photos = 5

        photos = []
        for i in range(1, num_photos + 1):
            img_path = source_dir / f"IMG_{i:03d}.jpg"
            img = Image.new("RGB", (800, 600), color=(255 - i * 40, i * 50, 100))
            img.save(img_path, "JPEG")
            photos.append(
                {
                    "source_path": str(img_path),
                    "dest_path": f"test/IMG_{i:03d}.jpg",
                    "metadata": {"index": i},
                }
            )

        provider_data = {
            "photos": photos,
            "collection_name": "parallel_test",
        }

        context = PluginContext(
            input_data=provider_data,
            config={"thumbnail_size": 200, "parallel": True, "max_workers": 2},
            output_dir=tmp_path / "output",
        )

        # Act
        plugin = ThumbnailProcessorPlugin()
        result = plugin.process_thumbnails(context)

        # Assert: All thumbnails generated
        assert result.success is True
        assert result.output_data["thumbnail_count"] == num_photos

        # Assert: All photos have thumbnail_path
        for photo in result.output_data["photos"]:
            assert "thumbnail_path" in photo
            thumbnail_path = Path(photo["thumbnail_path"])
            assert thumbnail_path.exists()

    def test_parallel_processing_matches_sequential_output(self, tmp_path):
        """Test that parallel processing produces same results as sequential."""
        # Arrange: Create test source images
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        num_photos = 3

        photos = []
        for i in range(1, num_photos + 1):
            img_path = source_dir / f"IMG_{i:03d}.jpg"
            img = Image.new("RGB", (600, 400), color=(i * 80, i * 60, i * 40))
            img.save(img_path, "JPEG")
            photos.append(
                {
                    "source_path": str(img_path),
                    "dest_path": f"test/IMG_{i:03d}.jpg",
                    "metadata": {"index": i},
                }
            )

        provider_data = {
            "photos": photos,
            "collection_name": "comparison_test",
        }

        # Run sequential
        seq_output = tmp_path / "output_sequential"
        seq_context = PluginContext(
            input_data=provider_data,
            config={"thumbnail_size": 150, "parallel": False},
            output_dir=seq_output,
        )
        plugin = ThumbnailProcessorPlugin()
        seq_result = plugin.process_thumbnails(seq_context)

        # Run parallel
        par_output = tmp_path / "output_parallel"
        par_context = PluginContext(
            input_data=provider_data,
            config={"thumbnail_size": 150, "parallel": True, "max_workers": 2},
            output_dir=par_output,
        )
        par_result = plugin.process_thumbnails(par_context)

        # Assert: Both succeed with same thumbnail count
        assert seq_result.success is True
        assert par_result.success is True
        assert seq_result.output_data["thumbnail_count"] == par_result.output_data["thumbnail_count"]

        # Assert: Same number of photos processed
        assert len(seq_result.output_data["photos"]) == len(par_result.output_data["photos"])

    def test_parallel_processing_collects_all_errors(self, tmp_path):
        """Test that parallel processing collects errors from all photos."""
        # Arrange: Create mix of valid and invalid photos
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        # One valid image
        valid_img_path = source_dir / "valid.jpg"
        img = Image.new("RGB", (400, 300), color="green")
        img.save(valid_img_path, "JPEG")

        # Two invalid images (corrupted files)
        corrupted1 = source_dir / "corrupted1.jpg"
        corrupted1.write_text("not an image")
        corrupted2 = source_dir / "corrupted2.jpg"
        corrupted2.write_text("also not an image")

        photos = [
            {"source_path": str(valid_img_path), "dest_path": "valid.jpg", "metadata": {}},
            {"source_path": str(corrupted1), "dest_path": "corrupted1.jpg", "metadata": {}},
            {"source_path": str(corrupted2), "dest_path": "corrupted2.jpg", "metadata": {}},
        ]

        provider_data = {
            "photos": photos,
            "collection_name": "error_test",
        }

        context = PluginContext(
            input_data=provider_data,
            config={"thumbnail_size": 100, "parallel": True, "max_workers": 2},
            output_dir=tmp_path / "output",
        )

        # Act
        plugin = ThumbnailProcessorPlugin()
        result = plugin.process_thumbnails(context)

        # Assert: Plugin succeeds overall (graceful error handling)
        assert result.success is True

        # Assert: One successful thumbnail, two errors
        assert result.output_data["thumbnail_count"] == 1
        assert len(result.errors) == 2

        # Assert: Valid photo has thumbnail, invalid ones have errors
        photos_by_dest = {p["dest_path"]: p for p in result.output_data["photos"]}
        assert "thumbnail_path" in photos_by_dest["valid.jpg"]
        assert "error" in photos_by_dest["corrupted1.jpg"]
        assert "error" in photos_by_dest["corrupted2.jpg"]

    def test_parallel_processing_respects_caching(self, tmp_path):
        """Test that parallel processing respects thumbnail caching."""
        # Arrange: Create test source image
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        img_path = source_dir / "IMG_001.jpg"
        img = Image.new("RGB", (800, 600), color="purple")
        img.save(img_path, "JPEG")

        output_dir = tmp_path / "output"
        thumbnails_dir = output_dir / "thumbnails"
        thumbnails_dir.mkdir(parents=True)

        # Create existing thumbnail
        existing_thumb = thumbnails_dir / "IMG_001.webp"
        thumb = Image.new("RGB", (200, 200), color="purple")
        thumb.save(existing_thumb, "WEBP")

        photos = [
            {"source_path": str(img_path), "dest_path": "test/IMG_001.jpg", "metadata": {}}
        ]

        provider_data = {
            "photos": photos,
            "collection_name": "cache_test",
        }

        context = PluginContext(
            input_data=provider_data,
            config={"thumbnail_size": 200, "parallel": True, "max_workers": 2, "use_cache": True},
            output_dir=output_dir,
        )

        # Act
        plugin = ThumbnailProcessorPlugin()
        result = plugin.process_thumbnails(context)

        # Assert: Should use cached thumbnail
        assert result.success is True
        photo = result.output_data["photos"][0]
        assert photo["cached"] is True
