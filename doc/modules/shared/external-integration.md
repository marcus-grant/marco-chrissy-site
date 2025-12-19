# External Project Integration

## Overview

The shared component system is designed to integrate with external projects and frameworks beyond just Pelican and Galleria. This document describes patterns and best practices for integration with other static site generators and build systems.

## Integration Architecture

### Template-Based Integration

The primary integration method uses template overrides and includes:

```
External Project
├── templates/
│   └── base.html          # Include shared components
├── static/
│   └── css/
│       └── external.css   # Project-specific styles
└── config/
    └── shared_path.conf   # Path to shared components
```

### File Structure Requirements

External projects should expect shared components at a configurable path:

```
shared_components/
├── templates/
│   └── shared/
│       ├── header.html    # Navigation component
│       ├── footer.html    # Footer component (future)
│       └── meta.html      # Common meta tags (future)
└── static/
    └── css/
        └── shared.css     # Shared styling
```

## Integration Patterns

### Template Include Pattern

External templates include shared components:

```jinja2
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <link rel="stylesheet" href="{{ shared_css_path }}">
</head>
<body>
    {% include "shared/header.html" %}
    
    <main>
        {{ content }}
    </main>
</body>
</html>
```

### CSS Integration Pattern

External projects can layer their styles on top of shared CSS:

```css
/* Import shared styles */
@import url("{{ shared_css_path }}");

/* Project-specific overrides */
.project-specific {
    /* Custom styling */
}
```

### Configuration Pattern

External projects should provide configuration for shared component paths:

```yaml
# Example configuration
shared_components:
  enabled: true
  template_path: "path/to/shared/templates"
  static_path: "path/to/shared/static"
  css_path: "shared.css"
```

## Framework-Specific Integration

### Jekyll Integration

Jekyll can integrate using includes and configuration:

```yaml
# _config.yml
shared_includes_dir: "_includes/shared"
shared_css: "/assets/css/shared.css"
```

```liquid
<!-- _layouts/default.html -->
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="{{ site.shared_css }}">
</head>
<body>
    {% include shared/header.html %}
    {{ content }}
</body>
</html>
```

### Hugo Integration

Hugo can use partial templates:

```go-template
<!-- layouts/_default/baseof.html -->
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="{{ .Site.BaseURL }}/css/shared.css">
</head>
<body>
    {{ partial "shared/header.html" . }}
    
    <main>
        {{ block "main" . }}{{ end }}
    </main>
</body>
</html>
```

### 11ty Integration

Eleventy can use includes and data:

```javascript
// .eleventy.js
module.exports = function(eleventyConfig) {
  eleventyConfig.addGlobalData("sharedCss", "/css/shared.css");
  return {
    dir: {
      includes: "_includes"
    }
  };
};
```

```liquid
<!-- _includes/layout.liquid -->
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="{{ sharedCss }}">
</head>
<body>
    {% include "shared/header.liquid" %}
    {{ content }}
</body>
</html>
```

## Template Context Considerations

### Variable Availability

Shared templates should use defensive programming for variable access:

```jinja2
<!-- Defensive variable checking -->
{% if site_name %}
    <h1>{{ site_name }}</h1>
{% elif SITENAME %}
    <h1>{{ SITENAME }}</h1>
{% elif title %}
    <h1>{{ title }}</h1>
{% else %}
    <h1>Website</h1>
{% endif %}
```

### Template Engine Compatibility

Different engines have different syntax:

| Engine | Include Syntax | Variable Syntax |
|--------|----------------|----------------|
| Jinja2 | `{% include "file.html" %}` | `{{ variable }}` |
| Liquid | `{% include file.html %}` | `{{ variable }}` |
| Go Templates | `{{ template "file.html" . }}` | `{{ .Variable }}` |

### Context Mapping

Create context adapters for different frameworks:

```jinja2
<!-- shared/header.html with context adapter -->
{% set nav_title = navigation_title or site_title or SITENAME or "Website" %}
{% set nav_url = base_url or site_url or SITEURL or "/" %}

<nav class="shared-nav">
    <a href="{{ nav_url }}">{{ nav_title }}</a>
</nav>
```

## CSS Integration Strategies

### Import Strategy

External projects import shared CSS:

```css
@import url("shared/css/shared.css");

/* Project-specific styles */
body {
    font-family: project-specific-font;
}
```

### Build-Time Concatenation

Build systems concatenate shared and project CSS:

```javascript
// webpack.config.js
module.exports = {
  entry: {
    styles: [
      './shared/css/shared.css',
      './src/css/project.css'
    ]
  }
};
```

### Runtime Loading

Templates load shared CSS at runtime:

```html
<link rel="stylesheet" href="{{ shared_css_url }}">
<link rel="stylesheet" href="{{ project_css_url }}">
```

## Best Practices

### Version Compatibility

- Pin shared component versions for stable integration
- Use semantic versioning for shared component releases
- Provide migration guides for breaking changes

### Testing Integration

```python
def test_external_integration():
    # Verify shared components work in external context
    template = render_template("external/page.html", context={
        "shared_css_path": "/shared/css/shared.css",
        "site_title": "External Site"
    })
    
    assert "shared-nav" in template
    assert "External Site" in template
```

### Documentation Requirements

External projects should document:

1. Shared component path configuration
2. Required template variables
3. CSS customization guidelines
4. Version compatibility matrix

## Migration Guide

### From Framework-Specific to Shared Components

1. **Identify common elements** (navigation, footer, meta tags)
2. **Extract to shared templates** with compatible variable names
3. **Update project templates** to include shared components
4. **Migrate CSS** to shared stylesheet with project overrides
5. **Test integration** across all target frameworks
6. **Document variable mappings** and configuration requirements

### Maintaining Backward Compatibility

- Keep original templates as fallbacks
- Use feature flags for shared component adoption
- Provide gradual migration path
- Maintain compatibility shims for common patterns

## Security Considerations

### Template Injection

- Validate all template paths and includes
- Sanitize variables passed to shared templates
- Use safe template rendering modes

### CSS Security

- Validate CSS files and imports
- Prevent CSS injection through variables
- Use Content Security Policy headers

## Future Enhancements

- **Component Package Manager** - npm-style package for shared components
- **Live Sync** - Real-time updates across integrated projects
- **Visual Testing** - Automated screenshot comparison across frameworks
- **Theme Variants** - Multiple shared theme options
- **Component Generator** - CLI tool for creating new shared components