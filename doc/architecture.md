# Architecture

## System Overview

The marco-chrissy-site project follows a modular, loosely-coupled architecture where each component has a single, well-defined responsibility.

## Core Principles

### Separation of Concerns
- **NormPic**: Photo organization (external tool)
- **Galleria**: Gallery generation with plugin system (internal module)
- **Pelican**: Static site generation (external framework)
- **Orchestrator**: Build coordination
- **Deployer**: CDN deployment

### No Tight Coupling
- Components communicate through files and manifests
- No direct imports between tools
- Configuration-driven behavior
- Clear data contracts (JSON manifests)

### Module Organization
Following functional organization patterns:
- Avoid generic "core" directories
- Organize by specific responsibility
- Clear module boundaries
- Each directory represents a type, not a collection

## Data Flow

### Current (Phase 1): Direct Tool Orchestration
```
Photos (source) -> NormPic -> Organized Photos + Manifest
                                      |
                                  Galleria
                                      |
                              Gallery HTML/CSS
                                      |
                    Pelican <- Content Pages
                                      |
                               Static Site -> CDN
```

### Planned (Phase 2): 4-Stage Pipeline
```
site validate -> site organize -> site build -> site deploy
     |               |              |            |
Pre-flight      NormPic       Galleria +    Bunny CDN
  checks      orchestration   Pelican      (dual bucket)
                             integration
```

Each stage is idempotent and automatically calls predecessors if needed.

## Directory Structure

### Current (Phase 1)
```
marco-chrissy-site/
├── galleria/           # Gallery generator (extractable)
├── config/            # All configurations
├── content/          # Pelican content
├── output/           # Generated site
└── pelican/          # Pelican configuration
```

### Planned (Phase 2): 4-Stage Pipeline Structure
```
marco-chrissy-site/
├── cli/              # Command-line interface (site command)
├── validator/        # Pre-flight checks module
├── build/           # Orchestration modules (Galleria + Pelican)
├── deploy/          # Bunny CDN deployment logic
├── serializers/     # Config loading with schema validation
├── config/          # All configuration files
│   ├── schemas/     # JSON schemas for validation
│   ├── site.json    # Pipeline orchestration config
│   ├── normpic.json # Photo organization config
│   ├── pelican.json # Site generation config
│   └── galleria.json # Gallery generation config
├── galleria/        # Gallery generator (extractable)
├── content/         # Pelican content pages
└── output/          # Generated site output
    ├── pics/        # Full photos -> Photos CDN bucket
    ├── galleries/   # Gallery pages + thumbs -> Site CDN
    ├── about/       # Pelican pages -> Site CDN
    └── index.html   # Site root -> Site CDN
```

## Galleria Plugin Architecture

Galleria uses a 5-stage plugin pipeline for extensible gallery generation:

1. **Provider** → Load photo collections (NormPic manifests, directories, databases)
2. **Processor** → Generate thumbnails and process images  
3. **Transform** → Manipulate data (pagination, sorting, filtering)
4. **Template** → Generate HTML structure
5. **CSS** → Generate stylesheets

### Plugin System Structure
```
galleria/
├── plugins/            # Plugin system foundation
│   ├── base.py         # BasePlugin interface
│   ├── interfaces.py   # Specific plugin interfaces
│   └── exceptions.py   # Plugin exception hierarchy
└── manager/            # Plugin orchestration
    └── hooks.py        # Hook system for extensibility
```

Each stage has defined data contracts and can be extended through the plugin system. The complete plugin system is implemented and tested with 239 comprehensive tests, including full end-to-end CLI validation.

See [Plugin System Documentation](modules/galleria/plugin-system.md) for detailed interface specifications.

### Galleria CLI Interface

Galleria provides a complete command-line interface for gallery generation:

```bash
# Basic usage
galleria generate --config config.json

# With output override and verbose logging
galleria generate --config config.json --output /path/to/output --verbose
```

The CLI orchestrates the complete plugin pipeline:
1. Loads and validates configuration files
2. Executes provider → processor → transform → template → css pipeline
3. Writes generated HTML, CSS, and thumbnail files to disk
4. Provides comprehensive error handling and progress reporting

**Status**: Fully implemented and tested with end-to-end validation.

## Phase 2 Integration Strategy

### Plugin-Based Pelican Integration

To maintain Galleria's extractability while achieving tight site integration, Phase 2 uses a custom template plugin approach:

**PelicanTemplatePlugin**:
- Extends Galleria's `TemplatePlugin` interface
- Uses shared Jinja2 templates for consistent navigation/styling
- Replaces `BasicTemplatePlugin` in site-specific Galleria configuration
- Site-specific integration logic stays in site repo, not in Galleria core

**Benefits**:
- Galleria remains generic and extractable
- Site integration happens through well-defined plugin interface  
- Shared template system ensures consistent styling across Galleria + Pelican
- Future projects can create their own template plugins

### Dual CDN Strategy

**Output Structure**:
- `output/pics/` -> Photos CDN bucket (large, stable files)
- Everything else -> Site CDN (pages, thumbnails, CSS - smaller, changing content)

**URL Structure**:
- Site pages: `base_url/about/`, `base_url/galleries/`
- Gallery pages: `base_url/galleries/wedding/page1`, etc.
- Full photos: `photos_cdn_url/pics/wedding/photo.jpg`

## Integration Points

### File-Based Communication
- NormPic writes manifests to photo directories
- Galleria reads manifests from photo directories
- Galleria writes HTML to output directory
- Pelican reads from content, writes to output

### Configuration Contracts
Each tool has its own configuration format:
- NormPic: Photo organization rules
- Galleria: Gallery generation settings
- Pelican: Site generation configuration
- Orchestrator: Build workflow settings

## Future Extensibility

### Django/FastAPI Integration
The architecture supports future dynamic features:
- Same content directories
- Same manifest format
- Same output structure
- Different serving mechanism

### Extraction Path
Galleria is designed for extraction:
- Self-contained module
- No parent project dependencies
- Clear interfaces
- Configuration-driven