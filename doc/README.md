# Marco & Chrissy's Website Documentation

## Overview

This is the main documentation index for our personal website project.
The site orchestrates multiple tools to generate static content deployed to Bunny CDN.

**Current Status:** Galleria (gallery generator) is at MVP. Phase 2 focuses on building the site orchestration system with a 4-stage idempotent pipeline and plugin-based Pelican integration. See [Architecture](architecture.md) for detailed system design.

## Documentation Structure

### Project Documentation

- [TODO](TODO.md) - Project roadmap and task tracking
- [E2E Workflow Guide](workflow.md) - Complete end-to-end usage guide
- [Architecture](architecture.md) - System design and integration patterns
- [Provider Architecture](provider-architecture.md) - Plugin-based photo collection providers
- [Configuration Guide](bconfiguration.md) - Config file formats and examples
- [Commands](commands/) - Command system and workflow documentation
- [Modules](modules/) - Module organization and structure

### Component Documentation

- [Galleria Documentation](../galleria/doc/README.md) - Gallery generator

## Quick Links

- **NormPic**: Photo organization tool (external dependency)
- **Pelican**: Static site generator framework
- **Bunny CDN**: Content delivery network

## Development Workflow

**Planned 4-Stage Pipeline:**
1. **Validate** - Pre-flight checks (configs, dependencies, permissions)
2. **Organize** - Photo organization with NormPic
3. **Build** - Gallery generation (Galleria) + site pages (Pelican)
4. **Deploy** - Upload to Bunny CDN (dual bucket strategy)

Each stage is idempotent and automatically calls predecessors if needed. See [Workflow Guide](workflow.md) for detailed usage and [Commands](commands/) for specific command documentation.

