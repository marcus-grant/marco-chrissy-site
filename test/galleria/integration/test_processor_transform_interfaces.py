"""Integration tests for Processor and Transform plugin interfaces."""

from pathlib import Path

from galleria.plugins import PluginContext, PluginResult


class TestProcessorTransformIntegration:
    """Integration tests for Processor ↔ Transform plugin interaction."""

    def test_transform_plugin_manipulates_processor_data(self, tmp_path):
        """Transform plugin should manipulate photo data from Processor output.

        This test defines the contract between Processor and Transform:
        - Processor outputs: {"photos": [...], "thumbnail_count": int}
        - Transform expects: photos list with thumbnail_path
        - Transform outputs: manipulated data (pagination, sorting, filtering)
        """
        from galleria.plugins.interfaces import TransformPlugin

        # Arrange: Create a concrete TransformPlugin implementation
        class TestPaginationTransform(TransformPlugin):
            @property
            def name(self) -> str:
                return "test-pagination-transform"

            @property
            def version(self) -> str:
                return "1.0.0"

            def transform_data(self, context: PluginContext) -> PluginResult:
                """Transform photo collection data."""
                photos = context.input_data["photos"]
                collection_name = context.input_data["collection_name"]

                # Mock pagination logic - split into pages
                photos_per_page = context.config.get("photos_per_page", 2)
                pages = []

                for i in range(0, len(photos), photos_per_page):
                    page_photos = photos[i : i + photos_per_page]
                    pages.append(
                        {
                            "page_number": len(pages) + 1,
                            "photos": page_photos,
                            "photo_count": len(page_photos),
                        }
                    )

                return PluginResult(
                    success=True,
                    output_data={
                        "pages": pages,
                        "collection_name": collection_name,
                        "page_count": len(pages),
                        "total_photos": len(photos),
                    },
                )

        # Create transform and test it with Processor output data
        transform = TestPaginationTransform()

        # Mock Processor output as Transform input
        processor_output = {
            "photos": [
                {
                    "source_path": "/source/photos/IMG_001.jpg",
                    "dest_path": "wedding/IMG_001.jpg",
                    "thumbnail_path": "thumbnails/IMG_001_thumb.webp",
                    "thumbnail_size": (300, 200),
                    "metadata": {"camera": "Canon EOS R5"},
                },
                {
                    "source_path": "/source/photos/IMG_002.jpg",
                    "dest_path": "wedding/IMG_002.jpg",
                    "thumbnail_path": "thumbnails/IMG_002_thumb.webp",
                    "thumbnail_size": (300, 200),
                    "metadata": {"camera": "Canon EOS R5"},
                },
                {
                    "source_path": "/source/photos/IMG_003.jpg",
                    "dest_path": "wedding/IMG_003.jpg",
                    "thumbnail_path": "thumbnails/IMG_003_thumb.webp",
                    "thumbnail_size": (300, 200),
                    "metadata": {"camera": "Canon EOS R5"},
                },
            ],
            "collection_name": "wedding_photos",
            "thumbnail_count": 3,
        }

        context = PluginContext(
            input_data=processor_output,
            config={"photos_per_page": 2},
            output_dir=tmp_path / "output",
        )

        # Act: Execute transform
        result = transform.transform_data(context)

        # Assert: Transform output includes pagination
        assert result.success
        assert "pages" in result.output_data
        assert "page_count" in result.output_data
        assert "total_photos" in result.output_data
        assert result.output_data["page_count"] == 2  # 3 photos, 2 per page = 2 pages
        assert result.output_data["total_photos"] == 3

        # Verify page structure
        pages = result.output_data["pages"]
        assert len(pages) == 2
        assert pages[0]["page_number"] == 1
        assert pages[0]["photo_count"] == 2
        assert pages[1]["page_number"] == 2
        assert pages[1]["photo_count"] == 1

        # Verify photos preserved with thumbnail data
        page1_photo = pages[0]["photos"][0]
        assert "thumbnail_path" in page1_photo
        assert page1_photo["thumbnail_path"] == "thumbnails/IMG_001_thumb.webp"

    def test_transform_plugin_handles_sorting_operations(self, tmp_path):
        """Transform plugin should handle sorting operations on photo data.

        This test validates Transform interface for sorting functionality:
        - Accepts Processor output with photo metadata
        - Sorts photos by various criteria
        - Maintains all photo data including thumbnails
        """
        from galleria.plugins.interfaces import TransformPlugin

        # Arrange: Create a sorting TransformPlugin implementation
        class TestSortTransform(TransformPlugin):
            @property
            def name(self) -> str:
                return "test-sort-transform"

            @property
            def version(self) -> str:
                return "1.0.0"

            def transform_data(self, context: PluginContext) -> PluginResult:
                """Transform photo data by sorting."""
                photos = context.input_data["photos"]
                collection_name = context.input_data["collection_name"]

                # Mock sorting by filename
                sort_key = context.config.get("sort_by", "dest_path")
                reverse = context.config.get("reverse", False)

                sorted_photos = sorted(
                    photos, key=lambda p: p[sort_key], reverse=reverse
                )

                return PluginResult(
                    success=True,
                    output_data={
                        "photos": sorted_photos,
                        "collection_name": collection_name,
                        "sort_criteria": {"key": sort_key, "reverse": reverse},
                        "photo_count": len(sorted_photos),
                    },
                )

        # Mock Processor output with unsorted photos
        processor_output = {
            "photos": [
                {
                    "source_path": "/source/photos/IMG_003.jpg",
                    "dest_path": "wedding/IMG_003.jpg",
                    "thumbnail_path": "thumbnails/IMG_003_thumb.webp",
                },
                {
                    "source_path": "/source/photos/IMG_001.jpg",
                    "dest_path": "wedding/IMG_001.jpg",
                    "thumbnail_path": "thumbnails/IMG_001_thumb.webp",
                },
                {
                    "source_path": "/source/photos/IMG_002.jpg",
                    "dest_path": "wedding/IMG_002.jpg",
                    "thumbnail_path": "thumbnails/IMG_002_thumb.webp",
                },
            ],
            "collection_name": "wedding_photos",
            "thumbnail_count": 3,
        }

        transform = TestSortTransform()
        context = PluginContext(
            input_data=processor_output,
            config={"sort_by": "dest_path", "reverse": False},
            output_dir=tmp_path / "output",
        )

        # Act: Execute sorting transform
        result = transform.transform_data(context)

        # Assert: Photos are sorted correctly
        assert result.success
        assert "photos" in result.output_data
        assert "sort_criteria" in result.output_data

        # Verify sorting worked
        sorted_photos = result.output_data["photos"]
        assert len(sorted_photos) == 3
        assert sorted_photos[0]["dest_path"] == "wedding/IMG_001.jpg"
        assert sorted_photos[1]["dest_path"] == "wedding/IMG_002.jpg"
        assert sorted_photos[2]["dest_path"] == "wedding/IMG_003.jpg"

        # Verify thumbnail data preserved
        assert sorted_photos[0]["thumbnail_path"] == "thumbnails/IMG_001_thumb.webp"

    def test_processor_to_transform_pipeline_integration(self, tmp_path):
        """Test complete Processor → Transform pipeline integration.

        This test verifies the data flow works end-to-end:
        1. Processor generates thumbnails and metadata
        2. Transform receives Processor output as input
        3. Pipeline produces final transformed output
        """
        from galleria.plugins.interfaces import ProcessorPlugin, TransformPlugin

        # Use the same test implementations from above
        class TestThumbnailProcessor(ProcessorPlugin):
            @property
            def name(self) -> str:
                return "test-thumbnail-processor"

            @property
            def version(self) -> str:
                return "1.0.0"

            def process_thumbnails(self, context: PluginContext) -> PluginResult:
                photos = context.input_data["photos"]
                processed_photos = []

                for photo in photos:
                    thumb_name = Path(photo["dest_path"]).stem + "_thumb.webp"
                    processed_photos.append(
                        {
                            **photo,
                            "thumbnail_path": f"thumbnails/{thumb_name}",
                            "thumbnail_size": (300, 200),
                        }
                    )

                return PluginResult(
                    success=True,
                    output_data={
                        "photos": processed_photos,
                        "collection_name": context.input_data["collection_name"],
                        "thumbnail_count": len(processed_photos),
                    },
                )

        class TestPaginationTransform(TransformPlugin):
            @property
            def name(self) -> str:
                return "test-pagination-transform"

            @property
            def version(self) -> str:
                return "1.0.0"

            def transform_data(self, context: PluginContext) -> PluginResult:
                photos = context.input_data["photos"]

                # Simple pagination - 2 photos per page
                pages = []
                for i in range(0, len(photos), 2):
                    pages.append(
                        {"page_number": len(pages) + 1, "photos": photos[i : i + 2]}
                    )

                return PluginResult(
                    success=True,
                    output_data={
                        "pages": pages,
                        "collection_name": context.input_data["collection_name"],
                        "page_count": len(pages),
                    },
                )

        # Arrange: Create output directory
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Act: Execute Processor → Transform pipeline
        processor = TestThumbnailProcessor()
        transform = TestPaginationTransform()

        # Stage 1: Processor (mock Provider output)
        processor_context = PluginContext(
            input_data={
                "photos": [
                    {"source_path": "/source/IMG_001.jpg", "dest_path": "IMG_001.jpg"},
                    {"source_path": "/source/IMG_002.jpg", "dest_path": "IMG_002.jpg"},
                    {"source_path": "/source/IMG_003.jpg", "dest_path": "IMG_003.jpg"},
                ],
                "collection_name": "test_photos",
            },
            config={},
            output_dir=output_dir,
        )
        processor_result = processor.process_thumbnails(processor_context)

        # Stage 2: Transform (uses Processor output as input)
        transform_context = PluginContext(
            input_data=processor_result.output_data,
            config={"photos_per_page": 2},
            output_dir=output_dir,
        )
        transform_result = transform.transform_data(transform_context)

        # Assert: End-to-end pipeline success
        assert processor_result.success
        assert transform_result.success

        # Verify data flow through pipeline
        assert processor_result.output_data["collection_name"] == "test_photos"
        assert transform_result.output_data["collection_name"] == "test_photos"

        # Verify transform operations
        assert transform_result.output_data["page_count"] == 2  # 3 photos / 2 per page

        # Verify thumbnail data preserved through pipeline
        pages = transform_result.output_data["pages"]
        page1_photo = pages[0]["photos"][0]
        assert page1_photo["thumbnail_path"] == "thumbnails/IMG_001_thumb.webp"
        assert page1_photo["thumbnail_size"] == (300, 200)
