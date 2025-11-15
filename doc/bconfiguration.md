# Configuration Guide

## Overview

The project uses JSON configuration files for each component, with a master orchestration config.

## Site Configuration

### config/site.json
```json
{
  "collections": [
    "wedding",
    "christmas-2024"
  ],
  "normpic_path": "/opt/normpic",
  "output_dir": "output",
  "pelican_config": "pelican/pelicanconf.py"
}
```

### Fields
- `collections`: List of photo collections to process
- `normpic_path`: Path to NormPic installation
- `output_dir`: Where to generate the site
- `pelican_config`: Pelican configuration file

## NormPic Configuration

### config/normpic/wedding.json
```json
{
  "collection_name": "wedding",
  "source_dir": "/home/user/Photos/wedding/original",
  "dest_dir": "/home/user/Photos/wedding/organized",
  "collection_description": "Our wedding day - August 9, 2025"
}
```

### Fields
- `collection_name`: Identifier for the collection
- `source_dir`: Original photo location
- `dest_dir`: Where to create organized photos
- `collection_description`: Human-readable description

## Galleria Configuration

### config/galleria/wedding.json
```json
{
  "manifest_path": "/home/user/Photos/wedding/organized/manifest.json",
  "output_dir": "output/galleries/wedding",
  "thumbnail_size": 400,
  "photos_per_page": 60,
  "theme": "minimal",
  "quality": 85,
  "format": "webp"
}
```

### Fields
- `manifest_path`: Path to NormPic manifest
- `output_dir`: Where to generate gallery
- `thumbnail_size`: Square thumbnail dimension
- `photos_per_page`: Photos per HTML page
- `theme`: Gallery theme name
- `quality`: Image compression quality (1-100)
- `format`: Output image format

## Pelican Configuration

### pelican/pelicanconf.py
```python
AUTHOR = 'Marco & Chrissy'
SITENAME = 'Marco & Chrissy'
SITEURL = 'https://marco-chrissy.com'

PATH = 'content'
OUTPUT_PATH = 'output'

TIMEZONE = 'Europe/Stockholm'
DEFAULT_LANG = 'en'

# Theme
THEME = 'pelican/theme/simple'

# Pagination
DEFAULT_PAGINATION = False

# Static files
STATIC_PATHS = ['images', 'extra']

# URL structure
ARTICLE_URL = '{date:%Y}/{slug}/'
PAGE_URL = '{slug}/'
```

## Environment Variables

### Required Variables
```bash
# Bunny CDN
export BUNNY_API_KEY="your-api-key"
export BUNNY_STORAGE_ZONE="your-zone"

# Paths (optional, override config)
export NORMPIC_PATH="/opt/normpic"
export OUTPUT_DIR="/var/www/site"
```

## Configuration Precedence

1. Command-line arguments (highest)
2. Environment variables
3. Configuration files
4. Default values (lowest)

## Validation

### Check Configuration
```bash
# Validate all configs
uv run python orchestrator/validate_config.py

# Test specific config
uv run python orchestrator/validate_config.py config/galleria/wedding.json
```

### Common Issues

- Paths must be absolute or relative to project root
- JSON must be valid (use jsonlint)
- Required fields cannot be null
- Numeric values must be within valid ranges