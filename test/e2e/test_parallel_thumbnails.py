"""E2E tests for parallel thumbnail processing.

Tests the complete parallel thumbnail processing workflow including:
- ProcessPoolExecutor-based parallel processing
- Benchmark metrics collection
- Correct thumbnail generation for all photos
"""

import pytest

from galleria.plugins.base import PluginContext
from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin


@pytest.mark.skip(reason="Parallel processing not implemented")
class TestParallelThumbnails:
    """E2E tests for parallel thumbnail processing."""

    def test_parallel_processing_generates_all_thumbnails(
        self,
        galleria_temp_filesystem,
        galleria_image_factory,
    ):
        """Test parallel processing generates thumbnails for all photos."""
        # Setup: Create test images
        num_photos = 5
        photos = []
        for i in range(1, num_photos + 1):
            source_path = galleria_image_factory(
                f"IMG_{i:03d}.jpg",
                directory="source",
                size=(1200, 800),
                color=(255 - i * 40, i * 50, 100),
            )
            photos.append(
                {
                    "source_path": str(source_path),
                    "dest_path": f"IMG_{i:03d}.jpg",
                    "metadata": {"index": i},
                }
            )

        output_dir = galleria_temp_filesystem / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Setup: Create plugin context with parallel config
        context = PluginContext(
            input_data={
                "photos": photos,
                "collection_name": "test_parallel",
            },
            config={
                "processor": {
                    "thumbnail_size": 200,
                    "quality": 80,
                    "parallel": True,
                    "max_workers": 2,
                }
            },
            output_dir=output_dir,
            metadata={},
        )

        # Act: Run thumbnail processor with parallel=True
        plugin = ThumbnailProcessorPlugin()
        result = plugin.process_thumbnails(context)

        # Assert: Processing succeeded
        assert result.success, f"Processing failed: {result.errors}"

        # Assert: All thumbnails generated
        assert result.output_data is not None
        assert result.output_data["thumbnail_count"] == num_photos

        # Assert: Each photo has thumbnail_path
        for photo in result.output_data["photos"]:
            assert "thumbnail_path" in photo, f"Missing thumbnail_path for {photo}"
            thumbnail_path = galleria_temp_filesystem / "output" / "thumbnails" / (
                photo["dest_path"].replace(".jpg", ".webp")
            )
            assert thumbnail_path.exists(), f"Thumbnail not created: {thumbnail_path}"

    def test_parallel_processing_captures_benchmark_metrics(
        self,
        galleria_temp_filesystem,
        galleria_image_factory,
    ):
        """Test parallel processing captures benchmark metrics when enabled."""
        # Setup: Create test images
        num_photos = 3
        photos = []
        for i in range(1, num_photos + 1):
            source_path = galleria_image_factory(
                f"IMG_{i:03d}.jpg",
                directory="source",
                size=(800, 600),
            )
            photos.append(
                {
                    "source_path": str(source_path),
                    "dest_path": f"IMG_{i:03d}.jpg",
                    "metadata": {},
                }
            )

        output_dir = galleria_temp_filesystem / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Setup: Create plugin context with parallel and benchmark enabled
        context = PluginContext(
            input_data={
                "photos": photos,
                "collection_name": "test_benchmark",
            },
            config={
                "processor": {
                    "thumbnail_size": 200,
                    "quality": 80,
                    "parallel": True,
                    "max_workers": 2,
                    "benchmark": True,
                }
            },
            output_dir=output_dir,
            metadata={},
        )

        # Act: Run thumbnail processor with benchmark=True
        plugin = ThumbnailProcessorPlugin()
        result = plugin.process_thumbnails(context)

        # Assert: Processing succeeded
        assert result.success, f"Processing failed: {result.errors}"

        # Assert: Benchmark metrics present in metadata
        assert result.metadata is not None
        assert "benchmark" in result.metadata, "Missing benchmark in metadata"

        benchmark = result.metadata["benchmark"]

        # Assert: Expected metric keys present
        assert "per_photo_times" in benchmark
        assert "total_duration_s" in benchmark
        assert "photos_per_second" in benchmark
        assert "output_sizes" in benchmark
        assert "total_output_bytes" in benchmark
        assert "average_output_bytes" in benchmark

        # Assert: Metrics have correct counts
        assert len(benchmark["per_photo_times"]) == num_photos
        assert len(benchmark["output_sizes"]) == num_photos
        assert benchmark["photos_per_second"] > 0
        assert benchmark["total_output_bytes"] > 0
