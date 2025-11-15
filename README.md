# Marco & Chrissy's Website

A static site generator orchestrating multiple tools to
create our personal website featuring photo galleries, updates, and shared content.

## Overview

This project combines:

- **NormPic** - Photo organization and manifest generation
- **Galleria** - Static gallery page generation
- **Pelican** - Static site generation for content pages
- **Orchestration** - Build and deployment automation

## Documentation

- [Project Documentation](doc/README.md) - Main documentation index
- [Galleria Documentation](galleria/doc/README.md) - Gallery generator documentation

## Quick Start

```bash
# Install dependencies
uv sync

# Build site
python build.py

# Deploy to CDN
python deploy.py
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

