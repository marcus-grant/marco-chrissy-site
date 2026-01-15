"""Thumbnail processor plugin for generating optimized WebP thumbnails from photo collections."""

import copy
from pathlib import Path

from galleria.plugins.base import PluginContext, PluginResult
from galleria.plugins.interfaces import ProcessorPlugin
from galleria.processor.image import ImageProcessingError, ImageProcessor


def _process_single_photo(
    photo: dict,
    thumbnails_dir: Path,
    thumbnail_size: int,
    quality: int,
    output_format: str,
    use_cache: bool,
) -> dict:
    """Process a single photo to generate a thumbnail.

    This is a standalone function (not a method) to enable pickling
    for ProcessPoolExecutor parallel processing.

    Args:
        photo: Photo dict with source_path, dest_path, metadata
        thumbnails_dir: Directory to write thumbnails to
        thumbnail_size: Target thumbnail size in pixels
        quality: WebP quality (0-100)
        output_format: Output format (e.g., "webp")
        use_cache: Whether to use cached thumbnails

    Returns:
        Dict with processed photo data including:
            - All original photo fields
            - thumbnail_path: Path to generated thumbnail
            - thumbnail_size: Tuple of (width, height)
            - cached: Whether thumbnail was from cache
            - error: Error message if processing failed (optional)
    """
    # Create image processor instance
    processor = ImageProcessor()

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
            if not processor.should_process(source_path, thumbnail_path):
                # Use cached thumbnail
                processed_photo["thumbnail_path"] = str(thumbnail_path)
                processed_photo["thumbnail_size"] = (thumbnail_size, thumbnail_size)
                processed_photo["cached"] = True
                return processed_photo

        # Process thumbnail
        try:
            result_path = processor.process_image(
                source_path=source_path,
                output_dir=thumbnails_dir,
                size=thumbnail_size,
                quality=quality,
                output_name=thumbnail_name,
            )

            # Add processor data to photo
            processed_photo["thumbnail_path"] = str(result_path)
            processed_photo["thumbnail_size"] = (thumbnail_size, thumbnail_size)
            processed_photo["cached"] = False

        except ImageProcessingError as e:
            # Individual photo processing failed
            processed_photo["error"] = f"Failed to process {source_path}: {e}"

        except Exception as e:
            # Unexpected error
            processed_photo["error"] = f"Unexpected error processing {source_path}: {e}"

        return processed_photo

    except Exception as e:
        # Error processing individual photo metadata
        error_photo = copy.deepcopy(photo)
        error_photo["error"] = f"Error processing photo metadata: {e}"
        return error_photo


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
                    errors=["Input data must be a dictionary"],
                )

            if "photos" not in context.input_data:
                return PluginResult(
                    success=False,
                    output_data=None,
                    errors=["Missing required field: photos"],
                )

            if "collection_name" not in context.input_data:
                return PluginResult(
                    success=False,
                    output_data=None,
                    errors=["Missing required field: collection_name"],
                )

            # Extract configuration options - support both nested and direct config patterns
            config = context.config or {}

            # Try nested config first (for multi-stage pipelines), fall back to direct access
            if "processor" in config:
                processor_config = config["processor"]
            else:
                processor_config = config

            thumbnail_size = processor_config.get("thumbnail_size", 400)
            quality = processor_config.get("quality", 85)
            use_cache = processor_config.get("use_cache", True)
            output_format = processor_config.get("output_format", "webp")

            # Parallel processing options (used in parallel path below)
            parallel = processor_config.get("parallel", False)
            max_workers = processor_config.get("max_workers", None)
            _ = (parallel, max_workers)  # Mark as intentionally unused until Commit 6

            # Create thumbnails directory
            thumbnails_dir = context.output_dir / "thumbnails"
            thumbnails_dir.mkdir(parents=True, exist_ok=True)

            # Process photos
            processed_photos = []
            thumbnail_count = 0
            processing_errors = []

            for photo in context.input_data["photos"]:
                # Process single photo using extracted function
                processed_photo = _process_single_photo(
                    photo=photo,
                    thumbnails_dir=thumbnails_dir,
                    thumbnail_size=thumbnail_size,
                    quality=quality,
                    output_format=output_format,
                    use_cache=use_cache,
                )

                # Track results
                if "error" in processed_photo:
                    processing_errors.append(processed_photo["error"])
                else:
                    thumbnail_count += 1

                processed_photos.append(processed_photo)

            # Build output data - preserve all input data and add processor results
            output_data = copy.deepcopy(context.input_data)
            output_data["photos"] = processed_photos
            output_data["thumbnail_count"] = thumbnail_count

            # Return result with any processing errors as context
            return PluginResult(
                success=True,
                output_data=output_data,
                errors=processing_errors,  # Non-fatal errors for individual photos
            )

        except Exception as e:
            # Fatal error that prevents any processing
            return PluginResult(
                success=False,
                output_data=None,
                errors=[f"Fatal error in thumbnail processing: {e}"],
            )
