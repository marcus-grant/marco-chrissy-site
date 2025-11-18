# Module Organization

## Overview

This project follows functional module organization with clear separation of concerns. Each module has a specific purpose and well-defined boundaries.

## Module Documentation

- [Organization Patterns](patterns.md) - Rules and anti-patterns for module structure
- [Site Project Structure](site-structure.md) - Main site project modules
- [Galleria Structure](galleria-structure.md) - Gallery generator overview
- [Galleria Modules](galleria/) - Detailed Galleria module documentation

## Key Principles

### Functional Organization
- Modules organized by specific function, not generic categories
- Each directory represents a clear responsibility
- Avoid catch-all patterns like 'core' or 'utils'

### Separation of Concerns
- Site project: orchestrates external tools (NormPic, Galleria, Pelican)
- Galleria: focused on gallery generation from manifests
- Clear boundaries between modules

### Future Extraction
- Galleria designed for eventual extraction to separate repository
- Loose coupling between site project and galleria
- Self-contained module interfaces