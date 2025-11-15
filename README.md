# Marco & Chrissy's Website

A static site generator orchestrating multiple tools to create our personal website featuring photo galleries, updates, and shared content.

## Overview

This project combines:
- **NormPic** - Photo organization and manifest generation
- **Galleria** - Static gallery page generation
- **Pelican** - Static site generation for content pages
- **Orchestration** - Build and deployment automation

## Documentation

- [Project Documentation](doc/README.md) - Main documentation index
- [Galleria Documentation](galleria/doc/README.md) - Gallery generator documentation

## Setup
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run build
uv run python build.py

# Deploy to CDN
uv run python deploy.py
```

## Development
```bash
# Run with uv
uv run python -m galleria --config config/galleria/wedding.json

# Run tests
uv run pytest
```

## Project Structure

- `galleria/` - Gallery generator (extractable module)
- `config/` - Configuration for all tools
- `content/` - Pelican content pages
- `output/` - Generated static site
- `orchestrator/` - Build orchestration
- `deployer/` - Deployment logic

## License

Private repository - All rights reserved