# Pelican Theme Override System

## Overview

The theme override system allows Pelican to use custom templates instead of the default theme templates. This enables integration with shared components while preserving Pelican's functionality.

## Configuration

### Setting: THEME_TEMPLATES_OVERRIDES

**Format:** String (path to override directory)
**Location:** `config/pelican.conf.py`
**Schema:** Defined in `config/schema/galleria.json`

```python
THEME_TEMPLATES_OVERRIDES = "themes/shared/templates"
```

## Override Template Structure

Override templates are located in `themes/shared/templates/`:

```
themes/shared/templates/
├── base.html           # Main page structure
├── index.html          # Article listing
├── article.html        # Individual articles
└── shared/
    └── header.html     # Shared navigation component
```

## Template Implementation

### base.html
- Replaces default theme base template
- Includes shared CSS from `themes/shared/static/css/shared.css`
- Provides consistent page structure
- Removes Pelican's automatic `<hgroup>` title generation

### index.html
- Clean article listing without site title conflicts
- Uses shared header component
- Maintains Pelican's article iteration functionality

### article.html
- Individual article rendering
- Proper H1 usage for article titles
- Integrated shared navigation

### shared/header.html
- Shared navigation component (must match `templates/navbar.html` used by Galleria)
- CSS-only responsive hamburger menu (checkbox toggle, no JavaScript)
- Sticky positioning, 44px touch targets, mobile collapse at 768px

## Template Override Process

1. Pelican loads the configured theme (e.g., "notmyidea")
2. `THEME_TEMPLATES_OVERRIDES` setting points to override directory
3. Pelican checks override directory for templates before using theme defaults
4. Override templates are used if they exist, otherwise defaults are used
5. Override templates can include/extend other templates normally

## Template Context

Override templates have access to all standard Pelican template variables:

- `SITENAME` - Site name from configuration
- `SITEURL` - Site URL from configuration  
- `articles` - List of articles (index.html)
- `article` - Current article object (article.html)
- Standard Pelican template functions and filters

## CSS Integration

Shared CSS is included via:

```html
<link rel="stylesheet" type="text/css" href="{{ SITEURL }}/theme/css/shared.css">
```

The CSS file is copied from `themes/shared/static/css/shared.css` to the output directory during the build process.

## Template Inheritance

Override templates can use Pelican's template inheritance system:

```jinja2
{% extends "base.html" %}
{% block content %}
<!-- Custom content -->
{% endblock %}
```

## Common Patterns

### Removing Pelican Auto-Generated Content

Pelican automatically generates certain HTML elements. To remove them:

```jinja2
{# Remove automatic hgroup elements #}
{% block title %}{% endblock %}
```

### Including Shared Components

```jinja2
{% include "shared/header.html" %}
```

### Conditional Content

```jinja2
{% if article %}
    <h1>{{ article.title }}</h1>
{% elif articles %}
    <h1>Latest Articles</h1>
{% endif %}
```

## Troubleshooting

### Template Not Found Errors
- Verify `THEME_TEMPLATES_OVERRIDES` path is correct
- Ensure template files exist in override directory
- Check file permissions

### Missing Shared Components
- Verify shared component templates exist
- Check include paths in override templates
- Ensure shared CSS is being copied to output

### Inconsistent Styling
- Verify shared CSS is included in override templates
- Check CSS file paths and SITEURL configuration
- Ensure CSS specificity doesn't conflict with theme styles