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

## Planned Commands (Future)

### validate
**Purpose**: Validate configuration and dependencies without generation
**Status**: ⏳ Not implemented

### serve
**Purpose**: Local development server with hot reload
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
```

## Configuration File Format

The configuration file should contain:

```json
{
  "input": {
    "manifest_path": "path/to/normpic/manifest.json"
  },
  "output": {
    "directory": "path/to/output"
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
        "quality": 90
      }
    },
    "transform": {
      "plugin": "basic-pagination",
      "config": {
        "page_size": 2
      }
    },
    "template": {
      "plugin": "basic-template",
      "config": {
        "theme": "minimal",
        "layout": "grid"
      }
    },
    "css": {
      "plugin": "basic-css",
      "config": {
        "theme": "light",
        "responsive": true
      }
    }
  }
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