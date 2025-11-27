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

## Usage Example

```python
from build.orchestrator import BuildOrchestrator

# Simple orchestrated build
orchestrator = BuildOrchestrator()
success = orchestrator.execute()

# Custom paths
orchestrator = BuildOrchestrator()
success = orchestrator.execute(
    config_dir=Path("custom/config"),
    base_dir=Path("/project/root")
)
```

## Testing Strategy

The build module uses a simplified testing approach:

- **Unit Tests**: Test each component in isolation with focused responsibilities
- **Integration Tests**: Test orchestrator coordination with mocked builders
- **E2E Tests**: Test complete workflow with temporary filesystems

See [Testing Guide](../../testing.md) for detailed testing patterns and examples.