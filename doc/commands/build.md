# Build Command

## Overview

The `site build` command orchestrates the complete site generation pipeline, integrating photo organization, gallery generation, and static site creation into a unified output structure.

## Usage

```bash
# Basic usage
uv run site build

# Build automatically runs prerequisite commands
uv run site build  # → organize → validate (cascading)
```

## Pipeline Integration

### Automatic Cascading
1. **Calls organize**: Runs `site organize` (which calls `site validate`)
2. **Gallery generation**: Calls `galleria.generate()` Python module
3. **Site generation**: Calls `pelican.Pelican().run()` Python module
4. **Output integration**: Combines all outputs into unified structure

### Python Module Integration
- **Galleria**: Direct `import galleria` for gallery generation
- **Pelican**: Direct `import pelican` for site page generation  
- **Error handling**: Python exceptions provide better debugging than subprocess calls
- **Performance**: No subprocess overhead for external tool coordination

## Output Structure

After successful build completion:

```
output/
├── pics/           # Organized photos (from organize/NormPic)
│   └── full/       # Original photos with NormPic naming
├── galleries/      # Gallery HTML/CSS/thumbnails (from galleria)
│   └── wedding/    # Gallery pages, CSS, and WebP thumbnails
│       ├── page_1.html
│       ├── gallery.css
│       └── thumbnails/
├── about/          # Site pages (from pelican)
└── index.html      # Site root (from pelican)
```

## Idempotent Behavior

The build command skips work when output already exists:
- Checks for `output/galleries` and `output/index.html` 
- Displays "already built and up to date" message
- Trusts galleria and pelican internal change detection
- Always runs organize cascade for dependency validation

## Error Handling

### Organize Failures
- Build stops immediately if organize fails
- Displays "Organize failed - stopping build" message
- Returns non-zero exit code

### Galleria Failures  
- Handles both exceptions and `success=False` results
- Displays specific error messages from galleria
- Returns non-zero exit code

### Pelican Failures
- Catches exceptions from `pelican.Pelican().run()`
- Displays "Pelican generation failed" with error details
- Returns non-zero exit code

## Configuration Requirements

Build command requires existing configuration files:
- `config/normpic.json` - Photo organization settings
- `config/galleria.json` - Gallery generation configuration  
- `config/pelican.json` - Site generation settings (planned)

## Progress Reporting

The command provides user feedback throughout execution:
```
Building site...
Running organization...
✓ Photos are already organized, skipping...
Generating galleries with Galleria...
✓ Galleria generation completed successfully!
Generating site pages with Pelican...
✓ Pelican generation completed successfully!
Build completed successfully!
```

## Implementation

**Location**: `cli/commands/build.py`
**Pattern**: Follows existing `organize.py` command structure
**Dependencies**: Click framework, galleria module, pelican module
**Testing**: 8 unit tests + comprehensive E2E test coverage