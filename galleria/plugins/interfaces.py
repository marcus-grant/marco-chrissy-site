"""Plugin interface definitions for Galleria plugin system.

This module defines the specific plugin interfaces for each stage of the pipeline:
- ProviderPlugin: Load photo collections from various sources
- ProcessorPlugin: Generate thumbnails and process images
- TransformPlugin: Manipulate photo collection data (pagination, sorting, filtering)
- TemplatePlugin: Generate HTML structure
- CSSPlugin: Generate stylesheets

Each interface inherits from BasePlugin and adds stage-specific abstract methods.
"""

from abc import abstractmethod

from .base import BasePlugin, PluginContext, PluginResult


class ProviderPlugin(BasePlugin):
    """Base class for provider plugins that load photo collections.

    Provider plugins are responsible for loading photo collection data from
    various sources like NormPic manifests, filesystem directories, or databases.

    Expected output format:
    {
        "photos": [
            {
                "source_path": str,  # Path to original photo file
                "dest_path": str,    # Relative destination path
                "metadata": dict     # Optional metadata (EXIF, etc.)
            },
            ...
        ],
        "collection_name": str,      # Name of the photo collection
        "manifest_version": str      # Version info (optional)
    }
    """

    @abstractmethod
    def load_collection(self, context: PluginContext) -> PluginResult:
        """Load photo collection from source.

        Args:
            context: Plugin execution context containing:
                - input_data: Source-specific data (manifest_path, directory, etc.)
                - config: Provider configuration options
                - output_dir: Target output directory

        Returns:
            PluginResult with photo collection data

        Raises:
            PluginValidationError: Invalid context or configuration
            PluginExecutionError: Failed to load collection
            PluginDependencyError: Missing required dependencies
        """
        pass

    def execute(self, context: PluginContext) -> PluginResult:
        """Execute the provider plugin by loading the collection.

        This method implements the BasePlugin execute interface by delegating
        to the load_collection method specific to provider plugins.
        """
        return self.load_collection(context)


class ProcessorPlugin(BasePlugin):
    """Base class for processor plugins that generate thumbnails and process images.

    Processor plugins take photo collection data from providers and generate
    thumbnails, apply transformations, or extract metadata.

    Expected input format (from ProviderPlugin):
    {
        "photos": [...],         # Photo collection from provider
        "collection_name": str,
        ...                      # Other provider data
    }

    Expected output format:
    {
        "photos": [
            {
                # All original photo data from provider
                "thumbnail_path": str,    # Path to generated thumbnail
                "thumbnail_size": tuple,  # (width, height) of thumbnail
                # Other processing results...
            },
            ...
        ],
        "collection_name": str,
        "thumbnail_count": int,       # Number of thumbnails generated
        ...                           # Other processing metadata
    }
    """

    @abstractmethod
    def process_thumbnails(self, context: PluginContext) -> PluginResult:
        """Generate thumbnails and process images from photo collection.

        Args:
            context: Plugin execution context containing:
                - input_data: Photo collection data from provider
                - config: Processor configuration (sizes, formats, etc.)
                - output_dir: Target output directory

        Returns:
            PluginResult with processed photo data including thumbnails

        Raises:
            PluginValidationError: Invalid input data or configuration
            PluginExecutionError: Failed to process images or generate thumbnails
            PluginDependencyError: Missing image processing dependencies
        """
        pass

    def execute(self, context: PluginContext) -> PluginResult:
        """Execute the processor plugin by processing thumbnails.

        This method implements the BasePlugin execute interface by delegating
        to the process_thumbnails method specific to processor plugins.
        """
        return self.process_thumbnails(context)
