# Galleria Documentation

## Overview

Galleria is a static gallery generator designed to work with NormPic manifests. It generates paginated HTML galleries with optimized thumbnails.

## Documentation Index

- [TODO](TODO.md) - Development tasks and roadmap
- [Architecture](architecture.md) - Module organization and design
- [Configuration](configuration.md) - Configuration file reference
- [Themes](themes.md) - Creating and customizing themes
- [API](api.md) - Module interfaces and usage

## Quick Start
```bash
# From parent project root
uv sync

# Generate a gallery
uv run python -m galleria --config config/galleria/wedding.json
```

## Module Structure
```
galleria/
\u251c\u2500\u2500 generator/      # Orchestration
\u251c\u2500\u2500 processor/      # Image processing
\u251c\u2500\u2500 renderer/       # HTML/CSS generation
\u251c\u2500\u2500 reader/         # Manifest parsing
\u2514\u2500\u2500 themes/         # Gallery themes
```

## Basic Usage

1. **Configure**: Create a JSON config pointing to a NormPic manifest
2. **Run**: Execute Galleria with the config
3. **Output**: Find generated gallery in output directory

## Example Config
```json
{
  "manifest_path": "/home/user/Photos/wedding/manifest.json",
  "output_dir": "output/galleries/wedding",
  "thumbnail_size": 400,
  "photos_per_page": 60,
  "theme": "minimal",
  "quality": 85
}
```

## Testing
```bash
# Run all tests
uv run pytest galleria/

# Run specific module tests
uv run pytest galleria/test/test_processor.py

# Run with coverage
uv run pytest --cov=galleria galleria/test/
```

## Development Workflow

1. Write tests first (TDD)
2. Implement functionality
3. Update documentation
4. Run tests with `uv run pytest`
5. Check code quality with `uv run ruff check`