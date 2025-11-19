"""Unit tests for plugin interface definitions."""

from abc import ABC

import pytest

from galleria.plugins import PluginContext, PluginResult
from galleria.plugins.interfaces import ProcessorPlugin, ProviderPlugin


class TestProviderPluginInterface:
    """Unit tests for ProviderPlugin interface contract."""

    def test_provider_plugin_is_abstract_base_class(self):
        """ProviderPlugin should be an abstract base class."""
        # Cannot instantiate abstract class directly
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            ProviderPlugin()

    def test_provider_plugin_inherits_from_base_plugin(self):
        """ProviderPlugin should inherit from BasePlugin."""
        from galleria.plugins import BasePlugin

        assert issubclass(ProviderPlugin, BasePlugin)
        assert issubclass(ProviderPlugin, ABC)

    def test_provider_plugin_requires_load_collection_implementation(self):
        """ProviderPlugin subclasses must implement load_collection method."""

        # Incomplete implementation should fail
        class IncompleteProvider(ProviderPlugin):
            @property
            def name(self) -> str:
                return "incomplete"

            @property
            def version(self) -> str:
                return "1.0.0"

            # Missing load_collection implementation

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteProvider()

    def test_provider_plugin_execute_delegates_to_load_collection(self, tmp_path):
        """ProviderPlugin.execute should delegate to load_collection method."""

        class TestProvider(ProviderPlugin):
            def __init__(self):
                self.load_collection_called = False

            @property
            def name(self) -> str:
                return "test-provider"

            @property
            def version(self) -> str:
                return "1.0.0"

            def load_collection(self, context: PluginContext) -> PluginResult:
                self.load_collection_called = True
                return PluginResult(
                    success=True,
                    output_data={"photos": [], "collection_name": "test"}
                )

        provider = TestProvider()
        context = PluginContext(
            input_data={"manifest_path": "test.json"},
            config={},
            output_dir=tmp_path
        )

        # execute should call load_collection
        result = provider.execute(context)

        assert provider.load_collection_called
        assert result.success
        assert result.output_data["collection_name"] == "test"

    def test_provider_plugin_contract_validation(self, tmp_path):
        """Test that ProviderPlugin contract is properly defined."""

        class ValidProvider(ProviderPlugin):
            @property
            def name(self) -> str:
                return "valid-provider"

            @property
            def version(self) -> str:
                return "1.0.0"

            def load_collection(self, context: PluginContext) -> PluginResult:
                # Validate expected input format
                assert "manifest_path" in context.input_data or "source_dir" in context.input_data

                # Return expected output format
                return PluginResult(
                    success=True,
                    output_data={
                        "photos": [
                            {
                                "source_path": "/source/test.jpg",
                                "dest_path": "test.jpg",
                                "metadata": {}
                            }
                        ],
                        "collection_name": "test_collection"
                    }
                )

        provider = ValidProvider()
        context = PluginContext(
            input_data={"manifest_path": "test.json"},
            config={},
            output_dir=tmp_path
        )

        result = provider.load_collection(context)

        # Verify output contract
        assert result.success
        assert "photos" in result.output_data
        assert "collection_name" in result.output_data
        assert isinstance(result.output_data["photos"], list)
        assert isinstance(result.output_data["collection_name"], str)


class TestProcessorPluginInterface:
    """Unit tests for ProcessorPlugin interface contract."""

    def test_processor_plugin_is_abstract_base_class(self):
        """ProcessorPlugin should be an abstract base class."""
        # Cannot instantiate abstract class directly
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            ProcessorPlugin()

    def test_processor_plugin_inherits_from_base_plugin(self):
        """ProcessorPlugin should inherit from BasePlugin."""
        from galleria.plugins import BasePlugin

        assert issubclass(ProcessorPlugin, BasePlugin)
        assert issubclass(ProcessorPlugin, ABC)

    def test_processor_plugin_requires_process_thumbnails_implementation(self):
        """ProcessorPlugin subclasses must implement process_thumbnails method."""

        class IncompleteProcessor(ProcessorPlugin):
            @property
            def name(self) -> str:
                return "incomplete"

            @property
            def version(self) -> str:
                return "1.0.0"

            # Missing process_thumbnails implementation

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteProcessor()

    def test_processor_plugin_execute_delegates_to_process_thumbnails(self, tmp_path):
        """ProcessorPlugin.execute should delegate to process_thumbnails method."""

        class TestProcessor(ProcessorPlugin):
            def __init__(self):
                self.process_thumbnails_called = False

            @property
            def name(self) -> str:
                return "test-processor"

            @property
            def version(self) -> str:
                return "1.0.0"

            def process_thumbnails(self, context: PluginContext) -> PluginResult:
                self.process_thumbnails_called = True
                photos = context.input_data.get("photos", [])
                return PluginResult(
                    success=True,
                    output_data={
                        "photos": photos,
                        "collection_name": context.input_data.get("collection_name", "test"),
                        "thumbnail_count": len(photos)
                    }
                )

        processor = TestProcessor()
        context = PluginContext(
            input_data={
                "photos": [{"source_path": "test.jpg", "dest_path": "test.jpg"}],
                "collection_name": "test"
            },
            config={},
            output_dir=tmp_path
        )

        # execute should call process_thumbnails
        result = processor.execute(context)

        assert processor.process_thumbnails_called
        assert result.success
        assert result.output_data["thumbnail_count"] == 1

    def test_processor_plugin_contract_validation(self, tmp_path):
        """Test that ProcessorPlugin contract is properly defined."""

        class ValidProcessor(ProcessorPlugin):
            @property
            def name(self) -> str:
                return "valid-processor"

            @property
            def version(self) -> str:
                return "1.0.0"

            def process_thumbnails(self, context: PluginContext) -> PluginResult:
                # Validate expected input format (from ProviderPlugin)
                assert "photos" in context.input_data
                assert "collection_name" in context.input_data

                photos = context.input_data["photos"]
                processed_photos = []

                for photo in photos:
                    # Validate provider photo format
                    assert "source_path" in photo
                    assert "dest_path" in photo

                    # Add processor data
                    processed_photos.append({
                        **photo,
                        "thumbnail_path": f"thumbs/{photo['dest_path']}.webp",
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

        processor = ValidProcessor()
        context = PluginContext(
            input_data={
                "photos": [
                    {
                        "source_path": "/source/test.jpg",
                        "dest_path": "test.jpg",
                        "metadata": {}
                    }
                ],
                "collection_name": "test_collection"
            },
            config={},
            output_dir=tmp_path
        )

        result = processor.process_thumbnails(context)

        # Verify output contract
        assert result.success
        assert "photos" in result.output_data
        assert "collection_name" in result.output_data
        assert "thumbnail_count" in result.output_data

        # Verify thumbnail data added
        processed_photo = result.output_data["photos"][0]
        assert "thumbnail_path" in processed_photo
        assert "thumbnail_size" in processed_photo
        assert processed_photo["thumbnail_path"] == "thumbs/test.jpg.webp"
        assert processed_photo["thumbnail_size"] == (300, 200)


class TestInterfaceIntegration:
    """Unit tests for interface integration and validation."""

    def test_provider_output_matches_processor_input_contract(self, tmp_path):
        """Provider output format should match Processor input expectations."""

        class TestProvider(ProviderPlugin):
            @property
            def name(self) -> str:
                return "contract-provider"

            @property
            def version(self) -> str:
                return "1.0.0"

            def load_collection(self, context: PluginContext) -> PluginResult:
                return PluginResult(
                    success=True,
                    output_data={
                        "photos": [
                            {
                                "source_path": "/source/img1.jpg",
                                "dest_path": "gallery/img1.jpg",
                                "metadata": {"size": 1024}
                            }
                        ],
                        "collection_name": "contract_test"
                    }
                )

        class TestProcessor(ProcessorPlugin):
            @property
            def name(self) -> str:
                return "contract-processor"

            @property
            def version(self) -> str:
                return "1.0.0"

            def process_thumbnails(self, context: PluginContext) -> PluginResult:
                # Should be able to process Provider output without modification
                photos = context.input_data["photos"]
                collection_name = context.input_data["collection_name"]

                processed = [{**p, "thumbnail_path": f"thumbs/{p['dest_path']}.webp"} for p in photos]

                return PluginResult(
                    success=True,
                    output_data={
                        "photos": processed,
                        "collection_name": collection_name,
                        "thumbnail_count": len(processed)
                    }
                )

        # Test that Provider → Processor contract works
        provider = TestProvider()
        processor = TestProcessor()

        # Provider stage
        provider_context = PluginContext(
            input_data={"manifest_path": "test.json"},
            config={},
            output_dir=tmp_path
        )
        provider_result = provider.load_collection(provider_context)

        # Processor stage (using Provider output)
        processor_context = PluginContext(
            input_data=provider_result.output_data,
            config={},
            output_dir=tmp_path
        )
        processor_result = processor.process_thumbnails(processor_context)

        # Verify seamless data flow
        assert provider_result.success
        assert processor_result.success
        assert processor_result.output_data["collection_name"] == "contract_test"
        assert processor_result.output_data["thumbnail_count"] == 1
        assert "thumbs/gallery/img1.jpg.webp" in processor_result.output_data["photos"][0]["thumbnail_path"]
