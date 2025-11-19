"""Pipeline manager for orchestrating plugin execution."""

from ..plugins.base import PluginResult
from ..plugins.registry import PluginRegistry


class PipelineManager:
    """Manager for orchestrating plugin pipeline execution."""

    def __init__(self, registry=None):
        """Initialize pipeline manager.
        
        Args:
            registry: PluginRegistry instance, creates new one if None
        """
        self.registry = registry or PluginRegistry()

    def execute_single_stage(self, stage, plugin_name, context):
        """Execute a single plugin stage.
        
        Args:
            stage: Stage name (e.g., 'provider', 'processor')
            plugin_name: Name of plugin to execute
            context: PluginContext with input data
            
        Returns:
            PluginResult with execution results
        """
        plugin = self.registry.get_plugin(plugin_name, stage)
        
        if plugin is None:
            return PluginResult(
                success=False,
                output_data={},
                errors=[f"Plugin '{plugin_name}' not found in stage '{stage}'"]
            )
        
        try:
            return plugin.execute(context)
        except Exception as e:
            return PluginResult(
                success=False,
                output_data={},
                errors=[f"Plugin execution failed: {str(e)}"]
            )