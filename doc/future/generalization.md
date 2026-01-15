# Generalization Strategy

## Vision

Transform current monolithic structure into reusable, modular components for building modern static+dynamic sites with deployment flexibility.

## Key Components

### 1. Galleria Extraction
- Extract galleria/ to standalone project
- Remove parent project dependencies
- Enable community contributions and broader adoption

### 2. SnakeCharmer Framework
- Python-based multi-paradigm site orchestration
- Extract core orchestration system (validate→organize→build→deploy)
- Manages the "menagerie" of tools: Galleria, Cobra, FastAPI, Bunny CDN, etc.
- Abstract Builder interfaces for SSG, API, and frontend builders
- Plugin/hook system for site-specific customizations
- Development server with hot reload and API integration

### 3. Cobra (Pelican Replacement)
- Python-based SSG inspired by 11ty's data-oriented architecture
- Simpler, less opinionated than Pelican
- Data-first pipeline: content → data → templates → output
- Integrates as a builder within SnakeCharmer

### 4. Endpoint Abstraction System
- **Core Concept**: Same endpoint logic can deploy as static CDN, FastAPI, HTMX, or edge functions
- Configuration-based deployment strategy per endpoint
- Progressive enhancement: start static, upgrade to dynamic as needed
- Performance optimization: CDN for hot paths, server-side for complex logic

### 5. This Repository Evolution
- Transform to configuration and deployment hub
- Custom plugins for site-specific business logic
- FastAPI routes for dynamic endpoints  
- Deployment scripts for Bunny CDN and infrastructure

## Endpoint Abstraction Example

```yaml
# config/endpoints.yaml
endpoints:
  contact_form:
    type: "form_handler"
    deployment: "fastapi"     # or "static", "htmx", "edge_function"
    
  photo_gallery:
    type: "content_display" 
    deployment: "static"      # High performance, CDN-served
    
  admin_dashboard:
    type: "dynamic_interface"
    deployment: "htmx"        # Server-rendered with interactions
```

## Migration Phases

1. **Phase 1**: Complete MVP with current architecture
2. **Phase 2**: Extract Galleria as standalone project
3. **Phase 3**: Extract SnakeCharmer orchestration framework
4. **Phase 4**: Develop Cobra SSG (Pelican replacement)
5. **Phase 5**: Prototype endpoint abstraction system
6. **Phase 6**: Migrate marco-chrissy-site to Cobra + SnakeCharmer

## Benefits

- **Modularity**: Reusable components across multiple site projects
- **Deployment Flexibility**: Choose optimal deployment strategy per endpoint
- **Performance**: Static CDN for speed, server-side for complex features
- **Development Speed**: Same code, different deployment targets
- **Community**: Extractable components enable broader contributions