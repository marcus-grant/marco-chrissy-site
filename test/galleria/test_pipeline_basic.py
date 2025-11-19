"""Basic unit tests for PipelineManager - just initialization."""

import pytest


class TestPipelineManagerBasic:
    """Basic tests for PipelineManager initialization."""

    def test_pipeline_manager_can_be_created(self):
        """Test PipelineManager can be instantiated."""
        from galleria.manager.pipeline import PipelineManager
        
        manager = PipelineManager()
        assert manager is not None

    def test_execute_single_stage_runs_plugin(self):
        """Test that execute_single_stage() executes one plugin stage."""
        from galleria.manager.pipeline import PipelineManager
        from galleria.plugins.registry import PluginRegistry
        from galleria.plugins.base import BasePlugin, PluginContext, PluginResult
        from pathlib import Path
        
        class MockPlugin(BasePlugin):
            @property
            def name(self):
                return "mock"
            
            @property  
            def version(self):
                return "1.0.0"
            
            def execute(self, context):
                return PluginResult(
                    success=True,
                    output_data={"processed": True},
                    metadata={"stage": "provider"}
                )
        
        # Setup registry with mock plugin
        registry = PluginRegistry()
        plugin = MockPlugin()
        registry.register(plugin, stage="provider")
        
        # Setup manager and context
        manager = PipelineManager(registry=registry)
        context = PluginContext(
            input_data={},
            config={},
            output_dir=Path("/tmp/test"),
            metadata={}
        )
        
        # This should execute the plugin
        result = manager.execute_single_stage("provider", "mock", context)
        
        assert result.success is True
        assert result.output_data["processed"] is True

    def test_execute_single_stage_handles_missing_plugin(self):
        """Test that execute_single_stage() handles missing plugins."""
        from galleria.manager.pipeline import PipelineManager
        from galleria.plugins.registry import PluginRegistry
        from galleria.plugins.base import PluginContext
        from pathlib import Path
        
        # Setup empty registry
        registry = PluginRegistry()
        manager = PipelineManager(registry=registry)
        
        context = PluginContext(
            input_data={},
            config={},
            output_dir=Path("/tmp/test"),
            metadata={}
        )
        
        # This should handle missing plugin gracefully
        result = manager.execute_single_stage("provider", "nonexistent", context)
        
        assert result.success is False
        assert "not found" in str(result.errors)