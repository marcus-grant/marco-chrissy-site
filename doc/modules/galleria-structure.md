# Galleria Module Structure

## Overview

Galleria is a focused gallery generator that converts NormPic manifests into static HTML galleries with plugin extensibility built-in from day one.

## Module Structure

```
galleria/
├── __init__.py         # Main module entry point
├── doc/               # Galleria-specific documentation
├── generator/         # Orchestrates gallery generation workflow
│   └── __init__.py
├── template/          # Template loading and rendering
│   └── __init__.py
├── processor/         # Image processing (thumbnails, optimization)
│   └── __init__.py
├── serializer/        # Config and manifest (de)serialization
│   └── __init__.py
└── themes/           # Gallery themes and assets
    ├── __init__.py
    └── minimal/      # Default minimal theme
        ├── __init__.py
        ├── config.json
        ├── templates/
        └── static/
```

## Implementation Status

**✅ Completed**: Core module directory structure and initialization files
**✅ Completed**: Serializer module with NormPic v0.1.0 compatibility and plugin architecture
**✅ Completed**: Processor module with thumbnail generation and caching
**🚧 Next**: Implement template rendering and theme system

## Module Responsibilities

### generator/
**Purpose**: Orchestrates the gallery generation workflow

**Responsibilities**:
- Coordinate serializer → processor → template workflow
- Handle plugin hook points for extensibility
- Manage generation progress and error reporting
- Control output directory structure

**Interface**:
- Called by `galleria generate` command
- Coordinates other galleria modules
- Provides plugin extension points

**Plugin Hooks**:
- Pre-processing manifest data
- Post-processing generated files
- Custom template variables
- Asset pipeline modifications

### template/
**Purpose**: Template loading and rendering with plugin support

**Responsibilities**:
- Load HTML templates from themes
- Render paginated gallery pages
- Generate navigation links
- Support plugin template injection

**Interface**:
- Called by generator during rendering phase
- Extensible through plugin system
- Theme-agnostic template loading

**Plugin Support**:
- Template variable injection
- Custom template filters
- Additional template includes

### processor/
**Purpose**: Image processing and optimization

**Responsibilities**:
- Generate optimized thumbnails (WebP, configurable size)
- Handle image format conversion
- Manage processing caches
- Support plugin processing pipelines

**Current Implementation**:
- `ImageProcessor` - Main processing class
- `process_image(source_path, output_dir, size=400, quality=85)` - Single image processing
- `process_collection(collection, output_dir, ...)` - Batch processing with progress
- `should_process(source_path, thumbnail_path)` - Naive caching via mtime comparison
- Center crop strategy for non-square images
- WebP output format with quality control
- Comprehensive error handling (ImageProcessingError)
- Progress callbacks for large collections

**Interface**:
- Called by generator during processing phase
- Memory-efficient for large collections
- Pluggable processing pipeline

**Plugin Support**:
- Custom image filters
- Additional output formats
- Metadata extraction

### serializer/
**Purpose**: Photo collection provider system

**Responsibilities**:
- Load photo collections from various sources (manifests, directories, databases)
- Provide standardized photo data structures
- Handle error validation and reporting
- Support pluggable collection providers

**Current Implementation**:
- `load_photo_collection(path)` - Main entry point
- `Photo` - Standardized photo data model (source_path, metadata, camera, GPS)
- `PhotoCollection` - Container for photo collections with metadata
- NormPic v0.1.0 manifest provider support
- Comprehensive error handling (ManifestNotFoundError, ManifestValidationError)

**Plugin Architecture**:
- Designed for future PhotoCollectionProvider plugins
- Support for non-manifest sources (directory scanning, databases, APIs)
- Clean separation between data models and source providers

**Interface**:
- Used by generator for loading photo collections
- Provider-agnostic data structures
- Extensible plugin system for new collection sources

### themes/
**Purpose**: Theme assets and templates

**Structure**:
```
themes/
├── minimal/           # Default minimal theme
│   ├── templates/     # HTML templates
│   ├── static/        # CSS, fonts, JS
│   └── config.json    # Theme configuration
└── [future themes]/
```

**Plugin Integration**:
- Themes can include plugin-specific templates
- Plugin assets can extend theme assets
- Plugin configuration integrated with theme config

**Minimal Theme Configuration**:
- Basic theme config with 400px thumbnails
- 20 photos per page default
- Modular template and static asset directories
- Extensible for future theme variants