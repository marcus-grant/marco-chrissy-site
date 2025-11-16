# Site Project Module Structure

## Overview

The main site project orchestrates external tools and manages the overall site building workflow.

## Module Structure

```
marco-chrissy-site/
├── build/              # Build workflow orchestration
├── validation/         # Config and dependency validation
├── deployment/         # CDN deployment management
├── configuration/      # Site-wide configuration management
├── galleria/          # Gallery generator (temporary residence)
└── content/           # Pelican content pages
```

## Module Responsibilities

### build/
**Purpose**: Orchestrates the site building workflow

**Responsibilities**:
- Coordinate NormPic → Galleria → Pelican workflow
- Manage build order and dependencies
- Handle build errors and reporting
- Integrate outputs from different tools

**Interface**:
- Called by `build` command
- Calls external tools via subprocess
- Returns build status and artifacts

### validation/
**Purpose**: Validates all configurations and dependencies

**Responsibilities**:
- Validate JSON config files (schema and content)
- Check file system paths and permissions
- Verify external tool availability (NormPic)
- Validate environment variables for deployment

**Interface**:
- Called by `validate` command (and cascaded by others)
- Returns validation results and error details
- Fails fast on critical issues

### deployment/
**Purpose**: Manages CDN deployment

**Responsibilities**:
- Upload files to Bunny CDN
- Set appropriate cache headers
- Validate deployment success
- Handle deployment rollback (future)

**Interface**:
- Called by `deploy` command
- Uses environment variables for credentials (never reads directly)
- Returns deployment status

### configuration/
**Purpose**: Manages site-wide configuration

**Responsibilities**:
- Load and parse site.json
- Provide configuration access to other modules
- Handle configuration inheritance and overrides
- Validate configuration relationships

**Interface**:
- Used by all other modules
- Provides read-only configuration objects
- Handles environment variable integration