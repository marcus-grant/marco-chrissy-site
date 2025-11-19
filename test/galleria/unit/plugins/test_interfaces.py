"""Unit tests for plugin interface definitions."""

from abc import ABC

import pytest

from galleria.plugins import PluginContext, PluginResult
from galleria.plugins.interfaces import ProcessorPlugin, ProviderPlugin, TransformPlugin


class TestProviderPluginInterface:
    """Unit tests for ProviderPlugin interface contract."""

    def test_provider_plugin_is_abstract_base_class(self):
        """ProviderPlugin should be an abstract base class."""
        # Cannot instantiate abstract class directly
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            ProviderPlugin()

    def test_provider_plugin_inherits_from_base_plugin(self):
        """ProviderPlugin should inherit from BasePlugin."""
        from galleria.plugins import BasePlugin

        assert issubclass(ProviderPlugin, BasePlugin)
        assert issubclass(ProviderPlugin, ABC)

    def test_provider_plugin_requires_load_collection_implementation(self):
        """ProviderPlugin subclasses must implement load_collection method."""

        # Incomplete implementation should fail
        class IncompleteProvider(ProviderPlugin):
            @property
            def name(self) -> str:
                return "incomplete"

            @property
            def version(self) -> str:
                return "1.0.0"

            # Missing load_collection implementation

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteProvider()

    def test_provider_plugin_execute_delegates_to_load_collection(self, tmp_path):
        """ProviderPlugin.execute should delegate to load_collection method."""

        class TestProvider(ProviderPlugin):
            def __init__(self):
                self.load_collection_called = False

            @property
            def name(self) -> str:
                return "test-provider"

            @property
            def version(self) -> str:
                return "1.0.0"

            def load_collection(self, context: PluginContext) -> PluginResult:
                self.load_collection_called = True
                return PluginResult(
                    success=True,
                    output_data={"photos": [], "collection_name": "test"}
                )

        provider = TestProvider()
        context = PluginContext(
            input_data={"manifest_path": "test.json"},
            config={},
            output_dir=tmp_path
        )

        # execute should call load_collection
        result = provider.execute(context)

        assert provider.load_collection_called
        assert result.success
        assert result.output_data["collection_name"] == "test"

    def test_provider_plugin_contract_validation(self, tmp_path):
        """Test that ProviderPlugin contract is properly defined."""

        class ValidProvider(ProviderPlugin):
            @property
            def name(self) -> str:
                return "valid-provider"

            @property
            def version(self) -> str:
                return "1.0.0"

            def load_collection(self, context: PluginContext) -> PluginResult:
                # Validate expected input format
                assert "manifest_path" in context.input_data or "source_dir" in context.input_data

                # Return expected output format
                return PluginResult(
                    success=True,
                    output_data={
                        "photos": [
                            {
                                "source_path": "/source/test.jpg",
                                "dest_path": "test.jpg",
                                "metadata": {}
                            }
                        ],
                        "collection_name": "test_collection"
                    }
                )

        provider = ValidProvider()
        context = PluginContext(
            input_data={"manifest_path": "test.json"},
            config={},
            output_dir=tmp_path
        )

        result = provider.load_collection(context)

        # Verify output contract
        assert result.success
        assert "photos" in result.output_data
        assert "collection_name" in result.output_data
        assert isinstance(result.output_data["photos"], list)
        assert isinstance(result.output_data["collection_name"], str)


class TestProcessorPluginInterface:
    """Unit tests for ProcessorPlugin interface contract."""

    def test_processor_plugin_is_abstract_base_class(self):
        """ProcessorPlugin should be an abstract base class."""
        # Cannot instantiate abstract class directly
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            ProcessorPlugin()

    def test_processor_plugin_inherits_from_base_plugin(self):
        """ProcessorPlugin should inherit from BasePlugin."""
        from galleria.plugins import BasePlugin

        assert issubclass(ProcessorPlugin, BasePlugin)
        assert issubclass(ProcessorPlugin, ABC)

    def test_processor_plugin_requires_process_thumbnails_implementation(self):
        """ProcessorPlugin subclasses must implement process_thumbnails method."""

        class IncompleteProcessor(ProcessorPlugin):
            @property
            def name(self) -> str:
                return "incomplete"

            @property
            def version(self) -> str:
                return "1.0.0"

            # Missing process_thumbnails implementation

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteProcessor()

    def test_processor_plugin_execute_delegates_to_process_thumbnails(self, tmp_path):
        """ProcessorPlugin.execute should delegate to process_thumbnails method."""

        class TestProcessor(ProcessorPlugin):
            def __init__(self):
                self.process_thumbnails_called = False

            @property
            def name(self) -> str:
                return "test-processor"

            @property
            def version(self) -> str:
                return "1.0.0"

            def process_thumbnails(self, context: PluginContext) -> PluginResult:
                self.process_thumbnails_called = True
                photos = context.input_data.get("photos", [])
                return PluginResult(
                    success=True,
                    output_data={
                        "photos": photos,
                        "collection_name": context.input_data.get("collection_name", "test"),
                        "thumbnail_count": len(photos)
                    }
                )

        processor = TestProcessor()
        context = PluginContext(
            input_data={
                "photos": [{"source_path": "test.jpg", "dest_path": "test.jpg"}],
                "collection_name": "test"
            },
            config={},
            output_dir=tmp_path
        )

        # execute should call process_thumbnails
        result = processor.execute(context)

        assert processor.process_thumbnails_called
        assert result.success
        assert result.output_data["thumbnail_count"] == 1

    def test_processor_plugin_contract_validation(self, tmp_path):
        """Test that ProcessorPlugin contract is properly defined."""

        class ValidProcessor(ProcessorPlugin):
            @property
            def name(self) -> str:
                return "valid-processor"

            @property
            def version(self) -> str:
                return "1.0.0"

            def process_thumbnails(self, context: PluginContext) -> PluginResult:
                # Validate expected input format (from ProviderPlugin)
                assert "photos" in context.input_data
                assert "collection_name" in context.input_data

                photos = context.input_data["photos"]
                processed_photos = []

                for photo in photos:
                    # Validate provider photo format
                    assert "source_path" in photo
                    assert "dest_path" in photo

                    # Add processor data
                    processed_photos.append({
                        **photo,
                        "thumbnail_path": f"thumbs/{photo['dest_path']}.webp",
                        "thumbnail_size": (300, 200)
                    })

                return PluginResult(
                    success=True,
                    output_data={
                        "photos": processed_photos,
                        "collection_name": context.input_data["collection_name"],
                        "thumbnail_count": len(processed_photos)
                    }
                )

        processor = ValidProcessor()
        context = PluginContext(
            input_data={
                "photos": [
                    {
                        "source_path": "/source/test.jpg",
                        "dest_path": "test.jpg",
                        "metadata": {}
                    }
                ],
                "collection_name": "test_collection"
            },
            config={},
            output_dir=tmp_path
        )

        result = processor.process_thumbnails(context)

        # Verify output contract
        assert result.success
        assert "photos" in result.output_data
        assert "collection_name" in result.output_data
        assert "thumbnail_count" in result.output_data

        # Verify thumbnail data added
        processed_photo = result.output_data["photos"][0]
        assert "thumbnail_path" in processed_photo
        assert "thumbnail_size" in processed_photo
        assert processed_photo["thumbnail_path"] == "thumbs/test.jpg.webp"
        assert processed_photo["thumbnail_size"] == (300, 200)


class TestInterfaceIntegration:
    """Unit tests for interface integration and validation."""

    def test_provider_output_matches_processor_input_contract(self, tmp_path):
        """Provider output format should match Processor input expectations."""

        class TestProvider(ProviderPlugin):
            @property
            def name(self) -> str:
                return "contract-provider"

            @property
            def version(self) -> str:
                return "1.0.0"

            def load_collection(self, context: PluginContext) -> PluginResult:
                return PluginResult(
                    success=True,
                    output_data={
                        "photos": [
                            {
                                "source_path": "/source/img1.jpg",
                                "dest_path": "gallery/img1.jpg",
                                "metadata": {"size": 1024}
                            }
                        ],
                        "collection_name": "contract_test"
                    }
                )

        class TestProcessor(ProcessorPlugin):
            @property
            def name(self) -> str:
                return "contract-processor"

            @property
            def version(self) -> str:
                return "1.0.0"

            def process_thumbnails(self, context: PluginContext) -> PluginResult:
                # Should be able to process Provider output without modification
                photos = context.input_data["photos"]
                collection_name = context.input_data["collection_name"]

                processed = [{**p, "thumbnail_path": f"thumbs/{p['dest_path']}.webp"} for p in photos]

                return PluginResult(
                    success=True,
                    output_data={
                        "photos": processed,
                        "collection_name": collection_name,
                        "thumbnail_count": len(processed)
                    }
                )

        # Test that Provider → Processor contract works
        provider = TestProvider()
        processor = TestProcessor()

        # Provider stage
        provider_context = PluginContext(
            input_data={"manifest_path": "test.json"},
            config={},
            output_dir=tmp_path
        )
        provider_result = provider.load_collection(provider_context)

        # Processor stage (using Provider output)
        processor_context = PluginContext(
            input_data=provider_result.output_data,
            config={},
            output_dir=tmp_path
        )
        processor_result = processor.process_thumbnails(processor_context)

        # Verify seamless data flow
        assert provider_result.success
        assert processor_result.success
        assert processor_result.output_data["collection_name"] == "contract_test"
        assert processor_result.output_data["thumbnail_count"] == 1
        assert "thumbs/gallery/img1.jpg.webp" in processor_result.output_data["photos"][0]["thumbnail_path"]


class TestTransformPluginInterface:
    """Unit tests for TransformPlugin interface contract."""

    def test_transform_plugin_is_abstract_base_class(self):
        """TransformPlugin should be an abstract base class."""
        # Cannot instantiate abstract class directly
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            TransformPlugin()

    def test_transform_plugin_inherits_from_base_plugin(self):
        """TransformPlugin should inherit from BasePlugin."""
        from galleria.plugins import BasePlugin

        assert issubclass(TransformPlugin, BasePlugin)
        assert issubclass(TransformPlugin, ABC)

    def test_transform_plugin_requires_transform_data_implementation(self):
        """TransformPlugin subclasses must implement transform_data method."""

        class IncompleteTransform(TransformPlugin):
            @property
            def name(self) -> str:
                return "incomplete"

            @property
            def version(self) -> str:
                return "1.0.0"

            # Missing transform_data implementation

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteTransform()

    def test_transform_plugin_execute_delegates_to_transform_data(self, tmp_path):
        """TransformPlugin.execute should delegate to transform_data method."""

        class TestTransform(TransformPlugin):
            def __init__(self):
                self.transform_data_called = False

            @property
            def name(self) -> str:
                return "test-transform"

            @property
            def version(self) -> str:
                return "1.0.0"

            def transform_data(self, context: PluginContext) -> PluginResult:
                self.transform_data_called = True
                photos = context.input_data.get("photos", [])
                return PluginResult(
                    success=True,
                    output_data={
                        "photos": photos,
                        "collection_name": context.input_data.get("collection_name", "test"),
                        "transform_metadata": {"operation": "test"}
                    }
                )

        transform = TestTransform()
        context = PluginContext(
            input_data={
                "photos": [{"source_path": "test.jpg", "thumbnail_path": "thumb.webp"}],
                "collection_name": "test"
            },
            config={},
            output_dir=tmp_path
        )

        # execute should call transform_data
        result = transform.execute(context)

        assert transform.transform_data_called
        assert result.success
        assert result.output_data["transform_metadata"]["operation"] == "test"

    def test_transform_plugin_contract_validation_pagination(self, tmp_path):
        """Test TransformPlugin contract for pagination operations."""

        class ValidPaginationTransform(TransformPlugin):
            @property
            def name(self) -> str:
                return "valid-pagination-transform"

            @property
            def version(self) -> str:
                return "1.0.0"

            def transform_data(self, context: PluginContext) -> PluginResult:
                # Validate expected input format (from ProcessorPlugin)
                assert "photos" in context.input_data
                assert "collection_name" in context.input_data
                assert "thumbnail_count" in context.input_data

                photos = context.input_data["photos"]
                photos_per_page = context.config.get("photos_per_page", 2)

                # Validate processor photo format
                for photo in photos:
                    assert "thumbnail_path" in photo
                    assert "thumbnail_size" in photo

                # Create pagination
                pages = []
                for i in range(0, len(photos), photos_per_page):
                    pages.append({
                        "page_number": len(pages) + 1,
                        "photos": photos[i:i + photos_per_page],
                        "photo_count": len(photos[i:i + photos_per_page])
                    })

                return PluginResult(
                    success=True,
                    output_data={
                        "pages": pages,
                        "collection_name": context.input_data["collection_name"],
                        "page_count": len(pages),
                        "total_photos": len(photos),
                        "transform_metadata": {"type": "pagination", "photos_per_page": photos_per_page}
                    }
                )

        transform = ValidPaginationTransform()
        context = PluginContext(
            input_data={
                "photos": [
                    {
                        "source_path": "/source/test1.jpg",
                        "dest_path": "test1.jpg",
                        "thumbnail_path": "thumbs/test1.webp",
                        "thumbnail_size": (300, 200)
                    },
                    {
                        "source_path": "/source/test2.jpg",
                        "dest_path": "test2.jpg",
                        "thumbnail_path": "thumbs/test2.webp",
                        "thumbnail_size": (300, 200)
                    },
                    {
                        "source_path": "/source/test3.jpg",
                        "dest_path": "test3.jpg",
                        "thumbnail_path": "thumbs/test3.webp",
                        "thumbnail_size": (300, 200)
                    }
                ],
                "collection_name": "test_collection",
                "thumbnail_count": 3
            },
            config={"photos_per_page": 2},
            output_dir=tmp_path
        )

        result = transform.transform_data(context)

        # Verify output contract for pagination
        assert result.success
        assert "pages" in result.output_data
        assert "page_count" in result.output_data
        assert "total_photos" in result.output_data
        assert "transform_metadata" in result.output_data

        # Verify pagination logic
        assert result.output_data["page_count"] == 2  # 3 photos / 2 per page = 2 pages
        assert result.output_data["total_photos"] == 3

        # Verify page structure
        pages = result.output_data["pages"]
        assert len(pages) == 2
        assert pages[0]["page_number"] == 1
        assert pages[0]["photo_count"] == 2
        assert pages[1]["page_number"] == 2
        assert pages[1]["photo_count"] == 1

        # Verify thumbnail data preserved
        page1_photo = pages[0]["photos"][0]
        assert page1_photo["thumbnail_path"] == "thumbs/test1.webp"
        assert page1_photo["thumbnail_size"] == (300, 200)

    def test_transform_plugin_contract_validation_sorting(self, tmp_path):
        """Test TransformPlugin contract for sorting operations."""

        class ValidSortTransform(TransformPlugin):
            @property
            def name(self) -> str:
                return "valid-sort-transform"

            @property
            def version(self) -> str:
                return "1.0.0"

            def transform_data(self, context: PluginContext) -> PluginResult:
                # Validate expected input format
                assert "photos" in context.input_data
                assert "collection_name" in context.input_data

                photos = context.input_data["photos"]
                sort_key = context.config.get("sort_by", "dest_path")
                reverse = context.config.get("reverse", False)

                # Sort photos
                sorted_photos = sorted(photos, key=lambda p: p[sort_key], reverse=reverse)

                return PluginResult(
                    success=True,
                    output_data={
                        "photos": sorted_photos,
                        "collection_name": context.input_data["collection_name"],
                        "photo_count": len(sorted_photos),
                        "transform_metadata": {
                            "type": "sorting",
                            "sort_key": sort_key,
                            "reverse": reverse
                        }
                    }
                )

        transform = ValidSortTransform()
        context = PluginContext(
            input_data={
                "photos": [
                    {"dest_path": "c.jpg", "thumbnail_path": "thumbs/c.webp"},
                    {"dest_path": "a.jpg", "thumbnail_path": "thumbs/a.webp"},
                    {"dest_path": "b.jpg", "thumbnail_path": "thumbs/b.webp"}
                ],
                "collection_name": "test_collection",
                "thumbnail_count": 3
            },
            config={"sort_by": "dest_path", "reverse": False},
            output_dir=tmp_path
        )

        result = transform.transform_data(context)

        # Verify output contract for sorting
        assert result.success
        assert "photos" in result.output_data
        assert "photo_count" in result.output_data
        assert "transform_metadata" in result.output_data

        # Verify sorting worked
        sorted_photos = result.output_data["photos"]
        assert len(sorted_photos) == 3
        assert sorted_photos[0]["dest_path"] == "a.jpg"
        assert sorted_photos[1]["dest_path"] == "b.jpg"
        assert sorted_photos[2]["dest_path"] == "c.jpg"

        # Verify thumbnail data preserved
        assert sorted_photos[0]["thumbnail_path"] == "thumbs/a.webp"


class TestTransformIntegration:
    """Unit tests for Transform plugin integration with other interfaces."""

    def test_processor_output_matches_transform_input_contract(self, tmp_path):
        """Processor output format should match Transform input expectations."""

        class TestProcessor(ProcessorPlugin):
            @property
            def name(self) -> str:
                return "contract-processor"

            @property
            def version(self) -> str:
                return "1.0.0"

            def process_thumbnails(self, context: PluginContext) -> PluginResult:
                photos = context.input_data["photos"]
                processed_photos = []

                for photo in photos:
                    processed_photos.append({
                        **photo,
                        "thumbnail_path": f"thumbs/{photo['dest_path']}.webp",
                        "thumbnail_size": (300, 200)
                    })

                return PluginResult(
                    success=True,
                    output_data={
                        "photos": processed_photos,
                        "collection_name": context.input_data["collection_name"],
                        "thumbnail_count": len(processed_photos)
                    }
                )

        class TestTransform(TransformPlugin):
            @property
            def name(self) -> str:
                return "contract-transform"

            @property
            def version(self) -> str:
                return "1.0.0"

            def transform_data(self, context: PluginContext) -> PluginResult:
                # Should be able to process Processor output without modification
                photos = context.input_data["photos"]
                collection_name = context.input_data["collection_name"]
                thumbnail_count = context.input_data["thumbnail_count"]

                # Simple pagination
                pages = [{"page_number": 1, "photos": photos}]

                return PluginResult(
                    success=True,
                    output_data={
                        "pages": pages,
                        "collection_name": collection_name,
                        "page_count": 1,
                        "original_thumbnail_count": thumbnail_count
                    }
                )

        # Test that Processor → Transform contract works
        processor = TestProcessor()
        transform = TestTransform()

        # Processor stage (mock Provider output)
        processor_context = PluginContext(
            input_data={
                "photos": [{"source_path": "/source/img1.jpg", "dest_path": "img1.jpg"}],
                "collection_name": "contract_test"
            },
            config={},
            output_dir=tmp_path
        )
        processor_result = processor.process_thumbnails(processor_context)

        # Transform stage (using Processor output)
        transform_context = PluginContext(
            input_data=processor_result.output_data,
            config={},
            output_dir=tmp_path
        )
        transform_result = transform.transform_data(transform_context)

        # Verify seamless data flow
        assert processor_result.success
        assert transform_result.success
        assert processor_result.output_data["collection_name"] == "contract_test"
        assert transform_result.output_data["collection_name"] == "contract_test"
        assert transform_result.output_data["original_thumbnail_count"] == 1

        # Verify thumbnail data preserved through pipeline
        page_photo = transform_result.output_data["pages"][0]["photos"][0]
        assert page_photo["thumbnail_path"] == "thumbs/img1.jpg.webp"
        assert page_photo["thumbnail_size"] == (300, 200)
