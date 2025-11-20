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

### NormPicProviderPlugin (Plugin System)
The NormPic provider has been implemented as a proper plugin:

**Location**: `galleria/plugins/providers/normpic.py`
**Interface**: Implements `ProviderPlugin` 
**Features**:
- Loads NormPic JSON manifest files through plugin interface
- Converts NormPic data to standardized ProviderPlugin contract format  
- Comprehensive error handling with plugin result system
- Full backward compatibility with legacy serializer API

### Plugin Usage
```python
from galleria.plugins.providers.normpic import NormPicProviderPlugin
from galleria.plugins import PluginContext
from pathlib import Path

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
    print(f"Errors: {result.errors}")
```

### Legacy Entry Point (Deprecated)
```python
from galleria.serializer.loader import load_photo_collection

collection = load_photo_collection("/path/to/manifest.json")
# Returns PhotoCollection with standardized Photo objects
```

### Plugin Error Handling
- Structured error reporting via `PluginResult.errors` list
- Graceful failure with success/failure status
- Detailed error messages for debugging
- Plugin-standard exception handling

## Plugin Architecture (Implemented)

### ProviderPlugin Interface
Base class for implementing new collection sources (see `galleria/plugins/interfaces.py`):

```python
from galleria.plugins import ProviderPlugin

class MyProvider(ProviderPlugin):
    @property
    def name(self) -> str:
        return "my-provider"
    
    @property  
    def version(self) -> str:
        return "1.0.0"
    
    def load_collection(self, context: PluginContext) -> PluginResult:
        """Load photo collection from source."""
        # Implementation here
        pass
```

The plugin system foundation is complete with comprehensive interface contracts, error handling, and hook system integration.

### Future Provider Examples
- **DirectoryProvider** - Scan filesystem directories for photos
- **DatabaseProvider** - Load from photo management databases
- **LightroomProvider** - Import from Lightroom catalogs
- **APIProvider** - Fetch from cloud photo services

### Plugin Integration
```python
# Current plugin system integration
# Providers implement the ProviderPlugin interface
# Plugin orchestration through manager/hooks system
# See plugin-system.md for complete architecture
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

## Development Status

### Completed (Commit 3)
1. ✅ **NormPicProviderPlugin Implementation** - Converted existing serializer to proper ProviderPlugin
2. ✅ **Comprehensive Test Coverage** - 15 tests covering unit and integration scenarios
3. ✅ **Plugin Interface Compliance** - Follows ProviderPlugin contract specification
4. ✅ **Backward Compatibility** - Legacy serializer API still available
5. ✅ **Error Handling** - Plugin-standard error reporting with PluginResult

### Next Steps  
1. **ThumbnailProcessorPlugin** (Commit 4) - Convert image processor to ProcessorPlugin
2. **Plugin Registry System** (Commit 5) - Provider discovery and orchestration
3. **Template/CSS Plugins** (Commit 6) - Complete remaining plugin implementations
4. **DirectoryProvider** - Scan filesystem directories for photos (future)
5. **DatabaseProvider** - Load from photo management databases (future)

### Extraction Preparation
- Designed for eventual extraction to separate package
- Minimal dependencies on Galleria-specific code
- Clear interfaces suitable for external consumption
- Comprehensive test suite for validation during extraction