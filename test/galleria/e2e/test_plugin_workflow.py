"""E2E tests for complete plugin workflow."""

from pathlib import Path

from galleria.manager.hooks import PluginHookManager
from galleria.plugins import BasePlugin, PluginContext, PluginResult


class TestGalleriaPluginWorkflow:
    """E2E tests for complete plugin pipeline workflow."""

    def test_complete_plugin_workflow_provider_to_processor_to_transform_to_template_to_css(
        self, tmp_path
    ):
        """E2E: Complete plugin workflow with hook execution.

        Tests the five-stage pipeline with hooks:
        Provider → Processor → Transform → Template → CSS

        Each stage should:
        1. Execute before_<stage> hooks
        2. Run plugin logic
        3. Execute after_<stage> hooks
        4. Pass PluginResult to next stage as PluginContext
        """

        # Arrange: Create mock plugins for each stage
        class MockProviderPlugin(BasePlugin):
            @property
            def name(self) -> str:
                return "mock-provider"

            @property
            def version(self) -> str:
                return "1.0.0"

            def execute(self, context: PluginContext) -> PluginResult:
                # Mock loading photo collection
                photos = [
                    {"source_path": "/photos/1.jpg", "dest_path": "1.jpg"},
                    {"source_path": "/photos/2.jpg", "dest_path": "2.jpg"},
                ]
                return PluginResult(
                    success=True,
                    output_data={"photos": photos, "collection_name": "test"},
                )

        class MockProcessorPlugin(BasePlugin):
            @property
            def name(self) -> str:
                return "mock-processor"

            @property
            def version(self) -> str:
                return "1.0.0"

            def execute(self, context: PluginContext) -> PluginResult:
                # Mock thumbnail generation
                photos = context.input_data["photos"]
                processed_photos = []
                for photo in photos:
                    processed_photos.append(
                        {
                            **photo,
                            "thumbnail_path": f"thumbs/{Path(photo['dest_path']).stem}.webp",
                        }
                    )
                return PluginResult(
                    success=True,
                    output_data={
                        "photos": processed_photos,
                        "collection_name": context.input_data["collection_name"],
                    },
                )

        class MockTransformPlugin(BasePlugin):
            @property
            def name(self) -> str:
                return "mock-transform"

            @property
            def version(self) -> str:
                return "1.0.0"

            def execute(self, context: PluginContext) -> PluginResult:
                # Mock pagination transform
                photos = context.input_data["photos"]
                pages = [photos[:1], photos[1:]]  # Split into 2 pages
                return PluginResult(
                    success=True,
                    output_data={
                        "pages": pages,
                        "collection_name": context.input_data["collection_name"],
                    },
                )

        class MockTemplatePlugin(BasePlugin):
            @property
            def name(self) -> str:
                return "mock-template"

            @property
            def version(self) -> str:
                return "1.0.0"

            def execute(self, context: PluginContext) -> PluginResult:
                # Mock HTML generation
                pages = context.input_data["pages"]
                html_files = []
                for i, _page in enumerate(pages):
                    html_files.append(f"page_{i + 1}.html")
                return PluginResult(
                    success=True,
                    output_data={
                        "html_files": html_files,
                        "collection_name": context.input_data["collection_name"],
                    },
                )

        class MockCSSPlugin(BasePlugin):
            @property
            def name(self) -> str:
                return "mock-css"

            @property
            def version(self) -> str:
                return "1.0.0"

            def execute(self, context: PluginContext) -> PluginResult:
                # Mock CSS generation
                return PluginResult(
                    success=True,
                    output_data={
                        "css_files": ["gallery.css", "theme.css"],
                        "html_files": context.input_data["html_files"],
                        "collection_name": context.input_data["collection_name"],
                    },
                )

        # Setup hook manager and track hook execution
        hook_manager = PluginHookManager()
        hook_execution_log = []

        def track_hook(stage: str, timing: str):
            def hook_fn(context: PluginContext) -> PluginResult:
                hook_execution_log.append(f"{timing}_{stage}")
                return PluginResult(success=True, output_data=context.input_data)

            return hook_fn

        # Register hooks for each stage
        hook_manager.register_hook("before_provider", track_hook("provider", "before"))
        hook_manager.register_hook("after_provider", track_hook("provider", "after"))
        hook_manager.register_hook(
            "before_processor", track_hook("processor", "before")
        )
        hook_manager.register_hook("after_processor", track_hook("processor", "after"))
        hook_manager.register_hook(
            "before_transform", track_hook("transform", "before")
        )
        hook_manager.register_hook("after_transform", track_hook("transform", "after"))
        hook_manager.register_hook("before_template", track_hook("template", "before"))
        hook_manager.register_hook("after_template", track_hook("template", "after"))
        hook_manager.register_hook("before_css", track_hook("css", "before"))
        hook_manager.register_hook("after_css", track_hook("css", "after"))

        # Create plugins
        provider = MockProviderPlugin()
        processor = MockProcessorPlugin()
        transform = MockTransformPlugin()
        template = MockTemplatePlugin()
        css = MockCSSPlugin()

        # Setup initial context
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Act: Execute complete pipeline with hooks
        # Stage 1: Provider
        hook_manager.execute_hook(
            "before_provider",
            PluginContext(
                input_data={"manifest_path": "test.json"},
                config={},
                output_dir=output_dir,
            ),
        )

        provider_result = provider.execute(
            PluginContext(
                input_data={"manifest_path": "test.json"},
                config={},
                output_dir=output_dir,
            )
        )

        hook_manager.execute_hook(
            "after_provider",
            PluginContext(
                input_data=provider_result.output_data, config={}, output_dir=output_dir
            ),
        )

        # Stage 2: Processor
        hook_manager.execute_hook(
            "before_processor",
            PluginContext(
                input_data=provider_result.output_data, config={}, output_dir=output_dir
            ),
        )

        processor_result = processor.execute(
            PluginContext(
                input_data=provider_result.output_data, config={}, output_dir=output_dir
            )
        )

        hook_manager.execute_hook(
            "after_processor",
            PluginContext(
                input_data=processor_result.output_data,
                config={},
                output_dir=output_dir,
            ),
        )

        # Stage 3: Transform
        hook_manager.execute_hook(
            "before_transform",
            PluginContext(
                input_data=processor_result.output_data,
                config={},
                output_dir=output_dir,
            ),
        )

        transform_result = transform.execute(
            PluginContext(
                input_data=processor_result.output_data,
                config={},
                output_dir=output_dir,
            )
        )

        hook_manager.execute_hook(
            "after_transform",
            PluginContext(
                input_data=transform_result.output_data,
                config={},
                output_dir=output_dir,
            ),
        )

        # Stage 4: Template
        hook_manager.execute_hook(
            "before_template",
            PluginContext(
                input_data=transform_result.output_data,
                config={},
                output_dir=output_dir,
            ),
        )

        template_result = template.execute(
            PluginContext(
                input_data=transform_result.output_data,
                config={},
                output_dir=output_dir,
            )
        )

        hook_manager.execute_hook(
            "after_template",
            PluginContext(
                input_data=template_result.output_data, config={}, output_dir=output_dir
            ),
        )

        # Stage 5: CSS
        hook_manager.execute_hook(
            "before_css",
            PluginContext(
                input_data=template_result.output_data, config={}, output_dir=output_dir
            ),
        )

        css_result = css.execute(
            PluginContext(
                input_data=template_result.output_data, config={}, output_dir=output_dir
            )
        )

        hook_manager.execute_hook(
            "after_css",
            PluginContext(
                input_data=css_result.output_data, config={}, output_dir=output_dir
            ),
        )

        # Assert: Verify complete pipeline execution
        assert provider_result.success
        assert processor_result.success
        assert transform_result.success
        assert template_result.success
        assert css_result.success

        # Verify data flow through pipeline
        assert provider_result.output_data["photos"]
        assert processor_result.output_data["photos"][0]["thumbnail_path"]
        assert transform_result.output_data["pages"]
        assert template_result.output_data["html_files"]
        assert css_result.output_data["css_files"]

        # Verify hooks executed in correct order
        expected_hook_order = [
            "before_provider",
            "after_provider",
            "before_processor",
            "after_processor",
            "before_transform",
            "after_transform",
            "before_template",
            "after_template",
            "before_css",
            "after_css",
        ]
        assert hook_execution_log == expected_hook_order

        # Verify final output contains all expected components
        final_output = css_result.output_data
        assert final_output["collection_name"] == "test"
        assert len(final_output["html_files"]) == 2  # 2 pages from pagination
        assert len(final_output["css_files"]) == 2  # gallery.css + theme.css
