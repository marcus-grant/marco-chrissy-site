"""Unit tests for TemplatePlugin interface and contract validation."""

import pytest
from pathlib import Path

from galleria.plugins.base import PluginContext, PluginResult
from galleria.plugins.interfaces import TemplatePlugin
from galleria.plugins.exceptions import (
    PluginValidationError,
    PluginExecutionError,
    PluginDependencyError,
)


class ConcreteTemplatePlugin(TemplatePlugin):
    """Concrete implementation for testing TemplatePlugin interface."""

    @property
    def name(self) -> str:
        return "test-template"

    @property
    def version(self) -> str:
        return "1.0.0"

    def generate_html(self, context: PluginContext) -> PluginResult:
        """Mock implementation for testing."""
        return PluginResult(
            success=True,
            output_data={
                "html_files": [{"filename": "test.html", "content": "<html></html>"}],
                "collection_name": context.input_data.get("collection_name", "test"),
                "file_count": 1,
            },
        )


class TestTemplatePluginInterface:
    """Test TemplatePlugin interface contract and validation."""

    def test_template_plugin_inherits_from_base_plugin(self):
        """TemplatePlugin should inherit from BasePlugin."""
        plugin = ConcreteTemplatePlugin()
        
        # Should have base plugin properties
        assert hasattr(plugin, "name")
        assert hasattr(plugin, "version")
        assert hasattr(plugin, "execute")
        
        # Should have template-specific method
        assert hasattr(plugin, "generate_html")

    def test_generate_html_abstract_method_required(self):
        """TemplatePlugin.generate_html should be abstract and required."""
        
        class IncompleteTemplatePlugin(TemplatePlugin):
            @property
            def name(self) -> str:
                return "incomplete"

            @property
            def version(self) -> str:
                return "1.0.0"
            # Missing generate_html implementation

        # Should not be able to instantiate without generate_html
        with pytest.raises(TypeError):
            IncompleteTemplatePlugin()

    def test_execute_delegates_to_generate_html(self, tmp_path):
        """TemplatePlugin.execute should delegate to generate_html method."""
        plugin = ConcreteTemplatePlugin()
        
        context = PluginContext(
            input_data={
                "pages": [["photo1.jpg", "photo2.jpg"]],
                "collection_name": "test_collection",
            },
            config={"theme": "minimal"},
            output_dir=tmp_path,
        )

        result = plugin.execute(context)

        # Should return PluginResult from generate_html
        assert result.success
        assert result.output_data["collection_name"] == "test_collection"
        assert result.output_data["html_files"]

    def test_generate_html_with_valid_transform_data(self, tmp_path):
        """generate_html should handle valid transform data input."""
        plugin = ConcreteTemplatePlugin()
        
        # Test with pages data (from pagination transform)
        pages_context = PluginContext(
            input_data={
                "pages": [
                    ["photo1.jpg", "photo2.jpg"],
                    ["photo3.jpg", "photo4.jpg"],
                ],
                "collection_name": "wedding",
                "transform_metadata": {"page_size": 2},
            },
            config={"theme": "elegant", "layout": "grid"},
            output_dir=tmp_path,
        )

        result = plugin.generate_html(pages_context)

        assert result.success
        assert "html_files" in result.output_data
        assert result.output_data["collection_name"] == "wedding"

    def test_generate_html_output_format_contract(self, tmp_path):
        """generate_html should return data in expected format."""
        plugin = ConcreteTemplatePlugin()
        
        context = PluginContext(
            input_data={
                "pages": [["photo1.jpg"]],
                "collection_name": "test",
            },
            config={},
            output_dir=tmp_path,
        )

        result = plugin.generate_html(context)

        # Verify required output format
        assert result.success
        assert "html_files" in result.output_data
        assert "collection_name" in result.output_data
        assert "file_count" in result.output_data

        # Verify html_files structure
        html_files = result.output_data["html_files"]
        assert isinstance(html_files, list)
        if html_files:
            html_file = html_files[0]
            assert "filename" in html_file

    def test_generate_html_preserves_collection_name(self, tmp_path):
        """generate_html should preserve collection_name from input."""
        plugin = ConcreteTemplatePlugin()
        
        context = PluginContext(
            input_data={
                "pages": [["photo1.jpg"]],
                "collection_name": "preserve_me",
            },
            config={},
            output_dir=tmp_path,
        )

        result = plugin.generate_html(context)

        assert result.output_data["collection_name"] == "preserve_me"

    def test_generate_html_with_empty_pages(self, tmp_path):
        """generate_html should handle empty pages gracefully."""
        plugin = ConcreteTemplatePlugin()
        
        context = PluginContext(
            input_data={
                "pages": [],
                "collection_name": "empty",
            },
            config={},
            output_dir=tmp_path,
        )

        result = plugin.generate_html(context)

        assert result.success
        assert result.output_data["collection_name"] == "empty"


class TestTemplatePluginValidation:
    """Test TemplatePlugin input validation and error handling."""

    def test_generate_html_validates_required_input_fields(self, tmp_path):
        """generate_html should validate required input fields."""
        
        class ValidatingTemplatePlugin(TemplatePlugin):
            @property
            def name(self) -> str:
                return "validator"

            @property 
            def version(self) -> str:
                return "1.0.0"

            def generate_html(self, context: PluginContext) -> PluginResult:
                # Validate required fields
                if "collection_name" not in context.input_data:
                    return PluginResult(
                        success=False,
                        output_data={},
                        errors=["MISSING_COLLECTION_NAME: collection_name required"]
                    )
                
                return PluginResult(success=True, output_data={"html_files": []})

        plugin = ValidatingTemplatePlugin()
        
        # Missing collection_name should fail validation
        context = PluginContext(
            input_data={"pages": []},  # Missing collection_name
            config={},
            output_dir=tmp_path,
        )

        result = plugin.generate_html(context)
        assert not result.success
        assert result.errors
        assert "MISSING_COLLECTION_NAME" in result.errors[0]

    def test_generate_html_handles_configuration_errors(self, tmp_path):
        """generate_html should handle invalid configuration gracefully."""
        
        class ConfigValidatingTemplatePlugin(TemplatePlugin):
            @property
            def name(self) -> str:
                return "config-validator"

            @property
            def version(self) -> str:
                return "1.0.0"

            def generate_html(self, context: PluginContext) -> PluginResult:
                # Validate theme configuration
                theme = context.config.get("theme")
                if theme and theme not in ["minimal", "elegant", "modern"]:
                    return PluginResult(
                        success=False,
                        output_data={},
                        errors=[f"INVALID_THEME: Unknown theme: {theme}"]
                    )
                
                return PluginResult(success=True, output_data={"html_files": []})

        plugin = ConfigValidatingTemplatePlugin()
        
        context = PluginContext(
            input_data={"collection_name": "test", "pages": []},
            config={"theme": "invalid_theme"},
            output_dir=tmp_path,
        )

        result = plugin.generate_html(context)
        assert not result.success
        assert "INVALID_THEME" in result.errors[0]