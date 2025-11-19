"""Plugin registry for managing plugin instances."""


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