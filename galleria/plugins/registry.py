"""Plugin registry for managing plugin instances."""

import inspect
import pkgutil

from .interfaces import (
    CSSPlugin,
    ProcessorPlugin,
    ProviderPlugin,
    TemplatePlugin,
    TransformPlugin,
)


class PluginRegistry:
    """Registry for managing plugin instances and discovery."""

    VALID_STAGES = {"provider", "processor", "transform", "template", "css"}

    def __init__(self):
        """Initialize empty plugin registry."""
        self._plugins = {}

    def register(self, plugin, stage):
        """Register a plugin for a specific stage.

        Args:
            plugin: Plugin instance to register
            stage: Stage name (e.g., 'provider', 'processor')

        Raises:
            ValueError: If stage is not valid
        """
        if stage not in self.VALID_STAGES:
            raise ValueError(f"Invalid stage '{stage}'. Valid stages: {sorted(self.VALID_STAGES)}")

        if stage not in self._plugins:
            self._plugins[stage] = []
        self._plugins[stage].append(plugin)

    def get_plugin(self, name, stage):
        """Retrieve a plugin by name and stage.

        Args:
            name: Plugin name to find
            stage: Stage name to search in

        Returns:
            Plugin instance if found, None otherwise

        Raises:
            ValueError: If stage is not valid
        """
        if stage not in self.VALID_STAGES:
            raise ValueError(f"Invalid stage '{stage}'. Valid stages: {sorted(self.VALID_STAGES)}")

        if stage not in self._plugins:
            return None

        for plugin in self._plugins[stage]:
            if plugin.name == name:
                return plugin
        return None

    def discover_plugins(self):
        """Discover concrete plugin implementations.

        Returns:
            Dict mapping stage names to lists of plugin classes
        """
        discovered = {stage: [] for stage in self.VALID_STAGES}

        # Stage -> interface mappings
        stage_interfaces = {
            "provider": ProviderPlugin,
            "processor": ProcessorPlugin,
            "transform": TransformPlugin,
            "template": TemplatePlugin,
            "css": CSSPlugin,
        }

        # Import and check plugin modules
        try:
            from . import providers
            self._discover_in_module(providers, "provider", stage_interfaces["provider"], discovered)
        except ImportError:
            pass

        try:
            from . import processors
            self._discover_in_module(processors, "processor", stage_interfaces["processor"], discovered)
        except ImportError:
            pass

        return discovered

    def _discover_in_module(self, module, stage, interface_cls, discovered):
        """Helper to discover plugins in a specific module."""
        for _importer, modname, _ispkg in pkgutil.iter_modules(module.__path__, module.__name__ + "."):
            try:
                plugin_module = __import__(modname, fromlist=[""])
                for _name, obj in inspect.getmembers(plugin_module, inspect.isclass):
                    if (issubclass(obj, interface_cls) and
                        obj is not interface_cls and
                        not inspect.isabstract(obj)):
                        discovered[stage].append(obj)
            except ImportError:
                continue
