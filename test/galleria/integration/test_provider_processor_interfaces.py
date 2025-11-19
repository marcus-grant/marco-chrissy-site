"""Integration tests for Provider and Processor plugin interfaces."""

from pathlib import Path

from galleria.plugins import PluginContext, PluginResult


class TestProviderProcessorIntegration:
    """Integration tests for Provider ↔ Processor plugin interaction."""

    def test_provider_plugin_loads_photo_collection_for_processor(self, tmp_path):
        """Provider plugin should load photo collection data that Processor can use.

        This test defines the contract between Provider and Processor:
        - Provider outputs: {"photos": [...], "collection_name": str}
        - Processor expects: photos list with source_path and dest_path
        - Processor outputs: photos with added thumbnail_path
        """
        from galleria.plugins.interfaces import ProviderPlugin

        # Arrange: Create a concrete ProviderPlugin implementation
        class TestNormPicProvider(ProviderPlugin):
            @property
            def name(self) -> str:
                return "test-normpic-provider"

            @property
            def version(self) -> str:
                return "1.0.0"

            def load_collection(self, context: PluginContext) -> PluginResult:
                """Load photo collection from source."""
                # Mock NormPic manifest loading
                photos = [
                    {
                        "source_path": "/source/photos/IMG_001.jpg",
                        "dest_path": "wedding/IMG_001.jpg",
                        "metadata": {"camera": "Canon EOS R5"}
                    },
                    {
                        "source_path": "/source/photos/IMG_002.jpg",
                        "dest_path": "wedding/IMG_002.jpg",
                        "metadata": {"camera": "Canon EOS R5"}
                    }
                ]
                return PluginResult(
                    success=True,
                    output_data={
                        "photos": photos,
                        "collection_name": "wedding_photos",
                        "manifest_version": "0.1.0"
                    }
                )

        # Create provider and test it produces expected output
        provider = TestNormPicProvider()
        manifest_path = tmp_path / "manifest.json"

        context = PluginContext(
            input_data={"manifest_path": str(manifest_path)},
            config={"output_format": "webp"},
            output_dir=tmp_path / "output"
        )

        # Act: Execute provider
        result = provider.load_collection(context)

        # Assert: Provider output matches Processor expectations
        assert result.success
        assert "photos" in result.output_data
        assert "collection_name" in result.output_data
        assert len(result.output_data["photos"]) == 2

        # Verify photo data structure expected by Processor
        photo = result.output_data["photos"][0]
        assert "source_path" in photo
        assert "dest_path" in photo
        assert photo["source_path"] == "/source/photos/IMG_001.jpg"
        assert photo["dest_path"] == "wedding/IMG_001.jpg"

    def test_processor_plugin_generates_thumbnails_from_provider_data(self, tmp_path):
        """Processor plugin should generate thumbnails from Provider photo data.

        This test defines the Processor interface contract:
        - Accepts Provider output format
        - Generates thumbnails for each photo
        - Outputs photos with thumbnail_path added
        """
        from galleria.plugins.interfaces import ProcessorPlugin

        # Arrange: Create a concrete ProcessorPlugin implementation
        class TestThumbnailProcessor(ProcessorPlugin):
            @property
            def name(self) -> str:
                return "test-thumbnail-processor"

            @property
            def version(self) -> str:
                return "1.0.0"

            def process_thumbnails(self, context: PluginContext) -> PluginResult:
                """Generate thumbnails for photo collection."""
                photos = context.input_data["photos"]
                processed_photos = []

                for photo in photos:
                    # Mock thumbnail generation
                    thumb_name = Path(photo["dest_path"]).stem + "_thumb.webp"
                    thumb_path = f"thumbnails/{thumb_name}"

                    processed_photos.append({
                        **photo,
                        "thumbnail_path": thumb_path,
                        "thumbnail_size": (300, 200)
                    })

                return PluginResult(
                    success=True,
                    output_data={
                        "photos": processed_photos,
                        "collection_name": context.input_data["collection_name"],
                        "thumbnail_count": len(processed_photos)
                    }
                )

        # Create processor with Provider output data
        processor = TestThumbnailProcessor()

        # Mock Provider output as Processor input
        provider_output = {
            "photos": [
                {
                    "source_path": "/source/photos/IMG_001.jpg",
                    "dest_path": "wedding/IMG_001.jpg",
                    "metadata": {"camera": "Canon EOS R5"}
                },
                {
                    "source_path": "/source/photos/IMG_002.jpg",
                    "dest_path": "wedding/IMG_002.jpg",
                    "metadata": {"camera": "Canon EOS R5"}
                }
            ],
            "collection_name": "wedding_photos",
            "manifest_version": "0.1.0"
        }

        context = PluginContext(
            input_data=provider_output,
            config={"thumbnail_size": (300, 200), "format": "webp"},
            output_dir=tmp_path / "output"
        )

        # Act: Execute processor
        result = processor.process_thumbnails(context)

        # Assert: Processor output includes thumbnails
        assert result.success
        assert "photos" in result.output_data
        assert "thumbnail_count" in result.output_data
        assert result.output_data["thumbnail_count"] == 2

        # Verify thumbnail data added to each photo
        processed_photo = result.output_data["photos"][0]
        assert "thumbnail_path" in processed_photo
        assert "thumbnail_size" in processed_photo
        assert processed_photo["thumbnail_path"] == "thumbnails/IMG_001_thumb.webp"
        assert processed_photo["thumbnail_size"] == (300, 200)

        # Verify original photo data preserved
        assert processed_photo["source_path"] == "/source/photos/IMG_001.jpg"
        assert processed_photo["dest_path"] == "wedding/IMG_001.jpg"
        assert processed_photo["metadata"]["camera"] == "Canon EOS R5"

    def test_provider_to_processor_pipeline_integration(self, tmp_path):
        """Test complete Provider → Processor pipeline integration.

        This test verifies the data flow works end-to-end:
        1. Provider loads photo collection
        2. Processor receives Provider output as input
        3. Pipeline produces final output with thumbnails
        """
        from galleria.plugins.interfaces import ProcessorPlugin, ProviderPlugin

        # Use the same test implementations from above
        class TestNormPicProvider(ProviderPlugin):
            @property
            def name(self) -> str:
                return "test-normpic-provider"

            @property
            def version(self) -> str:
                return "1.0.0"

            def load_collection(self, context: PluginContext) -> PluginResult:
                photos = [
                    {
                        "source_path": "/source/photos/IMG_001.jpg",
                        "dest_path": "wedding/IMG_001.jpg",
                        "metadata": {"camera": "Canon EOS R5"}
                    }
                ]
                return PluginResult(
                    success=True,
                    output_data={
                        "photos": photos,
                        "collection_name": "wedding_photos"
                    }
                )

        class TestThumbnailProcessor(ProcessorPlugin):
            @property
            def name(self) -> str:
                return "test-thumbnail-processor"

            @property
            def version(self) -> str:
                return "1.0.0"

            def process_thumbnails(self, context: PluginContext) -> PluginResult:
                photos = context.input_data["photos"]
                processed_photos = []

                for photo in photos:
                    thumb_name = Path(photo["dest_path"]).stem + "_thumb.webp"
                    processed_photos.append({
                        **photo,
                        "thumbnail_path": f"thumbnails/{thumb_name}"
                    })

                return PluginResult(
                    success=True,
                    output_data={
                        "photos": processed_photos,
                        "collection_name": context.input_data["collection_name"]
                    }
                )

        # Arrange: Create output directory
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Act: Execute Provider → Processor pipeline
        provider = TestNormPicProvider()
        processor = TestThumbnailProcessor()

        # Stage 1: Provider
        provider_context = PluginContext(
            input_data={"manifest_path": str(tmp_path / "manifest.json")},
            config={},
            output_dir=output_dir
        )
        provider_result = provider.load_collection(provider_context)

        # Stage 2: Processor (uses Provider output as input)
        processor_context = PluginContext(
            input_data=provider_result.output_data,
            config={"thumbnail_size": (300, 200)},
            output_dir=output_dir
        )
        processor_result = processor.process_thumbnails(processor_context)

        # Assert: End-to-end pipeline success
        assert provider_result.success
        assert processor_result.success

        # Verify data flow through pipeline
        assert provider_result.output_data["collection_name"] == "wedding_photos"
        assert processor_result.output_data["collection_name"] == "wedding_photos"

        # Verify thumbnail generation
        final_photo = processor_result.output_data["photos"][0]
        assert final_photo["thumbnail_path"] == "thumbnails/IMG_001_thumb.webp"
        assert final_photo["source_path"] == "/source/photos/IMG_001.jpg"
