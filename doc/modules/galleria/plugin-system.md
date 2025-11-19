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

## Plugin Interfaces

### ProviderPlugin Interface

Providers load photo collection data from various sources and must implement:

```python
from galleria.plugins import ProviderPlugin

class MyProvider(ProviderPlugin):
    def load_collection(self, context: PluginContext) -> PluginResult:
        # Load photos and return structured data
        pass
```

**Required Output Format:**
```python
{
    "photos": [
        {
            "source_path": str,    # Path to original photo file
            "dest_path": str,      # Relative destination path  
            "metadata": dict       # Optional metadata (EXIF, etc.)
        },
        ...
    ],
    "collection_name": str,        # Name of the photo collection
    "manifest_version": str        # Version info (optional)
}
```

**Example Implementations:**
- **NormPicProvider**: Loads NormPic v0.1.0 manifests (future)
- **DirectoryProvider**: Scans filesystem directories (future)
- **DatabaseProvider**: Loads from database sources (future)

### ProcessorPlugin Interface

Processors generate thumbnails and process images from provider data:

```python
from galleria.plugins import ProcessorPlugin

class MyProcessor(ProcessorPlugin):
    def process_thumbnails(self, context: PluginContext) -> PluginResult:
        # Generate thumbnails and process images
        pass
```

**Expected Input Format (from ProviderPlugin):**
```python
{
    "photos": [...],               # Photo collection from provider
    "collection_name": str,
    ...                           # Other provider data
}
```

**Required Output Format:**
```python
{
    "photos": [
        {
            # All original photo data from provider
            "thumbnail_path": str,      # Path to generated thumbnail
            "thumbnail_size": tuple,    # (width, height) of thumbnail
            # Other processing results...
        },
        ...
    ],
    "collection_name": str,
    "thumbnail_count": int,             # Number of thumbnails generated
    ...                                 # Other processing metadata
}
```

**Example Implementations:**
- **ThumbnailProcessor**: WebP thumbnail generation with caching (future)
- **MetadataProcessor**: EXIF data extraction (future)
- **WatermarkProcessor**: Watermark application (future)

### TransformPlugin Interface

Transforms manipulate processed photo data for pagination, sorting, and filtering:

```python
from galleria.plugins import TransformPlugin

class MyTransform(TransformPlugin):
    def transform_data(self, context: PluginContext) -> PluginResult:
        # Transform photo data according to plugin logic
        pass
```

**Expected Input Format (from ProcessorPlugin):**
```python
{
    "photos": [
        {
            # All photo data including thumbnails from processor
            "thumbnail_path": str,
            "thumbnail_size": tuple,
            ...
        },
        ...
    ],
    "collection_name": str,
    "thumbnail_count": int,
    ...                           # Other processor data
}
```

**Required Output Format:**
```python
{
    # Transformed data structure (varies by transform type)
    "pages": [...],              # For pagination transforms
    "photos": [...],             # For sorting/filtering transforms  
    "groups": [...],             # For grouping transforms
    "collection_name": str,      # Preserved from input
    "transform_metadata": dict,  # Transform-specific metadata
    ...
}
```

**Example Implementations:**
- **PaginationTransform**: Split collections into pages (future)
- **SortTransform**: Order photos by various criteria (future)
- **FilterTransform**: Apply visibility rules (future)
- **GroupTransform**: Create sub-collections (future)

### Template Plugins (Future)
Generate HTML structure:
- **TemplatePlugin**: Abstract interface for HTML generation (future)
- **GalleryTemplate**: Grid-based photo galleries  
- **CarouselTemplate**: Slideshow presentations
- **ListTemplate**: List-based layouts

### CSS Plugins (Future)
Generate stylesheets:
- **CSSPlugin**: Abstract interface for stylesheet generation (future)
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