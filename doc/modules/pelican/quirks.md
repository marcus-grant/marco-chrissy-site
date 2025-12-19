# Pelican Quirks and Workarounds

## Overview

This document covers Pelican-specific behaviors, limitations, and workarounds needed for proper shared component integration.

## Automatic HTML Generation Issues

### Automatic Title Generation

**Issue:** Pelican automatically generates `<hgroup>` elements and site titles that conflict with shared component headers.

**Symptoms:**
- Duplicate navigation bars
- Inconsistent page titles
- Extra `<hgroup>` elements in HTML output

**Workaround:**
Override the title block in templates to prevent automatic generation:

```jinja2
{% block title %}{% endblock %}
```

**Implementation:** Applied in `themes/shared/templates/base.html`

### Automatic Site Name Insertion

**Issue:** Pelican inserts `SITENAME` in various template contexts, causing duplicate site branding.

**Workaround:**
Use conditional logic to avoid duplication:

```jinja2
{% if not shared_header_included %}
    <h1>{{ SITENAME }}</h1>
{% endif %}
```

## Template Override Limitations

### Override Path Behavior

**Issue:** `THEME_TEMPLATES_OVERRIDES` must be a string path, not a list of paths.

**Configuration Format:**
```python
# Correct
THEME_TEMPLATES_OVERRIDES = "themes/shared/templates"

# Incorrect (would be nice but not supported)
THEME_TEMPLATES_OVERRIDES = [
    "themes/shared/templates",
    "themes/custom/templates"
]
```

### Template Resolution Order

**Behavior:** Pelican checks override directory first, then theme directory.

**Implication:** Override templates completely replace theme templates; no automatic merging.

**Best Practice:** Keep override templates minimal and focused on shared component integration only.

## Configuration Quirks

### Schema Validation Requirements

**Issue:** Pelican configuration schema requires exact setting names.

**Critical Detail:** Setting must be `THEME_TEMPLATES_OVERRIDES` (plural), not `THEME_TEMPLATE_OVERRIDES` (singular).

**Schema Location:** `config/schema/galleria.json`

### Path Resolution

**Issue:** Template override paths are resolved relative to the project root, not the config directory.

**Correct Path:** `themes/shared/templates`
**Incorrect Path:** `config/themes/shared/templates`

## Static File Handling

### CSS Integration

**Issue:** Shared CSS files must be copied to output directory manually or via Pelican's static file system.

**Solution:** Configure Pelican to copy shared static files:

```python
STATIC_PATHS = [
    'themes/shared/static',
    # other static paths
]
```

**Template Reference:**
```html
<link rel="stylesheet" href="{{ SITEURL }}/theme/css/shared.css">
```

## Template Context Limitations

### Variable Scope

**Issue:** Template variables from one system (Galleria) are not available in Pelican templates.

**Workaround:** Use conditional checks for variable existence:

```jinja2
{% if collection_name %}
    <!-- Galleria context -->
    <title>Gallery: {{ collection_name }}</title>
{% elif SITENAME %}
    <!-- Pelican context -->
    <title>{{ SITENAME }}</title>
{% endif %}
```

### Template Function Availability

**Issue:** Custom template functions/filters from one system may not work in the other.

**Best Practice:** Keep shared templates simple and use only standard Jinja2 functions.

## Build Process Considerations

### Template Override Loading

**Issue:** Template overrides are loaded at Pelican startup, not dynamically.

**Implication:** Changes to override templates require restarting the development server.

**Development Workflow:** Use `uv run site serve` which handles restarts automatically.

### Output Directory Conflicts

**Issue:** Both Pelican and Galleria write to the same output directory.

**Coordination Required:** Ensure output paths don't conflict:
- Pelican: Root level pages (`/`, `/about/`)
- Galleria: Gallery subdirectory (`/galleries/wedding/`)

## Testing Considerations

### Template Override Testing

**Challenge:** Testing template overrides requires full Pelican build process.

**Approach:** Use E2E tests that verify actual HTML output:

```python
def test_shared_component_integration():
    # Build site
    result = subprocess.run(["uv", "run", "site", "build"], cwd=temp_dir)
    
    # Check for shared navbar in output
    output_html = Path(temp_dir / "output" / "index.html").read_text()
    assert "shared-nav" in output_html
```

### Mock Limitations

**Issue:** Mocking Pelican's template system is complex and fragile.

**Best Practice:** Use real filesystem tests with temporary directories for reliable results.

## Debugging Tips

### Template Not Loading

1. Check `THEME_TEMPLATES_OVERRIDES` setting
2. Verify override file exists and has correct name
3. Check file permissions
4. Restart development server

### Missing Shared Components

1. Verify shared template files exist
2. Check include paths in override templates
3. Ensure shared CSS is being copied to output
4. Check browser network tab for 404s

### CSS Not Applied

1. Verify CSS file path in template
2. Check `SITEURL` configuration
3. Ensure CSS file is copied to output directory
4. Check for CSS specificity conflicts

## Known Issues

### Template Inheritance Complexity

**Issue:** Combining template overrides with template inheritance can create confusing template resolution paths.

**Recommendation:** Keep override templates simple and self-contained when possible.

### Development Server Caching

**Issue:** Pelican's development server may cache template files aggressively.

**Workaround:** Use `uv run site serve` which includes proper cache invalidation for shared components.