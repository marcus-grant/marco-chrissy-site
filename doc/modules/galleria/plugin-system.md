# Galleria Plugin System

## Overview

Galleria uses a plugin-based architecture to enable modular, extensible gallery generation. The plugin system provides a unified interface for different types of processing stages while maintaining clean separation of concerns.

## Module Architecture

### galleria/plugins/
- Plugin interfaces and abstract base classes
- Plugin-specific exceptions
- Plugin contract definitions
- Individual plugin implementations

### galleria/manager/ (Future)
- Plugin orchestration and lifecycle management
- Hook system for extensibility points
- Plugin registry and discovery
- Pipeline execution coordination

This separation ensures clean boundaries between plugin definitions and plugin management.

## Plugin Pipeline

The gallery generation follows a five-stage pipeline:

1. **Provider** → Photo collection loading (manifest/data sources)
2. **Processor** → Thumbnail generation and image processing
3. **Transform** → Data manipulation (pagination, sorting, filtering)
4. **Template** → HTML structure generation
5. **CSS** → Stylesheet generation and styling

Each stage receives structured input from the previous stage and produces structured output for the next stage.

## Base Plugin Interface

All plugins must inherit from `BasePlugin` and implement the required abstract methods:

```python
from galleria.plugins import BasePlugin

class MyPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "my-plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
```

### Required Properties

- **name**: Unique string identifier for the plugin
- **version**: Semantic version string (e.g., "1.0.0")

## Plugin Types (Future)

### Provider Plugins
Load photo collection data from various sources:
- **NormPicProvider**: Loads NormPic v0.1.0 manifests
- **DirectoryProvider**: Scans filesystem directories
- **DatabaseProvider**: Loads from database sources

### Processor Plugins  
Generate thumbnails and process images:
- **ThumbnailProcessor**: WebP thumbnail generation with caching
- **MetadataProcessor**: EXIF data extraction
- **WatermarkProcessor**: Watermark application

### Transform Plugins
Manipulate photo collection data:
- **PaginationTransform**: Split collections into pages
- **SortTransform**: Order photos by various criteria
- **FilterTransform**: Apply visibility rules
- **GroupTransform**: Create sub-collections

### Template Plugins
Generate HTML structure:
- **GalleryTemplate**: Grid-based photo galleries  
- **CarouselTemplate**: Slideshow presentations
- **ListTemplate**: List-based layouts

### CSS Plugins
Generate stylesheets:
- **ResponsiveCSS**: Mobile-first responsive styles
- **ThemeCSS**: Theme-based styling systems
- **UtilityCSS**: Utility-first CSS generation

## Error Handling

The plugin system includes a comprehensive exception hierarchy for consistent error handling:

### Exception Types

- **PluginError**: Base exception for all plugin-related errors
  - Supports plugin name tracking for debugging
  - All plugin exceptions inherit from this base class

- **PluginValidationError**: Invalid context or configuration
  - Raised when plugin input validation fails
  - Examples: invalid config parameters, missing context fields

- **PluginExecutionError**: Runtime execution failures  
  - Supports original exception chaining for debugging
  - Examples: file system errors, image processing failures

- **PluginDependencyError**: Missing or incompatible dependencies
  - Tracks list of missing dependencies for detailed reporting
  - Examples: missing Python packages, incompatible versions

### Usage Examples

```python
from galleria.plugins import PluginExecutionError

try:
    process_image(source_path)
except OSError as e:
    raise PluginExecutionError(
        "Failed to process image",
        plugin_name="thumbnail-processor",
        original_error=e
    )
```

All plugin exceptions can be caught using the base `PluginError` class for unified error handling across the plugin system.

## Hook System

The plugin system includes a comprehensive hook system for extensibility points throughout the pipeline.

### Hook Manager

The `PluginHookManager` provides hook registration and execution:

```python
from galleria.manager.hooks import PluginHookManager

# Create hook manager
hook_manager = PluginHookManager()

# Register hook callbacks
def log_stage(context):
    print(f"Processing: {context.input_data}")
    return PluginResult(success=True, output_data=context.input_data)

hook_manager.register_hook("before_provider", log_stage)
```

### Standard Hook Points

The plugin pipeline provides hooks at each stage:

- **before_provider** / **after_provider**: Photo collection loading stage
- **before_processor** / **after_processor**: Image processing stage  
- **before_transform** / **after_transform**: Data transformation stage
- **before_template** / **after_template**: HTML generation stage
- **before_css** / **after_css**: Stylesheet generation stage

### Hook Execution

Hooks are executed in registration order and receive `PluginContext`:

```python
# Execute hook with context
results = hook_manager.execute_hook("before_provider", context)

# Hooks can modify context data for debugging, logging, validation
for result in results:
    if not result.success:
        print(f"Hook failed: {result.errors}")
```

### Use Cases

Common hook use cases include:

- **Logging**: Track pipeline execution progress
- **Validation**: Verify context data at each stage
- **Debugging**: Inspect data flow between plugins
- **Metrics**: Collect performance and usage statistics
- **Caching**: Implement custom caching strategies

## Extensibility

The plugin system is designed for extensibility from day one:

- Plugin hooks enable custom processing at each stage (implemented)
- Plugin registry supports runtime discovery and loading (future)
- Clean interfaces allow easy testing and development
- Modular design enables independent plugin development

## Development Guidelines

When developing plugins:

1. Inherit from the appropriate base plugin class
2. Implement all required abstract methods
3. Follow semantic versioning for version property
4. Provide clear, descriptive names
5. Handle errors gracefully with appropriate exceptions
6. Include comprehensive unit tests
7. Document plugin-specific configuration options

## Future Enhancements

Planned plugin system enhancements include:

- Plugin registry and discovery mechanisms
- Configuration validation and dependency management
- Plugin performance monitoring and profiling
- Hot-reloading for development workflows