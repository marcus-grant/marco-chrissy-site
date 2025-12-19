# Galleria Theme System

## Overview

The Galleria theme system provides template management and shared component integration for consistent styling across gallery and site pages. The system supports both theme-specific and shared templates with proper precedence handling.

## Theme Architecture

### Template Search Paths

The theme system implements a hierarchical template search pattern:

1. **Theme-specific templates** (highest precedence)
   - Located in `themes/[theme-name]/templates/`
   - Override shared templates when present
   - Theme-specific customizations and layouts

2. **Shared templates** (lower precedence)
   - Located in `themes/shared/templates/`  
   - Available to both Galleria and Pelican systems
   - Common navigation, components, and layouts

3. **Plugin fallbacks** (lowest precedence)
   - Hardcoded templates in plugin code
   - Used when no theme or shared template found

### Template Loader Classes

#### GalleriaSharedTemplateLoader

**Purpose**: Enables Galleria to load templates from both theme-specific and shared locations.

**Usage**:
```python
from themes.shared.utils.template_loader import GalleriaSharedTemplateLoader

# Configuration includes external template paths
config = {
    "theme": {
        "external_templates": ["/path/to/themes/shared/templates"]
    }
}

loader = GalleriaSharedTemplateLoader(config, "/path/to/themes/minimal")
template = loader.get_template("navigation.html")
```

**Search Order**:
1. `themes/minimal/templates/navigation.html`
2. `themes/shared/templates/navigation.html`
3. Template not found (raises exception)

#### Pelican Integration

**Purpose**: Configure Pelican's Jinja2 environment to include shared templates.

**Usage**:
```python
from themes.shared.utils.template_loader import configure_pelican_shared_templates

# Returns list of template directories for Pelican configuration
template_dirs = configure_pelican_shared_templates("config/pelican.json")
```

**Configuration**:
```json
{
  "SITENAME": "Site Name",
  "SHARED_THEME_PATH": "/path/to/themes/shared",
  "THEME": "/path/to/themes/site"
}
```

## Shared Component Integration

### Asset Management

**Shared Asset Manager** provides consistent external dependency handling:

```python
from themes.shared.utils.asset_manager import AssetManager

asset_manager = AssetManager(output_dir)
css_path = asset_manager.ensure_asset("pico", "css")
css_url = asset_manager.get_asset_url("pico", "css")  # "/css/pico.min.css"
```

**Integration Points**:
- Downloads external dependencies (PicoCSS) to `output/css/`
- Provides consistent URLs across both systems
- Automatic directory creation and file management

### Context Adapters

**Purpose**: Standardize template context data between Pelican and Galleria systems.

**Base Interface**:
```python
from themes.shared.utils.context_adapters import BaseContextAdapter

class CustomContextAdapter(BaseContextAdapter):
    def to_shared_context(self) -> dict:
        return {
            "site": self._extract_site_info(),
            "navigation": self._build_navigation(),
            "page": self._extract_page_info()
        }
```

**Concrete Implementations**:
- `PelicanContextAdapter`: Converts Pelican template context
- `GalleriaContextAdapter`: Converts Galleria template context

## Theme Development Patterns

### Shared Template Structure

**Recommended Directory Structure**:
```
themes/
├── shared/
│   ├── templates/
│   │   ├── base.html              # Base page structure
│   │   ├── navigation/
│   │   │   ├── primary.html       # Main navigation
│   │   │   └── breadcrumbs.html   # Breadcrumb navigation
│   │   └── components/
│   │       ├── header.html        # Site header
│   │       └── footer.html        # Site footer
│   └── css/                       # Shared stylesheets
└── [theme-name]/
    └── templates/
        ├── index.html              # Theme-specific index
        └── gallery.html            # Theme-specific gallery
```

### Template Inclusion Patterns

**Shared Component Usage**:
```html
<!-- In both Pelican and Galleria templates -->
{% include "navigation/primary.html" %}
{% include "components/header.html" %}
{% include "components/footer.html" %}
```

**Theme Override Pattern**:
```html
<!-- themes/minimal/templates/custom.html -->
<!-- This overrides themes/shared/templates/custom.html -->
<div class="minimal-specific-styling">
    {% include "components/header.html" %}
</div>
```

## Configuration Integration

### Galleria Theme Configuration

```json
{
  "theme_path": "themes/shared",
  "theme": {
    "name": "minimal",
    "external_templates": [
      "/path/to/themes/shared/templates"
    ],
    "external_assets": {
      "css": ["/css/pico.min.css"],
      "js": []
    }
  }
}
```

**Note**: The `theme_path` property points to the shared component directory and enables Galleria to use shared templates and assets alongside theme-specific templates.

### Pelican Theme Configuration

```json
{
  "THEME": "/path/to/themes/site",
  "SHARED_THEME_PATH": "/path/to/themes/shared"
}
```

## Future Extensibility

### Plugin Integration

The theme system integrates with Galleria's plugin architecture:

```python
# Custom template plugin with shared theme support
class SharedThemeTemplatePlugin(TemplatePlugin):
    def __init__(self, config):
        self.loader = GalleriaSharedTemplateLoader(config, theme_path)
    
    def generate_html(self, context):
        template = self.loader.get_template("gallery.html")
        return template.render(context)
```

### Extraction Compatibility

**Design Principles**:
- No hardcoded dependencies on parent project structure
- Configuration-driven template path resolution  
- Interface-based template loading for dependency injection
- Clear separation between theme logic and site integration

**Post-Extraction Usage**:
```python
# Standalone Galleria with injected theme system
from galleria import Generator
from site_integration import SiteThemeLoader

generator = Generator()
generator.set_template_loader(SiteThemeLoader(
    theme_path="themes/minimal",
    shared_paths=["themes/shared/templates"]
))
```

## Testing Support

### Fixture Integration

The shared theme system includes testing fixtures for consistent test setup:

```python
def test_shared_template_loading(shared_theme_dirs):
    """Test using the shared theme directory fixture."""
    template_path = shared_theme_dirs["shared_templates"] / "test.html"
    template_path.write_text("<div>Test</div>")
    
    loader = GalleriaSharedTemplateLoader(config, theme_path)
    template = loader.get_template("test.html")
    assert template is not None
```

**Available Fixtures**:
- `shared_theme_dirs`: Creates standard shared theme directory structure
- Returns dict with `shared_templates` and `galleria_templates` paths
- Replaces repeated directory creation in multiple tests

## Benefits

### Consistency
- Same navigation and components across Pelican and Galleria pages
- Unified styling through shared CSS and templates
- Consistent URL generation and asset references

### Maintainability
- Single location for shared components reduces duplication
- Theme-specific overrides enable customization without affecting shared code
- Clear template search precedence prevents conflicts

### Extractability
- Galleria theme system designed for future package extraction
- Interface-based template loading supports dependency injection
- No tight coupling with parent project structure