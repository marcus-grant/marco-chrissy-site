# Serializer Module

## Overview

The serializer module provides a photo collection provider system that loads photo metadata from various sources (primarily NormPic manifests) and converts it into standardized data structures for gallery generation.

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

## Plugin Architecture

The serializer is designed with plugin extensibility in mind:

**Current**: NormPic manifest provider
**Future**: Directory scanner, database, API providers

**Design Principles**:
- Clean separation between data models and source providers
- Provider-agnostic data structures
- Extensible plugin system for new collection sources

## Future Enhancements

- PhotoCollectionProvider plugin interface
- Directory scanner provider (auto-discover photos)
- Database provider (load from SQLite/PostgreSQL)
- API provider (fetch from remote sources)
- Support for additional manifest formats
- Metadata caching and validation
