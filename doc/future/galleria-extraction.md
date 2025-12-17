# Galleria Extraction Strategy

## Overview

This document outlines the planned strategy for extracting Galleria as a standalone package post-MVP. The extraction follows dependency injection patterns to maintain loose coupling and enable reusable, generic gallery generation.

## Current Architecture Foundation

Galleria is currently designed with extraction in mind through several architectural patterns:

### Plugin System Independence
- 5-stage plugin pipeline (provider → processor → transform → template → css)
- No hardcoded dependencies on parent project
- Configuration-driven behavior through JSON manifests
- Clear plugin interfaces with defined data contracts

### Shared Component Integration
- `GalleriaSharedTemplateLoader` accepts external template paths
- Context adapters provide unified template data interfaces
- Asset management through external configuration
- Template search path precedence system

## Extraction Implementation Plan

### Phase 1: Package Structure
Extract Galleria to standalone package with clean API:

```python
# Standalone Galleria package
from galleria import Generator, TemplateLoader
from galleria.plugins import ProviderPlugin, TemplatePlugin

# Site-specific integration
generator = Generator(config_path="galleria.json")
generator.add_template_paths(["site/themes/shared/templates"])
generator.generate(output_dir="output/galleries")
```

### Phase 2: Dependency Injection Patterns

**Template System Integration**:
```python
# Current: Hardcoded template loader
loader = GalleriaSharedTemplateLoader(config, theme_path)

# Post-extraction: Injected dependencies
template_loader = SiteTemplateLoader(
    shared_paths=["themes/shared/templates"],
    theme_path="themes/minimal"
)
generator = GalleriaGenerator(template_loader=template_loader)
```

**Context Adapter Interface**:
```python
# Current: Site-specific context adapters
adapter = GalleriaContextAdapter(context)

# Post-extraction: Injected context processor
class SiteContextProcessor(ContextProcessor):
    def process_navigation_context(self, context):
        return {"nav": self.build_nav_data()}

generator = GalleriaGenerator(context_processor=SiteContextProcessor())
```

### Phase 3: Configuration Abstraction

**Asset Management Injection**:
```python
# Current: Hardcoded asset paths
asset_manager = AssetManager(output_dir)

# Post-extraction: Configurable asset strategy
class SiteAssetStrategy(AssetStrategy):
    def resolve_css_url(self, asset_name):
        return f"/css/{asset_name}.min.css"

generator = GalleriaGenerator(asset_strategy=SiteAssetStrategy())
```

**Plugin Registration System**:
```python
# Post-extraction: Site-specific plugin registration
from site.plugins import PelicanNavigationPlugin

generator = GalleriaGenerator()
generator.register_plugin('template', PelicanNavigationPlugin)
generator.register_plugin('provider', NormPicProvider)
```

## Migration Strategy

### Step 1: Interface Extraction
Extract core interfaces and base classes:
- `BaseProvider`, `BaseProcessor`, `BaseTransform`, `BaseTemplate`, `BaseCSS`
- `TemplateLoader` interface with search path management
- `ContextAdapter` abstract base class
- `AssetManager` interface

### Step 2: Site Integration Package
Create intermediate integration package:
```
galleria-site-integration/
├── plugins/
│   ├── pelican_template_plugin.py
│   ├── shared_context_adapter.py
│   └── site_asset_strategy.py
├── loaders/
│   └── shared_template_loader.py
└── config/
    └── site_config_schema.json
```

### Step 3: Core Galleria Package
Extract pure gallery generation logic:
```
galleria/
├── core/
│   ├── generator.py
│   ├── pipeline.py
│   └── interfaces.py
├── plugins/
│   ├── basic_provider.py
│   ├── thumbnail_processor.py
│   ├── pagination_transform.py
│   ├── jinja_template.py
│   └── css_generator.py
└── config/
    └── schema.json
```

### Step 4: Site Package Update
Update site to use extracted packages:
```python
# site/gallery_integration.py
from galleria import Generator
from galleria_site_integration import SiteTemplatePlugin

def create_site_generator():
    generator = Generator("config/galleria.json")
    generator.register_plugin('template', SiteTemplatePlugin)
    return generator
```

## Dependency Injection Benefits

### Testing Isolation
```python
# Easy mocking of external dependencies
mock_loader = Mock(spec=TemplateLoader)
generator = GalleriaGenerator(template_loader=mock_loader)
```

### Configuration Flexibility
```python
# Different asset strategies for different environments
dev_assets = LocalAssetStrategy(base_url="http://localhost:8000")
prod_assets = CDNAssetStrategy(base_url="https://cdn.example.com")
```

### Plugin Extensibility
```python
# Site-specific plugins without modifying core
class CustomNavigationPlugin(TemplatePlugin):
    def render_template(self, context, metadata):
        # Site-specific navigation logic
        pass
```

## Future Integration Patterns

### Multi-Site Support
```python
# Same Galleria core, different site integrations
wedding_generator = GalleriaGenerator(
    template_loader=WeddingSiteLoader(),
    context_processor=WeddingContextProcessor()
)

blog_generator = GalleriaGenerator(
    template_loader=BlogSiteLoader(),
    context_processor=BlogContextProcessor()
)
```

### Framework Integration
```python
# Django integration
from django_galleria import DjangoGalleriaIntegration

# FastAPI integration  
from fastapi_galleria import FastAPIGalleriaIntegration
```

## Implementation Timeline

**Post-MVP Phase 1** (Immediate):
- Extract interfaces and create injection points
- Implement dependency injection for template loading
- Create site-specific plugin registration system

**Post-MVP Phase 2** (Medium-term):
- Extract core Galleria package
- Create galleria-site-integration package
- Update site to use extracted packages

**Post-MVP Phase 3** (Long-term):
- Publish Galleria as open-source package
- Create integration packages for other frameworks
- Establish plugin ecosystem for community contributions

## Success Criteria

**Independence**: Galleria package has zero dependencies on parent site
**Reusability**: Same core package works with different site architectures  
**Maintainability**: Clear separation of concerns between gallery logic and site integration
**Extensibility**: Plugin system enables custom functionality without core modifications