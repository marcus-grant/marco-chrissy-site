"""Unit tests for BasePlugin abstract base class."""

from pathlib import Path

import pytest

from galleria.plugins.base import BasePlugin, PluginContext, PluginResult


class TestBasePlugin:
    """Tests for BasePlugin abstract base class."""

    def test_base_plugin_is_abstract_class(self):
        """BasePlugin cannot be instantiated directly due to abstract methods."""
        with pytest.raises(TypeError) as exc_info:
            BasePlugin()

        error_message = str(exc_info.value)
        assert "Can't instantiate abstract class BasePlugin" in error_message
        assert "abstract methods" in error_message

    def test_plugin_requires_name_property(self):
        """Concrete plugins must implement name property."""

        class IncompletePlugin(BasePlugin):
            # Missing name property
            @property
            def version(self) -> str:
                return "1.0.0"

        with pytest.raises(TypeError) as exc_info:
            IncompletePlugin()

        error_message = str(exc_info.value)
        assert "Can't instantiate abstract class IncompletePlugin" in error_message
        assert "name" in error_message

    def test_plugin_requires_version_property(self):
        """Concrete plugins must implement version property."""

        class IncompletePlugin(BasePlugin):
            # Missing version property
            @property
            def name(self) -> str:
                return "test-plugin"

        with pytest.raises(TypeError) as exc_info:
            IncompletePlugin()

        error_message = str(exc_info.value)
        assert "Can't instantiate abstract class IncompletePlugin" in error_message
        assert "version" in error_message

    def test_concrete_plugin_can_be_instantiated(self):
        """A plugin implementing all abstract methods can be instantiated."""

        class ConcretePlugin(BasePlugin):
            @property
            def name(self) -> str:
                return "test-plugin"

            @property
            def version(self) -> str:
                return "1.0.0"

        # Should not raise any exception
        plugin = ConcretePlugin()

        # Verify properties work correctly
        assert plugin.name == "test-plugin"
        assert plugin.version == "1.0.0"

    def test_plugin_name_property_returns_string(self):
        """Plugin name property must return a string."""

        class TestPlugin(BasePlugin):
            @property
            def name(self) -> str:
                return "my-plugin"

            @property
            def version(self) -> str:
                return "2.1.0"

        plugin = TestPlugin()
        assert isinstance(plugin.name, str)
        assert plugin.name == "my-plugin"

    def test_plugin_version_property_returns_string(self):
        """Plugin version property must return a string."""

        class TestPlugin(BasePlugin):
            @property
            def name(self) -> str:
                return "versioned-plugin"

            @property
            def version(self) -> str:
                return "3.2.1"

        plugin = TestPlugin()
        assert isinstance(plugin.version, str)
        assert plugin.version == "3.2.1"


class TestPluginContext:
    """Tests for PluginContext dataclass."""

    def test_plugin_context_creation_with_required_fields(self):
        """PluginContext can be created with all required fields."""
        context = PluginContext(
            input_data={"photos": []},
            config={"size": 400},
            output_dir=Path("/tmp/output")
        )

        assert context.input_data == {"photos": []}
        assert context.config == {"size": 400}
        assert context.output_dir == Path("/tmp/output")
        assert context.metadata == {}  # Default empty dict

    def test_plugin_context_with_metadata(self):
        """PluginContext can be created with custom metadata."""
        metadata = {"stage": "processing", "timestamp": 1234567890}
        context = PluginContext(
            input_data="test_data",
            config={},
            output_dir=Path("/tmp"),
            metadata=metadata
        )

        assert context.metadata == metadata

    def test_plugin_context_metadata_defaults_to_empty_dict(self):
        """PluginContext metadata defaults to empty dict if not provided."""
        context = PluginContext(
            input_data=None,
            config={},
            output_dir=Path("/tmp")
        )

        assert context.metadata == {}
        assert isinstance(context.metadata, dict)

    def test_plugin_context_accepts_any_input_data_type(self):
        """PluginContext accepts various input data types."""
        # Test with different data types
        for input_data in [None, "string", 123, [], {}, Path("/test")]:
            context = PluginContext(
                input_data=input_data,
                config={},
                output_dir=Path("/tmp")
            )
            assert context.input_data == input_data

    def test_plugin_context_output_dir_is_path_object(self):
        """PluginContext output_dir should be a Path object."""
        output_dir = Path("/some/output/path")
        context = PluginContext(
            input_data=None,
            config={},
            output_dir=output_dir
        )

        assert isinstance(context.output_dir, Path)
        assert context.output_dir == output_dir


class TestPluginResult:
    """Tests for PluginResult dataclass."""

    def test_plugin_result_creation_with_required_fields(self):
        """PluginResult can be created with all required fields."""
        result = PluginResult(
            success=True,
            output_data=["thumbnail1.webp", "thumbnail2.webp"]
        )

        assert result.success is True
        assert result.output_data == ["thumbnail1.webp", "thumbnail2.webp"]
        assert result.errors == []  # Default empty list
        assert result.metadata == {}  # Default empty dict

    def test_plugin_result_failure_with_errors(self):
        """PluginResult can represent failure with error messages."""
        errors = ["File not found", "Permission denied"]
        result = PluginResult(
            success=False,
            output_data=None,
            errors=errors
        )

        assert result.success is False
        assert result.output_data is None
        assert result.errors == errors

    def test_plugin_result_with_metadata(self):
        """PluginResult can include execution metadata."""
        metadata = {"duration": 2.5, "files_processed": 10}
        result = PluginResult(
            success=True,
            output_data="completed",
            metadata=metadata
        )

        assert result.metadata == metadata

    def test_plugin_result_defaults_empty_collections(self):
        """PluginResult errors and metadata default to empty collections."""
        result = PluginResult(
            success=True,
            output_data="test"
        )

        assert result.errors == []
        assert result.metadata == {}
        assert isinstance(result.errors, list)
        assert isinstance(result.metadata, dict)

    def test_plugin_result_accepts_any_output_data_type(self):
        """PluginResult accepts various output data types."""
        # Test with different data types
        for output_data in [None, "string", 123, [], {}, Path("/test")]:
            result = PluginResult(
                success=True,
                output_data=output_data
            )
            assert result.output_data == output_data

    def test_plugin_result_success_is_boolean(self):
        """PluginResult success field should be boolean."""
        # Test both boolean values
        for success_value in [True, False]:
            result = PluginResult(
                success=success_value,
                output_data=None
            )
            assert isinstance(result.success, bool)
            assert result.success == success_value
