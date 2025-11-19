# Architecture

## System Overview

The marco-chrissy-site project follows a modular, loosely-coupled architecture where each component has a single, well-defined responsibility.

## Core Principles

### Separation of Concerns
- **NormPic**: Photo organization (external tool)
- **Galleria**: Gallery generation with plugin system (internal module)
- **Pelican**: Static site generation (external framework)
- **Orchestrator**: Build coordination
- **Deployer**: CDN deployment

### No Tight Coupling
- Components communicate through files and manifests
- No direct imports between tools
- Configuration-driven behavior
- Clear data contracts (JSON manifests)

### Module Organization
Following functional organization patterns:
- Avoid generic "core" directories
- Organize by specific responsibility
- Clear module boundaries
- Each directory represents a type, not a collection

## Data Flow
```
Photos (source) \u2192 NormPic \u2192 Organized Photos + Manifest
                                      \u2193
                                  Galleria
                                      \u2193
                              Gallery HTML/CSS
                                      \u2193
                    Pelican \u2190 Content Pages
                                      \u2193
                               Static Site \u2192 CDN
```

## Directory Structure
```
marco-chrissy-site/
\u251c\u2500\u2500 galleria/           # Gallery generator (extractable)
\u251c\u2500\u2500 orchestrator/       # Build orchestration
\u251c\u2500\u2500 deployer/          # Deployment logic
\u251c\u2500\u2500 config/            # All configurations
\u2502   \u251c\u2500\u2500 normpic/      # NormPic configs
\u2502   \u2514\u2500\u2500 galleria/     # Galleria configs
\u251c\u2500\u2500 content/          # Pelican content
\u251c\u2500\u2500 output/           # Generated site
\u2514\u2500\u2500 pelican/          # Pelican configuration
```

## Galleria Plugin Architecture

Galleria uses a 5-stage plugin pipeline for extensible gallery generation:

1. **Provider** → Load photo collections (NormPic manifests, directories, databases)
2. **Processor** → Generate thumbnails and process images  
3. **Transform** → Manipulate data (pagination, sorting, filtering)
4. **Template** → Generate HTML structure
5. **CSS** → Generate stylesheets

### Plugin System Structure
```
galleria/
├── plugins/            # Plugin system foundation
│   ├── base.py         # BasePlugin interface
│   ├── interfaces.py   # Specific plugin interfaces
│   └── exceptions.py   # Plugin exception hierarchy
└── manager/            # Plugin orchestration
    └── hooks.py        # Hook system for extensibility
```

Each stage has defined data contracts and can be extended through the plugin system. The complete interface foundation is implemented and tested with 130 comprehensive tests.

See [Plugin System Documentation](modules/galleria/plugin-system.md) for detailed interface specifications.

## Integration Points

### File-Based Communication
- NormPic writes manifests to photo directories
- Galleria reads manifests from photo directories
- Galleria writes HTML to output directory
- Pelican reads from content, writes to output

### Configuration Contracts
Each tool has its own configuration format:
- NormPic: Photo organization rules
- Galleria: Gallery generation settings
- Pelican: Site generation configuration
- Orchestrator: Build workflow settings

## Future Extensibility

### Django/FastAPI Integration
The architecture supports future dynamic features:
- Same content directories
- Same manifest format
- Same output structure
- Different serving mechanism

### Extraction Path
Galleria is designed for extraction:
- Self-contained module
- No parent project dependencies
- Clear interfaces
- Configuration-driven