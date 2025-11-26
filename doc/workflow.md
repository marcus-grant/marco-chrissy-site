# Site Development Workflow Guide

## Overview

This guide covers the complete development workflow for the marco-chrissy-site project, including our nested TDD approach and the site command pipeline.

## Nested TDD Workflow

### Outer Cycle (E2E/Integration Tests)

E2E tests drive our development workflow by surfacing missing or broken functionality:

1. **Write E2E test** - Create test for desired functionality 
2. **Run test** - Should fail, revealing what's missing
3. **Mark with `@pytest.mark.skip`** - Keep test suite in passing state
4. **Move to inner cycle** - Write unit tests for missing pieces

### Inner Cycle (Unit TDD)

Unit tests implement the specific functionality identified by E2E tests:

1. **Write unit test** - For specific missing functionality 
2. **Red** - Ensure test fails as expected
3. **Green** - Implement minimal code to make test pass
4. **Refactor** - Improve solution while keeping test green
5. **Commit** - Small change (typically <300 LOC)
6. **Repeat** - Continue until E2E test can pass

### Test Management Pattern

```python
# E2E test - initially skipped
@pytest.mark.skip(reason="Deploy command functionality not yet implemented")
def test_deploy_calls_build_automatically(self):
    """Test that deploy automatically calls build if needed."""
    # This test drives development
    pass

# Unit tests - implement pieces needed for E2E test
def test_deploy_command_calls_build_module(self):
    """Test specific unit of functionality."""
    # Implementation happens here
    pass
```

### Workflow Benefits

- **Clear direction** - E2E tests show what needs building
- **Small commits** - Each unit test leads to focused changes
- **Always passing** - Test suite stays green between features
- **Continuous progress** - Can see advancement by unskipping tests

## Site Command Pipeline

### 4-Stage Idempotent Pipeline

```bash
site validate → site organize → site build → site deploy
```

Each command automatically calls predecessors if needed, but skips work already done.

### Example Usage

```bash
# Run full pipeline
uv run site deploy

# Run specific stage  
uv run site validate

# Each stage checks dependencies automatically
uv run site build  # Calls organize and validate if needed

# Build creates complete site with galleries and pages
uv run site build  # organize → galleria → pelican integration
```

### Build Command Integration

The `uv run site build` command orchestrates the complete site generation:

1. **Automatic cascade**: Calls `organize` (which calls `validate`)
2. **Gallery generation**: Uses galleria Python module to create galleries
3. **Site generation**: Uses pelican Python module to create site pages  
4. **Output integration**: Combines all outputs into unified structure

**Expected output after build:**
```
output/
├── pics/           # Organized photos (from organize/NormPic)
├── galleries/      # Gallery HTML/CSS/thumbnails (from galleria)  
│   └── wedding/    # Gallery pages: page_1.html, etc.
├── about/          # Site pages (from pelican)
└── index.html      # Site root (from pelican)

## Workflow Steps

### 1. Photo Organization with NormPic

Before using Galleria, organize your photos using NormPic:

```bash
# Install NormPic (external dependency)
pip install normpic

# Organize photos and generate manifest
normpic organize /path/to/photos --output /path/to/organized
```

This creates a `manifest.json` file that Galleria uses as input.

### 2. Galleria Configuration

Create a configuration file for your gallery:

**config/wedding-gallery.json:**
```json
{
  "input": {
    "manifest_path": "/path/to/organized/manifest.json"
  },
  "output": {
    "directory": "/path/to/gallery/output"
  },
  "pipeline": {
    "provider": {
      "plugin": "normpic-provider",
      "config": {}
    },
    "processor": {
      "plugin": "thumbnail-processor",
      "config": {
        "thumbnail_size": 400,
        "quality": 90,
        "use_cache": true,
        "output_format": "webp"
      }
    },
    "transform": {
      "plugin": "basic-pagination",
      "config": {
        "page_size": 12
      }
    },
    "template": {
      "plugin": "basic-template",
      "config": {
        "theme": "elegant",
        "layout": "grid",
        "title": "Wedding Gallery"
      }
    },
    "css": {
      "plugin": "basic-css",
      "config": {
        "theme": "light",
        "responsive": true,
        "custom_colors": {
          "primary": "#2c3e50",
          "accent": "#e74c3c"
        }
      }
    }
  }
}
```

### 3. Gallery Generation

Generate the complete gallery:

```bash
# Basic generation
python -m galleria generate --config config/wedding-gallery.json

# With verbose output and custom output directory
python -m galleria generate \
  --config config/wedding-gallery.json \
  --output /custom/output/path \
  --verbose
```

### 4. Generated Output Structure

The generate command creates a complete static gallery:

```
output/
├── page_1.html              # Gallery pages with thumbnails
├── page_2.html              # Additional pages (if needed)
├── page_N.html              # etc.
├── gallery.css              # Main gallery styles
├── theme-elegant.css        # Theme-specific styles  
├── responsive.css           # Mobile-responsive styles
└── thumbnails/              # Generated WebP thumbnails
    ├── IMG_001.webp
    ├── IMG_002.webp
    └── ...
```

### 5. Development Workflow with Serve Command

For iterative development and testing, use the development server:

```bash
# Start development server with hot reload
python -m galleria serve --config config/wedding-gallery.json --verbose

# Server starts at http://127.0.0.1:8000
# Opens generated gallery in browser
# Automatically watches for file changes
```

**Development Server Features:**
- **Automatic Generation**: Runs `generate` command before serving
- **Hot Reload**: Monitors config and manifest files for changes  
- **File Serving**: Serves HTML, CSS, and thumbnails with proper MIME types
- **Live Updates**: Regenerates gallery when watched files change
- **Verbose Logging**: Detailed progress reporting during generation and serving

**Development Workflow:**
1. Start development server: `galleria serve --config config.json --verbose`
2. Open http://127.0.0.1:8000 in browser
3. Edit gallery configuration (theme, layout, pagination)
4. Save config file - gallery automatically regenerates
5. Refresh browser to see changes
6. Iterate on design and configuration

**Serve Command Options:**
```bash
# Custom port (useful when 8000 is busy)
python -m galleria serve --config config.json --port 3000

# Serve without file watching (for testing)
python -m galleria serve --config config.json --no-watch

# Serve existing gallery without regeneration
python -m galleria serve --config config.json --no-generate

# Bind to all interfaces (for network access)
python -m galleria serve --config config.json --host 0.0.0.0
```

### 6. Integration with Static Site Generators

#### Pelican Integration

Include the generated gallery in your Pelican site:

**pelicanconf.py:**
```python
STATIC_PATHS = [
    'galleries',  # Gallery output directory
    'images',
    'extra'
]

EXTRA_PATH_METADATA = {
    'galleries/wedding/page_1.html': {'path': 'wedding/index.html'},
    'galleries/wedding/gallery.css': {'path': 'wedding/gallery.css'},
    # etc.
}
```

#### Manual Integration

Copy gallery files to your web server:

```bash
# Copy to web root
cp -r output/* /var/www/html/wedding-gallery/

# Or sync with rsync
rsync -av output/ user@server:/var/www/html/wedding-gallery/
```

## E2E Testing Approach

Galleria uses comprehensive E2E testing to ensure the complete workflow functions correctly.

### Test Architecture

The E2E test suite validates the entire pipeline:

1. **CLI Integration Tests**
   - Test complete `generate` command execution
   - Validate argument parsing and configuration loading
   - Test error handling for missing files and invalid configs

2. **Plugin Pipeline Tests**  
   - Test complete 5-stage pipeline execution
   - Validate data flow between plugins
   - Test real image processing with actual JPEG files

3. **File System Tests**
   - Test actual file generation (HTML, CSS, thumbnails)
   - Validate output directory structure
   - Test with realistic photo collections

### Running E2E Tests

```bash
# Run complete test suite
uv run pytest

# Run only E2E tests
uv run pytest test/galleria/test_pipeline_basic.py -v

# Run CLI-specific E2E tests
uv run pytest test/galleria/test_cli.py -v
```

### Test Coverage

Current test metrics:
- **239 tests passing** (0 skipped)
- **Complete pipeline coverage** (Provider → Processor → Transform → Template → CSS)
- **Real image processing** (actual JPEG files, not mocks)
- **CLI validation** (argument parsing, config loading, error handling)

## Production Deployment

### Performance Considerations

1. **Thumbnail Caching**
   - Enable `use_cache: true` in processor config
   - Thumbnails are cached to avoid regeneration
   - Cache invalidation based on source file modification time

2. **Large Collections**
   - Use pagination with appropriate page sizes (8-20 photos per page)
   - Consider Smart Pagination for balanced page sizes
   - Monitor memory usage during processing

3. **Output Optimization**
   - WebP format provides excellent compression
   - Responsive CSS reduces bandwidth on mobile
   - Lazy loading can be added with custom templates

### Monitoring and Debugging

1. **Verbose Mode**
   ```bash
   python -m galleria generate --config config.json --verbose
   ```

2. **Error Handling**
   - Configuration validation with clear error messages
   - Graceful handling of missing or corrupted photos
   - Plugin-specific error reporting with context

3. **Log Output**
   - Progress reporting during pipeline execution
   - File generation confirmation
   - Performance metrics (thumbnail count, processing time)

## Common Use Cases

### Wedding Photography

```json
{
  "pipeline": {
    "processor": {
      "config": {
        "thumbnail_size": 600,
        "quality": 95
      }
    },
    "transform": {
      "config": {
        "page_size": 8
      }
    },
    "template": {
      "config": {
        "theme": "elegant",
        "title": "Sarah & Mike's Wedding"
      }
    }
  }
}
```

### Portfolio Website

```json
{
  "pipeline": {
    "processor": {
      "config": {
        "thumbnail_size": 800,
        "quality": 85
      }
    },
    "transform": {
      "config": {
        "page_size": 15
      }
    },
    "template": {
      "config": {
        "theme": "modern",
        "layout": "grid",
        "title": "Photography Portfolio"
      }
    }
  }
}
```

### Event Documentation

```json
{
  "pipeline": {
    "processor": {
      "config": {
        "thumbnail_size": 300,
        "quality": 80
      }
    },
    "transform": {
      "config": {
        "page_size": 20
      }
    },
    "template": {
      "config": {
        "theme": "minimal",
        "title": "Company Retreat 2025"
      }
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **Configuration Errors**
   ```
   Configuration error: Manifest file not found: /path/to/manifest.json
   ```
   - Solution: Verify manifest path exists and is accessible

2. **Image Processing Failures**
   ```
   Plugin execution error: Failed to process image: corrupted.jpg
   ```
   - Solution: Check image file integrity, remove corrupted files

3. **Permission Errors**
   ```
   Plugin execution error: Permission denied: /output/directory
   ```
   - Solution: Ensure write permissions for output directory

### Debug Mode

Enable verbose output for detailed debugging:

```bash
python -m galleria generate --config config.json --verbose
```

This provides:
- Configuration loading details
- Plugin execution progress
- File generation confirmation  
- Error context and stack traces

## Future Enhancements

Planned workflow improvements:

1. **serve Command**: Local development server with hot reload
2. **validate Command**: Configuration and dependency validation
3. **watch Mode**: Automatic regeneration on file changes
4. **Incremental Processing**: Only process changed photos
5. **Cloud Integration**: Direct upload to CDN/cloud storage

See the [TODO](TODO.md) for complete roadmap and implementation timeline.

## Unified Configuration System Workflow

### Configuration Setup

The site uses a unified configuration system with schema validation. Set up your configuration files:

#### 1. Site Configuration - `config/site.json`
```json
{
  "output_dir": "output",
  "cdn": {
    "photos": "https://photos.cdn.example.com",
    "site": "https://site.cdn.example.com"
  }
}
```

#### 2. Photo Organization - `config/normpic.json`
```json
{
  "source_dir": "~/Pictures/wedding/full",
  "dest_dir": "output/pics/full",
  "collection_name": "wedding",
  "create_symlinks": true
}
```

#### 3. Gallery Generation - `config/galleria.json`
```json
{
  "manifest_path": "output/pics/full/manifest.json",
  "output_dir": "output/galleries",
  "thumbnail_size": 400,
  "photos_per_page": 60,
  "theme": "minimal",
  "quality": 85
}
```

#### 4. Site Generation - `config/pelican.json`
```json
{
  "theme": "minimal",
  "site_url": "https://example.com",
  "author": "Your Name",
  "sitename": "Your Site Title"
}
```

### Site Command Pipeline

Use the unified `site` command for the complete workflow:

```bash
# Validate all configurations
uv run site validate

# Organize photos with NormPic
uv run site organize

# Build site and galleries  
uv run site build

# Deploy to CDN (planned)
uv run site deploy
```

#### Command Cascading

Commands automatically call their prerequisites:
- `site deploy` → calls `site build` → calls `site organize` → calls `site validate`
- Commands skip work if output is already up-to-date (idempotent behavior)
- Each command loads and validates its required configurations

### Configuration Validation

#### Schema Validation
All configs are validated against JSON schemas in `config/schema/`:
- Detailed error messages for missing or invalid fields
- Type checking (string, integer, URI, etc.)
- Required vs optional field validation

```bash
# Check all config files
uv run site validate

# Example validation error:
# Config validation error in config/galleria.json: Field 'manifest_path': 'missing_field' is a required property
```

#### Error Handling
- **Missing files**: Clear messages about which config files are missing
- **Invalid JSON**: Parsing errors with line/column information  
- **Schema violations**: Field-specific validation errors with context
- **File permissions**: Access errors with suggested fixes

### Development Workflow

#### 1. Initial Setup
```bash
# Set up project structure
mkdir -p config/schema
mkdir -p output/{pics,galleries}

# Create configuration files (see examples above)
# Schemas are provided in config/schema/
```

#### 2. Photo Organization
```bash
# Organize photos and generate manifest
uv run site organize

# This runs NormPic with config from normpic.json
# Creates organized photos and manifest.json
```

#### 3. Site Generation
```bash
# Build complete site with galleries
uv run site build

# This runs:
# 1. Galleria CLI with galleria.json config
# 2. Pelican with pelican.json config
# Uses output paths from site.json
```

#### 4. Configuration Changes
```bash
# After changing configs, validate first
uv run site validate

# Then rebuild (idempotent - only regenerates if needed)
uv run site build
```

### Config File Examples

#### Wedding Photography Site
**`config/galleria.json`:**
```json
{
  "manifest_path": "output/pics/wedding/manifest.json",
  "output_dir": "output/galleries/wedding",
  "thumbnail_size": 600,
  "photos_per_page": 48,
  "theme": "elegant",
  "quality": 95
}
```

#### Portfolio Website
**`config/galleria.json`:**
```json
{
  "manifest_path": "output/pics/portfolio/manifest.json", 
  "output_dir": "output/galleries/portfolio",
  "thumbnail_size": 800,
  "photos_per_page": 24,
  "theme": "modern",
  "quality": 85
}
```

#### Event Documentation
**`config/galleria.json`:**
```json
{
  "manifest_path": "output/pics/event/manifest.json",
  "output_dir": "output/galleries/event", 
  "thumbnail_size": 300,
  "photos_per_page": 80,
  "theme": "minimal",
  "quality": 80
}
```

### Error Troubleshooting

#### Configuration Validation Errors
```bash
# Run validation to see specific errors
uv run site validate

# Common fixes:
# 1. Check required fields in schema files
# 2. Verify file paths exist
# 3. Check JSON syntax
# 4. Ensure proper field types (string vs integer)
```

#### Command Failures
```bash
# Organize command fails
uv run site organize --help

# Build command fails - check individual configs
uv run site validate
```

### Integration Benefits

- **Schema Validation**: Catch configuration errors early with detailed messages
- **Unified Loading**: Single JsonConfigLoader handles all config types
- **Extraction Ready**: Galleria config works as standalone package
- **Command Integration**: All commands use validated configurations
- **Error Context**: Clear error messages guide configuration fixes

For complete configuration reference, see [Configuration Guide](configuration.md).