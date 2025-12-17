# Generalization Strategy

## Vision

Transform current monolithic structure into reusable, modular components for building modern static+dynamic sites with deployment flexibility.

## Key Components

### 1. Galleria Extraction
- Extract galleria/ to standalone project
- Remove parent project dependencies  
- Enable community contributions and broader adoption

### 2. SiteForge Framework
- Extract core orchestration system (validate→organize→build→deploy)
- Plugin system for extensible architecture
- Multi-generator support (Pelican, Hugo, 11ty, custom)
- Development server with hot reload and API integration

### 3. Endpoint Abstraction System
- **Core Concept**: Same endpoint logic can deploy as static CDN, FastAPI, HTMX, or edge functions
- Configuration-based deployment strategy per endpoint
- Progressive enhancement: start static, upgrade to dynamic as needed
- Performance optimization: CDN for hot paths, server-side for complex logic

### 4. This Repository Evolution
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
3. **Phase 3**: Design SiteForge framework interfaces
4. **Phase 4**: Prototype endpoint abstraction system
5. **Phase 5**: Migrate marco-chrissy-site to new architecture

## Benefits

- **Modularity**: Reusable components across multiple site projects
- **Deployment Flexibility**: Choose optimal deployment strategy per endpoint
- **Performance**: Static CDN for speed, server-side for complex features
- **Development Speed**: Same code, different deployment targets
- **Community**: Extractable components enable broader contributions