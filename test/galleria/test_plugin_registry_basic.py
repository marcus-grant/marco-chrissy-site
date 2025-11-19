"""Basic unit tests for PluginRegistry - just initialization."""

import pytest


class TestPluginRegistryBasic:
    """Basic tests for PluginRegistry initialization."""

    def test_plugin_registry_can_be_created(self):
        """Test PluginRegistry can be instantiated."""
        from galleria.plugins.registry import PluginRegistry
        
        registry = PluginRegistry()
        assert registry is not None

    def test_register_plugin_stores_plugin_instance(self):
        """Test that register() method stores plugin instances."""
        from galleria.plugins.registry import PluginRegistry
        from galleria.plugins.base import BasePlugin
        
        # Create mock plugin
        class MockPlugin(BasePlugin):
            @property
            def name(self):
                return "mock"
            
            @property  
            def version(self):
                return "1.0.0"
            
            def execute(self, context):
                return None
        
        registry = PluginRegistry()
        plugin = MockPlugin()
        
        # This should work
        registry.register(plugin, stage="provider")
        
    def test_register_plugin_requires_stage_parameter(self):
        """Test that register() requires a stage parameter."""
        from galleria.plugins.registry import PluginRegistry
        from galleria.plugins.base import BasePlugin
        
        class MockPlugin(BasePlugin):
            @property
            def name(self):
                return "mock"
            
            @property  
            def version(self):
                return "1.0.0"
            
            def execute(self, context):
                return None
        
        registry = PluginRegistry()
        plugin = MockPlugin()
        
        # This should require stage parameter
        try:
            registry.register(plugin)
            assert False, "Should require stage parameter"
        except TypeError:
            pass  # Expected

    def test_get_plugin_retrieves_registered_plugin(self):
        """Test that get_plugin() retrieves plugins by name and stage."""
        from galleria.plugins.registry import PluginRegistry
        from galleria.plugins.base import BasePlugin
        
        class MockPlugin(BasePlugin):
            @property
            def name(self):
                return "mock"
            
            @property  
            def version(self):
                return "1.0.0"
            
            def execute(self, context):
                return None
        
        registry = PluginRegistry()
        plugin = MockPlugin()
        
        registry.register(plugin, stage="provider")
        
        # This should retrieve the plugin
        retrieved = registry.get_plugin("mock", stage="provider")
        assert retrieved is plugin

    def test_get_plugin_returns_none_for_missing_plugin(self):
        """Test that get_plugin() returns None for missing plugins."""
        from galleria.plugins.registry import PluginRegistry
        
        registry = PluginRegistry()
        
        # This should return None
        result = registry.get_plugin("nonexistent", stage="provider")
        assert result is None

    def test_register_plugin_validates_stage_names(self):
        """Test that register() validates stage names."""
        from galleria.plugins.registry import PluginRegistry
        from galleria.plugins.base import BasePlugin
        
        class MockPlugin(BasePlugin):
            @property
            def name(self):
                return "mock"
            
            @property  
            def version(self):
                return "1.0.0"
            
            def execute(self, context):
                return None
        
        registry = PluginRegistry()
        plugin = MockPlugin()
        
        # Valid stages should work
        registry.register(plugin, stage="provider")
        
        # Invalid stage should raise error
        try:
            registry.register(plugin, stage="invalid")
            assert False, "Should reject invalid stage"
        except ValueError as e:
            assert "invalid" in str(e).lower()

    def test_get_plugin_validates_stage_names(self):
        """Test that get_plugin() validates stage names."""
        from galleria.plugins.registry import PluginRegistry
        
        registry = PluginRegistry()
        
        # Invalid stage should raise error
        try:
            registry.get_plugin("test", stage="invalid")
            assert False, "Should reject invalid stage"
        except ValueError as e:
            assert "invalid" in str(e).lower()