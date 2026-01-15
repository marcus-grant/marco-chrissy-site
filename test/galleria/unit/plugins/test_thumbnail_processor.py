"""Unit tests for ThumbnailProcessorPlugin implementation."""

from pathlib import Path

from PIL import Image

from galleria.plugins import PluginContext
from galleria.plugins.processors.thumbnail import _process_single_photo


class TestThumbnailProcessorPlugin:
    """Unit tests for ThumbnailProcessorPlugin.process_thumbnails() method."""

    def test_process_thumbnails_returns_success_with_valid_provider_data(
        self, tmp_path
    ):
        """Test that process_thumbnails returns PluginResult with success=True for valid input."""
        # This import will FAIL initially - expected for TDD red phase
        from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin

        # Arrange: Create test source image
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        img_path = source_dir / "IMG_001.jpg"
        img = Image.new("RGB", (800, 600), color="red")
        img.save(img_path, "JPEG")

        # Arrange: Valid provider plugin output format
        provider_data = {
            "photos": [
                {
                    "source_path": str(img_path),
                    "dest_path": "test/IMG_001.jpg",
                    "metadata": {
                        "hash": "abc123",
                        "size_bytes": 1000000,
                        "mtime": 1635789012.34,
                    },
                }
            ],
            "collection_name": "test_collection",
        }

        context = PluginContext(
            input_data=provider_data,
            config={"thumbnail_size": 300, "quality": 80},
            output_dir=tmp_path / "output",
        )

        # Act
        plugin = ThumbnailProcessorPlugin()
        result = plugin.process_thumbnails(context)

        # Assert
        assert result.success is True
        assert result.errors == []

    def test_process_thumbnails_returns_required_processor_contract_fields(
        self, tmp_path
    ):
        """Test that process_thumbnails returns all required ProcessorPlugin contract fields."""
        from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin

        # Arrange: Create test source image
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        img_path = source_dir / "IMG_001.jpg"
        img = Image.new("RGB", (1200, 800), color="blue")
        img.save(img_path, "JPEG")

        provider_data = {
            "photos": [
                {
                    "source_path": str(img_path),
                    "dest_path": "wedding/IMG_001.jpg",
                    "metadata": {
                        "hash": "hash123",
                        "size_bytes": 2000000,
                        "mtime": 1635789015.67,
                        "camera": "Canon EOS R5",
                    },
                }
            ],
            "collection_name": "wedding_photos",
            "collection_description": "Wedding photos",
        }

        context = PluginContext(
            input_data=provider_data,
            config={"thumbnail_size": 400},
            output_dir=tmp_path / "output",
        )

        # Act
        plugin = ThumbnailProcessorPlugin()
        result = plugin.process_thumbnails(context)

        # Assert: Required ProcessorPlugin contract fields
        assert "photos" in result.output_data
        assert "collection_name" in result.output_data
        assert "thumbnail_count" in result.output_data
        assert isinstance(result.output_data["photos"], list)
        assert result.output_data["collection_name"] == "wedding_photos"
        assert result.output_data["thumbnail_count"] == 1

    def test_process_thumbnails_adds_thumbnail_data_to_photos(self, tmp_path):
        """Test that each photo gets thumbnail_path and thumbnail_size added."""
        from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin

        # Arrange: Create test source image
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        img_path = source_dir / "IMG_001.jpg"
        img = Image.new("RGB", (1000, 1000), color="green")
        img.save(img_path, "JPEG")

        provider_data = {
            "photos": [
                {
                    "source_path": str(img_path),
                    "dest_path": "test/IMG_001.jpg",
                    "metadata": {
                        "hash": "abc123def456",
                        "size_bytes": 25000000,
                        "mtime": 1635789012.34,
                        "camera": "Sony A7R IV",
                    },
                }
            ],
            "collection_name": "test",
        }

        context = PluginContext(
            input_data=provider_data,
            config={"thumbnail_size": 350, "quality": 75},
            output_dir=tmp_path / "output",
        )

        # Act
        plugin = ThumbnailProcessorPlugin()
        result = plugin.process_thumbnails(context)

        # Assert: Photo has ProcessorPlugin additions
        photo = result.output_data["photos"][0]

        # Original provider data preserved
        assert photo["source_path"] == str(img_path)
        assert photo["dest_path"] == "test/IMG_001.jpg"
        assert photo["metadata"]["camera"] == "Sony A7R IV"

        # New processor data added
        assert "thumbnail_path" in photo
        assert "thumbnail_size" in photo
        assert photo["thumbnail_size"] == (350, 350)  # Square thumbnails

        # Verify thumbnail file actually exists
        thumbnail_path = Path(photo["thumbnail_path"])
        assert thumbnail_path.exists()
        assert thumbnail_path.suffix == ".webp"

    def test_process_thumbnails_handles_missing_source_files(self, tmp_path):
        """Test that missing source files are handled gracefully with error information."""
        from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin

        # Arrange: Provider data with non-existent source file
        provider_data = {
            "photos": [
                {
                    "source_path": "/nonexistent/IMG_001.jpg",
                    "dest_path": "test/IMG_001.jpg",
                    "metadata": {"hash": "abc123"},
                }
            ],
            "collection_name": "test",
        }

        context = PluginContext(
            input_data=provider_data,
            config={"thumbnail_size": 300},
            output_dir=tmp_path / "output",
        )

        # Act
        plugin = ThumbnailProcessorPlugin()
        result = plugin.process_thumbnails(context)

        # Assert: Should continue processing with error info
        assert (
            result.success is True
        )  # Plugin continues despite individual photo errors
        photo = result.output_data["photos"][0]

        # Original data preserved
        assert photo["source_path"] == "/nonexistent/IMG_001.jpg"
        assert photo["dest_path"] == "test/IMG_001.jpg"

        # Error information added
        assert "error" in photo
        assert len(result.errors) > 0 or "error" in photo

    def test_process_thumbnails_validates_input_data_format(self, tmp_path):
        """Test that invalid input data returns validation failure."""
        from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin

        # Arrange: Invalid input data (missing photos field)
        invalid_data = {
            "collection_name": "test"
            # Missing photos field
        }

        context = PluginContext(
            input_data=invalid_data, config={}, output_dir=tmp_path / "output"
        )

        # Act
        plugin = ThumbnailProcessorPlugin()
        result = plugin.process_thumbnails(context)

        # Assert
        assert result.success is False
        assert len(result.errors) > 0
        assert any("photos" in error.lower() for error in result.errors)

    def test_process_thumbnails_validates_missing_collection_name(self, tmp_path):
        """Test that missing collection_name returns validation failure."""
        from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin

        # Arrange: Input data without collection_name
        invalid_data = {
            "photos": [
                {
                    "source_path": "/test/IMG_001.jpg",
                    "dest_path": "test/IMG_001.jpg",
                    "metadata": {"hash": "abc123"},
                }
            ]
            # Missing collection_name
        }

        context = PluginContext(
            input_data=invalid_data, config={}, output_dir=tmp_path / "output"
        )

        # Act
        plugin = ThumbnailProcessorPlugin()
        result = plugin.process_thumbnails(context)

        # Assert
        assert result.success is False
        assert any("collection_name" in error.lower() for error in result.errors)

    def test_process_thumbnails_uses_configuration_options(self, tmp_path):
        """Test that plugin respects configuration options for size and quality."""
        from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin

        # Arrange: Create test source image
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        img_path = source_dir / "IMG_001.jpg"
        img = Image.new("RGB", (1600, 1200), color="yellow")
        img.save(img_path, "JPEG")

        provider_data = {
            "photos": [
                {
                    "source_path": str(img_path),
                    "dest_path": "test/IMG_001.jpg",
                    "metadata": {"hash": "config123"},
                }
            ],
            "collection_name": "config_test",
        }

        # Test custom configuration
        context = PluginContext(
            input_data=provider_data,
            config={"thumbnail_size": 500, "quality": 95, "output_format": "webp"},
            output_dir=tmp_path / "output",
        )

        # Act
        plugin = ThumbnailProcessorPlugin()
        result = plugin.process_thumbnails(context)

        # Assert: Configuration applied
        photo = result.output_data["photos"][0]
        assert photo["thumbnail_size"] == (500, 500)

        # Verify actual thumbnail size
        thumbnail_path = Path(photo["thumbnail_path"])
        with Image.open(thumbnail_path) as thumb:
            assert thumb.size == (500, 500)
            assert thumb.format == "WEBP"

    def test_process_thumbnails_implements_caching(self, tmp_path):
        """Test that plugin implements caching to skip existing valid thumbnails."""
        from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin

        # Arrange: Create test source image
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        output_dir = tmp_path / "output"
        thumbnails_dir = output_dir / "thumbnails"
        thumbnails_dir.mkdir(parents=True)

        img_path = source_dir / "IMG_001.jpg"
        img = Image.new("RGB", (800, 600), color="purple")
        img.save(img_path, "JPEG")

        # Create existing thumbnail (simulate previous processing)
        existing_thumb = thumbnails_dir / "IMG_001.webp"
        thumb = Image.new("RGB", (300, 300), color="purple")
        thumb.save(existing_thumb, "WEBP")

        provider_data = {
            "photos": [
                {
                    "source_path": str(img_path),
                    "dest_path": "test/IMG_001.jpg",
                    "metadata": {"hash": "cache123"},
                }
            ],
            "collection_name": "cache_test",
        }

        context = PluginContext(
            input_data=provider_data,
            config={"thumbnail_size": 300, "use_cache": True},
            output_dir=output_dir,
        )

        # Act
        plugin = ThumbnailProcessorPlugin()
        result = plugin.process_thumbnails(context)

        # Assert: Should use cached thumbnail
        assert result.success is True
        photo = result.output_data["photos"][0]
        assert "thumbnail_path" in photo
        assert "cached" in photo
        assert photo["cached"] is True

    def test_process_thumbnails_handles_corrupted_images(self, tmp_path):
        """Test that corrupted images are handled gracefully."""
        from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin

        # Arrange: Create corrupted image file
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        corrupted_img = source_dir / "corrupted.jpg"
        corrupted_img.write_text("This is not a valid image file")

        provider_data = {
            "photos": [
                {
                    "source_path": str(corrupted_img),
                    "dest_path": "test/corrupted.jpg",
                    "metadata": {"hash": "corrupted123"},
                }
            ],
            "collection_name": "corruption_test",
        }

        context = PluginContext(
            input_data=provider_data,
            config={"thumbnail_size": 300},
            output_dir=tmp_path / "output",
        )

        # Act
        plugin = ThumbnailProcessorPlugin()
        result = plugin.process_thumbnails(context)

        # Assert: Should handle corruption gracefully
        assert result.success is True  # Plugin continues despite individual failures
        photo = result.output_data["photos"][0]
        assert "error" in photo
        assert photo["source_path"] == str(corrupted_img)  # Original data preserved

    def test_plugin_has_required_properties(self):
        """Test that ThumbnailProcessorPlugin implements required BasePlugin properties."""
        from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin

        # Act
        plugin = ThumbnailProcessorPlugin()

        # Assert: BasePlugin interface requirements
        assert hasattr(plugin, "name")
        assert hasattr(plugin, "version")
        assert isinstance(plugin.name, str)
        assert isinstance(plugin.version, str)
        assert len(plugin.name) > 0
        assert len(plugin.version) > 0

    def test_process_thumbnails_preserves_all_provider_data(self, tmp_path):
        """Test that all provider data is preserved through processing."""
        from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin

        # Arrange: Create test source image
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        img_path = source_dir / "IMG_001.jpg"
        img = Image.new("RGB", (1200, 900), color="orange")
        img.save(img_path, "JPEG")

        # Provider data with all optional fields
        provider_data = {
            "photos": [
                {
                    "source_path": str(img_path),
                    "dest_path": "test/IMG_001.jpg",
                    "metadata": {
                        "hash": "preserve123",
                        "size_bytes": 1500000,
                        "mtime": 1635789012.34,
                        "camera": "Nikon D850",
                        "gps": {"lat": 37.7749, "lon": -122.4194},
                        "custom_field": "custom_value",
                    },
                }
            ],
            "collection_name": "preservation_test",
            "collection_description": "Test preserving data",
            "manifest_version": "0.1.0",
        }

        context = PluginContext(
            input_data=provider_data,
            config={"thumbnail_size": 250},
            output_dir=tmp_path / "output",
        )

        # Act
        plugin = ThumbnailProcessorPlugin()
        result = plugin.process_thumbnails(context)

        # Assert: All original data preserved
        output = result.output_data
        assert output["collection_name"] == "preservation_test"
        assert output["collection_description"] == "Test preserving data"
        assert output["manifest_version"] == "0.1.0"

        photo = output["photos"][0]
        assert photo["source_path"] == str(img_path)
        assert photo["dest_path"] == "test/IMG_001.jpg"

        metadata = photo["metadata"]
        assert metadata["camera"] == "Nikon D850"
        assert metadata["gps"] == {"lat": 37.7749, "lon": -122.4194}
        assert metadata["custom_field"] == "custom_value"

        # New processor data added
        assert "thumbnail_path" in photo
        assert photo["thumbnail_size"] == (250, 250)


class TestProcessSinglePhoto:
    """Unit tests for _process_single_photo standalone function."""

    def test_process_single_photo_creates_thumbnail(self, tmp_path):
        """Test that _process_single_photo creates a thumbnail file."""
        # Arrange: Create test source image
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        img_path = source_dir / "IMG_001.jpg"
        img = Image.new("RGB", (800, 600), color="red")
        img.save(img_path, "JPEG")

        thumbnails_dir = tmp_path / "thumbnails"
        thumbnails_dir.mkdir()

        photo = {
            "source_path": str(img_path),
            "dest_path": "test/IMG_001.jpg",
            "metadata": {"hash": "test123"},
        }

        # Act
        result = _process_single_photo(
            photo=photo,
            thumbnails_dir=thumbnails_dir,
            thumbnail_size=200,
            quality=80,
            output_format="webp",
            use_cache=True,
        )

        # Assert
        assert "thumbnail_path" in result
        assert "thumbnail_size" in result
        assert result["thumbnail_size"] == (200, 200)
        assert result["cached"] is False
        assert "error" not in result

        # Verify file exists
        thumbnail_path = Path(result["thumbnail_path"])
        assert thumbnail_path.exists()
        assert thumbnail_path.suffix == ".webp"

    def test_process_single_photo_uses_cache(self, tmp_path):
        """Test that _process_single_photo uses cached thumbnail when valid."""
        # Arrange: Create test source image
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        img_path = source_dir / "IMG_001.jpg"
        img = Image.new("RGB", (800, 600), color="blue")
        img.save(img_path, "JPEG")

        thumbnails_dir = tmp_path / "thumbnails"
        thumbnails_dir.mkdir()

        # Create existing thumbnail (older than source won't work, but same time does)
        existing_thumb = thumbnails_dir / "IMG_001.webp"
        thumb = Image.new("RGB", (200, 200), color="blue")
        thumb.save(existing_thumb, "WEBP")

        photo = {
            "source_path": str(img_path),
            "dest_path": "test/IMG_001.jpg",
            "metadata": {},
        }

        # Act
        result = _process_single_photo(
            photo=photo,
            thumbnails_dir=thumbnails_dir,
            thumbnail_size=200,
            quality=80,
            output_format="webp",
            use_cache=True,
        )

        # Assert: Should use cached version
        assert "thumbnail_path" in result
        assert result["cached"] is True
        assert "error" not in result

    def test_process_single_photo_handles_missing_file(self, tmp_path):
        """Test that _process_single_photo handles missing source file."""
        thumbnails_dir = tmp_path / "thumbnails"
        thumbnails_dir.mkdir()

        photo = {
            "source_path": "/nonexistent/IMG_001.jpg",
            "dest_path": "test/IMG_001.jpg",
            "metadata": {},
        }

        # Act
        result = _process_single_photo(
            photo=photo,
            thumbnails_dir=thumbnails_dir,
            thumbnail_size=200,
            quality=80,
            output_format="webp",
            use_cache=True,
        )

        # Assert: Should return error
        assert "error" in result
        assert result["source_path"] == "/nonexistent/IMG_001.jpg"

    def test_process_single_photo_handles_corrupted_image(self, tmp_path):
        """Test that _process_single_photo handles corrupted image."""
        # Arrange: Create corrupted image file
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        corrupted_img = source_dir / "corrupted.jpg"
        corrupted_img.write_text("This is not a valid image")

        thumbnails_dir = tmp_path / "thumbnails"
        thumbnails_dir.mkdir()

        photo = {
            "source_path": str(corrupted_img),
            "dest_path": "test/corrupted.jpg",
            "metadata": {},
        }

        # Act
        result = _process_single_photo(
            photo=photo,
            thumbnails_dir=thumbnails_dir,
            thumbnail_size=200,
            quality=80,
            output_format="webp",
            use_cache=True,
        )

        # Assert: Should return error
        assert "error" in result
        assert result["source_path"] == str(corrupted_img)

    def test_process_single_photo_preserves_original_data(self, tmp_path):
        """Test that _process_single_photo preserves all original photo data."""
        # Arrange: Create test source image
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        img_path = source_dir / "IMG_001.jpg"
        img = Image.new("RGB", (800, 600), color="green")
        img.save(img_path, "JPEG")

        thumbnails_dir = tmp_path / "thumbnails"
        thumbnails_dir.mkdir()

        photo = {
            "source_path": str(img_path),
            "dest_path": "test/IMG_001.jpg",
            "metadata": {
                "hash": "abc123",
                "camera": "Canon EOS R5",
                "custom_field": "custom_value",
            },
        }

        # Act
        result = _process_single_photo(
            photo=photo,
            thumbnails_dir=thumbnails_dir,
            thumbnail_size=200,
            quality=80,
            output_format="webp",
            use_cache=True,
        )

        # Assert: Original data preserved
        assert result["source_path"] == str(img_path)
        assert result["dest_path"] == "test/IMG_001.jpg"
        assert result["metadata"]["hash"] == "abc123"
        assert result["metadata"]["camera"] == "Canon EOS R5"
        assert result["metadata"]["custom_field"] == "custom_value"


class TestParallelConfig:
    """Tests for parallel processing configuration options."""

    def test_parallel_defaults_to_false(self, tmp_path):
        """Test that parallel processing is disabled by default."""
        from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin

        # Arrange: Create test source image
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        img_path = source_dir / "IMG_001.jpg"
        img = Image.new("RGB", (800, 600), color="red")
        img.save(img_path, "JPEG")

        provider_data = {
            "photos": [
                {
                    "source_path": str(img_path),
                    "dest_path": "test/IMG_001.jpg",
                    "metadata": {},
                }
            ],
            "collection_name": "test",
        }

        # No parallel config specified
        context = PluginContext(
            input_data=provider_data,
            config={"thumbnail_size": 200},
            output_dir=tmp_path / "output",
        )

        # Act
        plugin = ThumbnailProcessorPlugin()
        result = plugin.process_thumbnails(context)

        # Assert: Processing succeeds (parallel=False by default, uses sequential)
        assert result.success is True
        assert result.output_data["thumbnail_count"] == 1

    def test_parallel_config_is_parsed(self, tmp_path):
        """Test that parallel=True config is parsed correctly."""
        from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin

        # Arrange: Create test source image
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        img_path = source_dir / "IMG_001.jpg"
        img = Image.new("RGB", (800, 600), color="blue")
        img.save(img_path, "JPEG")

        provider_data = {
            "photos": [
                {
                    "source_path": str(img_path),
                    "dest_path": "test/IMG_001.jpg",
                    "metadata": {},
                }
            ],
            "collection_name": "test",
        }

        # Explicit parallel config (still uses sequential until Commit 6)
        context = PluginContext(
            input_data=provider_data,
            config={"thumbnail_size": 200, "parallel": True, "max_workers": 2},
            output_dir=tmp_path / "output",
        )

        # Act
        plugin = ThumbnailProcessorPlugin()
        result = plugin.process_thumbnails(context)

        # Assert: Processing succeeds (config is parsed, parallel impl comes in Commit 6)
        assert result.success is True
        assert result.output_data["thumbnail_count"] == 1

    def test_max_workers_config_is_parsed(self, tmp_path):
        """Test that max_workers config is parsed correctly."""
        from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin

        # Arrange: Create test source image
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        img_path = source_dir / "IMG_001.jpg"
        img = Image.new("RGB", (800, 600), color="green")
        img.save(img_path, "JPEG")

        provider_data = {
            "photos": [
                {
                    "source_path": str(img_path),
                    "dest_path": "test/IMG_001.jpg",
                    "metadata": {},
                }
            ],
            "collection_name": "test",
        }

        # Explicit max_workers config
        context = PluginContext(
            input_data=provider_data,
            config={"thumbnail_size": 200, "parallel": True, "max_workers": 4},
            output_dir=tmp_path / "output",
        )

        # Act
        plugin = ThumbnailProcessorPlugin()
        result = plugin.process_thumbnails(context)

        # Assert: Processing succeeds
        assert result.success is True
        assert result.output_data["thumbnail_count"] == 1


class TestBenchmarkIntegration:
    """Tests for benchmark metrics collection."""

    def test_benchmark_disabled_by_default(self, tmp_path):
        """Test that benchmark data is not collected by default."""
        from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin

        # Arrange: Create test source image
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        img_path = source_dir / "IMG_001.jpg"
        img = Image.new("RGB", (800, 600), color="red")
        img.save(img_path, "JPEG")

        provider_data = {
            "photos": [
                {
                    "source_path": str(img_path),
                    "dest_path": "test/IMG_001.jpg",
                    "metadata": {},
                }
            ],
            "collection_name": "test",
        }

        # No benchmark config
        context = PluginContext(
            input_data=provider_data,
            config={"thumbnail_size": 200},
            output_dir=tmp_path / "output",
        )

        # Act
        plugin = ThumbnailProcessorPlugin()
        result = plugin.process_thumbnails(context)

        # Assert: No benchmark data in output
        assert result.success is True
        assert "benchmark" not in result.output_data

    def test_benchmark_enabled_collects_metrics(self, tmp_path):
        """Test that benchmark=True collects timing and size metrics."""
        from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin

        # Arrange: Create test source images
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        for i in range(3):
            img_path = source_dir / f"IMG_{i:03d}.jpg"
            img = Image.new("RGB", (800, 600), color=(i * 80, 100, 100))
            img.save(img_path, "JPEG")

        photos = [
            {
                "source_path": str(source_dir / f"IMG_{i:03d}.jpg"),
                "dest_path": f"test/IMG_{i:03d}.jpg",
                "metadata": {},
            }
            for i in range(3)
        ]

        provider_data = {
            "photos": photos,
            "collection_name": "benchmark_test",
        }

        context = PluginContext(
            input_data=provider_data,
            config={"thumbnail_size": 200, "benchmark": True},
            output_dir=tmp_path / "output",
        )

        # Act
        plugin = ThumbnailProcessorPlugin()
        result = plugin.process_thumbnails(context)

        # Assert: Benchmark data present with required fields
        assert result.success is True
        assert "benchmark" in result.output_data

        benchmark = result.output_data["benchmark"]
        assert "per_photo_times" in benchmark
        assert "total_duration_s" in benchmark
        assert "photos_per_second" in benchmark
        assert "output_sizes" in benchmark
        assert "total_output_bytes" in benchmark
        assert "average_output_bytes" in benchmark

        # Verify data integrity
        assert len(benchmark["per_photo_times"]) == 3
        assert len(benchmark["output_sizes"]) == 3
        assert all(t > 0 for t in benchmark["per_photo_times"])
        assert all(s > 0 for s in benchmark["output_sizes"])

    def test_benchmark_with_parallel_processing(self, tmp_path):
        """Test that benchmark works with parallel processing."""
        from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin

        # Arrange: Create test source images
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        for i in range(3):
            img_path = source_dir / f"IMG_{i:03d}.jpg"
            img = Image.new("RGB", (800, 600), color=(100, i * 80, 100))
            img.save(img_path, "JPEG")

        photos = [
            {
                "source_path": str(source_dir / f"IMG_{i:03d}.jpg"),
                "dest_path": f"test/IMG_{i:03d}.jpg",
                "metadata": {},
            }
            for i in range(3)
        ]

        provider_data = {
            "photos": photos,
            "collection_name": "parallel_benchmark_test",
        }

        context = PluginContext(
            input_data=provider_data,
            config={"thumbnail_size": 200, "benchmark": True, "parallel": True, "max_workers": 2},
            output_dir=tmp_path / "output",
        )

        # Act
        plugin = ThumbnailProcessorPlugin()
        result = plugin.process_thumbnails(context)

        # Assert: Benchmark data collected in parallel mode
        assert result.success is True
        assert "benchmark" in result.output_data

        benchmark = result.output_data["benchmark"]
        assert len(benchmark["per_photo_times"]) == 3
        assert len(benchmark["output_sizes"]) == 3

    def test_benchmark_data_not_leaked_to_photos(self, tmp_path):
        """Test that internal benchmark fields are not in photo output."""
        from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin

        # Arrange
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        img_path = source_dir / "IMG_001.jpg"
        img = Image.new("RGB", (800, 600), color="blue")
        img.save(img_path, "JPEG")

        provider_data = {
            "photos": [
                {
                    "source_path": str(img_path),
                    "dest_path": "test/IMG_001.jpg",
                    "metadata": {},
                }
            ],
            "collection_name": "test",
        }

        context = PluginContext(
            input_data=provider_data,
            config={"thumbnail_size": 200, "benchmark": True},
            output_dir=tmp_path / "output",
        )

        # Act
        plugin = ThumbnailProcessorPlugin()
        result = plugin.process_thumbnails(context)

        # Assert: Internal fields removed from photo output
        photo = result.output_data["photos"][0]
        assert "_timing_s" not in photo
        assert "_output_bytes" not in photo
