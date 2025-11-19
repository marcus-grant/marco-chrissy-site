"""Plugin registry for managing plugin instances."""


class PluginRegistry:
    """Registry for managing plugin instances and discovery."""

    def __init__(self):
        """Initialize empty plugin registry."""
        self._plugins = {}

    def register(self, plugin, stage):
        """Register a plugin for a specific stage.
        
        Args:
            plugin: Plugin instance to register
            stage: Stage name (e.g., 'provider', 'processor')
        """
        if stage not in self._plugins:
            self._plugins[stage] = []
        self._plugins[stage].append(plugin)