# Configuration Guide

## Overview

The unified configuration system uses JSON files with schema validation to configure all components of the site generation pipeline.

## Configuration Files

### Site Orchestration - `config/site.json`

Controls overall site generation behavior:

```json
{
  "output_dir": "output",
  "cdn": {
    "photos": "https://photos.example.com",
    "site": "https://site.example.com"
  }
}
```

**Required fields:**
- `output_dir`: Base directory for all generated content

**Optional fields:**
- `cdn.photos`: CDN URL for photo content
- `cdn.site`: CDN URL for site content

### Photo Organization - `config/normpic.json`

Configures NormPic photo organization:

```json
{
  "source_dir": "~/Pictures/wedding/full",
  "dest_dir": "output/pics/full", 
  "collection_name": "wedding",
  "create_symlinks": true
}
```

**Required fields:**
- `source_dir`: Source directory containing photos
- `dest_dir`: Destination directory for organized photos
- `collection_name`: Name of the photo collection

**Optional fields:**
- `create_symlinks`: Whether to create symlinks (default: false)

### Gallery Generation - `config/galleria.json`

Configures Galleria gallery generator:

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

**Required fields:**
- `manifest_path`: Path to NormPic manifest file
- `output_dir`: Output directory for generated galleries

**Optional fields:**
- `thumbnail_size`: Thumbnail size in pixels (default: 400)
- `photos_per_page`: Photos per gallery page (default: 60)  
- `theme`: Gallery theme name (default: "minimal")
- `quality`: JPEG quality 1-100 (default: 85)

### Site Generation - `config/pelican.json`

Configures Pelican static site generator:

```json
{
  "theme": "minimal",
  "site_url": "https://example.com",
  "author": "Author Name", 
  "sitename": "Site Title"
}
```

**Required fields:**
- `theme`: Theme name for site generation
- `site_url`: Base URL for the site
- `author`: Site author name
- `sitename`: Site title/name

**Optional fields:**
- `timezone`: Site timezone (default: "UTC")
- `default_lang`: Default language code (default: "en")

## Schema Validation

All configuration files are validated against JSON Schema files in `config/schema/`:

- `config/schema/site.json` - Site orchestration schema
- `config/schema/normpic.json` - NormPic configuration schema  
- `config/schema/pelican.json` - Pelican configuration schema
- `config/schema/galleria.json` - Galleria configuration schema

Invalid configurations will show detailed validation error messages indicating which fields are missing or incorrect.

## Usage

Configuration files are automatically loaded by commands:

- `site validate` - Validates all config files exist and have valid content
- `site organize` - Uses normpic.json for photo organization
- `site build` - Uses site.json and galleria.json for site generation
- `site deploy` - Uses site.json for deployment configuration

## Extraction Readiness

The galleria configuration is designed to be extraction-ready for future standalone package use. The schema contains no wedding-site-specific fields and follows generic configuration patterns.