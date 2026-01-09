# Template Filters Module

## Overview

The template filters module (`galleria/template/filters.py`) provides Jinja2 template filters for context-aware URL generation. This module enables template plugins to generate appropriate URLs based on the build environment (production vs development).

## Module Design

The filters module implements BuildContext-aware URL generation to support seamless switching between production and development builds without template changes.

```python
# galleria/template/filters.py
from build.context import BuildContext

def full_url(path: str, context: BuildContext, site_url: str) -> str:
    """Generate full URL from path using BuildContext."""
```

## Core Functionality

### `full_url()` Filter

The primary filter for converting file paths to full URLs with environment awareness.

**Function Signature:**
```python
def full_url(path: str, context: BuildContext, site_url: str) -> str
```

**Parameters:**
- `path`: File path (absolute or relative)
- `context`: BuildContext with production flag
- `site_url`: Base site URL to use

**Returns:**
- Full URL with proper base URL applied

**Path Processing:**
- Converts absolute filesystem paths to relative web paths
- Extracts parts after 'output' directory for web-friendly URLs
- Handles both absolute and relative path inputs gracefully

## BuildContext Integration

### Relative URL Generation

The filter generates relative URLs starting with `/` for flexible CDN routing via Edge Rules:

```python
# Current implementation generates relative URLs
full_url("/abs/path/output/galleries/wedding/page1", context, site_url)
# Returns: "/galleries/wedding/page1"

full_url("/abs/path/output/pics/full/photo.jpg", context, site_url)  
# Returns: "/pics/full/photo.jpg"
```

**Edge Rules Integration**: Relative URLs enable CDN-level routing where `/pics/full/*` requests are redirected to the photo storage zone while `/galleries/*` requests are served from the site CDN.

### Template Plugin Usage

Template plugins access the filter through BuildContext metadata:

```python
# In template plugin execute() method
build_context = context.metadata.get("build_context")
site_url = context.metadata.get("site_url")

if build_context:
    from galleria.template.filters import full_url
    # Generate context-aware URLs in templates
    generated_url = full_url(image_path, build_context, site_url)
```

## Path Conversion Logic

### `_make_relative_path()` Helper

Internal helper function for converting filesystem paths to web paths:

```python
def _make_relative_path(path: str) -> str:
    """Convert absolute filesystem path to relative web path."""
```

**Conversion Examples:**
```python
# Input: /abs/path/to/output/galleries/wedding/thumbnails/img.webp
# Output: galleries/wedding/thumbnails/img.webp

# Input: galleries/wedding/page1
# Output: galleries/wedding/page1 (already relative)

# Input: /some/other/path/file.jpg (no 'output' directory)
# Output: file.jpg (basename only)
```

## URL Construction

### Base URL Processing

The filter ensures proper URL construction:

- Strips trailing slashes from base URLs
- Ensures web paths start with forward slash
- Combines base URL and path correctly

```python
# Examples:
base_url = "https://site.example.com/"
web_path = "galleries/wedding/page1"
# Result: "https://site.example.com/galleries/wedding/page1"

base_url = "http://localhost:8000"
web_path = "/galleries/wedding/page1"
# Result: "http://localhost:8000/galleries/wedding/page1"
```

## Integration Points

### Pipeline Metadata

The filter integrates with the Galleria pipeline through metadata:

```python
# BuildOrchestrator → GalleriaBuilder → Pipeline
metadata = {
    "build_context": BuildContext(production=False),
    "site_url": "http://localhost:8000"
}

# Available in template plugins via context.metadata
```

### Template System

Template plugins can use the filter for any URL generation needs:

- Gallery page navigation links
- Image thumbnail URLs
- CSS and asset references
- Cross-page linking

## Error Handling

The filter provides graceful degradation:

- Empty paths return as-is
- Paths without 'output' directory use basename
- Missing BuildContext gracefully handled by template plugins
- Invalid paths processed without exceptions

## Usage Examples

### Basic Usage
```python
from galleria.template.filters import full_url
from build.context import BuildContext

# Relative URL generation (current implementation)
context = BuildContext(production=True)
url = full_url("galleries/wedding/page1", context, site_url)
# Result: "/galleries/wedding/page1"

url = full_url("pics/full/photo.jpg", context, site_url)
# Result: "/pics/full/photo.jpg"
```

### Template Plugin Integration
```python
class CustomTemplatePlugin(TemplatePlugin):
    def generate_html(self, context: PluginContext) -> PluginResult:
        build_context = context.metadata.get("build_context")
        site_url = context.metadata.get("site_url")
        
        if build_context:
            # Generate context-aware URLs in templates
            page_url = full_url("galleries/wedding/page2", build_context, site_url)
            thumbnail_url = full_url("galleries/wedding/thumbnails/img.webp", build_context, site_url)
```

## Testing

The filter module is tested with comprehensive unit tests covering:

- Path conversion logic for various input formats
- URL construction with different base URLs
- BuildContext integration scenarios
- Edge cases and error conditions

See template filter tests in the test suite for detailed examples.

## Design Benefits

**Environment Flexibility**: Single filter supports both production and development URLs without template changes.

**Path Abstraction**: Converts filesystem paths to web paths automatically.

**Clean Integration**: Seamlessly integrates with Galleria plugin metadata system.

**Extensibility**: Additional filters can be added following the same pattern.