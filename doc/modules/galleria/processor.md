# Processor Module

## Overview

The processor module provides image processing and optimization for gallery generation, now implemented through the plugin system. Photo thumbnails are generated via the `ThumbnailProcessorPlugin` which implements the standardized `ProcessorPlugin` interface.

**Current Status**: The processor API remains for backward compatibility, but new development should use the `ThumbnailProcessorPlugin` directly through the plugin system.

## Architecture

**Location**: `galleria/processor/`

**Main Components**:
- `image.py` - ImageProcessor class and processing logic

## ImageProcessor API

### Class: ImageProcessor

Main class for processing images into thumbnails.

#### Methods

##### process_image(source_path, output_dir, size=400, quality=85, output_name=None)

Process a single image to generate a WebP thumbnail.

**Parameters**:
- `source_path` (Path|str): Path to source image file
- `output_dir` (Path|str): Directory to save thumbnail
- `size` (int): Thumbnail size in pixels (creates square thumbnail, default 400)
- `quality` (int): WebP quality setting 0-100 (default 85)
- `output_name` (str|None): Optional custom output name (defaults to source stem)

**Returns**: Path to generated thumbnail

**Raises**: `ImageProcessingError` if processing fails

**Example**:
```python
from galleria.processor.image import ImageProcessor

processor = ImageProcessor()
thumb_path = processor.process_image(
    "/photos/IMG_001.jpg",
    "/output/thumbnails",
    size=400,
    quality=85
)
```

##### process_collection(collection, output_dir, size=400, quality=85, progress_callback=None)

Process a photo collection to generate thumbnails.

**Parameters**:
- `collection` (PhotoCollection): Collection with photos to process
- `output_dir` (Path|str): Directory to save thumbnails
- `size` (int): Thumbnail size (default 400)
- `quality` (int): WebP quality setting (default 85)
- `progress_callback` (callable|None): Optional callback(current, total, photo_path)

**Returns**: List of result dictionaries with processing status

**Result Format**:
```python
# Success:
{"source_path": str, "thumbnail_path": str, "cached": bool}

# Error:
{"source_path": str, "error": str}
```

**Example**:
```python
def progress(current, total, path):
    print(f"Processing {current}/{total}: {path}")

results = processor.process_collection(
    collection,
    "/output/thumbnails",
    progress_callback=progress
)
```

##### should_process(source_path, thumbnail_path)

Check if image should be processed (naive caching).

**Parameters**:
- `source_path` (Path|str): Path to source image
- `thumbnail_path` (Path|str): Path to thumbnail

**Returns**: True if should process, False if cached thumbnail is valid

**Caching Strategy**: Compares file modification times. If thumbnail exists and is newer than source, returns False.

## Processing Pipeline

1. **Load Image**: Open with Pillow, handle format detection
2. **Color Conversion**: Convert to RGB if needed (handles RGBA, grayscale, etc.)
3. **Center Crop**: Crop to square using center crop strategy
4. **Resize**: Scale to target size using high-quality Lanczos resampling
5. **Save**: Output as WebP with quality setting

## Center Crop Strategy

For non-square images, the processor uses center cropping:

- **Landscape** (width > height): Crop left and right edges equally
- **Portrait** (height > width): Crop top and bottom edges equally
- **Square**: No cropping needed

This ensures the most important central content is preserved in thumbnails.

## Caching

**Strategy**: Naive file timestamp comparison

**Algorithm**:
1. Check if thumbnail file exists
2. If not, must process
3. Compare source mtime with thumbnail mtime
4. If source is newer, must reprocess
5. Otherwise, skip processing (cache hit)

**Cache Invalidation**: Delete thumbnail files or use 'clean' command (future implementation)

## Error Handling

**Exception**: `ImageProcessingError`

**Common Errors**:
- Source file not found
- Invalid/corrupted image data
- Insufficient permissions
- Disk space issues

**Behavior**: Process continues for other images in collection. Errors are returned in results list, not raised.

## Format Support

**Input Formats**: All Pillow-supported formats (JPEG, PNG, GIF, BMP, TIFF, WebP, etc.)

**Output Format**: WebP only (optimized for web delivery)

**Quality Settings**:
- 60-70: High compression, visible artifacts
- 75-85: Balanced (recommended, default 85)
- 90-100: Minimal compression, larger files

## Performance

**Memory Efficiency**: Processes one image at a time, suitable for large collections

**Progress Reporting**: Optional callback for UI integration

**Typical Performance**: ~50-100ms per image on modern hardware (varies by source size)

## Plugin System Integration

The processor functionality has been migrated to the plugin system:

**New Plugin**: `ThumbnailProcessorPlugin` (`galleria/plugins/processors/thumbnail.py`)
**Interface**: Implements `ProcessorPlugin` from `galleria.plugins.interfaces`
**Migration**: Legacy `ImageProcessor` class remains for backward compatibility

### Using the Plugin System

```python
from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin
from galleria.plugins import PluginContext
from pathlib import Path

# Create plugin context with ProviderPlugin output
context = PluginContext(
    input_data={
        "photos": [
            {
                "source_path": "/photos/IMG_001.jpg",
                "dest_path": "wedding/IMG_001.jpg",
                "metadata": {"camera": "Canon EOS R5"}
            }
        ],
        "collection_name": "wedding_photos"
    },
    config={
        "thumbnail_size": 400,
        "quality": 85,
        "use_cache": True
    },
    output_dir=Path("/output")
)

# Process thumbnails via plugin
plugin = ThumbnailProcessorPlugin()
result = plugin.process_thumbnails(context)

if result.success:
    photos = result.output_data["photos"]
    thumbnail_count = result.output_data["thumbnail_count"]
    
    for photo in photos:
        print(f"Thumbnail: {photo['thumbnail_path']}")
        print(f"Size: {photo['thumbnail_size']}")
else:
    print(f"Errors: {result.errors}")
```

### Plugin Output Format

The `ThumbnailProcessorPlugin` follows the `ProcessorPlugin` contract:

```python
{
    "photos": [
        {
            # All original ProviderPlugin data preserved
            "source_path": "/photos/IMG_001.jpg",
            "dest_path": "wedding/IMG_001.jpg", 
            "metadata": {"camera": "Canon EOS R5"},
            # New ProcessorPlugin data added
            "thumbnail_path": "/output/thumbnails/IMG_001.webp",
            "thumbnail_size": (400, 400),
            "cached": false
        }
    ],
    "collection_name": "wedding_photos",  # Preserved from input
    "thumbnail_count": 1,                 # Number of successful thumbnails
    # All other ProviderPlugin data preserved
}
```

### Plugin Features

- **Full ProviderPlugin Integration**: Seamlessly processes ProviderPlugin output
- **Advanced Configuration**: Thumbnail size, quality, caching, output format
- **Robust Error Handling**: Individual photo errors don't stop batch processing
- **Intelligent Caching**: Reuses existing thumbnails when source unchanged
- **Data Preservation**: All ProviderPlugin data flows through unchanged

## Migration Notes

**For Existing Code**:
- Continue using `ImageProcessor` class for now
- Plugin system provides better error handling and standardized interface
- Plugin integrates seamlessly with ProviderPlugin output

**For New Code**:
- Use `ThumbnailProcessorPlugin` directly
- Follow `ProcessorPlugin` interface contract
- Benefits from plugin system architecture (orchestration, pipelines, etc.)

## Legacy API (Deprecated)

The original `ImageProcessor` API remains available for backward compatibility but new development should use the plugin system.
