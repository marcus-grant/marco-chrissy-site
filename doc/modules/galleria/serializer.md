# Serializer Module

## Overview

The serializer module provides legacy support for photo collection loading, now superseded by the plugin system. Photo collections are loaded via the `NormPicProviderPlugin` which implements the standardized `ProviderPlugin` interface.

**Current Status**: The serializer API remains for backward compatibility, but new development should use the `NormPicProviderPlugin` directly through the plugin system.

## Architecture

**Location**: `galleria/serializer/`

**Main Components**:
- `models.py` - Photo and PhotoCollection data classes
- `loader.py` - Manifest loading and parsing
- `exceptions.py` - Custom exception classes

## Data Models

### Class: Photo

Represents a single photo with metadata.

**Attributes**:
- `source_path` (str): Path to original source image file
- `dest_path` (str): Destination path for organized photo
- `hash` (str): Photo content hash (for deduplication)
- `size_bytes` (int): File size in bytes
- `mtime` (float): Modification timestamp
- `camera` (str|None): Camera model information (optional)
- `gps` (dict|None): GPS coordinates {"lat": float, "lon": float} (optional)

**Example**:
```python
from galleria.serializer.models import Photo

photo = Photo(
    source_path="/photos/IMG_001.jpg",
    dest_path="/organized/wedding-001.jpg",
    hash="abc123",
    size_bytes=2048000,
    mtime=1699123456.789,
    camera="Canon EOS R5",
    gps={"lat": 40.7128, "lon": -74.0060}
)
```

### Class: PhotoCollection

Container for a collection of photos with metadata.

**Attributes**:
- `name` (str): Collection name
- `description` (str|None): Collection description (optional)
- `photos` (list[Photo]): List of Photo objects (defaults to empty list)

**Example**:
```python
from galleria.serializer.models import PhotoCollection, Photo

collection = PhotoCollection(
    name="wedding",
    description="John and Jane's wedding photos",
    photos=[photo1, photo2, photo3]
)
```

## Loader API

### Function: load_photo_collection(path)

Main entry point for loading photo collections from manifest files.

**Parameters**:
- `path` (str): Path to manifest file (NormPic JSON format)

**Returns**: PhotoCollection object

**Raises**:
- `ManifestNotFoundError`: If manifest file doesn't exist
- `ManifestValidationError`: If manifest is invalid or missing required fields

**Example**:
```python
from galleria.serializer.loader import load_photo_collection

collection = load_photo_collection("/path/to/manifest.json")
print(f"Loaded {len(collection.photos)} photos from {collection.name}")
```

## Error Handling

### ManifestNotFoundError

Raised when the manifest file cannot be found.

**Inheritance**: Exception → ManifestNotFoundError

**Usage**:
```python
try:
    collection = load_photo_collection("/missing/manifest.json")
except ManifestNotFoundError as e:
    print(f"Manifest not found: {e}")
```

### ManifestValidationError

Raised when manifest file is invalid or missing required fields.

**Inheritance**: Exception → ManifestValidationError

**Usage**:
```python
try:
    collection = load_photo_collection("/invalid/manifest.json")
except ManifestValidationError as e:
    print(f"Invalid manifest: {e}")
```

## NormPic Manifest Format

The serializer currently supports NormPic v0.1.0 manifest format.

**Required Fields**:
- `version`: "0.1.0"
- `collection_name`: String identifier for the collection
- `pics`: Array of photo objects

**Photo Object Fields** (in manifest):
- `source_path`: Original file path
- `dest_path`: Organized destination path
- `hash`: Content hash
- `size_bytes`: File size
- `mtime`: Modification time
- `camera`: Camera model (optional)
- `gps`: GPS coordinates object (optional)

**Example Manifest**:
```json
{
  "version": "0.1.0",
  "collection_name": "wedding",
  "generated_at": "2024-10-05T14:00:00Z",
  "pics": [
    {
      "source_path": "/photos/IMG_001.jpg",
      "dest_path": "/organized/wedding-001.jpg",
      "hash": "abc123",
      "size_bytes": 2048000,
      "mtime": 1699123456.789,
      "camera": "Canon EOS R5",
      "gps": {"lat": 40.7128, "lon": -74.0060}
    }
  ],
  "collection_description": "Wedding photos"
}
```

## Plugin System Integration

The serializer functionality has been migrated to the plugin system:

**New Plugin**: `NormPicProviderPlugin` (`galleria/plugins/providers/normpic.py`)
**Interface**: Implements `ProviderPlugin` from `galleria.plugins.interfaces`
**Migration**: Legacy `load_photo_collection()` function remains for backward compatibility

### Using the Plugin System

```python
from galleria.plugins.providers.normpic import NormPicProviderPlugin
from galleria.plugins import PluginContext

# Create plugin context
context = PluginContext(
    input_data={"manifest_path": "/path/to/manifest.json"},
    config={},
    output_dir=Path("/output")
)

# Load collection via plugin
plugin = NormPicProviderPlugin()
result = plugin.load_collection(context)

if result.success:
    photos = result.output_data["photos"]
    collection_name = result.output_data["collection_name"]
else:
    print(f"Error: {result.errors}")
```

### Plugin Output Format

The `NormPicProviderPlugin` follows the `ProviderPlugin` contract:

```python
{
    "photos": [
        {
            "source_path": "/photos/IMG_001.jpg",
            "dest_path": "wedding/IMG_001.jpg",
            "metadata": {
                "hash": "abc123",
                "size_bytes": 2048000,
                "mtime": 1699123456.789,
                "camera": "Canon EOS R5",
                "gps": {"lat": 40.7128, "lon": -74.0060}
            }
        }
    ],
    "collection_name": "wedding_photos",
    "collection_description": "Wedding photos",  # Optional
    "manifest_version": "0.1.0"                  # Optional
}
```

## Migration Notes

**For Existing Code**:
- Continue using `load_photo_collection()` for now
- Plan migration to plugin system for new features
- Plugin system provides better error handling and standardized interface

**For New Code**:
- Use `NormPicProviderPlugin` directly
- Follow `ProviderPlugin` interface contract
- Benefits from plugin system architecture (orchestration, pipelines, etc.)
