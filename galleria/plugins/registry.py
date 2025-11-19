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

    def get_plugin(self, name, stage):
        """Retrieve a plugin by name and stage.
        
        Args:
            name: Plugin name to find
            stage: Stage name to search in
            
        Returns:
            Plugin instance if found, None otherwise
        """
        if stage not in self._plugins:
            return None
        
        for plugin in self._plugins[stage]:
            if plugin.name == name:
                return plugin
        return None