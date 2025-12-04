# Serve Module Architecture

## Overview

The serve module implements a development server architecture that separates CLI concerns from serve orchestration logic, following the orchestrator pattern established by the build module.

## Architecture Pattern

The serve module follows the same orchestrator pattern used throughout the project:

```
cli/commands/serve.py (simplified CLI interface)
         ↓
ServeOrchestrator.start()
    ├── SiteServeProxy (request routing)
    ├── HTTP Server (request handling)
    ├── Galleria subprocess
    └── Pelican subprocess
```

### Key Components

- **ServeOrchestrator** (`serve/orchestrator.py`): Main coordination class that manages the complete serve workflow
- **SiteServeProxy** (`serve/proxy.py`): Handles request routing between Galleria, Pelican, and static files
- **ProxyHTTPHandler** (`serve/proxy.py`): HTTP request handler for the proxy server
- **CLI Command** (`cli/commands/serve.py`): Simplified interface focused on argument parsing and result reporting

## Design Benefits

**Business Logic Separation**:
- CLI layer only handles argument parsing and user interaction  
- Core serve logic completely independent of CLI framework
- ServeOrchestrator callable from any context (API, scripts, tests)

**Improved Testability**:
- Unit tests can mock ServeOrchestrator instead of complex server setup
- Proxy logic testable independently from server coordination
- E2E tests focus on actual proxy behavior, not CLI integration

**Maintainability**:
- Clear separation between HTTP routing logic and server lifecycle management
- Signal handling isolated in orchestrator with proper cleanup
- Each component has single, well-defined responsibility

## Request Routing Architecture

The serve system routes requests through a three-tier proxy:

```
Proxy Server (port 8000)
    ├── /galleries/* → Galleria Server (port 8001)
    ├── /pics/* → Static File Server (filesystem)
    └── everything else → Pelican Server (port 8002)
```

### Routing Logic

**Gallery Requests** (`/galleries/*`):
- Forwarded to Galleria server via HTTP proxy
- Includes gallery pages, thumbnails, CSS
- Galleria handles hot reloading for gallery changes

**Photo Requests** (`/pics/*`):
- Served directly from `output/pics/` directory
- Uses efficient static file serving
- Handles proper content-type headers

**Site Requests** (everything else):
- Forwarded to Pelican server via HTTP proxy
- Includes homepage, about pages, feeds
- Pelican handles hot reloading for content changes

## Server Lifecycle Management

### Startup Sequence

1. **Configuration Validation**: Check for required config files
2. **Subprocess Creation**: Start Galleria and Pelican servers
3. **Proxy Setup**: Initialize SiteServeProxy with routing logic
4. **HTTP Server**: Start proxy server with ProxyHTTPHandler
5. **Signal Handlers**: Register graceful shutdown handlers

### Shutdown Sequence

1. **Signal Reception**: SIGINT/SIGTERM triggers stop event
2. **HTTP Server Shutdown**: Gracefully stop accepting new requests
3. **Subprocess Cleanup**: Terminate Galleria and Pelican servers
4. **Resource Cleanup**: Close server socket and cleanup resources

### Critical Architecture Fix

**Problem**: Original implementation had signal handlers calling cleanup directly from the same thread as `serve_forever()`, causing deadlocks.

**Solution**: 
- Signal handlers set `_stop_event` flag instead of calling cleanup directly
- HTTP server runs in background thread with event-driven shutdown
- Cleanup happens in main thread after server thread completes
- Prevents deadlocks while maintaining graceful shutdown

## Error Handling

The proxy handles errors gracefully:

**Connection Errors**:
- Backend server unreachable → 502 Bad Gateway
- Includes error logging for debugging

**File System Errors**:
- Static file not found → 404 Not Found
- Permission errors → 500 Internal Server Error

**Server Lifecycle Errors**:
- Subprocess startup failures → Early exit with error message
- Configuration errors → Validation failure before server start

## Testing Strategy

**Unit Tests**:
- `test/unit/test_serve_orchestrator.py`: ServeOrchestrator lifecycle and signal handling
- `test/unit/test_serve_proxy.py`: Proxy routing logic and subprocess management  
- `test/unit/test_site_serve.py`: CLI interface and argument handling

**E2E Tests**:
- `test/e2e/test_site_serve.py`: Complete server coordination and routing behavior
- Real subprocess management with proper cleanup
- HTTP request routing validation
- Development URL generation testing

## Integration with Build System

The serve module integrates with the build system for development workflow:

**Build Context Integration**:
- ServeOrchestrator creates `BuildContext(production=False)`
- Passes `override_site_url` to build pipeline
- Generates localhost URLs for development

**Hot Reloading Support**:
- Galleria server detects gallery config changes
- Pelican server detects content changes
- Proxy routes requests to appropriate updated backend

**Output Directory Management**:
- Serves from existing `output/` directory structure
- No rebuild required for static file changes
- Respects the same directory structure as build output