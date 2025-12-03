# Build Module Documentation

## Overview

The build module implements the orchestrator pattern for coordinating site generation. This module replaced a 195-line "god function" build command with a clean, testable architecture that achieves 77% code reduction while providing better maintainability and reusability.

## Architecture

The build module follows a layered orchestrator pattern:

```
BuildOrchestrator
├── ConfigManager (unified config loading)
├── GalleriaBuilder (gallery generation) 
└── PelicanBuilder (site generation)
```

This architecture separates business logic from CLI concerns, making the build process callable from any context (CLI, API, tests, scripts).

## Module Components

### Core Orchestration

- [**BuildOrchestrator**](orchestrator.md) - Main coordination class that executes complete build workflow
- [**ConfigManager**](config-manager.md) - Unified configuration loading for all config files

### Builder Components

- [**GalleriaBuilder**](galleria-builder.md) - Gallery generation using Galleria plugin system
- [**PelicanBuilder**](pelican-builder.md) - Static site generation using Pelican

### Supporting Infrastructure

- [**Build Exceptions**](exceptions.md) - Comprehensive exception hierarchy for build errors

## Key Benefits

- **Simplified Testing**: Mock 1 orchestrator instead of 4+ dependencies
- **Business Logic Separation**: Core functionality independent of CLI presentation
- **Reusability**: BuildOrchestrator callable from non-CLI contexts
- **Single Responsibility**: Each class has one clear job
- **Error Handling**: Comprehensive exception hierarchy with proper chaining
- **BuildContext Integration**: Environment-aware builds for production vs development modes

## Usage Example

```python
from build.orchestrator import BuildOrchestrator

# Simple orchestrated build (production mode)
orchestrator = BuildOrchestrator()
success = orchestrator.execute()

# Custom paths
orchestrator = BuildOrchestrator()
success = orchestrator.execute(
    config_dir=Path("custom/config"),
    base_dir=Path("/project/root")
)

# Development mode with localhost URLs
success = orchestrator.execute(
    override_site_url="http://localhost:8000"
)
```

## Testing Strategy

The build module uses a simplified testing approach:

- **Unit Tests**: Test each component in isolation with focused responsibilities
- **Integration Tests**: Test orchestrator coordination with mocked builders
- **E2E Tests**: Test complete workflow with temporary filesystems

See [Testing Guide](../../testing.md) for detailed testing patterns and examples.

## BuildContext Integration

The build module implements environment-aware building through the BuildContext system. This enables seamless switching between production and development builds with appropriate URL generation.

### GalleriaBuilder BuildContext Support

The `GalleriaBuilder` now accepts BuildContext parameters for context-aware gallery generation:

```python
from build.galleria_builder import GalleriaBuilder
from build.context import BuildContext

builder = GalleriaBuilder()

# Production build - uses config CDN URLs
build_context = BuildContext(production=True)
builder.build(
    galleria_config=config,
    base_dir=Path.cwd(),
    build_context=build_context,
    site_url="https://site.example.com"
)

# Development build - uses localhost URLs
build_context = BuildContext(production=False)
builder.build(
    galleria_config=config,
    base_dir=Path.cwd(), 
    build_context=build_context,
    site_url="http://localhost:8000"
)
```

### Metadata Passing

The GalleriaBuilder passes BuildContext through the Galleria pipeline metadata, enabling template plugins to access environment information:

```python
# GalleriaBuilder creates metadata with BuildContext
metadata = {
    "build_context": build_context,
    "site_url": site_url
}

# Passed to PluginContext for pipeline execution
initial_context = PluginContext(
    input_data={"manifest_path": str(manifest_path)},
    config=plugin_config,
    output_dir=output_dir,
    metadata=metadata  # Contains BuildContext
)
```

### Template Plugin Integration

Template plugins can access BuildContext from the pipeline metadata for environment-aware URL generation:

```python
# In template plugins
build_context = context.metadata.get("build_context")
site_url = context.metadata.get("site_url")

if build_context:
    # Use context-aware URL generation
    from galleria.template.filters import full_url
    generated_url = full_url(path, build_context, site_url)
```