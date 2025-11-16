# Galleria Module Structure

## Overview

Galleria is a focused gallery generator that converts NormPic manifests into static HTML galleries with plugin extensibility built-in from day one.

## Module Structure

```
galleria/
├── generator/          # Orchestrates gallery generation workflow
├── template/           # Template loading and rendering
├── processor/          # Image processing (thumbnails, optimization)
├── serializer/         # Config and manifest (de)serialization
└── themes/            # Gallery themes and assets
```

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

**Interface**:
- Called by generator during processing phase
- Memory-efficient for large collections
- Pluggable processing pipeline

**Plugin Support**:
- Custom image filters
- Additional output formats
- Metadata extraction

### serializer/
**Purpose**: Configuration and manifest (de)serialization

**Responsibilities**:
- Parse NormPic JSON manifests
- Load and validate galleria configuration
- Convert between JSON and Python objects
- Handle schema validation

**Interface**:
- Used by all modules for data loading
- Provides validated data structures
- Centralized error handling for malformed data

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