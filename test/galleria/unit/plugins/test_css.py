"""Unit tests for CSSPlugin interface and contract validation."""

import pytest

from galleria.plugins.base import PluginContext, PluginResult
from galleria.plugins.interfaces import CSSPlugin


class ConcreteCSSPlugin(CSSPlugin):
    """Concrete implementation for testing CSSPlugin interface."""

    @property
    def name(self) -> str:
        return "test-css"

    @property
    def version(self) -> str:
        return "1.0.0"

    def generate_css(self, context: PluginContext) -> PluginResult:
        """Mock implementation for testing."""
        return PluginResult(
            success=True,
            output_data={
                "css_files": [
                    {"filename": "gallery.css", "content": "body { margin: 0; }"}
                ],
                "html_files": context.input_data.get("html_files", []),
                "collection_name": context.input_data.get("collection_name", "test"),
                "css_count": 1,
            },
        )


class TestCSSPluginInterface:
    """Test CSSPlugin interface contract and validation."""

    def test_css_plugin_inherits_from_base_plugin(self):
        """CSSPlugin should inherit from BasePlugin."""
        plugin = ConcreteCSSPlugin()

        # Should have base plugin properties
        assert hasattr(plugin, "name")
        assert hasattr(plugin, "version")
        assert hasattr(plugin, "execute")

        # Should have css-specific method
        assert hasattr(plugin, "generate_css")

    def test_generate_css_abstract_method_required(self):
        """CSSPlugin.generate_css should be abstract and required."""

        class IncompleteCSSPlugin(CSSPlugin):
            @property
            def name(self) -> str:
                return "incomplete"

            @property
            def version(self) -> str:
                return "1.0.0"

            # Missing generate_css implementation

        # Should not be able to instantiate without generate_css
        with pytest.raises(TypeError):
            IncompleteCSSPlugin()

    def test_execute_delegates_to_generate_css(self, tmp_path):
        """CSSPlugin.execute should delegate to generate_css method."""
        plugin = ConcreteCSSPlugin()

        context = PluginContext(
            input_data={
                "html_files": [{"filename": "page_1.html", "page_number": 1}],
                "collection_name": "test_collection",
                "file_count": 1,
            },
            config={"theme": "dark"},
            output_dir=tmp_path,
        )

        result = plugin.execute(context)

        # Should return PluginResult from generate_css
        assert result.success
        assert result.output_data["collection_name"] == "test_collection"
        assert result.output_data["css_files"]

    def test_generate_css_with_valid_template_data(self, tmp_path):
        """generate_css should handle valid template data input."""
        plugin = ConcreteCSSPlugin()

        # Test with html_files data (from template stage)
        template_context = PluginContext(
            input_data={
                "html_files": [
                    {
                        "filename": "page_1.html",
                        "content": "<html></html>",
                        "page_number": 1,
                    },
                    {
                        "filename": "page_2.html",
                        "content": "<html></html>",
                        "page_number": 2,
                    },
                ],
                "collection_name": "wedding",
                "file_count": 2,
            },
            config={"theme": "elegant", "responsive": True},
            output_dir=tmp_path,
        )

        result = plugin.generate_css(template_context)

        assert result.success
        assert "css_files" in result.output_data
        assert result.output_data["collection_name"] == "wedding"

    def test_generate_css_output_format_contract(self, tmp_path):
        """generate_css should return data in expected format."""
        plugin = ConcreteCSSPlugin()

        context = PluginContext(
            input_data={
                "html_files": [{"filename": "index.html"}],
                "collection_name": "test",
                "file_count": 1,
            },
            config={},
            output_dir=tmp_path,
        )

        result = plugin.generate_css(context)

        # Verify required output format
        assert result.success
        assert "css_files" in result.output_data
        assert "html_files" in result.output_data  # Pass through from input
        assert "collection_name" in result.output_data
        assert "css_count" in result.output_data

        # Verify css_files structure
        css_files = result.output_data["css_files"]
        assert isinstance(css_files, list)
        if css_files:
            css_file = css_files[0]
            assert "filename" in css_file

    def test_generate_css_preserves_html_files(self, tmp_path):
        """generate_css should pass through html_files from input."""
        plugin = ConcreteCSSPlugin()

        html_files = [
            {"filename": "page_1.html", "page_number": 1},
            {"filename": "page_2.html", "page_number": 2},
        ]

        context = PluginContext(
            input_data={
                "html_files": html_files,
                "collection_name": "preserve_test",
                "file_count": 2,
            },
            config={},
            output_dir=tmp_path,
        )

        result = plugin.generate_css(context)

        assert result.output_data["html_files"] == html_files
        assert result.output_data["collection_name"] == "preserve_test"

    def test_generate_css_with_empty_html_files(self, tmp_path):
        """generate_css should handle empty html_files gracefully."""
        plugin = ConcreteCSSPlugin()

        context = PluginContext(
            input_data={
                "html_files": [],
                "collection_name": "empty",
                "file_count": 0,
            },
            config={},
            output_dir=tmp_path,
        )

        result = plugin.generate_css(context)

        assert result.success
        assert result.output_data["collection_name"] == "empty"
        assert result.output_data["html_files"] == []


class TestCSSPluginValidation:
    """Test CSSPlugin input validation and error handling."""

    def test_generate_css_validates_required_input_fields(self, tmp_path):
        """generate_css should validate required input fields."""

        class ValidatingCSSPlugin(CSSPlugin):
            @property
            def name(self) -> str:
                return "validator"

            @property
            def version(self) -> str:
                return "1.0.0"

            def generate_css(self, context: PluginContext) -> PluginResult:
                # Validate required fields
                if "collection_name" not in context.input_data:
                    return PluginResult(
                        success=False,
                        output_data={},
                        errors=["MISSING_COLLECTION_NAME: collection_name required"],
                    )

                if "html_files" not in context.input_data:
                    return PluginResult(
                        success=False,
                        output_data={},
                        errors=["MISSING_HTML_FILES: html_files required"],
                    )

                return PluginResult(
                    success=True,
                    output_data={
                        "css_files": [],
                        "html_files": context.input_data["html_files"],
                        "collection_name": context.input_data["collection_name"],
                        "css_count": 0,
                    },
                )

        plugin = ValidatingCSSPlugin()

        # Missing collection_name should fail validation
        context = PluginContext(
            input_data={"html_files": []},  # Missing collection_name
            config={},
            output_dir=tmp_path,
        )

        result = plugin.generate_css(context)
        assert not result.success
        assert result.errors
        assert "MISSING_COLLECTION_NAME" in result.errors[0]

        # Missing html_files should fail validation
        context = PluginContext(
            input_data={"collection_name": "test"},  # Missing html_files
            config={},
            output_dir=tmp_path,
        )

        result = plugin.generate_css(context)
        assert not result.success
        assert result.errors
        assert "MISSING_HTML_FILES" in result.errors[0]

    def test_generate_css_handles_configuration_errors(self, tmp_path):
        """generate_css should handle invalid configuration gracefully."""

        class ConfigValidatingCSSPlugin(CSSPlugin):
            @property
            def name(self) -> str:
                return "config-validator"

            @property
            def version(self) -> str:
                return "1.0.0"

            def generate_css(self, context: PluginContext) -> PluginResult:
                # Validate theme configuration
                theme = context.config.get("theme")
                if theme and theme not in ["light", "dark", "auto"]:
                    return PluginResult(
                        success=False,
                        output_data={},
                        errors=[f"INVALID_THEME: Unknown theme: {theme}"],
                    )

                return PluginResult(
                    success=True,
                    output_data={
                        "css_files": [],
                        "html_files": [],
                        "collection_name": "test",
                        "css_count": 0,
                    },
                )

        plugin = ConfigValidatingCSSPlugin()

        context = PluginContext(
            input_data={"collection_name": "test", "html_files": []},
            config={"theme": "invalid_theme"},
            output_dir=tmp_path,
        )

        result = plugin.generate_css(context)
        assert not result.success
        assert "INVALID_THEME" in result.errors[0]

    def test_generate_css_with_large_content_payload(self, galleria_temp_filesystem):
        """generate_css should handle large content payloads without infinite loops."""

        class LargeContentCSSPlugin(CSSPlugin):
            @property
            def name(self) -> str:
                return "large-content"

            @property
            def version(self) -> str:
                return "1.0.0"

            def generate_css(self, context: PluginContext) -> PluginResult:
                # Generate very large CSS content (1MB)
                large_css_content = "body { margin: 0; }\n" * 50000
                return PluginResult(
                    success=True,
                    output_data={
                        "css_files": [
                            {"filename": "large.css", "content": large_css_content}
                        ],
                        "html_files": context.input_data.get("html_files", []),
                        "collection_name": context.input_data.get(
                            "collection_name", "test"
                        ),
                        "css_count": 1,
                    },
                )

        plugin = LargeContentCSSPlugin()
        context = PluginContext(
            input_data={
                "collection_name": "large_test",
                "html_files": [],
                "file_count": 0,
            },
            config={},
            output_dir=galleria_temp_filesystem,
        )

        result = plugin.generate_css(context)
        assert result.success
        assert result.output_data["css_files"][0]["content"]
        # Content should be large but finite
        assert len(result.output_data["css_files"][0]["content"]) > 100000

    def test_generate_css_with_malformed_content_structure(
        self, galleria_temp_filesystem
    ):
        """generate_css should handle malformed content structure gracefully."""

        class MalformedContentCSSPlugin(CSSPlugin):
            @property
            def name(self) -> str:
                return "malformed"

            @property
            def version(self) -> str:
                return "1.0.0"

            def generate_css(self, context: PluginContext) -> PluginResult:
                # Test with various malformed content types
                return PluginResult(
                    success=True,
                    output_data={
                        "css_files": [
                            {"filename": "test.css", "content": None},  # None content
                            {"filename": "test2.css"},  # Missing content key
                            {
                                "filename": "test3.css",
                                "content": 123,
                            },  # Non-string content
                        ],
                        "html_files": [],
                        "collection_name": "malformed",
                        "css_count": 3,
                    },
                )

        plugin = MalformedContentCSSPlugin()
        context = PluginContext(
            input_data={"collection_name": "test", "html_files": []},
            config={},
            output_dir=galleria_temp_filesystem,
        )

        result = plugin.generate_css(context)
        assert result.success
        # Plugin returns malformed data - this tests CLI resilience


class TestResponsiveGalleryGrid:
    """Test gallery CSS generates mobile-first responsive grid breakpoints."""

    def test_gallery_css_has_mobile_first_default(self, tmp_path):
        """Verify gallery CSS defaults to 2 columns for mobile-first approach."""
        from galleria.plugins.css import BasicCSSPlugin

        plugin = BasicCSSPlugin()
        context = PluginContext(
            input_data={
                "collection_name": "test",
                "html_files": [{"filename": "page_1.html"}],
            },
            config={"layout": "grid"},
            output_dir=tmp_path,
        )

        result = plugin.generate_css(context)
        assert result.success

        # Find gallery.css content
        gallery_css = None
        for css_file in result.output_data["css_files"]:
            if css_file["filename"] == "gallery.css":
                gallery_css = css_file["content"]
                break

        assert gallery_css is not None, "gallery.css should be generated"
        # Mobile-first: default should be 2 columns
        assert "grid-template-columns: repeat(2, 1fr)" in gallery_css, \
            "Gallery should default to 2 columns (mobile-first)"

    def test_gallery_css_has_560px_breakpoint(self, tmp_path):
        """Verify gallery CSS has 3 columns at 560px breakpoint."""
        from galleria.plugins.css import BasicCSSPlugin

        plugin = BasicCSSPlugin()
        context = PluginContext(
            input_data={
                "collection_name": "test",
                "html_files": [{"filename": "page_1.html"}],
            },
            config={"layout": "grid"},
            output_dir=tmp_path,
        )

        result = plugin.generate_css(context)
        gallery_css = next(
            f["content"] for f in result.output_data["css_files"]
            if f["filename"] == "gallery.css"
        )

        assert "560px" in gallery_css, "Should have 560px breakpoint"
        assert "repeat(3, 1fr)" in gallery_css, "Should have 3 columns at 560px"

    def test_gallery_css_has_768px_breakpoint(self, tmp_path):
        """Verify gallery CSS has 4 columns at 768px breakpoint."""
        from galleria.plugins.css import BasicCSSPlugin

        plugin = BasicCSSPlugin()
        context = PluginContext(
            input_data={
                "collection_name": "test",
                "html_files": [{"filename": "page_1.html"}],
            },
            config={"layout": "grid"},
            output_dir=tmp_path,
        )

        result = plugin.generate_css(context)
        gallery_css = next(
            f["content"] for f in result.output_data["css_files"]
            if f["filename"] == "gallery.css"
        )

        assert "768px" in gallery_css, "Should have 768px breakpoint"
        assert "repeat(4, 1fr)" in gallery_css, "Should have 4 columns at 768px"

    def test_gallery_css_has_1024px_breakpoint(self, tmp_path):
        """Verify gallery CSS has 6 columns at 1024px breakpoint."""
        from galleria.plugins.css import BasicCSSPlugin

        plugin = BasicCSSPlugin()
        context = PluginContext(
            input_data={
                "collection_name": "test",
                "html_files": [{"filename": "page_1.html"}],
            },
            config={"layout": "grid"},
            output_dir=tmp_path,
        )

        result = plugin.generate_css(context)
        gallery_css = next(
            f["content"] for f in result.output_data["css_files"]
            if f["filename"] == "gallery.css"
        )

        assert "1024px" in gallery_css, "Should have 1024px breakpoint"
        assert "repeat(6, 1fr)" in gallery_css, "Should have 6 columns at 1024px"

    def test_gallery_css_breakpoints_are_min_width(self, tmp_path):
        """Verify breakpoints use min-width for mobile-first approach."""
        from galleria.plugins.css import BasicCSSPlugin

        plugin = BasicCSSPlugin()
        context = PluginContext(
            input_data={
                "collection_name": "test",
                "html_files": [{"filename": "page_1.html"}],
            },
            config={"layout": "grid"},
            output_dir=tmp_path,
        )

        result = plugin.generate_css(context)
        gallery_css = next(
            f["content"] for f in result.output_data["css_files"]
            if f["filename"] == "gallery.css"
        )

        # Mobile-first uses min-width media queries
        assert "min-width: 560px" in gallery_css, "Should use min-width for 560px"
        assert "min-width: 768px" in gallery_css, "Should use min-width for 768px"
        assert "min-width: 1024px" in gallery_css, "Should use min-width for 1024px"


class TestPaginationTouchTargets:
    """Test pagination CSS has touch-friendly target sizes per WCAG 2.1 AAA."""

    def test_pagination_links_have_min_height_44px(self, tmp_path):
        """Verify pagination links have min-height: 44px for touch accessibility."""
        from galleria.plugins.css import BasicCSSPlugin

        plugin = BasicCSSPlugin()
        context = PluginContext(
            input_data={
                "collection_name": "test",
                "html_files": [{"filename": "page_1.html"}],
            },
            config={"layout": "grid"},
            output_dir=tmp_path,
        )

        result = plugin.generate_css(context)
        gallery_css = next(
            f["content"] for f in result.output_data["css_files"]
            if f["filename"] == "gallery.css"
        )

        # Pagination links should have min-height for touch targets
        assert "min-height: 44px" in gallery_css, \
            "Pagination links should have min-height: 44px for touch accessibility"

    def test_pagination_links_have_min_width_for_consistency(self, tmp_path):
        """Verify pagination links have min-width for consistent button sizing."""
        from galleria.plugins.css import BasicCSSPlugin

        plugin = BasicCSSPlugin()
        context = PluginContext(
            input_data={
                "collection_name": "test",
                "html_files": [{"filename": "page_1.html"}],
            },
            config={"layout": "grid"},
            output_dir=tmp_path,
        )

        result = plugin.generate_css(context)
        gallery_css = next(
            f["content"] for f in result.output_data["css_files"]
            if f["filename"] == "gallery.css"
        )

        # Pagination links should have min-width for consistent sizing (6em > 44px at 16px base)
        assert "min-width: 6em" in gallery_css, \
            "Pagination links should have min-width: 6em for consistent button width"
