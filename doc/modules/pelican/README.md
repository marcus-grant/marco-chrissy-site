# Pelican Integration

This module documents the integration patterns for using Pelican with the shared component system.

## Overview

Pelican is the static site generator framework used for creating main site pages (about, blog posts, etc.). Our integration enables Pelican to use shared components (navbar, CSS) that are also used by Galleria for consistent styling across the entire site.

## Key Integration Points

### Template Override System

Pelican uses a template override system to replace default theme templates with shared components. This is configured via the `THEME_TEMPLATES_OVERRIDES` setting in the Pelican configuration.

**Configuration:**
- Setting: `THEME_TEMPLATES_OVERRIDES` (string format)
- Purpose: Override default theme templates with shared component templates
- Location: `config/pelican.conf.py`

### Shared Component Integration

The integration works through template overrides that replace Pelican's default templates with versions that include shared components:

1. **Base template override**: Includes shared CSS and structure
2. **Header template override**: Uses shared navigation component
3. **Content templates**: Maintain Pelican functionality while using shared styling

### Output Integration

Pelican generates HTML pages that include:
- Shared navigation components
- Shared CSS styling
- Consistent page structure with Galleria pages
- Proper semantic HTML structure (H1 for content titles, shared nav components)

## Configuration Schema

The Pelican configuration includes:

```json
{
  "theme_templates_overrides": {
    "type": "string",
    "description": "Path to directory containing template override files"
  }
}
```

## Template Structure

Override templates are located in `themes/shared/templates/` and include:

- `base.html` - Main page structure with shared CSS
- `index.html` - Article listing page
- `article.html` - Individual article pages
- `shared/header.html` - Shared navigation component

## Related Documentation

- [Theme Overrides](theme-overrides.md) - Detailed template override system
- [Quirks and Workarounds](quirks.md) - Pelican-specific issues and solutions