"""Unit tests for benchmark data structures and utilities."""

import json
from datetime import UTC, datetime


class TestBenchmarkResult:
    """Test BenchmarkResult data structure."""

    def test_benchmark_result_has_metadata_section(self):
        """Test BenchmarkResult includes metadata with required fields."""
        from build.benchmark import BenchmarkMetadata, BenchmarkResult

        metadata = BenchmarkMetadata(
            date=datetime.now(UTC),
            commit="abc1234",
            description="Test benchmark",
        )
        result = BenchmarkResult(metadata=metadata)

        assert result.metadata is not None
        assert result.metadata.commit == "abc1234"
        assert result.metadata.description == "Test benchmark"

    def test_benchmark_result_has_build_metrics_section(self):
        """Test BenchmarkResult includes build_metrics with timing fields."""
        from build.benchmark import BenchmarkMetadata, BenchmarkResult, BuildMetrics

        metadata = BenchmarkMetadata(
            date=datetime.now(UTC),
            commit="abc1234",
            description="Test benchmark",
        )
        build_metrics = BuildMetrics(
            validate_duration_s=0.5,
            organize_duration_s=0.4,
            build_duration_s=100.0,
        )
        result = BenchmarkResult(metadata=metadata, build_metrics=build_metrics)

        assert result.build_metrics is not None
        assert result.build_metrics.validate_duration_s == 0.5
        assert result.build_metrics.organize_duration_s == 0.4
        assert result.build_metrics.build_duration_s == 100.0

    def test_benchmark_result_serializes_to_json(self):
        """Test BenchmarkResult can be serialized to JSON."""
        from build.benchmark import BenchmarkMetadata, BenchmarkResult, BuildMetrics

        metadata = BenchmarkMetadata(
            date=datetime(2026, 1, 13, 12, 0, 0, tzinfo=UTC),
            commit="abc1234",
            description="Test benchmark",
            config={"photos_per_page": 96},
            notes="Test notes",
        )
        build_metrics = BuildMetrics(
            validate_duration_s=0.5,
            organize_duration_s=0.4,
            build_duration_s=100.0,
            thumbnail_count=645,
            thumbnail_total_bytes=19000000,
        )
        result = BenchmarkResult(metadata=metadata, build_metrics=build_metrics)

        # Convert to JSON-serializable dict
        json_str = result.to_json()
        data = json.loads(json_str)

        assert "metadata" in data
        assert data["metadata"]["commit"] == "abc1234"
        assert data["metadata"]["config"]["photos_per_page"] == 96
        assert "build_metrics" in data
        assert data["build_metrics"]["validate_duration_s"] == 0.5

    def test_benchmark_metadata_has_optional_config_field(self):
        """Test BenchmarkMetadata config field is optional."""
        from build.benchmark import BenchmarkMetadata

        # Without config
        metadata = BenchmarkMetadata(
            date=datetime.now(UTC),
            commit="abc1234",
            description="Test",
        )
        assert metadata.config is None

        # With config
        metadata_with_config = BenchmarkMetadata(
            date=datetime.now(UTC),
            commit="abc1234",
            description="Test",
            config={"key": "value"},
        )
        assert metadata_with_config.config == {"key": "value"}

    def test_build_metrics_has_optional_size_fields(self):
        """Test BuildMetrics size fields are optional."""
        from build.benchmark import BuildMetrics

        # Minimal metrics (just timing)
        metrics = BuildMetrics(
            validate_duration_s=0.5,
            organize_duration_s=0.4,
            build_duration_s=100.0,
        )
        assert metrics.thumbnail_count is None
        assert metrics.thumbnail_total_bytes is None

        # Full metrics
        full_metrics = BuildMetrics(
            validate_duration_s=0.5,
            organize_duration_s=0.4,
            build_duration_s=100.0,
            thumbnail_count=645,
            thumbnail_total_bytes=19000000,
            html_total_bytes=194000,
            css_total_bytes=2800,
        )
        assert full_metrics.thumbnail_count == 645


class TestBuildMetrics:
    """Test BuildMetrics data structure."""

    def test_build_metrics_calculates_total_pipeline_time(self):
        """Test BuildMetrics can calculate total pipeline duration."""
        from build.benchmark import BuildMetrics

        metrics = BuildMetrics(
            validate_duration_s=0.5,
            organize_duration_s=0.4,
            build_duration_s=100.0,
        )

        assert metrics.total_pipeline_s == 100.9

    def test_build_metrics_total_handles_none_values(self):
        """Test total_pipeline_s handles None values gracefully."""
        from build.benchmark import BuildMetrics

        # Only build duration set
        metrics = BuildMetrics(build_duration_s=100.0)

        # Should still calculate total with available values
        assert metrics.total_pipeline_s == 100.0
