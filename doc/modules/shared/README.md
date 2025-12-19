# Shared Component System

## Overview

The shared component system provides consistent styling and navigation across both Pelican-generated pages and Galleria-generated galleries. This ensures a unified user experience throughout the entire site.

## Architecture

### Component Structure

```
themes/shared/
├── templates/          # Shared template components
│   ├── base.html      # Main page structure
│   ├── index.html     # Article listing
│   ├── article.html   # Individual articles
│   └── shared/
│       └── header.html # Navigation component
└── static/
    └── css/
        └── shared.css  # Shared styling
```

### Integration Points

The shared component system integrates with:

1. **Pelican** - Via template override system (`THEME_TEMPLATES_OVERRIDES`)
2. **Galleria** - Via external theme configuration (`theme_path`)

## Key Components

### Navigation Component
**Location:** `themes/shared/templates/shared/header.html`
**Purpose:** Consistent navigation across all pages
**Content:** Main site navigation menu

### Shared CSS
**Location:** `themes/shared/static/css/shared.css`
**Purpose:** Consistent styling and layout
**Scope:** Site-wide visual consistency

### Base Template Structure
**Location:** `themes/shared/templates/base.html`
**Purpose:** Common HTML structure and meta tags
**Features:**
- Responsive viewport configuration
- Shared CSS inclusion
- Semantic HTML structure

## Configuration

### Pelican Integration
Configure in `config/pelican.conf.py`:

```python
THEME_TEMPLATES_OVERRIDES = "themes/shared/templates"
```

### Galleria Integration
Configure in `config/galleria.yml`:

```yaml
theme_path: "themes/shared"
```

## Template System

### Template Hierarchy

1. **System-specific templates** (Pelican theme, Galleria theme)
2. **Shared component overrides** (themes/shared/templates/)
3. **Common base structure** (shared base.html)

### Template Context

Shared templates use conditional logic to adapt to different system contexts:

```jinja2
{% if collection_name %}
    <!-- Galleria context -->
    <h1>Gallery: {{ collection_name }}</h1>
{% elif SITENAME %}
    <!-- Pelican context -->
    <h1>{{ SITENAME }}</h1>
{% endif %}
```

## Benefits

### Consistency
- Identical navigation across all pages
- Unified visual styling
- Consistent semantic HTML structure

### Maintainability
- Single source of truth for navigation
- Centralized CSS management
- Reduced code duplication

### Extensibility
- Easy to add new shared components
- System-agnostic design
- Modular architecture

## Usage Patterns

### Adding New Shared Components

1. Create component template in `themes/shared/templates/shared/`
2. Add CSS rules to `themes/shared/static/css/shared.css`
3. Include component in relevant page templates
4. Test integration with both systems

### Modifying Existing Components

1. Edit component template or CSS
2. Test changes with both Pelican and Galleria
3. Verify consistent appearance across all pages
4. Update documentation if needed

## Testing Strategy

### Integration Testing
- Verify shared components appear in both system outputs
- Check CSS inclusion and application
- Validate HTML structure consistency

### Visual Testing
- Manual browser testing across different devices
- Automated screenshot comparison (future enhancement)
- Cross-browser compatibility testing

## Related Documentation

- [External Integration](external-integration.md) - Integration with external projects
- [Pelican Integration](../pelican/README.md) - Pelican-specific configuration
- [Galleria Themes](../galleria/themes.md) - Galleria theme system

## Future Enhancements

- Context-aware header variations
- Dynamic navigation based on site structure
- Theme switching capabilities
- Component plugin system