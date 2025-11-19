"""Thumbnail processor plugin for generating optimized WebP thumbnails from photo collections."""

import copy
from pathlib import Path

from galleria.plugins.base import PluginContext, PluginResult
from galleria.plugins.interfaces import ProcessorPlugin
from galleria.processor.image import ImageProcessingError, ImageProcessor


class ThumbnailProcessorPlugin(ProcessorPlugin):
    """Processor plugin for generating thumbnails from photo collections.

    Converts existing galleria.processor.image functionality to ProcessorPlugin
    contract format. Takes ProviderPlugin output and generates WebP thumbnails
    with proper caching and error handling.
    """

    @property
    def name(self) -> str:
        """Plugin name identifier."""
        return "thumbnail-processor"

    @property
    def version(self) -> str:
        """Plugin version."""
        return "1.0.0"

    def process_thumbnails(self, context: PluginContext) -> PluginResult:
        """Generate thumbnails for photo collection from provider data.

        Args:
            context: Plugin execution context containing:
                - input_data: ProviderPlugin output with photos array
                - config: Processor configuration (thumbnail_size, quality, etc.)
                - output_dir: Target output directory

        Returns:
            PluginResult with success/failure and processed photo data

        Expected input format (ProviderPlugin output):
        {
            "photos": [
                {
                    "source_path": str,
                    "dest_path": str,
                    "metadata": {...}
                },
                ...
            ],
            "collection_name": str,
            ...
        }

        Expected output format (ProcessorPlugin contract):
        {
            "photos": [
                {
                    # All original photo data from provider
                    "source_path": str,
                    "dest_path": str,
                    "metadata": {...},
                    # New processor data
                    "thumbnail_path": str,
                    "thumbnail_size": tuple,
                    "cached": bool  # Optional, indicates if thumbnail was cached
                },
                ...
            ],
            "collection_name": str,  # Preserved from input
            "thumbnail_count": int,  # Number of successful thumbnails
            # All other provider data preserved
        }
        """
        try:
            # Validate input data
            if not isinstance(context.input_data, dict):
                return PluginResult(
                    success=False,
                    output_data=None,
                    errors=["Input data must be a dictionary"]
                )

            if "photos" not in context.input_data:
                return PluginResult(
                    success=False,
                    output_data=None,
                    errors=["Missing required field: photos"]
                )

            if "collection_name" not in context.input_data:
                return PluginResult(
                    success=False,
                    output_data=None,
                    errors=["Missing required field: collection_name"]
                )

            # Extract configuration options
            config = context.config or {}
            thumbnail_size = config.get("thumbnail_size", 400)
            quality = config.get("quality", 85)
            use_cache = config.get("use_cache", True)
            output_format = config.get("output_format", "webp")

            # Create thumbnails directory
            thumbnails_dir = context.output_dir / "thumbnails"
            thumbnails_dir.mkdir(parents=True, exist_ok=True)

            # Process photos
            processed_photos = []
            thumbnail_count = 0
            processing_errors = []

            # Create image processor instance
            processor = ImageProcessor()

            for photo in context.input_data["photos"]:
                try:
                    # Copy original photo data to preserve it
                    processed_photo = copy.deepcopy(photo)

                    # Extract paths
                    source_path = Path(photo["source_path"])
                    dest_path_obj = Path(photo["dest_path"])
                    thumbnail_name = dest_path_obj.stem + f".{output_format}"
                    thumbnail_path = thumbnails_dir / thumbnail_name

                    # Check caching if enabled
                    if use_cache and thumbnail_path.exists():
                        if processor.should_process(source_path, thumbnail_path):
                            # Source is newer, need to reprocess
                            pass
                        else:
                            # Use cached thumbnail
                            processed_photo["thumbnail_path"] = str(thumbnail_path)
                            processed_photo["thumbnail_size"] = (thumbnail_size, thumbnail_size)
                            processed_photo["cached"] = True
                            thumbnail_count += 1
                            processed_photos.append(processed_photo)
                            continue

                    # Process thumbnail
                    try:
                        result_path = processor.process_image(
                            source_path=source_path,
                            output_dir=thumbnails_dir,
                            size=thumbnail_size,
                            quality=quality,
                            output_name=thumbnail_name
                        )

                        # Add processor data to photo
                        processed_photo["thumbnail_path"] = str(result_path)
                        processed_photo["thumbnail_size"] = (thumbnail_size, thumbnail_size)
                        processed_photo["cached"] = False
                        thumbnail_count += 1

                    except ImageProcessingError as e:
                        # Individual photo processing failed
                        processed_photo["error"] = str(e)
                        processing_errors.append(f"Failed to process {source_path}: {e}")

                    except Exception as e:
                        # Unexpected error
                        processed_photo["error"] = f"Unexpected error: {e}"
                        processing_errors.append(f"Unexpected error processing {source_path}: {e}")

                    processed_photos.append(processed_photo)

                except Exception as e:
                    # Error processing individual photo metadata
                    error_msg = f"Error processing photo metadata: {e}"
                    processing_errors.append(error_msg)
                    # Still add photo with error info
                    error_photo = copy.deepcopy(photo)
                    error_photo["error"] = error_msg
                    processed_photos.append(error_photo)

            # Build output data - preserve all input data and add processor results
            output_data = copy.deepcopy(context.input_data)
            output_data["photos"] = processed_photos
            output_data["thumbnail_count"] = thumbnail_count

            # Return result with any processing errors as context
            return PluginResult(
                success=True,
                output_data=output_data,
                errors=processing_errors  # Non-fatal errors for individual photos
            )

        except Exception as e:
            # Fatal error that prevents any processing
            return PluginResult(
                success=False,
                output_data=None,
                errors=[f"Fatal error in thumbnail processing: {e}"]
            )
