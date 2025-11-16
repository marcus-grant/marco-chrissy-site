# Galleria Commands

## Pipeline Commands

Galleria has a simpler command structure since it has one focused purpose:

### 1. validate
**Purpose**: Validate galleria-specific configs and dependencies  
**Calls**: Nothing (base command)

**Responsibilities**:
- Validate galleria config JSON
- Check manifest file exists and is readable
- Verify image processing dependencies (Pillow, etc.)
- Check output directory is writable

### 2. generate
**Purpose**: Generate gallery from manifest  
**Calls**: `validate` only

**Responsibilities**:
- Parse NormPic manifest
- Generate optimized thumbnails (WebP, 400x400)
- Render HTML pages with pagination (60 photos/page)
- Generate CSS stylesheets
- Copy theme assets

## Development Commands

### serve
**Purpose**: Local development server for gallery  
**Calls**: `generate` only (which calls `validate`)

**Responsibilities**:
- Generate fresh gallery
- Serve locally for development
- Enable plugin development workflow

### clean
**Purpose**: Clean galleria output  
**Calls**: Nothing

**Responsibilities**:
- Remove generated gallery files
- Clear thumbnail caches

### debug
**Purpose**: Verbose generation for troubleshooting  
**Calls**: `generate` only

**Responsibilities**:
- Generate gallery with verbose output
- Log detailed processing information
- Help diagnose issues

## Usage Examples

```bash
# Generate gallery from config
uv run python -m galleria generate --config config/galleria/wedding.json

# Serve for development
uv run python -m galleria serve --config config/galleria/wedding.json

# Debug generation issues
uv run python -m galleria debug --config config/galleria/wedding.json --verbose
```