# Galleria Commands

## Implemented Commands

Galleria currently implements a focused CLI interface centered around the `generate` command:

### generate
**Purpose**: Generate complete gallery from manifest using plugin pipeline  
**Status**: ✅ Fully implemented

**Options**:
- `--config, -c`: Path to galleria configuration file (required)
- `--output, -o`: Output directory override (optional)
- `--verbose, -v`: Enable detailed progress reporting (optional)

**Responsibilities**:
- Load and validate galleria configuration JSON
- Validate manifest file exists and is accessible
- Execute complete plugin pipeline:
  1. **Provider**: Load NormPic manifest data
  2. **Processor**: Generate optimized WebP thumbnails (configurable size/quality)
  3. **Transform**: Apply pagination (configurable page size)
  4. **Template**: Generate HTML pages with navigation
  5. **CSS**: Generate responsive stylesheets
- Write all generated files (HTML, CSS, thumbnails) to output directory
- Provide comprehensive error handling and progress reporting

### serve
**Purpose**: Development server with automatic generation and hot reload  
**Status**: ✅ Fully implemented

**Options**:
- `--config, -c`: Path to galleria configuration file (required)
- `--port, -p`: Port number for development server (default: 8000)
- `--host, -h`: Host address to bind server (default: 127.0.0.1)
- `--no-generate`: Skip gallery generation phase (serve existing files only)
- `--no-watch`: Disable file watching and hot reload functionality
- `--verbose, -v`: Enable detailed progress reporting (optional)

**Responsibilities**:
- Load and validate galleria configuration JSON
- Execute complete plugin pipeline (unless `--no-generate` is specified):
  1. **Provider**: Load NormPic manifest data
  2. **Processor**: Generate optimized WebP thumbnails
  3. **Transform**: Apply pagination
  4. **Template**: Generate HTML pages with navigation
  5. **CSS**: Generate responsive stylesheets
- Start local HTTP development server on specified port
- Serve generated gallery files with proper MIME types
- Monitor configuration and manifest files for changes (hot reload)
- Automatically regenerate gallery when watched files change
- Provide comprehensive error handling and verbose logging

**Hot Reload Functionality**:
- Watches configuration file and manifest file for changes
- Automatically triggers gallery regeneration when files are modified
- Serves updated content without requiring server restart
- Can be disabled with `--no-watch` flag for production-like testing

## Planned Commands (Future)

### validate
**Purpose**: Validate configuration and dependencies without generation
**Status**: ⏳ Not implemented

### clean
**Purpose**: Clean output and cache files
**Status**: ⏳ Not implemented

## Usage Examples

```bash
# Basic gallery generation
python -m galleria generate --config config/galleria/wedding.json

# Generate with output override
python -m galleria generate --config config/galleria/wedding.json --output /custom/output/path

# Generate with verbose logging
python -m galleria generate --config config/galleria/wedding.json --verbose

# Full example with all options
python -m galleria generate \
  --config config/galleria/wedding.json \
  --output /path/to/gallery/output \
  --verbose

# Development server commands
# Basic development server (generates gallery then serves on port 8000)
python -m galleria serve --config config/galleria/wedding.json

# Development server with custom port
python -m galleria serve --config config/galleria/wedding.json --port 3000

# Development server with verbose logging and hot reload
python -m galleria serve --config config/galleria/wedding.json --verbose

# Serve existing gallery without regeneration
python -m galleria serve --config config/galleria/wedding.json --no-generate

# Development server without file watching (for testing)
python -m galleria serve --config config/galleria/wedding.json --no-watch

# Full development server example with all options
python -m galleria serve \
  --config config/galleria/wedding.json \
  --port 3000 \
  --host 0.0.0.0 \
  --verbose

# Development workflow example
python -m galleria serve --config config/galleria/wedding.json --verbose
# Server starts at http://127.0.0.1:8000
# Edit config/galleria/wedding.json or manifest.json
# Gallery automatically regenerates and updates in browser
```

## Configuration File Format

The configuration file uses a flat format for simplicity:

```json
{
  "manifest_path": "path/to/normpic/manifest.json",
  "output_dir": "path/to/output",
  "thumbnail_size": 400,
  "quality": 90,
  "page_size": 20,
  "theme": "minimal",
  "layout": "grid"
}
```

## Output Structure

The generate command creates:

```
output/
├── page_1.html          # First page of gallery
├── page_2.html          # Additional pages (if pagination needed)
├── gallery.css          # Main gallery styles
├── theme-light.css      # Theme-specific styles
├── responsive.css       # Responsive design styles
└── thumbnails/          # Generated thumbnail images
    ├── photo_001.webp
    ├── photo_002.webp
    └── ...
```