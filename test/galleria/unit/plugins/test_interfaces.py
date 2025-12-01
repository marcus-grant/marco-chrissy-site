"""Unit tests for plugin interface definitions."""

from abc import ABC

import pytest

from galleria.plugins import PluginContext, PluginResult
from galleria.plugins.interfaces import (
    CSSPlugin,
    ProcessorPlugin,
    ProviderPlugin,
    TemplatePlugin,
    TransformPlugin,
)


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
                    success=True, output_data={"photos": [], "collection_name": "test"}
                )

        provider = TestProvider()
        context = PluginContext(
            input_data={"manifest_path": "test.json"}, config={}, output_dir=tmp_path
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
                assert (
                    "manifest_path" in context.input_data
                    or "source_dir" in context.input_data
                )

                # Return expected output format
                return PluginResult(
                    success=True,
                    output_data={
                        "photos": [
                            {
                                "source_path": "/source/test.jpg",
                                "dest_path": "test.jpg",
                                "metadata": {},
                            }
                        ],
                        "collection_name": "test_collection",
                    },
                )

        provider = ValidProvider()
        context = PluginContext(
            input_data={"manifest_path": "test.json"}, config={}, output_dir=tmp_path
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
                        "collection_name": context.input_data.get(
                            "collection_name", "test"
                        ),
                        "thumbnail_count": len(photos),
                    },
                )

        processor = TestProcessor()
        context = PluginContext(
            input_data={
                "photos": [{"source_path": "test.jpg", "dest_path": "test.jpg"}],
                "collection_name": "test",
            },
            config={},
            output_dir=tmp_path,
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
                    processed_photos.append(
                        {
                            **photo,
                            "thumbnail_path": f"thumbs/{photo['dest_path']}.webp",
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

        processor = ValidProcessor()
        context = PluginContext(
            input_data={
                "photos": [
                    {
                        "source_path": "/source/test.jpg",
                        "dest_path": "test.jpg",
                        "metadata": {},
                    }
                ],
                "collection_name": "test_collection",
            },
            config={},
            output_dir=tmp_path,
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
                                "metadata": {"size": 1024},
                            }
                        ],
                        "collection_name": "contract_test",
                    },
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

                processed = [
                    {**p, "thumbnail_path": f"thumbs/{p['dest_path']}.webp"}
                    for p in photos
                ]

                return PluginResult(
                    success=True,
                    output_data={
                        "photos": processed,
                        "collection_name": collection_name,
                        "thumbnail_count": len(processed),
                    },
                )

        # Test that Provider → Processor contract works
        provider = TestProvider()
        processor = TestProcessor()

        # Provider stage
        provider_context = PluginContext(
            input_data={"manifest_path": "test.json"}, config={}, output_dir=tmp_path
        )
        provider_result = provider.load_collection(provider_context)

        # Processor stage (using Provider output)
        processor_context = PluginContext(
            input_data=provider_result.output_data, config={}, output_dir=tmp_path
        )
        processor_result = processor.process_thumbnails(processor_context)

        # Verify seamless data flow
        assert provider_result.success
        assert processor_result.success
        assert processor_result.output_data["collection_name"] == "contract_test"
        assert processor_result.output_data["thumbnail_count"] == 1
        assert (
            "thumbs/gallery/img1.jpg.webp"
            in processor_result.output_data["photos"][0]["thumbnail_path"]
        )


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
                        "collection_name": context.input_data.get(
                            "collection_name", "test"
                        ),
                        "transform_metadata": {"operation": "test"},
                    },
                )

        transform = TestTransform()
        context = PluginContext(
            input_data={
                "photos": [{"source_path": "test.jpg", "thumbnail_path": "thumb.webp"}],
                "collection_name": "test",
            },
            config={},
            output_dir=tmp_path,
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
                    pages.append(
                        {
                            "page_number": len(pages) + 1,
                            "photos": photos[i : i + photos_per_page],
                            "photo_count": len(photos[i : i + photos_per_page]),
                        }
                    )

                return PluginResult(
                    success=True,
                    output_data={
                        "pages": pages,
                        "collection_name": context.input_data["collection_name"],
                        "page_count": len(pages),
                        "total_photos": len(photos),
                        "transform_metadata": {
                            "type": "pagination",
                            "photos_per_page": photos_per_page,
                        },
                    },
                )

        transform = ValidPaginationTransform()
        context = PluginContext(
            input_data={
                "photos": [
                    {
                        "source_path": "/source/test1.jpg",
                        "dest_path": "test1.jpg",
                        "thumbnail_path": "thumbs/test1.webp",
                        "thumbnail_size": (300, 200),
                    },
                    {
                        "source_path": "/source/test2.jpg",
                        "dest_path": "test2.jpg",
                        "thumbnail_path": "thumbs/test2.webp",
                        "thumbnail_size": (300, 200),
                    },
                    {
                        "source_path": "/source/test3.jpg",
                        "dest_path": "test3.jpg",
                        "thumbnail_path": "thumbs/test3.webp",
                        "thumbnail_size": (300, 200),
                    },
                ],
                "collection_name": "test_collection",
                "thumbnail_count": 3,
            },
            config={"photos_per_page": 2},
            output_dir=tmp_path,
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
                sorted_photos = sorted(
                    photos, key=lambda p: p[sort_key], reverse=reverse
                )

                return PluginResult(
                    success=True,
                    output_data={
                        "photos": sorted_photos,
                        "collection_name": context.input_data["collection_name"],
                        "photo_count": len(sorted_photos),
                        "transform_metadata": {
                            "type": "sorting",
                            "sort_key": sort_key,
                            "reverse": reverse,
                        },
                    },
                )

        transform = ValidSortTransform()
        context = PluginContext(
            input_data={
                "photos": [
                    {"dest_path": "c.jpg", "thumbnail_path": "thumbs/c.webp"},
                    {"dest_path": "a.jpg", "thumbnail_path": "thumbs/a.webp"},
                    {"dest_path": "b.jpg", "thumbnail_path": "thumbs/b.webp"},
                ],
                "collection_name": "test_collection",
                "thumbnail_count": 3,
            },
            config={"sort_by": "dest_path", "reverse": False},
            output_dir=tmp_path,
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
                    processed_photos.append(
                        {
                            **photo,
                            "thumbnail_path": f"thumbs/{photo['dest_path']}.webp",
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
                        "original_thumbnail_count": thumbnail_count,
                    },
                )

        # Test that Processor → Transform contract works
        processor = TestProcessor()
        transform = TestTransform()

        # Processor stage (mock Provider output)
        processor_context = PluginContext(
            input_data={
                "photos": [
                    {"source_path": "/source/img1.jpg", "dest_path": "img1.jpg"}
                ],
                "collection_name": "contract_test",
            },
            config={},
            output_dir=tmp_path,
        )
        processor_result = processor.process_thumbnails(processor_context)

        # Transform stage (using Processor output)
        transform_context = PluginContext(
            input_data=processor_result.output_data, config={}, output_dir=tmp_path
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


class TestTemplatePluginInterface:
    """Unit tests for TemplatePlugin interface contract."""

    def test_template_plugin_is_abstract_base_class(self):
        """TemplatePlugin should be an abstract base class."""
        # Cannot instantiate abstract class directly
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            TemplatePlugin()

    def test_template_plugin_inherits_from_base_plugin(self):
        """TemplatePlugin should inherit from BasePlugin."""
        from galleria.plugins import BasePlugin

        assert issubclass(TemplatePlugin, BasePlugin)
        assert issubclass(TemplatePlugin, ABC)

    def test_template_plugin_requires_generate_html_implementation(self):
        """TemplatePlugin subclasses must implement generate_html method."""

        class IncompleteTemplate(TemplatePlugin):
            @property
            def name(self) -> str:
                return "incomplete"

            @property
            def version(self) -> str:
                return "1.0.0"

            # Missing generate_html implementation

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteTemplate()

    def test_template_plugin_execute_delegates_to_generate_html(self, tmp_path):
        """TemplatePlugin.execute should delegate to generate_html method."""

        class TestTemplate(TemplatePlugin):
            def __init__(self):
                self.generate_html_called = False

            @property
            def name(self) -> str:
                return "test-template"

            @property
            def version(self) -> str:
                return "1.0.0"

            def generate_html(self, context: PluginContext) -> PluginResult:
                self.generate_html_called = True
                pages = context.input_data.get("pages", [])
                html_files = []

                for page in pages:
                    html_files.append(
                        {
                            "filename": f"page_{page.get('page_number', 1)}.html",
                            "page_number": page.get("page_number", 1),
                        }
                    )

                return PluginResult(
                    success=True,
                    output_data={
                        "html_files": html_files,
                        "collection_name": context.input_data.get(
                            "collection_name", "test"
                        ),
                        "file_count": len(html_files),
                    },
                )

        template = TestTemplate()
        context = PluginContext(
            input_data={
                "pages": [{"page_number": 1, "photos": []}],
                "collection_name": "test",
            },
            config={},
            output_dir=tmp_path,
        )

        # execute should call generate_html
        result = template.execute(context)

        assert template.generate_html_called
        assert result.success
        assert result.output_data["file_count"] == 1

    def test_template_plugin_contract_validation(self, tmp_path):
        """Test that TemplatePlugin contract is properly defined."""

        class ValidTemplate(TemplatePlugin):
            @property
            def name(self) -> str:
                return "valid-template"

            @property
            def version(self) -> str:
                return "1.0.0"

            def generate_html(self, context: PluginContext) -> PluginResult:
                # Validate expected input format (from TransformPlugin)
                assert "pages" in context.input_data or "photos" in context.input_data
                assert "collection_name" in context.input_data

                pages = context.input_data.get("pages", [])
                collection_name = context.input_data["collection_name"]
                html_files = []

                for page in pages:
                    # Validate page format
                    assert "page_number" in page
                    assert "photos" in page

                    # Generate HTML file metadata
                    html_files.append(
                        {
                            "filename": f"page_{page['page_number']}.html",
                            "content": f"<html><title>{collection_name}</title></html>",
                            "page_number": page["page_number"],
                        }
                    )

                return PluginResult(
                    success=True,
                    output_data={
                        "html_files": html_files,
                        "collection_name": collection_name,
                        "file_count": len(html_files),
                    },
                )

        template = ValidTemplate()
        context = PluginContext(
            input_data={
                "pages": [
                    {
                        "page_number": 1,
                        "photos": [
                            {
                                "dest_path": "test.jpg",
                                "thumbnail_path": "thumbs/test.webp",
                                "thumbnail_size": (300, 200),
                            }
                        ],
                        "photo_count": 1,
                    }
                ],
                "collection_name": "test_collection",
                "page_count": 1,
            },
            config={"theme": "minimal"},
            output_dir=tmp_path,
        )

        result = template.generate_html(context)

        # Verify output contract
        assert result.success
        assert "html_files" in result.output_data
        assert "collection_name" in result.output_data
        assert "file_count" in result.output_data

        # Verify HTML file structure
        html_file = result.output_data["html_files"][0]
        assert "filename" in html_file
        assert "content" in html_file
        assert "page_number" in html_file
        assert html_file["filename"] == "page_1.html"
        assert "test_collection" in html_file["content"]


class TestCSSPluginInterface:
    """Unit tests for CSSPlugin interface contract."""

    def test_css_plugin_is_abstract_base_class(self):
        """CSSPlugin should be an abstract base class."""
        # Cannot instantiate abstract class directly
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            CSSPlugin()

    def test_css_plugin_inherits_from_base_plugin(self):
        """CSSPlugin should inherit from BasePlugin."""
        from galleria.plugins import BasePlugin

        assert issubclass(CSSPlugin, BasePlugin)
        assert issubclass(CSSPlugin, ABC)

    def test_css_plugin_requires_generate_css_implementation(self):
        """CSSPlugin subclasses must implement generate_css method."""

        class IncompleteCSS(CSSPlugin):
            @property
            def name(self) -> str:
                return "incomplete"

            @property
            def version(self) -> str:
                return "1.0.0"

            # Missing generate_css implementation

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteCSS()

    def test_css_plugin_execute_delegates_to_generate_css(self, tmp_path):
        """CSSPlugin.execute should delegate to generate_css method."""

        class TestCSS(CSSPlugin):
            def __init__(self):
                self.generate_css_called = False

            @property
            def name(self) -> str:
                return "test-css"

            @property
            def version(self) -> str:
                return "1.0.0"

            def generate_css(self, context: PluginContext) -> PluginResult:
                self.generate_css_called = True
                html_files = context.input_data.get("html_files", [])
                css_files = [
                    {"filename": "gallery.css", "type": "gallery"},
                    {"filename": "theme.css", "type": "theme"},
                ]

                return PluginResult(
                    success=True,
                    output_data={
                        "css_files": css_files,
                        "html_files": html_files,  # Pass through
                        "collection_name": context.input_data.get(
                            "collection_name", "test"
                        ),
                        "css_count": len(css_files),
                    },
                )

        css_plugin = TestCSS()
        context = PluginContext(
            input_data={
                "html_files": [{"filename": "page_1.html", "page_number": 1}],
                "collection_name": "test",
            },
            config={},
            output_dir=tmp_path,
        )

        # execute should call generate_css
        result = css_plugin.execute(context)

        assert css_plugin.generate_css_called
        assert result.success
        assert result.output_data["css_count"] == 2

    def test_css_plugin_contract_validation(self, tmp_path):
        """Test that CSSPlugin contract is properly defined."""

        class ValidCSS(CSSPlugin):
            @property
            def name(self) -> str:
                return "valid-css"

            @property
            def version(self) -> str:
                return "1.0.0"

            def generate_css(self, context: PluginContext) -> PluginResult:
                # Validate expected input format (from TemplatePlugin)
                assert "html_files" in context.input_data
                assert "collection_name" in context.input_data

                html_files = context.input_data["html_files"]
                collection_name = context.input_data["collection_name"]
                theme = context.config.get("theme", "default")
                css_files = []

                # Validate HTML file format
                for html_file in html_files:
                    assert "filename" in html_file
                    assert "page_number" in html_file

                # Generate gallery CSS
                css_files.append(
                    {
                        "filename": "gallery.css",
                        "content": f"/* Gallery styles for {collection_name} */\n.gallery {{ display: grid; }}",
                        "type": "gallery",
                    }
                )

                # Generate theme CSS
                if theme != "default":
                    css_files.append(
                        {
                            "filename": f"theme-{theme}.css",
                            "content": f"/* Theme: {theme} */\nbody {{ font-family: Arial; }}",
                            "type": "theme",
                        }
                    )

                return PluginResult(
                    success=True,
                    output_data={
                        "css_files": css_files,
                        "html_files": html_files,  # Pass through
                        "collection_name": collection_name,
                        "css_count": len(css_files),
                    },
                )

        css_plugin = ValidCSS()
        context = PluginContext(
            input_data={
                "html_files": [
                    {
                        "filename": "page_1.html",
                        "content": "<html>...</html>",
                        "page_number": 1,
                    }
                ],
                "collection_name": "test_collection",
                "file_count": 1,
            },
            config={"theme": "minimal"},
            output_dir=tmp_path,
        )

        result = css_plugin.generate_css(context)

        # Verify output contract
        assert result.success
        assert "css_files" in result.output_data
        assert "html_files" in result.output_data
        assert "collection_name" in result.output_data
        assert "css_count" in result.output_data

        # Verify CSS file structure
        css_files = result.output_data["css_files"]
        assert len(css_files) == 2
        assert css_files[0]["filename"] == "gallery.css"
        assert css_files[0]["type"] == "gallery"
        assert "test_collection" in css_files[0]["content"]
        assert css_files[1]["filename"] == "theme-minimal.css"
        assert css_files[1]["type"] == "theme"

        # Verify HTML files passed through
        assert "html_files" in result.output_data
        assert len(result.output_data["html_files"]) == 1


class TestTemplateCSSIntegration:
    """Unit tests for Template and CSS plugin integration contracts."""

    def test_template_output_matches_css_input_contract(self, tmp_path):
        """Template output format should match CSS input expectations."""

        class TestTemplate(TemplatePlugin):
            @property
            def name(self) -> str:
                return "contract-template"

            @property
            def version(self) -> str:
                return "1.0.0"

            def generate_html(self, context: PluginContext) -> PluginResult:
                pages = context.input_data["pages"]
                collection_name = context.input_data["collection_name"]
                html_files = []

                for page in pages:
                    html_files.append(
                        {
                            "filename": f"page_{page['page_number']}.html",
                            "content": f"<html><title>{collection_name}</title></html>",
                            "page_number": page["page_number"],
                        }
                    )

                return PluginResult(
                    success=True,
                    output_data={
                        "html_files": html_files,
                        "collection_name": collection_name,
                        "file_count": len(html_files),
                    },
                )

        class TestCSS(CSSPlugin):
            @property
            def name(self) -> str:
                return "contract-css"

            @property
            def version(self) -> str:
                return "1.0.0"

            def generate_css(self, context: PluginContext) -> PluginResult:
                # Should be able to process Template output without modification
                html_files = context.input_data["html_files"]
                collection_name = context.input_data["collection_name"]
                file_count = context.input_data["file_count"]

                css_files = [{"filename": "styles.css", "type": "main"}]

                return PluginResult(
                    success=True,
                    output_data={
                        "css_files": css_files,
                        "html_files": html_files,
                        "collection_name": collection_name,
                        "css_count": 1,
                        "original_file_count": file_count,
                    },
                )

        # Test that Template → CSS contract works
        template = TestTemplate()
        css_plugin = TestCSS()

        # Template stage (mock Transform output)
        template_context = PluginContext(
            input_data={
                "pages": [
                    {"page_number": 1, "photos": [{"thumbnail_path": "thumb1.webp"}]}
                ],
                "collection_name": "contract_test",
            },
            config={},
            output_dir=tmp_path,
        )
        template_result = template.generate_html(template_context)

        # CSS stage (using Template output)
        css_context = PluginContext(
            input_data=template_result.output_data, config={}, output_dir=tmp_path
        )
        css_result = css_plugin.generate_css(css_context)

        # Verify seamless data flow
        assert template_result.success
        assert css_result.success
        assert template_result.output_data["collection_name"] == "contract_test"
        assert css_result.output_data["collection_name"] == "contract_test"
        assert css_result.output_data["original_file_count"] == 1

        # Verify HTML data preserved through pipeline
        html_files = css_result.output_data["html_files"]
        assert len(html_files) == 1
        assert html_files[0]["filename"] == "page_1.html"
        assert "contract_test" in html_files[0]["content"]

    def test_transform_to_template_to_css_contract_integration(self, tmp_path):
        """Test complete Transform → Template → CSS contract integration."""

        class TestTransform(TransformPlugin):
            @property
            def name(self) -> str:
                return "contract-transform"

            @property
            def version(self) -> str:
                return "1.0.0"

            def transform_data(self, context: PluginContext) -> PluginResult:
                photos = context.input_data["photos"]
                pages = [
                    {"page_number": 1, "photos": photos, "photo_count": len(photos)}
                ]

                return PluginResult(
                    success=True,
                    output_data={
                        "pages": pages,
                        "collection_name": context.input_data["collection_name"],
                        "page_count": 1,
                    },
                )

        class TestTemplate(TemplatePlugin):
            @property
            def name(self) -> str:
                return "contract-template"

            @property
            def version(self) -> str:
                return "1.0.0"

            def generate_html(self, context: PluginContext) -> PluginResult:
                html_files = [{"filename": "gallery.html", "page_number": 1}]

                return PluginResult(
                    success=True,
                    output_data={
                        "html_files": html_files,
                        "collection_name": context.input_data["collection_name"],
                        "file_count": 1,
                    },
                )

        class TestCSS(CSSPlugin):
            @property
            def name(self) -> str:
                return "contract-css"

            @property
            def version(self) -> str:
                return "1.0.0"

            def generate_css(self, context: PluginContext) -> PluginResult:
                css_files = [{"filename": "gallery.css", "type": "gallery"}]

                return PluginResult(
                    success=True,
                    output_data={
                        "css_files": css_files,
                        "html_files": context.input_data["html_files"],
                        "collection_name": context.input_data["collection_name"],
                        "css_count": 1,
                    },
                )

        # Test that Transform → Template → CSS contract works end-to-end
        transform = TestTransform()
        template = TestTemplate()
        css_plugin = TestCSS()

        # Transform stage
        transform_context = PluginContext(
            input_data={
                "photos": [{"thumbnail_path": "thumb1.webp"}],
                "collection_name": "contract_test",
            },
            config={},
            output_dir=tmp_path,
        )
        transform_result = transform.transform_data(transform_context)

        # Template stage
        template_context = PluginContext(
            input_data=transform_result.output_data, config={}, output_dir=tmp_path
        )
        template_result = template.generate_html(template_context)

        # CSS stage
        css_context = PluginContext(
            input_data=template_result.output_data, config={}, output_dir=tmp_path
        )
        css_result = css_plugin.generate_css(css_context)

        # Verify end-to-end pipeline success
        assert transform_result.success
        assert template_result.success
        assert css_result.success

        # Verify data flow through entire pipeline
        assert transform_result.output_data["collection_name"] == "contract_test"
        assert template_result.output_data["collection_name"] == "contract_test"
        assert css_result.output_data["collection_name"] == "contract_test"

        # Verify final output contains all expected components
        final_output = css_result.output_data
        assert "html_files" in final_output
        assert "css_files" in final_output
        assert len(final_output["html_files"]) == 1
        assert len(final_output["css_files"]) == 1
