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

    def execute_stages(self, stages, initial_context):
        """Execute multiple stages in sequence.

        Args:
            stages: List of stage configs. Supports both formats:
                - Dict format: [{"stage": "provider", "plugin": "name"}, ...]
                - Tuple format: [("provider", "plugin-name"), ...]
            initial_context: Initial PluginContext

        Returns:
            Final PluginResult from last stage
        """
        current_context = initial_context

        for stage_config in stages:
            # Handle both tuple and dict formats
            if isinstance(stage_config, tuple):
                stage, plugin_name = stage_config
            else:
                stage = stage_config["stage"]
                plugin_name = stage_config["plugin"]

            # Execute this stage
            result = self.execute_single_stage(stage, plugin_name, current_context)

            # If stage failed, return failure
            if not result.success:
                return result

            # Prepare context for next stage with this stage's output
            from ..plugins.base import PluginContext
            current_context = PluginContext(
                input_data=result.output_data,
                config=current_context.config,
                output_dir=current_context.output_dir,
                metadata={**current_context.metadata, **result.metadata}
            )

        return result

    def execute_workflow(self, workflow_name, **kwargs):
        """Execute a predefined workflow.

        Args:
            workflow_name: Name of workflow to execute
            **kwargs: Workflow-specific parameters

        Returns:
            PluginResult with workflow execution results
        """
        # Define supported workflows
        workflows = {
            "manifest-to-thumbnails": [
                {"stage": "provider", "plugin": "normpic-provider"},
                {"stage": "processor", "plugin": "thumbnail-processor"}
            ]
        }

        if workflow_name not in workflows:
            return PluginResult(
                success=False,
                output_data={},
                errors=[f"Unknown workflow '{workflow_name}'. Available: {list(workflows.keys())}"]
            )

        # Create initial context from workflow parameters
        from ..plugins.base import PluginContext
        initial_context = PluginContext(
            input_data={"manifest_path": kwargs.get("manifest_path")},
            config={},
            output_dir=kwargs.get("output_dir"),
            metadata={"workflow": workflow_name}
        )

        # Execute the workflow stages
        stages = workflows[workflow_name]
        return self.execute_stages(stages, initial_context)
