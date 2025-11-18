# Galleria Provider Architecture

## Overview

The Galleria provider system provides a plugin-based architecture for loading photo collections from various sources. It abstracts the source of photo data (manifests, directories, databases) behind a common PhotoCollection interface.

## Data Models

### Photo
Standardized representation of a single photo with metadata:

```python
class Photo:
    source_path: str      # Path to original photo file
    dest_path: str        # Path to organized photo file
    hash: str            # Content hash for deduplication
    size_bytes: int      # File size in bytes
    mtime: float         # File modification time
    camera: str          # Camera model (optional)
    gps: dict           # GPS coordinates {"lat": float, "lon": float} (optional)
```

### PhotoCollection
Container for a collection of photos with metadata:

```python
class PhotoCollection:
    name: str                    # Collection name
    description: str             # Collection description (optional)
    photos: List[Photo]          # List of photos in collection
```

## Current Implementation

### NormPic v0.1.0 Provider
- Loads NormPic JSON manifest files
- Converts NormPic data format to standardized Photo/PhotoCollection models
- Handles all NormPic v0.1.0 fields (camera, GPS, timestamps, errors)

### Entry Point
```python
from galleria.serializer.loader import load_photo_collection

collection = load_photo_collection("/path/to/manifest.json")
# Returns PhotoCollection with standardized Photo objects
```

### Error Handling
- `ManifestNotFoundError` - File not found
- `ManifestValidationError` - Invalid manifest data format

## Plugin Architecture (Future)

### PhotoCollectionProvider Interface
Base class for implementing new collection sources:

```python
class PhotoCollectionProvider(ABC):
    def can_handle(self, source: str) -> bool:
        """Check if this provider can handle the given source."""
        pass
    
    def load_collection(self, source: str) -> PhotoCollection:
        """Load photo collection from source.""" 
        pass
```

### Future Provider Examples
- **DirectoryProvider** - Scan filesystem directories for photos
- **DatabaseProvider** - Load from photo management databases
- **LightroomProvider** - Import from Lightroom catalogs
- **APIProvider** - Fetch from cloud photo services

### Provider Registration
```python
# Future plugin registration system
register_provider("normpic", NormPicProvider())
register_provider("directory", DirectoryProvider())
register_provider("lightroom", LightroomProvider())
```

## Design Principles

### Separation of Concerns
- **Data Models**: Provider-agnostic photo representation
- **Providers**: Source-specific loading logic
- **Interface**: Common abstraction for all sources

### Extensibility
- Plugin system allows new photo sources without core changes
- Standardized data models work with any provider
- Clean provider interface for consistent behavior

### Error Handling
- Provider-specific errors converted to common exceptions
- Clear error messages for debugging
- Graceful handling of malformed data

## Testing Strategy

### Comprehensive Coverage
- **Model Tests**: Photo and PhotoCollection creation and behavior
- **Provider Tests**: NormPic manifest loading with various data formats
- **Integration Tests**: E2E workflow from manifest to PhotoCollection
- **Edge Cases**: Invalid data, missing files, malformed JSON

### TDD Approach
- E2E integration tests drive implementation
- Unit tests focus on specific component behavior
- Tests verify both success and failure scenarios

## Future Development

### Next Steps
1. Implement DirectoryProvider for manifest-free photo collections
2. Add provider auto-detection based on source type
3. Create provider registry and plugin loading system
4. Add configuration for provider selection and options

### Extraction Preparation
- Designed for eventual extraction to separate package
- Minimal dependencies on Galleria-specific code
- Clear interfaces suitable for external consumption
- Comprehensive test suite for validation during extraction