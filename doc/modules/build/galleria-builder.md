# GalleriaBuilder

## Overview

The GalleriaBuilder handles gallery generation using the Galleria plugin system. It provides a clean interface for executing the complete galleria workflow while maintaining the plugin-based architecture for extensibility.

## Class Design

```python
class GalleriaBuilder:
    def __init__(self):
        pass  # Stateless builder
    
    def build(self, galleria_config: dict, base_dir: Path = Path.cwd()) -> bool:
        # Executes galleria plugin pipeline
```

## Key Features

### Plugin System Integration
- Uses Galleria's PipelineManager for plugin orchestration
- Registers and configures all required plugins (Provider, Processor, Transform, Template, CSS)
- Maintains Galleria's extensible architecture

### Configuration Mapping
- Converts site build configuration to Galleria plugin configuration
- Maps config file paths to plugin requirements
- Handles plugin-specific configuration options

### Error Handling
- Catches plugin execution errors and wraps in GalleriaError
- Provides clear error messages for plugin failures
- Maintains exception chaining for debugging

## API Reference

### `build(galleria_config: dict, base_dir: Path = Path.cwd()) -> bool`

Executes the complete galleria build workflow.

**Parameters:**
- `galleria_config`: Configuration dictionary loaded from galleria.json
- `base_dir`: Base directory for resolving relative paths

**Returns:**
- `True` if galleria build completed successfully

**Raises:**
- `GalleriaError`: If plugin registration, configuration, or execution fails

## Configuration Format

Expected galleria_config structure:
```json
{
    "manifest_path": "path/to/manifest.json",
    "output_dir": "output/galleries", 
    "theme": "minimal",
    "pagination": {
        "page_size": 12
    },
    "thumbnail": {
        "size": 400,
        "quality": 85
    }
}
```

## Plugin Workflow

The GalleriaBuilder executes this plugin pipeline:

1. **Provider Stage**: Load photo collection from NormPic manifest
2. **Processor Stage**: Generate thumbnails from source photos  
3. **Transform Stage**: Apply pagination to photo collection
4. **Template Stage**: Generate HTML gallery pages
5. **CSS Stage**: Generate stylesheet files

## Usage Patterns

### Basic Usage
```python
from build.galleria_builder import GalleriaBuilder

builder = GalleriaBuilder()
galleria_config = {
    "manifest_path": "photos/manifest.json",
    "output_dir": "output/galleries"
}
success = builder.build(galleria_config)
```

### Custom Base Directory
```python
from pathlib import Path
from build.galleria_builder import GalleriaBuilder

builder = GalleriaBuilder()
success = builder.build(
    galleria_config,
    base_dir=Path("/project/root")
)
```

### Error Handling
```python
from build.galleria_builder import GalleriaBuilder
from build.exceptions import GalleriaError

builder = GalleriaBuilder()
try:
    success = builder.build(galleria_config)
except GalleriaError as e:
    print(f"Gallery generation failed: {e}")
```

## Plugin Registration

The builder automatically registers these plugins:

```python
# Internally registers:
registry.register_plugin("provider", NormPicProviderPlugin())
registry.register_plugin("processor", ThumbnailProcessorPlugin()) 
registry.register_plugin("transform", BasicPaginationPlugin())
registry.register_plugin("template", BasicTemplatePlugin())
registry.register_plugin("css", BasicCSSPlugin())
```

## Testing

GalleriaBuilder is tested with unit tests that mock the plugin system:

```python
@patch('build.galleria_builder.PipelineManager')
def test_build_galleria(mock_pipeline_manager):
    mock_pipeline = Mock()
    mock_pipeline_manager.return_value = mock_pipeline
    mock_result = Mock(success=True)
    mock_pipeline.execute_stages.return_value = mock_result
    
    builder = GalleriaBuilder()
    success = builder.build(galleria_config)
    
    assert success is True
    mock_pipeline.execute_stages.assert_called_once()
```

## Integration with Galleria

The GalleriaBuilder maintains clean separation from the main site build while leveraging Galleria's plugin architecture:

### Plugin Configuration
- Maps site configuration to plugin-specific config
- Handles plugin initialization and registration
- Manages plugin execution workflow

### Output Management  
- Ensures gallery output goes to configured directory
- Handles output path resolution relative to base directory
- Coordinates with site build for proper file placement

## Design Benefits

### Encapsulation
- Isolates Galleria integration complexity from orchestrator
- Provides simple success/failure interface
- Handles all plugin system details internally

### Maintainability
- Clear separation between gallery and site generation
- Plugin system remains extensible
- Easy to update Galleria integration without affecting other builders

### Testability
- Single mock point for plugin system
- Isolated testing of gallery-specific logic  
- Clear configuration interface for test setup