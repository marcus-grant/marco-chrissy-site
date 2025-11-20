"""Unit tests for PaginationPlugin interface and contract validation."""

import pytest

from galleria.plugins.base import PluginContext, PluginResult
from galleria.plugins.interfaces import TransformPlugin


class PaginationPlugin(TransformPlugin):
    """Pagination plugin for splitting photos into pages."""

    @property
    def name(self) -> str:
        return "pagination"

    @property
    def version(self) -> str:
        return "1.0.0"

    def transform_data(self, context: PluginContext) -> PluginResult:
        """Transform photo data by splitting into pages."""
        page_size = context.config.get("page_size", 20)
        photos = context.input_data.get("photos", [])

        # Split photos into pages
        pages = []
        for i in range(0, len(photos), page_size):
            pages.append(photos[i:i + page_size])

        return PluginResult(
            success=True,
            output_data={
                "pages": pages,
                "collection_name": context.input_data.get("collection_name", ""),
                "transform_metadata": {
                    "page_size": page_size,
                    "total_pages": len(pages),
                    "total_photos": len(photos)
                }
            }
        )


class TestPaginationPluginInterface:
    """Test PaginationPlugin interface contract and validation."""

    def test_pagination_plugin_inherits_from_transform_plugin(self):
        """PaginationPlugin should inherit from TransformPlugin."""
        plugin = PaginationPlugin()

        # Should have base plugin properties
        assert hasattr(plugin, "name")
        assert hasattr(plugin, "version")
        assert hasattr(plugin, "execute")

        # Should have transform-specific method
        assert hasattr(plugin, "transform_data")

    def test_transform_data_abstract_method_required(self):
        """TransformPlugin.transform_data should be abstract and required."""

        class IncompleteTransformPlugin(TransformPlugin):
            @property
            def name(self) -> str:
                return "incomplete"

            @property
            def version(self) -> str:
                return "1.0.0"
            # Missing transform_data implementation

        # Should not be able to instantiate without transform_data
        with pytest.raises(TypeError):
            IncompleteTransformPlugin()

    def test_execute_delegates_to_transform_data(self, tmp_path):
        """TransformPlugin.execute should delegate to transform_data method."""
        plugin = PaginationPlugin()

        context = PluginContext(
            input_data={
                "photos": [{"dest_path": f"photo_{i}.jpg"} for i in range(5)],
                "collection_name": "test_collection",
            },
            config={"page_size": 2},
            output_dir=tmp_path,
        )

        result = plugin.execute(context)

        # Should return PluginResult from transform_data
        assert result.success
        assert result.output_data["collection_name"] == "test_collection"
        assert "pages" in result.output_data

    def test_pagination_with_valid_processor_data(self, tmp_path):
        """Pagination should handle valid processor data input."""
        plugin = PaginationPlugin()

        # Test with photos data (from processor stage)
        processor_context = PluginContext(
            input_data={
                "photos": [
                    {"dest_path": "photo1.jpg", "thumbnail_path": "thumb1.webp"},
                    {"dest_path": "photo2.jpg", "thumbnail_path": "thumb2.webp"},
                    {"dest_path": "photo3.jpg", "thumbnail_path": "thumb3.webp"},
                    {"dest_path": "photo4.jpg", "thumbnail_path": "thumb4.webp"},
                ],
                "collection_name": "wedding",
                "thumbnail_count": 4,
            },
            config={"page_size": 2},
            output_dir=tmp_path,
        )

        result = plugin.transform_data(processor_context)

        assert result.success
        assert "pages" in result.output_data
        assert result.output_data["collection_name"] == "wedding"
        assert len(result.output_data["pages"]) == 2  # 4 photos / 2 per page

    def test_pagination_output_format_contract(self, tmp_path):
        """Pagination should return data in expected format."""
        plugin = PaginationPlugin()

        context = PluginContext(
            input_data={
                "photos": [{"dest_path": f"photo_{i}.jpg"} for i in range(3)],
                "collection_name": "test",
            },
            config={"page_size": 2},
            output_dir=tmp_path,
        )

        result = plugin.transform_data(context)

        # Verify required output format
        assert result.success
        assert "pages" in result.output_data
        assert "collection_name" in result.output_data
        assert "transform_metadata" in result.output_data

        # Verify pages structure
        pages = result.output_data["pages"]
        assert isinstance(pages, list)
        assert len(pages) == 2  # 3 photos with page_size=2 → 2 pages

        # Verify metadata
        metadata = result.output_data["transform_metadata"]
        assert metadata["page_size"] == 2
        assert metadata["total_pages"] == 2
        assert metadata["total_photos"] == 3

    def test_pagination_preserves_collection_name(self, tmp_path):
        """Pagination should preserve collection_name from input."""
        plugin = PaginationPlugin()

        context = PluginContext(
            input_data={
                "photos": [{"dest_path": "photo1.jpg"}],
                "collection_name": "preserve_me",
            },
            config={"page_size": 10},
            output_dir=tmp_path,
        )

        result = plugin.transform_data(context)

        assert result.output_data["collection_name"] == "preserve_me"

    def test_pagination_with_empty_photos(self, tmp_path):
        """Pagination should handle empty photos gracefully."""
        plugin = PaginationPlugin()

        context = PluginContext(
            input_data={
                "photos": [],
                "collection_name": "empty",
            },
            config={"page_size": 10},
            output_dir=tmp_path,
        )

        result = plugin.transform_data(context)

        assert result.success
        assert result.output_data["collection_name"] == "empty"
        assert result.output_data["pages"] == []
        assert result.output_data["transform_metadata"]["total_photos"] == 0

    def test_pagination_with_default_page_size(self, tmp_path):
        """Pagination should use default page_size when not configured."""
        plugin = PaginationPlugin()

        context = PluginContext(
            input_data={
                "photos": [{"dest_path": f"photo_{i}.jpg"} for i in range(25)],
                "collection_name": "test",
            },
            config={},  # No page_size specified
            output_dir=tmp_path,
        )

        result = plugin.transform_data(context)

        assert result.success
        metadata = result.output_data["transform_metadata"]
        assert metadata["page_size"] == 20  # Default page size
        assert metadata["total_pages"] == 2  # 25 photos / 20 per page → 2 pages


class TestPaginationPluginValidation:
    """Test PaginationPlugin input validation and error handling."""

    def test_pagination_validates_page_size_configuration(self, tmp_path):
        """Pagination should validate page_size configuration."""

        class ValidatingPaginationPlugin(TransformPlugin):
            @property
            def name(self) -> str:
                return "validator"

            @property
            def version(self) -> str:
                return "1.0.0"

            def transform_data(self, context: PluginContext) -> PluginResult:
                # Validate page_size configuration
                page_size = context.config.get("page_size", 20)
                if page_size <= 0:
                    return PluginResult(
                        success=False,
                        output_data={},
                        errors=["INVALID_PAGE_SIZE: page_size must be positive"]
                    )

                if page_size > 100:
                    return PluginResult(
                        success=False,
                        output_data={},
                        errors=["INVALID_PAGE_SIZE: page_size must be <= 100"]
                    )

                return PluginResult(
                    success=True,
                    output_data={
                        "pages": [],
                        "collection_name": "test",
                        "transform_metadata": {"page_size": page_size}
                    }
                )

        plugin = ValidatingPaginationPlugin()

        # Invalid page_size (negative) should fail validation
        context = PluginContext(
            input_data={"photos": [], "collection_name": "test"},
            config={"page_size": -1},
            output_dir=tmp_path,
        )

        result = plugin.transform_data(context)
        assert not result.success
        assert result.errors
        assert "INVALID_PAGE_SIZE" in result.errors[0]

        # Invalid page_size (too large) should fail validation
        context = PluginContext(
            input_data={"photos": [], "collection_name": "test"},
            config={"page_size": 200},
            output_dir=tmp_path,
        )

        result = plugin.transform_data(context)
        assert not result.success
        assert result.errors
        assert "INVALID_PAGE_SIZE" in result.errors[0]

    def test_pagination_handles_missing_photos_gracefully(self, tmp_path):
        """Pagination should handle missing photos field gracefully."""
        plugin = PaginationPlugin()

        context = PluginContext(
            input_data={"collection_name": "test"},  # Missing photos
            config={"page_size": 10},
            output_dir=tmp_path,
        )

        result = plugin.transform_data(context)

        # Should succeed with empty photos list
        assert result.success
        assert result.output_data["pages"] == []
        assert result.output_data["transform_metadata"]["total_photos"] == 0
