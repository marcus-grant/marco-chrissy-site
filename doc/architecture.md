# Architecture

## System Overview

The marco-chrissy-site project follows a modular, loosely-coupled architecture where each component has a single, well-defined responsibility.

## Core Principles

### Separation of Concerns
- **NormPic**: Photo organization (external tool)
- **Galleria**: Gallery generation with plugin system (internal module)
- **Pelican**: Static site generation (external framework)
- **Validator**: Pre-flight checks (configs, dependencies, permissions)
- **Site CLI**: Command orchestration and pipeline management

### Test-Driven Development
- **Nested TDD workflow**: E2E tests drive development direction
- **E2E tests** surface missing functionality and define requirements
- **Unit tests** implement specific pieces identified by E2E failures  
- **Continuous integration**: Test suite remains passing throughout development
- **Skip pattern**: New features start with skipped E2E tests until implementation complete

### Loose Coupling with Python Module Integration
- **Extractable Modules**: NormPic already split out, Galleria designed for post-MVP extraction
- **Python Package Imports**: Use `import galleria` and `import pelican` for better error handling
- **Independent Development**: Each module can be developed, tested, and versioned separately
- **Configuration-driven**: All tools configured via JSON manifests and config files
- **Clear APIs**: Well-defined function interfaces enable easy package boundary changes

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

### Current (Phase 2): 4-Stage Pipeline Implementation
```
site validate -> site organize -> site build -> site deploy
     |               |              |            |
Pre-flight      NormPic       Galleria +    Bunny CDN
  checks    (import normpic)  (import galleria)  (planned)
                              (import pelican)
```

**Implementation Details:**
- **Cascading calls**: Each stage calls only its immediate predecessor
- **Python integration**: Direct module imports for better error handling and performance
- **Idempotent behavior**: Commands skip work if output already exists
- **Extractable design**: Galleria module prepared for post-MVP package extraction

**✅ Current Status - Build Orchestrator Pattern Implemented:**
- **Completed**: Major refactoring from 195-line "god function" to clean orchestrator pattern
- **77% Code Reduction**: Build command reduced from 195 to 45 lines
- **Business Logic Separation**: Core functionality separated from CLI presentation
- **Perfect Testability**: Mock 1 orchestrator instead of 4+ dependencies per test
- **Full Reusability**: BuildOrchestrator callable from CLI, API, scripts, or any context
- **Complete Integration**: Both Galleria and Pelican integration working end-to-end

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

### Current (Phase 2): 4-Stage Pipeline Structure - Implemented
```
marco-chrissy-site/
├── cli/              # Command-line interface (site command)
├── validator/        # Pre-flight checks module (supports configurable base_path)
├── build/           # ✅ Build orchestration modules
│   ├── orchestrator.py     # Main coordination class
│   ├── config_manager.py   # Unified config loading
│   ├── galleria_builder.py # Gallery generation
│   ├── pelican_builder.py  # Site generation
│   └── exceptions.py       # Build exception hierarchy
├── organizer/        # Photo organization (NormPic integration)
├── serializer/       # JSON config loading with schema validation
├── config/          # All configuration files
│   ├── schema/      # JSON schemas for validation
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

## Build Orchestrator Architecture

The build system uses an orchestrator pattern that separates business logic from CLI concerns, enabling better testability and reusability.

### Orchestrator Pattern Structure
```
cli/commands/build.py (45 lines)
         ↓
BuildOrchestrator.execute()
    ├── ConfigManager.load_*_config()
    ├── GalleriaBuilder.build()
    └── PelicanBuilder.build()
```

### Key Components

- **BuildOrchestrator**: Main coordination class that manages the complete build workflow
- **ConfigManager**: Unified configuration loading for all config files (site.json, galleria.json, pelican.json, normpic.json)  
- **GalleriaBuilder**: Handles gallery generation using Galleria plugin system
- **PelicanBuilder**: Handles static site generation using Pelican
- **Build Exceptions**: Comprehensive hierarchy (BuildError → ConfigError, GalleriaError, PelicanError)

### Architecture Benefits

**Code Reduction**: 77% reduction from 195-line "god function" to 45-line simple orchestrator call

**Testing Simplification**: 
- Before: Mock 4+ dependencies per test (JsonConfigLoader, PipelineManager, pelican module, etc.)
- After: Mock 1 BuildOrchestrator class

**Business Logic Separation**:
- CLI layer only handles user interaction and error display
- Core build logic completely independent of CLI framework
- Orchestrator callable from any context (API, scripts, tests)

**Single Responsibility**:
- Each builder class has one clear job (gallery vs site generation)
- Configuration loading centralized and reusable
- Error handling consistent across all components

See [Build Module Documentation](modules/build/) for detailed usage and API reference.

## Serve Orchestrator Architecture

The serve system uses the same orchestrator pattern as the build system, separating CLI concerns from serve coordination logic for better testability and maintainability.

### Orchestrator Pattern Structure
```
cli/commands/serve.py (simplified CLI interface)
         ↓
ServeOrchestrator.start()
    ├── SiteServeProxy (request routing)
    ├── HTTP Server (proxy coordination)
    ├── Galleria subprocess (gallery serving)
    └── Pelican subprocess (site serving)
```

### Key Components

- **ServeOrchestrator**: Main coordination class that manages the complete serve workflow
- **SiteServeProxy**: Handles request routing between Galleria, Pelican, and static files
- **ProxyHTTPHandler**: HTTP request handler for the proxy server
- **CLI Command**: Simplified interface focused on argument parsing and result reporting

### Architecture Benefits

**Business Logic Separation**:
- CLI layer only handles argument parsing and user interaction  
- Core serve logic completely independent of CLI framework
- ServeOrchestrator callable from any context (API, scripts, tests)

**Improved Testability**:
- Unit tests can mock ServeOrchestrator instead of complex server setup
- Proxy logic testable independently from server coordination
- Clear separation enables focused testing of each component

**Signal Handling Fix**:
- Previous implementation had deadlock issues with signal handlers calling cleanup from serve_forever() thread
- New implementation uses event-driven shutdown with _stop_event flag
- Cleanup happens in main thread after server shutdown completes

See [Serve Module Documentation](modules/serve/) for detailed implementation and testing information.

## BuildContext System

The BuildContext system provides environment-aware build coordination for production vs development scenarios. This system enables context-sensitive URL generation and build behavior throughout the pipeline.

### BuildContext Architecture

```
BuildOrchestrator.execute(override_site_url)
         ↓
Creates BuildContext(production=override_site_url is None)
         ↓
GalleriaBuilder.build(build_context, site_url)
         ↓
Galleria Pipeline (metadata with BuildContext)
         ↓
Template Plugins (context-aware URL generation)
```

### Context States

**Production Mode** (`BuildContext(production=True)`):
- Triggered when `override_site_url=None` in BuildOrchestrator
- Uses site URL from `config/site.json` CDN configuration
- Generates absolute URLs for production deployment
- Default mode for `site build` command

**Development Mode** (`BuildContext(production=False)`):
- Triggered when `override_site_url` provided to BuildOrchestrator
- Uses override URL (typically `http://localhost:8000`)
- Generates localhost URLs for local development
- Used by `site serve` command for development workflow

### URL Generation Flow

The template filter system generates relative URLs for flexible CDN routing:

```python
# Template filter usage
full_url(path, context, site_url)
    ↓
# Generates relative URLs starting with /
"/galleries/wedding/page1"
"/pics/full/photo.jpg"
    ↓
# Edge Rules handle CDN routing
"/pics/full/*" → Photo storage zone
"/galleries/*" → Site CDN
```

### Integration Points

**BuildOrchestrator**:
- Creates appropriate BuildContext based on parameters
- Passes both BuildContext and resolved site_url to GalleriaBuilder
- Maintains production vs development mode coordination

**GalleriaBuilder**:
- Receives BuildContext and site_url as parameters
- Passes both through pipeline metadata for plugin access
- Enables template plugins to generate context-appropriate URLs

**Template System**:
- `galleria/template/filters.py` provides `full_url()` filter
- Template plugins use BuildContext for URL generation decisions
- Seamless switching between production and development URL patterns

### Design Benefits

**Environment Flexibility**: Single build system supports both production deployment and local development without configuration changes.

**URL Consistency**: All URL generation flows through BuildContext system, ensuring consistent behavior across templates and plugins.

**Development Workflow**: Local development server URLs work seamlessly with the same template system used for production.

**Plugin Extensibility**: Any template plugin can access BuildContext for environment-aware behavior without direct environment detection.

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

See [Galleria Module Documentation](modules/galleria/README.md) for detailed interface specifications.

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

## Path Management Architecture

### Current Challenge: Hardcoded Paths

**Issue Discovered**: Hardcoded paths scattered throughout codebase create testing and deployment brittleness:
- `ConfigValidator`: Hardcoded `"config/schema/normpic.json"` paths
- Test code: Direct filesystem access patterns (`glob()`, `shutil.copy()`, `os.chdir()`)
- Inflexible for different deployment scenarios (Docker, different environments)

### Temporary Solution: Dependency Injection

**Implemented**: `base_path` parameter pattern for configurable path resolution:
```python
# Production: uses current working directory  
validator = ConfigValidator()

# Testing: isolated temporary directory
validator = ConfigValidator(base_path=temp_filesystem)

# Deployment: custom base directory
validator = ConfigValidator(base_path="/app/config")
```

### Future Architecture: Centralized PathConfig

**Post-MVP Priority**: Centralized path configuration system:
```python
# Centralized path management
path_config = PathConfig.from_config("config/site.json")
validator = ConfigValidator(path_config=path_config)
```

**Benefits**:
- Docker volume mounting flexibility
- Development vs production path differences  
- CDN integration path configuration
- Deployment environment customization

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

### Index Page Conflict Resolution

**Critical Architecture Decision**: The build system automatically resolves conflicts between Pelican's default blog index and custom page content.

**Problem**: Pelican's default behavior generates a blog index at `/index.html`. If content contains a page with `slug: index`, both attempt to create the same file, triggering Pelican's "File to be overwritten" error.

**Solution**: Smart conflict detection and conditional configuration:

```python
# PelicanBuilder automatically detects conflicting content
has_index_content = any('slug: index' in file.read_text() 
                       for file in content_dir.glob('**/*.md'))

# Conditionally disable default blog index
pelican_config['INDEX_SAVE_AS'] = '' if has_index_content else 'index.html'
```

**Architecture Benefits**:
- **Zero Configuration**: Users don't need to know about this conflict
- **Automatic Detection**: System scans content directory for conflicts
- **Graceful Degradation**: Works whether custom index exists or not
- **Preserve Intent**: Custom index pages take precedence over default blog index

**Integration Points**:
- Content authoring: Users can freely create `content/index.md` with `slug: index`
- Build process: Automatic conflict resolution during PelicanBuilder.build()
- Testing: Comprehensive coverage for both conflict scenarios

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

## Unified Configuration Architecture

### Design Principles

The unified configuration system implements a centralized approach to configuration management with the following principles:

- **Schema Validation**: All configs validated against JSON Schema draft-07 specifications
- **Centralized Loading**: Single `JsonConfigLoader` class handles all configuration loading
- **Extraction Ready**: Galleria config designed for future standalone package use
- **Backward Compatible**: Graceful degradation when schema files are missing
- **Comprehensive Error Handling**: Detailed validation messages with field context

### Configuration Flow

```
Commands -> ConfigValidator -> JsonConfigLoader -> JSON Schema -> Config Files
    |                                                                    |
    v                                                                    v
Business Logic <- Validated Config Data <- Schema Validation <- Raw JSON
```

**Implementation Details:**
- Commands load configs through `JsonConfigLoader` with optional schema validation
- `ConfigValidator` provides comprehensive validation across all config types
- Schema files in `config/schema/` define validation rules for each config type
- Detailed error messages guide users to fix configuration issues

### Configuration Types

**Site Orchestration** (`config/site.json`):
- Output directory configuration
- CDN URL mappings for dual-bucket strategy
- Top-level orchestration settings

**Photo Organization** (`config/normpic.json`):
- Source and destination directories for photo organization
- Collection naming and symlink preferences
- Integration with NormPic external tool

**Gallery Generation** (`config/galleria.json`):
- Manifest path and output directory
- Thumbnail generation settings (size, quality, theme)
- Designed for extraction-ready galleria package

**Site Generation** (`config/pelican.json`):
- Theme and styling configuration  
- Site metadata (URL, author, title)
- Static site generation settings

### Schema Architecture

**Schema Location**: `config/schema/*.json`
**Schema Standard**: JSON Schema draft-07
**Validation Library**: `jsonschema` (optional dependency)

Each schema defines:
- Required vs optional fields
- Field types and formats (string, integer, URI, etc.)
- Value constraints (minimum/maximum, enums)
- Default values and examples

**Schema Design for Extraction**:
- Galleria schema contains no wedding-site-specific fields
- Generic configuration patterns suitable for any project
- Clear separation between site-specific and tool-specific configuration

### Shared Component System

The shared component system enables unified theme and asset management between Pelican and Galleria through template overrides and external template integration, preserving Galleria's extractability for future modularization.

#### Component Architecture

**Pelican Template Override System**:
- Uses `THEME_TEMPLATES_OVERRIDES` setting to replace default theme templates
- Override templates located in `themes/shared/templates/`
- Includes shared navigation, CSS, and page structure
- Eliminates duplicate navbars and inconsistent styling

**Galleria External Template Integration**:
- Uses `theme_path` configuration to access shared component directory
- Template loader searches shared templates alongside theme-specific templates
- Enables consistent navigation and styling with Galleria galleries
- Maintains plugin-based architecture for future extraction

**Shared Template Components**:
- `themes/shared/templates/base.html` - Main page structure with shared CSS
- `themes/shared/templates/shared/header.html` - Navigation component
- `themes/shared/static/css/shared.css` - Unified styling
- Template overrides for both systems using identical shared components

#### Integration Flow

```
Shared Components System
├── Template Override System
│   ├── Pelican: THEME_TEMPLATES_OVERRIDES → themes/shared/templates/
│   ├── Galleria: theme_path → themes/shared/
│   └── Shared templates: base.html, shared/header.html
├── CSS Integration
│   ├── themes/shared/static/css/shared.css → Unified styling
│   ├── Pelican build process → Copies to output/theme/css/
│   └── Galleria build process → References shared CSS
└── Navigation Consistency
    ├── shared/header.html → Same navigation component
    ├── Both systems include identical navbar HTML
    └── Eliminates duplicate navigation and styling inconsistencies
```

#### Architecture Benefits

**Template Override Integration**: Uses native Pelican template override system (`THEME_TEMPLATES_OVERRIDES`) and Galleria external template configuration (`theme_path`) without modifying core systems.

**Extraction Compatibility**: Galleria's shared template integration designed to support future extraction - no tight coupling with parent project.

**Navigation Consistency**: Both systems use identical shared navigation component, eliminating duplicate navbars and styling inconsistencies.

**Configuration-Driven**: Integration enabled through standard configuration settings, no code modifications required.

#### Future Considerations

**Version Pinning**: Asset manager currently uses latest versions - post-MVP enhancement will add config-based version pinning with integrity hashes.

**Dependency Injection**: Context adapters designed to support future Galleria extraction through dependency injection patterns.

**Plugin Integration**: System integrates with Galleria's plugin architecture and Pelican's template system without requiring core modifications.

### Error Handling Architecture

**Exception Hierarchy**:
```
ConfigError (base)
├── ConfigLoadError (file/parsing errors)
└── ConfigValidationError (schema violations)
```

**Error Context**:
- File path information for all errors
- Field path context for validation errors
- Original exception chaining for debugging
- User-friendly error messages for configuration fixes

### Testing Strategy

**Unit Tests**:
- Schema validation success/failure scenarios
- Error handling and exception types
- Configuration loading with various file states

**Integration Tests**:  
- ConfigValidator with actual schema files
- End-to-end configuration loading workflows
- Backward compatibility testing

**E2E Tests**:
- Complete command workflows using configuration system
- Invalid configuration handling across all commands
- Missing file scenarios and error reporting