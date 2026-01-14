# Release Documentation

This directory contains archived changelog entries organized by release version. As the main CHANGELOG.md grows, entries are moved here to keep the current changelog manageable.

## Organization

- **Current Development**: See [../CHANGELOG.md](../CHANGELOG.md) for recent changes
- **Released Versions**: Each version gets its own archived changelog file

## Release History

### Version 0.1.0 (MVP)
**File**: [0-1.md](0-1.md)
**Status**: In Development
**Focus**: Complete static site pipeline for personal website with photo galleries

**Core Pipeline**:
- 4-stage idempotent pipeline: validate → organize → build → deploy
- Cascading command architecture (each stage auto-calls predecessors)
- Build orchestrator pattern separating CLI from business logic

**Galleria Gallery Generator**:
- 5-stage plugin system: Provider → Processor → Transform → Template → CSS
- NormPic manifest integration for photo organization
- WebP thumbnail generation with caching
- Paginated gallery output with configurable page sizes
- Theme system with Jinja2 templates and external CSS

**Shared Component System**:
- Unified navbar and styling across Pelican and Galleria
- Template override mechanism for consistent look
- PicoCSS integration for responsive design

**Development Server**:
- HTTP proxy routing (/galleries/* → Galleria, else → Pelican)
- Serve command with automatic build cascade
- Development vs production URL context

**Deployment**:
- Bunny CDN integration with dual zone strategy (photos + site content)
- Relative URL generation with Edge Rules routing
- Configurable deploy credentials via environment variables

**Infrastructure**:
- JSON schema validation for all config files
- Comprehensive test suite (500+ tests) with TDD methodology
- Performance benchmarking with pagination optimization

### Future Releases
Additional release files will be added here as versions are completed and archived.