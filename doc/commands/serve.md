# Site Serve Command

## Overview

The `site serve` command provides a development server that coordinates multiple backend servers through a smart HTTP proxy. It enables live development of the complete site with hot reloading capabilities.

## Usage

```bash
site serve [OPTIONS]
```

### Automatic Build Pipeline

The serve command follows the cascading pipeline pattern:
- **Checks for output directory** - If missing, automatically calls `build` command
- **Build cascade** - build→organize→validate pipeline runs automatically  
- **Error handling** - Exits gracefully if build pipeline fails
- **Development ready** - Starts server only after successful build

### Options

- `--host TEXT`: Host to bind proxy server (default: 127.0.0.1)
- `--port INTEGER`: Port for proxy server (default: 8000)  
- `--galleria-port INTEGER`: Port for Galleria server (default: 8001)
- `--pelican-port INTEGER`: Port for Pelican server (default: 8002)

### Example

```bash
# Start development server on default ports
site serve

# Start on custom ports
site serve --port 3000 --galleria-port 3001 --pelican-port 3002

# Bind to all interfaces
site serve --host 0.0.0.0
```

## Architecture

### Proxy Routing

The serve command starts three servers:

1. **Proxy Server** (port 8000) - Routes requests intelligently
2. **Galleria Server** (port 8001) - Serves gallery pages  
3. **Pelican Server** (port 8002) - Serves site content

### Request Routing Rules

| URL Pattern | Target | Purpose |
|-------------|--------|---------|
| `/galleries/*` | Galleria Server (8001) | Gallery pages and thumbnails |
| `/pics/*` | Static File Server | Full-resolution photos |
| Everything else | Pelican Server (8002) | Site pages, feeds, assets |

### Example URLs

```bash
# Gallery content → Galleria server
http://localhost:8000/galleries/wedding/page_1.html

# Full photos → Static files from output/pics/
http://localhost:8000/pics/full/photo1.jpg  

# Site content → Pelican server
http://localhost:8000/                        # Homepage
http://localhost:8000/about.html              # About page
http://localhost:8000/feeds/all.atom.xml      # RSS feed
```

## Development Workflow

1. **Start Development Server**
   ```bash
   site serve
   ```

2. **Access Site**
   - Open http://localhost:8000 in browser
   - All requests automatically routed to appropriate backend

3. **Make Changes**
   - Edit gallery configs → Galleria hot reload
   - Edit Pelican content → Pelican hot reload
   - Changes reflected immediately in browser

4. **Stop Server**
   - Press Ctrl+C to gracefully shutdown all servers

## Error Handling

The proxy handles errors gracefully:

- **502 Bad Gateway**: Backend server unreachable
- **404 Not Found**: Static file or page doesn't exist
- **Connection Errors**: Logged and returned as 502

## Implementation Details

The serve command uses an orchestrator pattern that separates CLI concerns from server coordination logic.

### Core Components

- **ServeOrchestrator** (`serve/orchestrator.py`): Main coordination class that manages the complete serve workflow
  - Handles server lifecycle (startup, shutdown, cleanup)  
  - Manages signal handlers for graceful shutdown
  - Creates and coordinates proxy, Galleria, and Pelican servers

- **SiteServeProxy** (`serve/proxy.py`): Routing logic and subprocess management
  - Creates and manages Galleria and Pelican server subprocesses
  - Routes requests based on URL patterns
  - Handles graceful cleanup on shutdown

- **ProxyHTTPHandler** (`serve/proxy.py`): HTTP request handling and forwarding
  - Forwards `/galleries/*` requests to Galleria server
  - Serves `/pics/*` requests directly from filesystem
  - Forwards all other requests to Pelican server
  - Handles connection errors with 502/404 responses

- **CLI Command** (`cli/commands/serve.py`): Simplified interface for argument parsing
  - Parses command-line arguments
  - Creates ServeOrchestrator and calls start()
  - Reports results to user

### Backend Server Management

The serve command automatically starts required backend servers:

1. **Galleria Server**: Started with `galleria serve --config config/galleria.json --port <galleria-port>`
2. **Pelican Server**: Started with `pelican --listen --port <pelican-port> --bind 127.0.0.1 output`

Both servers are terminated cleanly when the proxy server shuts down.

### Architecture Benefits

**Business Logic Separation**:
- CLI layer only handles argument parsing and user interaction
- Core serve logic completely independent of CLI framework  
- ServeOrchestrator callable from any context (API, scripts, tests)

**Improved Testability**:
- Unit tests can mock ServeOrchestrator instead of complex server setup
- Proxy logic testable independently from server coordination
- Clear separation enables focused testing of each component

### Testing

The serve command has comprehensive test coverage:

- **Unit tests** covering orchestrator lifecycle, proxy routing, and CLI interface
- **E2E tests** for complete server coordination and request routing
- **Signal handling tests** for graceful shutdown scenarios

See `test/unit/test_serve_orchestrator.py`, `test/unit/test_serve_proxy.py`, `test/unit/test_site_serve.py`, and `test/e2e/test_site_serve.py` for detailed test examples.

For detailed architecture documentation, see [Serve Module Documentation](../modules/serve/).