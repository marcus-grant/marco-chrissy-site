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
                "css_files": [{"filename": "gallery.css", "content": "body { margin: 0; }"}],
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
                    {"filename": "page_1.html", "content": "<html></html>", "page_number": 1},
                    {"filename": "page_2.html", "content": "<html></html>", "page_number": 2},
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
                        errors=["MISSING_COLLECTION_NAME: collection_name required"]
                    )

                if "html_files" not in context.input_data:
                    return PluginResult(
                        success=False,
                        output_data={},
                        errors=["MISSING_HTML_FILES: html_files required"]
                    )

                return PluginResult(success=True, output_data={
                    "css_files": [],
                    "html_files": context.input_data["html_files"],
                    "collection_name": context.input_data["collection_name"],
                    "css_count": 0,
                })

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
                        errors=[f"INVALID_THEME: Unknown theme: {theme}"]
                    )

                return PluginResult(success=True, output_data={
                    "css_files": [],
                    "html_files": [],
                    "collection_name": "test",
                    "css_count": 0,
                })

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
                return PluginResult(success=True, output_data={
                    "css_files": [{"filename": "large.css", "content": large_css_content}],
                    "html_files": context.input_data.get("html_files", []),
                    "collection_name": context.input_data.get("collection_name", "test"),
                    "css_count": 1,
                })

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

    def test_generate_css_with_malformed_content_structure(self, galleria_temp_filesystem):
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
                return PluginResult(success=True, output_data={
                    "css_files": [
                        {"filename": "test.css", "content": None},  # None content
                        {"filename": "test2.css"},  # Missing content key
                        {"filename": "test3.css", "content": 123},  # Non-string content
                    ],
                    "html_files": [],
                    "collection_name": "malformed",
                    "css_count": 3,
                })

        plugin = MalformedContentCSSPlugin()
        context = PluginContext(
            input_data={"collection_name": "test", "html_files": []},
            config={},
            output_dir=galleria_temp_filesystem,
        )

        result = plugin.generate_css(context)
        assert result.success
        # Plugin returns malformed data - this tests CLI resilience
