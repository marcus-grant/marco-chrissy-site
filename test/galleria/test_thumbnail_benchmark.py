"""Tests for thumbnail encoding benchmark instrumentation.

This module is kept separate for future galleria extraction.
"""

from galleria.benchmark import ThumbnailBenchmark


class TestThumbnailBenchmark:
    """Test thumbnail encoding performance metrics collection."""

    def test_thumbnail_encode_timing_per_photo(
        self,
        galleria_temp_filesystem,
        galleria_image_factory,
        galleria_file_factory,
    ):
        """Test that thumbnail encoding captures per-photo timing."""
        # Setup: Create test images (to verify fixtures work)
        galleria_image_factory("IMG_001.jpg", directory="source", size=(1200, 800))
        galleria_image_factory("IMG_002.jpg", directory="source", size=(1200, 800))
        galleria_image_factory("IMG_003.jpg", directory="source", size=(1200, 800))

        # Act: Simulate thumbnail encoding with benchmark
        benchmark = ThumbnailBenchmark()
        benchmark.record_photo(duration_s=0.15, output_bytes=25000)
        benchmark.record_photo(duration_s=0.12, output_bytes=23000)
        benchmark.record_photo(duration_s=0.18, output_bytes=27000)

        # Assert: Per-photo timing captured
        metrics = benchmark.get_metrics()
        assert "per_photo_times" in metrics, "Should capture per-photo times"
        assert len(metrics["per_photo_times"]) == 3, "Should have timing for each photo"
        assert all(t > 0 for t in metrics["per_photo_times"]), "Times should be positive"

    def test_thumbnail_batch_throughput(
        self,
        galleria_temp_filesystem,
        galleria_image_factory,
    ):
        """Test that thumbnail encoding captures batch throughput metrics."""
        # Setup: Create test images (to verify fixtures work)
        for i in range(5):
            galleria_image_factory(
                f"IMG_{i:03d}.jpg", directory="source", size=(1200, 800)
            )

        # Act: Simulate thumbnail encoding with benchmark
        benchmark = ThumbnailBenchmark()
        for i in range(5):
            benchmark.record_photo(duration_s=0.1 + i * 0.02, output_bytes=20000 + i * 1000)

        # Assert: Batch throughput captured
        metrics = benchmark.get_metrics()
        assert "total_duration_s" in metrics, "Should capture total duration"
        assert "photos_per_second" in metrics, "Should calculate throughput"
        assert metrics["photos_per_second"] > 0, "Throughput should be positive"
        # Verify calculation: 5 photos / total_duration
        expected_throughput = 5 / metrics["total_duration_s"]
        assert abs(metrics["photos_per_second"] - expected_throughput) < 0.001

    def test_thumbnail_output_size_metrics(
        self,
        galleria_temp_filesystem,
        galleria_image_factory,
    ):
        """Test that thumbnail encoding captures output size metrics."""
        # Setup: Create test images of varying sizes (to verify fixtures work)
        galleria_image_factory("small.jpg", directory="source", size=(800, 600))
        galleria_image_factory("medium.jpg", directory="source", size=(1600, 1200))
        galleria_image_factory("large.jpg", directory="source", size=(3200, 2400))

        # Act: Simulate thumbnail encoding with benchmark
        benchmark = ThumbnailBenchmark()
        benchmark.record_photo(duration_s=0.08, output_bytes=15000)  # small
        benchmark.record_photo(duration_s=0.12, output_bytes=25000)  # medium
        benchmark.record_photo(duration_s=0.20, output_bytes=35000)  # large

        # Assert: Size metrics captured
        metrics = benchmark.get_metrics()
        assert "output_sizes" in metrics, "Should capture output sizes"
        assert "total_output_bytes" in metrics, "Should capture total bytes"
        assert "average_output_bytes" in metrics, "Should calculate average"
        assert len(metrics["output_sizes"]) == 3, "Should have size for each thumbnail"
        # Verify calculations
        assert metrics["total_output_bytes"] == 75000
        assert metrics["average_output_bytes"] == 25000
