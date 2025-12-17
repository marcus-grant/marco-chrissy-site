# Galleria Template Plugins

Template plugins in Galleria are responsible for generating HTML, CSS, and applying data transformations to photo collections. This document covers the template system plugins: TemplatePlugin, CSSPlugin, and pagination transforms.

## Plugin Types

### TemplatePlugin

Template plugins generate HTML markup from transformed photo data.

**Interface**: `TemplatePlugin`
**Method**: `generate_html(context: PluginContext) -> PluginResult`

#### Input Format
```python
{
    "pages": [...],              # For pagination transforms
    "photos": [...],             # For sorting/filtering transforms
    "collection_name": str,      # Preserved from input
    "transform_metadata": dict,  # Transform-specific metadata
}
```

#### Output Format
```python
{
    "html_files": [
        {
            "filename": str,        # HTML file name
            "content": str,         # HTML content (optional)
            "page_number": int,     # Page number (for pagination)
        },
        ...
    ],
    "collection_name": str,         # Preserved from input
    "file_count": int,              # Number of HTML files generated
}
```

#### BasicTemplatePlugin

Generates semantic HTML5 gallery pages with responsive design. Supports both hardcoded templates and theme-based file loading.

**Features:**
- Pagination support with navigation
- Configurable themes and layouts
- Lazy loading images
- Empty gallery state handling
- SEO-friendly markup
- Theme system integration with fallback to hardcoded templates

**Configuration:**
```python
{
    "theme": "minimal|elegant|modern",  # Default: "minimal" (hardcoded mode)
    "layout": "grid|flex",              # Default: "grid"
    "theme_path": "/path/to/theme/dir", # Optional: enables theme system
}
```

**Theme System:**
When `theme_path` is configured, the plugin loads templates from external theme files:

- **Template Directory**: `{theme_path}/templates/`
- **Main Template**: `gallery.j2.html` (Jinja2 format)
- **Template Variables**: 
  - `collection_name` - Gallery title
  - `photos` - List of photo objects with `thumb_url`, `photo_url`, `collection_name`
  - `page_num` - Current page number
  - `total_pages` - Total number of pages

**Fallback Behavior:**
Without `theme_path`, uses hardcoded HTML templates for backward compatibility.

### CSSPlugin

CSS plugins generate stylesheets for the HTML templates.

**Interface**: `CSSPlugin`
**Method**: `generate_css(context: PluginContext) -> PluginResult`

#### Input Format
```python
{
    "html_files": [
        {
            "filename": str,
            "content": str,         # Optional
            "page_number": int,
        },
        ...
    ],
    "collection_name": str,
    "file_count": int,
}
```

#### Output Format
```python
{
    "css_files": [
        {
            "filename": str,        # CSS file name
            "content": str,         # CSS content (optional)
            "type": str,            # CSS type (gallery, theme, responsive)
        },
        ...
    ],
    "html_files": [...],            # Pass through from template
    "collection_name": str,         # Preserved from input
    "css_count": int,               # Number of CSS files generated
}
```

#### BasicCSSPlugin

Generates comprehensive stylesheets with theme and responsive support. Supports both hardcoded CSS generation and theme-based file loading.

**Features:**
- Light, dark, and auto themes
- Responsive design (mobile/tablet breakpoints)
- Grid and flexbox layout support
- Pagination navigation styling
- Modern typography and spacing
- Theme system integration with fallback to hardcoded CSS

**Configuration:**
```python
{
    "theme": "light|dark|auto",         # Default: None (no theme)
    "layout": "grid|flex",              # Default: "grid"
    "responsive": bool,                 # Default: True
    "theme_path": "/path/to/theme/dir", # Optional: enables theme system
}
```

**Theme System:**
When `theme_path` is configured, the plugin loads CSS from external theme files:

- **CSS Directory**: `{theme_path}/static/css/`
- **CSS Files**: All `.css` files in the directory
- **Load Order**: Alphabetical, with `custom.css` loaded last for highest priority
- **File Structure**: Each CSS file becomes a separate output file

**Generated Files:**
- **Theme Mode**: Files from theme directory (e.g., `gallery.css`, `custom.css`)
- **Hardcoded Mode**: 
  - `gallery.css` - Base gallery styles
  - `theme-{name}.css` - Theme-specific styles (if theme specified)
  - `responsive.css` - Responsive breakpoints (if enabled)

**Fallback Behavior:**
Without `theme_path`, generates hardcoded CSS for backward compatibility.

## Transform Plugins

### PaginationPlugin

Pagination plugins split photo collections into pages for large galleries.

**Interface**: `TransformPlugin`
**Method**: `transform_data(context: PluginContext) -> PluginResult`

#### Input Format
```python
{
    "photos": [
        {
            "dest_path": str,
            "thumbnail_path": str,
            "thumbnail_size": tuple,
            # Other photo data...
        },
        ...
    ],
    "collection_name": str,
    "thumbnail_count": int,
}
```

#### Output Format
```python
{
    "pages": [
        [photo1, photo2, ...],      # Page 1 photos
        [photo3, photo4, ...],      # Page 2 photos
        ...
    ],
    "collection_name": str,         # Preserved from input
    "transform_metadata": {
        "page_size": int,
        "total_pages": int,
        "total_photos": int,
        "pagination_enabled": bool,
        # Additional metadata...
    },
}
```

#### BasicPaginationPlugin

Simple pagination with configurable page size.

**Features:**
- Configurable page size (1-100 photos per page)
- Default page size: 20 photos
- Detailed pagination metadata
- Empty collection handling

**Configuration:**
```python
{
    "page_size": int,               # Default: 20, Range: 1-100
}
```

#### SmartPaginationPlugin

Intelligent pagination with adaptive page balancing.

**Features:**
- Avoids small last pages by redistributing photos
- Configurable min/max page sizes
- Multiple pagination strategies
- Detailed balancing metadata

**Configuration:**
```python
{
    "page_size": int,               # Target page size (default: 20)
    "min_page_size": int,           # Minimum page size (default: page_size // 2)
    "max_page_size": int,           # Maximum page size (default: page_size * 1.5)
    "balance_pages": bool,          # Enable smart balancing (default: True)
}
```

## Theme System Architecture

### ThemeValidator

Validates theme directory structure and configuration.

**Location**: `galleria.theme.validator`
**Method**: `validate_theme_directory(theme_path: Path) -> bool`

#### Validation Requirements:
- `theme.json` configuration file exists
- `templates/` directory exists
- `static/css/` directory exists
- `theme.json` contains valid configuration

#### Theme Configuration Format:
```json
{
  "name": "Theme Name",
  "version": "1.0.0",
  "templates": ["gallery.j2.html", "page.j2.html"],
  "css": ["gallery.css", "custom.css"]
}
```

### TemplateLoader

Loads and renders Jinja2 templates from theme directory.

**Location**: `galleria.theme.loader`
**Method**: `load_template(template_name: str) -> jinja2.Template`

#### Features:
- Jinja2 environment with theme directory as template root
- Template inheritance support
- Error handling for missing templates
- UTF-8 encoding support

#### Template Structure:
```
theme_directory/
├── theme.json
├── templates/
│   ├── gallery.j2.html       # Main gallery template
│   ├── base.j2.html          # Base template (optional)
│   └── components/           # Template components (optional)
└── static/
    └── css/
        ├── gallery.css       # Main styles
        ├── responsive.css    # Responsive styles (optional)
        └── custom.css        # Custom overrides (optional)
```

## Usage Examples

### Basic Gallery Generation

```python
from galleria.plugins.template import BasicTemplatePlugin
from galleria.plugins.css import BasicCSSPlugin
from galleria.plugins.pagination import BasicPaginationPlugin

# Configure pagination
pagination = BasicPaginationPlugin()
pagination_result = pagination.transform_data(PluginContext(
    input_data=processor_output,
    config={"page_size": 15},
    output_dir=output_path
))

# Generate HTML
template = BasicTemplatePlugin()
html_result = template.generate_html(PluginContext(
    input_data=pagination_result.output_data,
    config={"theme": "elegant", "layout": "grid"},
    output_dir=output_path
))

# Generate CSS
css = BasicCSSPlugin()
css_result = css.generate_css(PluginContext(
    input_data=html_result.output_data,
    config={"theme": "dark", "responsive": True},
    output_dir=output_path
))
```

### Smart Pagination with Balancing

```python
from galleria.plugins.pagination import SmartPaginationPlugin

smart_pagination = SmartPaginationPlugin()
result = smart_pagination.transform_data(PluginContext(
    input_data=processor_output,
    config={
        "page_size": 25,
        "min_page_size": 15,
        "max_page_size": 35,
        "balance_pages": True
    },
    output_dir=output_path
))

# Check pagination strategy used
strategy = result.output_data["transform_metadata"]["pagination_strategy"]
print(f"Used {strategy} pagination strategy")
```

### Theme-Based Gallery Generation

```python
from galleria.theme.validator import ThemeValidator
from galleria.plugins.template import BasicTemplatePlugin
from galleria.plugins.css import BasicCSSPlugin
from pathlib import Path

# Validate theme directory
theme_path = Path("themes/my_custom_theme")
validator = ThemeValidator()
if not validator.validate_theme_directory(theme_path):
    raise ValueError("Invalid theme directory")

# Configure plugins with theme path
theme_config = {"theme_path": str(theme_path)}

# Generate HTML using theme templates
template = BasicTemplatePlugin()
html_result = template.generate_html(PluginContext(
    input_data=pagination_result.output_data,
    config=theme_config,
    output_dir=output_path
))

# Generate CSS using theme files
css = BasicCSSPlugin()
css_result = css.generate_css(PluginContext(
    input_data=html_result.output_data,
    config=theme_config,
    output_dir=output_path
))

# Output will use theme files instead of hardcoded templates/CSS
print(f"Generated {len(css_result.output_data['css_files'])} CSS files from theme")
```

## Error Handling

All template plugins implement comprehensive error handling:

### Common Errors

- **MISSING_COLLECTION_NAME**: Required collection_name field missing
- **MISSING_HTML_FILES**: Required html_files field missing (CSS plugins)
- **INVALID_THEME**: Unknown theme specified in configuration
- **INVALID_PAGE_SIZE**: Page size outside valid range (1-100)
- **TEMPLATE_ERROR**: General template generation error
- **CSS_ERROR**: General CSS generation error
- **PAGINATION_ERROR**: General pagination error

### Error Response Format

```python
PluginResult(
    success=False,
    output_data={},
    errors=["ERROR_CODE: Detailed error message"]
)
```

## Plugin Pipeline Integration

Template plugins work together in the standard Galleria pipeline:

```
Provider → Processor → Transform → Template → CSS
                      ↑
                 Pagination
```

1. **Processor** outputs photos with thumbnails
2. **Transform** (Pagination) splits into pages
3. **Template** generates HTML from pages
4. **CSS** generates stylesheets for HTML

Each stage passes data through while adding its own output format.