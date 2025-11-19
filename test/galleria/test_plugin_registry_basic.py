"""Basic unit tests for PluginRegistry - just initialization."""

import pytest


class TestPluginRegistryBasic:
    """Basic tests for PluginRegistry initialization."""

    def test_plugin_registry_can_be_created(self):
        """Test PluginRegistry can be instantiated."""
        # This will fail - registry doesn't exist yet
        from galleria.plugins.registry import PluginRegistry
        
        registry = PluginRegistry()
        assert registry is not None