# Site Serve Command

## Overview

The `site serve` command provides a development server that coordinates multiple backend servers through a smart HTTP proxy. It enables live development of the complete site with hot reloading capabilities.

## Usage

```bash
site serve [OPTIONS]
```

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

### Core Components

- **SiteServeProxy**: Routing logic and subprocess management
- **ProxyHTTPHandler**: HTTP request handling and forwarding
- **Static File Server**: Direct filesystem serving for photos

### Testing

The serve command has comprehensive test coverage:

- **15 unit tests** covering all proxy functionality
- **E2E tests** for server coordination and routing
- **Error handling tests** for connection failures

See `test/unit/test_site_serve.py` for detailed test examples.