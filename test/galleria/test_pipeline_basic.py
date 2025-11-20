"""Basic unit tests for PipelineManager - just initialization."""



class TestPipelineManagerBasic:
    """Basic tests for PipelineManager initialization."""

    def test_pipeline_manager_can_be_created(self):
        """Test PipelineManager can be instantiated."""
        from galleria.manager.pipeline import PipelineManager

        manager = PipelineManager()
        assert manager is not None

    def test_execute_single_stage_runs_plugin(self):
        """Test that execute_single_stage() executes one plugin stage."""
        from pathlib import Path

        from galleria.manager.pipeline import PipelineManager
        from galleria.plugins.base import BasePlugin, PluginContext, PluginResult
        from galleria.plugins.registry import PluginRegistry

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
        from pathlib import Path

        from galleria.manager.pipeline import PipelineManager
        from galleria.plugins.base import PluginContext
        from galleria.plugins.registry import PluginRegistry

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

    def test_execute_stages_coordinates_pipeline(self):
        """Test that execute_stages() coordinates multi-stage pipeline."""
        from pathlib import Path

        from galleria.manager.pipeline import PipelineManager
        from galleria.plugins.base import BasePlugin, PluginContext, PluginResult
        from galleria.plugins.registry import PluginRegistry

        class ProviderPlugin(BasePlugin):
            @property
            def name(self):
                return "provider"

            @property
            def version(self):
                return "1.0.0"

            def execute(self, context):
                return PluginResult(
                    success=True,
                    output_data={"photos": ["photo1.jpg", "photo2.jpg"]},
                    metadata={"stage": "provider"}
                )

        class ProcessorPlugin(BasePlugin):
            @property
            def name(self):
                return "processor"

            @property
            def version(self):
                return "1.0.0"

            def execute(self, context):
                photos = context.input_data.get("photos", [])
                return PluginResult(
                    success=True,
                    output_data={"thumbnails": [f"{p}.webp" for p in photos]},
                    metadata={"stage": "processor"}
                )

        # Setup registry with plugins
        registry = PluginRegistry()
        provider = ProviderPlugin()
        processor = ProcessorPlugin()
        registry.register(provider, stage="provider")
        registry.register(processor, stage="processor")

        # Setup manager and stages
        manager = PipelineManager(registry=registry)
        stages = [
            {"stage": "provider", "plugin": "provider"},
            {"stage": "processor", "plugin": "processor"}
        ]

        initial_context = PluginContext(
            input_data={},
            config={},
            output_dir=Path("/tmp/test"),
            metadata={}
        )

        # This should execute Provider → Processor pipeline
        final_result = manager.execute_stages(stages, initial_context)

        assert final_result.success is True
        assert "thumbnails" in final_result.output_data
        assert len(final_result.output_data["thumbnails"]) == 2

    def test_execute_stages_handles_stage_failure(self):
        """Test that execute_stages() handles stage failures."""
        from pathlib import Path

        from galleria.manager.pipeline import PipelineManager
        from galleria.plugins.base import BasePlugin, PluginContext, PluginResult
        from galleria.plugins.registry import PluginRegistry

        class FailingPlugin(BasePlugin):
            @property
            def name(self):
                return "failing"

            @property
            def version(self):
                return "1.0.0"

            def execute(self, context):
                return PluginResult(
                    success=False,
                    output_data={},
                    errors=["Simulated failure"]
                )

        # Setup registry
        registry = PluginRegistry()
        plugin = FailingPlugin()
        registry.register(plugin, stage="provider")

        manager = PipelineManager(registry=registry)
        stages = [{"stage": "provider", "plugin": "failing"}]

        initial_context = PluginContext(
            input_data={},
            config={},
            output_dir=Path("/tmp/test"),
            metadata={}
        )

        # This should handle failure gracefully
        result = manager.execute_stages(stages, initial_context)

        assert result.success is False
        assert "Simulated failure" in str(result.errors)

    def test_execute_workflow_provides_high_level_api(self):
        """Test that execute_workflow() provides convenient high-level API."""
        from pathlib import Path

        from galleria.manager.pipeline import PipelineManager
        from galleria.plugins.base import BasePlugin, PluginResult
        from galleria.plugins.registry import PluginRegistry

        class MockProviderPlugin(BasePlugin):
            @property
            def name(self):
                return "normpic-provider"

            @property
            def version(self):
                return "1.0.0"

            def execute(self, context):
                return PluginResult(
                    success=True,
                    output_data={"collection_name": "test", "photos": [{"filename": "test.jpg"}]},
                    metadata={"stage": "provider"}
                )

        class MockProcessorPlugin(BasePlugin):
            @property
            def name(self):
                return "thumbnail-processor"

            @property
            def version(self):
                return "1.0.0"

            def execute(self, context):
                photos = context.input_data.get("photos", [])
                return PluginResult(
                    success=True,
                    output_data={"collection_name": context.input_data["collection_name"], "photos": photos},
                    metadata={"stage": "processor"}
                )

        # Setup registry with plugins
        registry = PluginRegistry()
        provider = MockProviderPlugin()
        processor = MockProcessorPlugin()
        registry.register(provider, stage="provider")
        registry.register(processor, stage="processor")

        # Setup manager
        manager = PipelineManager(registry=registry)

        # This should execute complete manifest-to-thumbnails workflow
        result = manager.execute_workflow("manifest-to-thumbnails",
                                        manifest_path=Path("/tmp/manifest.json"),
                                        output_dir=Path("/tmp/output"))

        assert result.success is True
        assert "collection_name" in result.output_data
        assert result.output_data["collection_name"] == "test"

    def test_execute_workflow_handles_unknown_workflow(self):
        """Test that execute_workflow() handles unknown workflow types."""
        from pathlib import Path

        from galleria.manager.pipeline import PipelineManager
        from galleria.plugins.registry import PluginRegistry

        registry = PluginRegistry()
        manager = PipelineManager(registry=registry)

        # This should handle unknown workflow gracefully
        result = manager.execute_workflow("unknown-workflow",
                                        manifest_path=Path("/tmp/test.json"),
                                        output_dir=Path("/tmp/output"))

        assert result.success is False
        assert "Unknown workflow" in str(result.errors)
