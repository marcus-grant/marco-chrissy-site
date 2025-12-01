"""Basic unit tests for PluginRegistry - just initialization."""


class TestPluginRegistryBasic:
    """Basic tests for PluginRegistry initialization."""

    def test_plugin_registry_can_be_created(self):
        """Test PluginRegistry can be instantiated."""
        from galleria.plugins.registry import PluginRegistry

        registry = PluginRegistry()
        assert registry is not None

    def test_register_plugin_stores_plugin_instance(self):
        """Test that register() method stores plugin instances."""
        from galleria.plugins.base import BasePlugin
        from galleria.plugins.registry import PluginRegistry

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
        from galleria.plugins.base import BasePlugin
        from galleria.plugins.registry import PluginRegistry

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
            raise AssertionError("Should require stage parameter")
        except TypeError:
            pass  # Expected

    def test_get_plugin_retrieves_registered_plugin(self):
        """Test that get_plugin() retrieves plugins by name and stage."""
        from galleria.plugins.base import BasePlugin
        from galleria.plugins.registry import PluginRegistry

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
        from galleria.plugins.base import BasePlugin
        from galleria.plugins.registry import PluginRegistry

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
            raise AssertionError("Should reject invalid stage")
        except ValueError as e:
            assert "invalid" in str(e).lower()

    def test_get_plugin_validates_stage_names(self):
        """Test that get_plugin() validates stage names."""
        from galleria.plugins.registry import PluginRegistry

        registry = PluginRegistry()

        # Invalid stage should raise error
        try:
            registry.get_plugin("test", stage="invalid")
            raise AssertionError("Should reject invalid stage")
        except ValueError as e:
            assert "invalid" in str(e).lower()

    def test_discover_plugins_finds_concrete_implementations(self):
        """Test that discover_plugins() finds concrete plugin implementations."""
        from galleria.plugins.registry import PluginRegistry

        registry = PluginRegistry()

        # This should find NormPic and Thumbnail plugins
        discovered = registry.discover_plugins()

        # Should return dict with stage -> list of plugin classes
        assert isinstance(discovered, dict)
        assert "provider" in discovered
        assert "processor" in discovered

        # Should find actual plugin classes
        provider_classes = discovered["provider"]
        assert len(provider_classes) > 0
        assert any("normpic" in cls.__name__.lower() for cls in provider_classes)

        processor_classes = discovered["processor"]
        assert len(processor_classes) > 0
        assert any("thumbnail" in cls.__name__.lower() for cls in processor_classes)

    def test_discover_plugins_returns_only_concrete_classes(self):
        """Test that discover_plugins() excludes abstract base classes."""
        from galleria.plugins.registry import PluginRegistry

        registry = PluginRegistry()
        discovered = registry.discover_plugins()

        # Should not include abstract base classes
        for _stage, plugin_classes in discovered.items():
            for plugin_cls in plugin_classes:
                # Should be able to instantiate (concrete, not abstract)
                try:
                    instance = plugin_cls()
                    assert hasattr(instance, "name")
                    assert hasattr(instance, "version")
                except TypeError as e:
                    raise AssertionError(
                        f"{plugin_cls} should be concrete, not abstract"
                    ) from e
