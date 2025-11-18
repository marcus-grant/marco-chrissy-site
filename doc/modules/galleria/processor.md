# Processor Module

## Overview

The processor module handles image processing and optimization for gallery generation. It converts source images into optimized WebP thumbnails with intelligent caching.

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

## Future Enhancements

- Plugin support for custom image filters
- Additional output formats (AVIF, etc.)
- Metadata extraction and embedding
- Parallel processing for large collections
- Smart cropping using focal point detection
