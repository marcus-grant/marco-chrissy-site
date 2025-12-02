"""Unit tests for BasicPaginationPlugin pagination math."""

from pathlib import Path

from galleria.plugins.base import PluginContext
from galleria.plugins.pagination import BasicPaginationPlugin


class TestBasicPaginationPlugin:
    """Test BasicPaginationPlugin pagination calculation logic."""

    def test_pagination_math_exact_pages(self):
        """Test pagination with photos that divide evenly into pages."""
        plugin = BasicPaginationPlugin()

        # 6 photos, page_size=3 → should create exactly 2 pages
        context = PluginContext(
            input_data={
                "photos": [{"id": i} for i in range(6)],
                "collection_name": "test",
            },
            config={"page_size": 3},
            output_dir=Path("/tmp"),
        )

        result = plugin.transform_data(context)

        assert result.success
        assert result.output_data["transform_metadata"]["total_pages"] == 2
        assert result.output_data["transform_metadata"]["total_photos"] == 6
        assert result.output_data["transform_metadata"]["page_size"] == 3
        assert len(result.output_data["pages"]) == 2
        assert len(result.output_data["pages"][0]) == 3  # First page: 3 photos
        assert len(result.output_data["pages"][1]) == 3  # Second page: 3 photos

    def test_pagination_math_partial_last_page(self):
        """Test pagination with photos that don't divide evenly (partial last page)."""
        plugin = BasicPaginationPlugin()

        # 7 photos, page_size=3 → should create 3 pages (3+3+1)
        context = PluginContext(
            input_data={
                "photos": [{"id": i} for i in range(7)],
                "collection_name": "test",
            },
            config={"page_size": 3},
            output_dir=Path("/tmp"),
        )

        result = plugin.transform_data(context)

        assert result.success
        assert result.output_data["transform_metadata"]["total_pages"] == 3
        assert result.output_data["transform_metadata"]["total_photos"] == 7
        assert len(result.output_data["pages"]) == 3
        assert len(result.output_data["pages"][0]) == 3  # First page: 3 photos
        assert len(result.output_data["pages"][1]) == 3  # Second page: 3 photos
        assert len(result.output_data["pages"][2]) == 1  # Third page: 1 photo

    def test_pagination_math_single_page(self):
        """Test pagination with fewer photos than page size (single page)."""
        plugin = BasicPaginationPlugin()

        # 2 photos, page_size=5 → should create 1 page
        context = PluginContext(
            input_data={
                "photos": [{"id": i} for i in range(2)],
                "collection_name": "test",
            },
            config={"page_size": 5},
            output_dir=Path("/tmp"),
        )

        result = plugin.transform_data(context)

        assert result.success
        assert result.output_data["transform_metadata"]["total_pages"] == 1
        assert result.output_data["transform_metadata"]["total_photos"] == 2
        assert len(result.output_data["pages"]) == 1
        assert len(result.output_data["pages"][0]) == 2

    def test_pagination_math_empty_collection(self):
        """Test pagination with empty photo collection."""
        plugin = BasicPaginationPlugin()

        # 0 photos → should create 1 empty page
        context = PluginContext(
            input_data={"photos": [], "collection_name": "empty"},
            config={"page_size": 3},
            output_dir=Path("/tmp"),
        )

        result = plugin.transform_data(context)

        assert result.success
        assert result.output_data["transform_metadata"]["total_pages"] == 1
        assert result.output_data["transform_metadata"]["total_photos"] == 0
        assert len(result.output_data["pages"]) == 1
        assert len(result.output_data["pages"][0]) == 0

    def test_pagination_math_large_page_size(self):
        """Test pagination with page size larger than collection."""
        plugin = BasicPaginationPlugin()

        # 3 photos, page_size=10 → should create 1 page
        context = PluginContext(
            input_data={
                "photos": [{"id": i} for i in range(3)],
                "collection_name": "test",
            },
            config={"page_size": 10},
            output_dir=Path("/tmp"),
        )

        result = plugin.transform_data(context)

        assert result.success
        assert result.output_data["transform_metadata"]["total_pages"] == 1
        assert result.output_data["transform_metadata"]["total_photos"] == 3
        assert len(result.output_data["pages"]) == 1
        assert len(result.output_data["pages"][0]) == 3

    def test_pagination_math_page_size_one(self):
        """Test pagination with page_size=1 (one photo per page)."""
        plugin = BasicPaginationPlugin()

        # 4 photos, page_size=1 → should create 4 pages
        context = PluginContext(
            input_data={
                "photos": [{"id": i} for i in range(4)],
                "collection_name": "test",
            },
            config={"page_size": 1},
            output_dir=Path("/tmp"),
        )

        result = plugin.transform_data(context)

        assert result.success
        assert result.output_data["transform_metadata"]["total_pages"] == 4
        assert result.output_data["transform_metadata"]["total_photos"] == 4
        assert len(result.output_data["pages"]) == 4
        for i in range(4):
            assert len(result.output_data["pages"][i]) == 1

    def test_pagination_calculation_formula(self):
        """Test the pagination calculation formula directly."""
        plugin = BasicPaginationPlugin()

        # Test various combinations to verify ceil(total_photos / page_size)
        test_cases = [
            (10, 3, 4),  # 10 photos, page_size 3 → 4 pages (3+3+3+1)
            (10, 5, 2),  # 10 photos, page_size 5 → 2 pages (5+5)
            (1, 1, 1),  # 1 photo, page_size 1 → 1 page
            (15, 4, 4),  # 15 photos, page_size 4 → 4 pages (4+4+4+3)
            (100, 7, 15),  # 100 photos, page_size 7 → 15 pages (14×7 + 1×2)
        ]

        for total_photos, page_size, expected_pages in test_cases:
            context = PluginContext(
                input_data={
                    "photos": [{"id": i} for i in range(total_photos)],
                    "collection_name": "formula_test",
                },
                config={"page_size": page_size},
                output_dir=Path("/tmp"),
            )

            result = plugin.transform_data(context)
            actual_pages = result.output_data["transform_metadata"]["total_pages"]

            assert actual_pages == expected_pages, (
                f"Photos: {total_photos}, Page size: {page_size}, Expected: {expected_pages}, Got: {actual_pages}"
            )
