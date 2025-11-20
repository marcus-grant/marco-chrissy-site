# Galleria Module Structure

## Overview

Galleria is a focused gallery generator that converts NormPic manifests into static HTML galleries with plugin extensibility built-in from day one.

## Module Structure

```
galleria/
├── __init__.py         # Main module entry point
├── __main__.py         # CLI entry point for python -m galleria
├── config.py           # Configuration loading and validation
├── manager/            # Plugin orchestration
│   ├── __init__.py
│   ├── pipeline.py     # Pipeline execution management
│   └── registry.py     # Plugin discovery and registration
├── plugins/            # Plugin system implementation
│   ├── __init__.py
│   ├── base.py         # BasePlugin abstract class
│   ├── interfaces.py   # Specific plugin interfaces
│   ├── exceptions.py   # Plugin exception hierarchy
│   ├── css.py          # CSS generation plugins
│   ├── pagination.py   # Pagination transform plugins
│   ├── template.py     # HTML template plugins
│   ├── processors/     # Image processing plugins
│   │   └── thumbnail.py
│   └── providers/      # Data provider plugins
│       └── normpic.py
├── processor/          # Core image processing logic
│   └── image.py        # ImageProcessor for WebP generation
└── serializer/         # Manifest loading and data models
    ├── __init__.py
    ├── loader.py       # PhotoCollection loading
    ├── models.py       # Data model definitions
    └── exceptions.py   # Serialization exceptions
```

## Implementation Status

**Completed**: Full plugin-based architecture with CLI
**Completed**: All 5 plugin stages implemented and tested
**Completed**: CLI generate command with file writing and error handling
**Completed**: 239 comprehensive tests with full E2E validation
**Ready**: For extraction as standalone package

## Module Responsibilities

### CLI (__main__.py)
**Purpose**: Command-line interface for gallery generation

**Responsibilities**:
- Parse command-line arguments (--config, --output, --verbose)
- Load and validate configuration files
- Execute plugin pipeline through PipelineManager
- Write generated files (HTML, CSS, thumbnails) to disk
- Provide progress reporting and error handling

### manager/
**Purpose**: Plugin orchestration and pipeline execution

**Responsibilities**:
- Register and discover plugins by stage
- Execute multi-stage plugin pipeline
- Coordinate data flow between pipeline stages
- Handle plugin errors and validation

### plugins/
**Purpose**: Modular gallery generation stages

**Responsibilities**:
- **providers/**: Load photo collections from manifests
- **processors/**: Generate thumbnails and process images
- **pagination.py**: Transform data with pagination logic
- **template.py**: Generate HTML structure and pages
- **css.py**: Generate responsive stylesheets

### processor/
**Purpose**: Core image processing functionality

**Responsibilities**:
- Convert JPEG/PNG images to optimized WebP thumbnails
- Apply center-crop resizing for consistent aspect ratios
- Implement caching to skip unchanged images
- Handle image format conversion and quality settings

### serializer/
**Purpose**: Data loading and model definitions

**Responsibilities**:
- Load and parse NormPic manifest files
- Define data models for PhotoCollection and Photo
- Handle manifest validation and error reporting
- Provide data transformation for plugin pipeline

### config.py
**Purpose**: Configuration management

**Responsibilities**:
- Load and validate JSON configuration files
- Parse pipeline stage configurations
- Handle CLI option overrides (output directory)
- Validate file paths and dependencies

## Current Implementation Status

The Galleria module is fully implemented with a complete plugin-based architecture:

- **CLI Interface**: Complete with argument parsing, config validation, and file writing
- **Plugin Pipeline**: All 5 stages implemented and tested (Provider → Processor → Transform → Template → CSS)  
- **Test Coverage**: 239 comprehensive tests including E2E validation
- **Error Handling**: Graceful error handling with detailed progress reporting
- **File Output**: HTML pages, CSS stylesheets, and WebP thumbnails generated and written to disk

Ready for production use and Phase 2 integration.