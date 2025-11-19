"""Unit tests for BasePlugin abstract base class."""

import pytest

from galleria.plugins.base import BasePlugin


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
