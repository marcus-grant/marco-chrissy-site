"""E2E tests for real plugin integration workflow."""

import json

from galleria.manager.pipeline import PipelineManager
from galleria.plugins.base import PluginContext
from galleria.plugins.css import BasicCSSPlugin
from galleria.plugins.pagination import BasicPaginationPlugin
from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin
from galleria.plugins.providers.normpic import NormPicProviderPlugin
from galleria.plugins.template import BasicTemplatePlugin


class TestRealPluginIntegration:
    """E2E tests for complete real plugin pipeline workflow."""

    def test_complete_real_plugin_workflow_normpic_to_css(self, tmp_path):
        """E2E: Complete real plugin workflow with actual implementations.

        Tests the five-stage pipeline with real plugins:
        NormPicProvider → ThumbnailProcessor → Pagination → Template → CSS

        This test should initially fail until all real plugin integrations
        are properly implemented and orchestrated via PipelineManager.
        """
        # Arrange: Create test NormPic manifest
        test_photos_dir = tmp_path / "photos"
        test_photos_dir.mkdir()

        # Create test photo files (empty files for testing)
        photo_paths = []
        for i in range(3):
            photo_path = test_photos_dir / f"photo_{i}.jpg"
            photo_path.write_bytes(b"\xff\xd8\xff\xe0")  # Minimal JPEG header
            photo_paths.append(str(photo_path))

        # Create NormPic manifest
        manifest = {
            "version": "0.1.0",
            "collection_name": "test_real_workflow",
            "pics": [
                {
                    "source_path": str(photo_paths[0]),
                    "dest_path": "photo_0.jpg",
                    "hash": "abc123",
                    "size_bytes": 1024,
                    "mtime": 1234567890,
                },
                {
                    "source_path": str(photo_paths[1]),
                    "dest_path": "photo_1.jpg",
                    "hash": "def456",
                    "size_bytes": 2048,
                    "mtime": 1234567891,
                },
                {
                    "source_path": str(photo_paths[2]),
                    "dest_path": "photo_2.jpg",
                    "hash": "ghi789",
                    "size_bytes": 3072,
                    "mtime": 1234567892,
                },
            ],
        }

        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest))

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create pipeline manager and register real plugins
        pipeline = PipelineManager()

        # Register all real plugins
        pipeline.registry.register(NormPicProviderPlugin(), "provider")
        pipeline.registry.register(ThumbnailProcessorPlugin(), "processor")
        pipeline.registry.register(BasicPaginationPlugin(), "transform")
        pipeline.registry.register(BasicTemplatePlugin(), "template")
        pipeline.registry.register(BasicCSSPlugin(), "css")

        # Define pipeline stages with plugin names
        stages = [
            ("provider", "normpic-provider"),
            ("processor", "thumbnail-processor"),
            ("transform", "basic-pagination"),
            ("template", "basic-template"),
            ("css", "basic-css"),
        ]

        # Create initial context
        initial_context = PluginContext(
            input_data={"manifest_path": str(manifest_path)},
            config={
                "provider": {},
                "processor": {"thumbnail_size": 200, "quality": 85},
                "transform": {"page_size": 2},
                "template": {"theme": "minimal", "layout": "grid"},
                "css": {"theme": "light", "responsive": True},
            },
            output_dir=output_dir,
        )

        # Act: Execute complete pipeline
        final_result = pipeline.execute_stages(stages, initial_context)

        # Assert: Verify complete pipeline execution
        assert final_result.success, f"Pipeline failed: {final_result.errors}"

        # Verify final output contains all expected components
        final_output = final_result.output_data
        assert final_output["collection_name"] == "test_real_workflow"

        # Verify CSS stage output (final stage)
        assert "css_files" in final_output
        assert "html_files" in final_output
        assert "css_count" in final_output

        # Verify CSS files were generated
        css_files = final_output["css_files"]
        assert len(css_files) >= 1  # At least gallery.css
        assert any(f["filename"] == "gallery.css" for f in css_files)

        # Verify HTML files were generated from pagination
        html_files = final_output["html_files"]
        assert len(html_files) == 3  # 3 photos / page_size=2 → 2 pages + 1 index.html redirect
        assert all("filename" in html_file for html_file in html_files)

        # Verify photos were processed through entire pipeline
        # Should have original data plus thumbnail paths and pagination structure
        assert final_output["collection_name"] == "test_real_workflow"

    def test_real_plugin_error_handling(self, tmp_path):
        """Test real plugin pipeline handles errors gracefully."""
        # Arrange: Create invalid manifest
        invalid_manifest = {
            "version": "0.1.0",
            "collection_name": "error_test",
            "pics": [
                {
                    "source_path": "/nonexistent/photo.jpg",  # Invalid path
                    "dest_path": "photo.jpg",
                    "hash": "invalid",
                    "size_bytes": 0,
                    "mtime": 0,
                }
            ],
        }

        manifest_path = tmp_path / "invalid_manifest.json"
        manifest_path.write_text(json.dumps(invalid_manifest))

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create pipeline with real plugins
        pipeline = PipelineManager()
        pipeline.registry.register(NormPicProviderPlugin(), "provider")
        pipeline.registry.register(ThumbnailProcessorPlugin(), "processor")

        stages = [
            ("provider", "normpic-provider"),
            ("processor", "thumbnail-processor"),  # This should fail on invalid photo
        ]

        initial_context = PluginContext(
            input_data={"manifest_path": str(manifest_path)},
            config={"provider": {}, "processor": {}},
            output_dir=output_dir,
        )

        # Act: Execute pipeline (should handle errors gracefully)
        result = pipeline.execute_stages(stages, initial_context)

        # Assert: Pipeline should succeed but log errors for individual photos
        # This is the correct behavior - graceful error handling rather than complete failure
        assert result.success  # Pipeline succeeds overall
        assert result.errors  # But individual photos have errors logged
        assert any(
            "error" in error.lower() or "fail" in error.lower()
            for error in result.errors
        )

        # Verify that the collection data is still present despite photo errors
        assert "collection_name" in result.output_data
        assert result.output_data["collection_name"] == "error_test"

    def test_complete_pipeline_with_high_page_size(self, tmp_path):
        """E2E: Pipeline should support page_size up to 500.

        Tests that pagination works correctly with page_size=384,
        which is needed for performance benchmarking different
        pagination configurations.
        """
        # Arrange: Create test NormPic manifest with many photos
        test_photos_dir = tmp_path / "photos"
        test_photos_dir.mkdir()

        # Create 400 test photo files to exceed page_size
        photo_paths = []
        manifest_pics = []
        for i in range(400):
            photo_path = test_photos_dir / f"photo_{i}.jpg"
            photo_path.write_bytes(b"\xff\xd8\xff\xe0")  # Minimal JPEG header
            photo_paths.append(str(photo_path))
            manifest_pics.append({
                "source_path": str(photo_path),
                "dest_path": f"photo_{i}.jpg",
                "hash": f"hash_{i:03d}",
                "size_bytes": 1024,
                "mtime": 1234567890 + i,
            })

        manifest = {
            "version": "0.1.0",
            "collection_name": "high_page_size_test",
            "pics": manifest_pics,
        }

        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest))

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create pipeline manager and register real plugins
        pipeline = PipelineManager()
        pipeline.registry.register(NormPicProviderPlugin(), "provider")
        pipeline.registry.register(ThumbnailProcessorPlugin(), "processor")
        pipeline.registry.register(BasicPaginationPlugin(), "transform")
        pipeline.registry.register(BasicTemplatePlugin(), "template")
        pipeline.registry.register(BasicCSSPlugin(), "css")

        stages = [
            ("provider", "normpic-provider"),
            ("processor", "thumbnail-processor"),
            ("transform", "basic-pagination"),
            ("template", "basic-template"),
            ("css", "basic-css"),
        ]

        # Create context with high page_size (384)
        initial_context = PluginContext(
            input_data={"manifest_path": str(manifest_path)},
            config={
                "provider": {},
                "processor": {"thumbnail_size": 200, "quality": 85},
                "transform": {"page_size": 384},
                "template": {"theme": "minimal", "layout": "grid"},
                "css": {"theme": "light", "responsive": True},
            },
            output_dir=output_dir,
        )

        # Act: Execute complete pipeline
        final_result = pipeline.execute_stages(stages, initial_context)

        # Assert: Verify pipeline succeeded with high page_size
        assert final_result.success, f"Pipeline failed: {final_result.errors}"

        # Verify pagination metadata reflects high page_size
        assert final_result.output_data["collection_name"] == "high_page_size_test"

        # 400 photos / 384 per page = 2 pages (page 1: 384, page 2: 16)
        html_files = final_result.output_data["html_files"]
        assert len(html_files) == 3  # 2 pages + 1 index.html redirect
