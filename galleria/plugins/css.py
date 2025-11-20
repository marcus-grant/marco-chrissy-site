"""CSS plugin implementations for stylesheet generation."""

from .base import PluginContext, PluginResult
from .interfaces import CSSPlugin


class BasicCSSPlugin(CSSPlugin):
    """Basic CSS plugin for generating gallery stylesheets."""

    @property
    def name(self) -> str:
        return "basic-css"

    @property
    def version(self) -> str:
        return "1.0.0"

    def generate_css(self, context: PluginContext) -> PluginResult:
        """Generate CSS files from template HTML data."""
        try:
            # Validate required input fields
            if "collection_name" not in context.input_data:
                return PluginResult(
                    success=False,
                    output_data={},
                    errors=["MISSING_COLLECTION_NAME: collection_name required"]
                )

            if "html_files" not in context.input_data:
                return PluginResult(
                    success=False,
                    output_data={},
                    errors=["MISSING_HTML_FILES: html_files required"]
                )

            # Get CSS and template configurations - support both nested and direct patterns
            config = context.config or {}
            
            # Handle nested config pattern (multi-stage) vs direct config pattern (single plugin)
            if "css" in config or "template" in config:
                css_config = config.get("css", {})
                template_config = config.get("template", {})
            else:
                # Direct config access pattern - assume all config is for this plugin
                css_config = config
                template_config = config
            
            # Validate theme configuration
            theme = css_config.get("theme")
            if theme and theme not in ["light", "dark", "auto"]:
                return PluginResult(
                    success=False,
                    output_data={},
                    errors=[f"INVALID_THEME: Unknown theme: {theme}"]
                )

            collection_name = context.input_data["collection_name"]
            html_files = context.input_data["html_files"]
            
            # Generate CSS files
            css_files = []
            
            # Main gallery CSS (needs layout from template config)
            gallery_css = self._generate_gallery_css(template_config)
            css_files.append({
                "filename": "gallery.css",
                "content": gallery_css,
                "type": "gallery"
            })

            # Theme-specific CSS if theme is specified
            if theme:
                theme_css = self._generate_theme_css(theme, context.config)
                css_files.append({
                    "filename": f"theme-{theme}.css",
                    "content": theme_css,
                    "type": "theme"
                })

            # Responsive CSS if enabled
            if css_config.get("responsive", True):
                responsive_css = self._generate_responsive_css(css_config)
                css_files.append({
                    "filename": "responsive.css",
                    "content": responsive_css,
                    "type": "responsive"
                })

            return PluginResult(
                success=True,
                output_data={
                    "css_files": css_files,
                    "html_files": html_files,  # Pass through from input
                    "collection_name": collection_name,
                    "css_count": len(css_files)
                }
            )

        except Exception as e:
            return PluginResult(
                success=False,
                output_data={},
                errors=[f"CSS_ERROR: {str(e)}"]
            )

    def _generate_gallery_css(self, config: dict) -> str:
        """Generate base gallery CSS styles."""
        layout = config.get("layout", "grid")
        
        if layout == "grid":
            gallery_layout_css = """
.gallery.layout-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    padding: 1rem;
}

.gallery.layout-grid .photo-item {
    aspect-ratio: 1;
    overflow: hidden;
    border-radius: 0.5rem;
}"""
        else:
            # Default to flexbox layout
            gallery_layout_css = """
.gallery {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    padding: 1rem;
}

.gallery .photo-item {
    flex: 1 1 200px;
    max-width: 300px;
}"""

        return f"""/* Galleria Base Styles */

/* Reset and base styles */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
                 Oxygen, Ubuntu, Cantarell, sans-serif;
    line-height: 1.6;
    color: #333;
    background: #fff;
}}

/* Header styles */
header {{
    padding: 2rem 1rem;
    text-align: center;
    border-bottom: 1px solid #eee;
}}

header h1 {{
    font-size: 2.5rem;
    font-weight: 300;
    letter-spacing: -0.5px;
}}

/* Gallery layout */
{gallery_layout_css}

.photo-item {{
    transition: transform 0.2s ease;
}}

.photo-item:hover {{
    transform: scale(1.02);
}}

.photo-item a {{
    display: block;
    width: 100%;
    height: 100%;
}}

.photo-item img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}}

/* Pagination navigation */
.pagination {{
    text-align: center;
    padding: 2rem 1rem;
    border-top: 1px solid #eee;
}}

.pagination a {{
    display: inline-block;
    padding: 0.5rem 1rem;
    margin: 0 0.5rem;
    text-decoration: none;
    color: #0066cc;
    border: 1px solid #ddd;
    border-radius: 0.25rem;
    transition: background-color 0.2s ease;
}}

.pagination a:hover {{
    background-color: #f5f5f5;
}}

.pagination span {{
    margin: 0 1rem;
    color: #666;
}}

/* Footer */
footer {{
    text-align: center;
    padding: 2rem 1rem;
    color: #666;
    font-size: 0.875rem;
}}

/* Empty gallery state */
.empty-message {{
    text-align: center;
    padding: 4rem 1rem;
    color: #666;
    font-style: italic;
}}"""

    def _generate_theme_css(self, theme: str, config: dict) -> str:
        """Generate theme-specific CSS styles."""
        if theme == "dark":
            return """/* Dark Theme */
body.theme-dark {
    background: #1a1a1a;
    color: #e0e0e0;
}

.theme-dark header {
    border-bottom-color: #333;
}

.theme-dark header h1 {
    color: #fff;
}

.theme-dark .pagination {
    border-top-color: #333;
}

.theme-dark .pagination a {
    color: #4a9eff;
    border-color: #444;
    background: #2a2a2a;
}

.theme-dark .pagination a:hover {
    background-color: #333;
}

.theme-dark footer {
    color: #999;
}

.theme-dark .empty-message {
    color: #999;
}"""
        elif theme == "light":
            return """/* Light Theme (Default) */
body.theme-light {
    background: #fff;
    color: #333;
}"""
        else:  # auto theme
            return """/* Auto Theme */
@media (prefers-color-scheme: dark) {
    body.theme-auto {
        background: #1a1a1a;
        color: #e0e0e0;
    }
    
    .theme-auto header {
        border-bottom-color: #333;
    }
    
    .theme-auto header h1 {
        color: #fff;
    }
    
    .theme-auto .pagination {
        border-top-color: #333;
    }
    
    .theme-auto .pagination a {
        color: #4a9eff;
        border-color: #444;
        background: #2a2a2a;
    }
    
    .theme-auto .pagination a:hover {
        background-color: #333;
    }
    
    .theme-auto footer {
        color: #999;
    }
    
    .theme-auto .empty-message {
        color: #999;
    }
}"""

    def _generate_responsive_css(self, config: dict) -> str:
        """Generate responsive CSS for mobile and tablet devices."""
        return """/* Responsive Design */

@media (max-width: 768px) {
    header h1 {
        font-size: 2rem;
    }
    
    .gallery.layout-grid {
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 0.5rem;
        padding: 0.5rem;
    }
    
    .gallery {
        gap: 0.5rem;
        padding: 0.5rem;
    }
    
    .gallery .photo-item {
        flex: 1 1 150px;
    }
    
    .pagination {
        padding: 1rem 0.5rem;
    }
    
    .pagination a {
        padding: 0.375rem 0.75rem;
        margin: 0 0.25rem;
        font-size: 0.875rem;
    }
}

@media (max-width: 480px) {
    header {
        padding: 1rem 0.5rem;
    }
    
    header h1 {
        font-size: 1.5rem;
    }
    
    .gallery.layout-grid {
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    }
    
    .gallery .photo-item {
        flex: 1 1 120px;
    }
    
    .pagination span {
        display: block;
        margin: 0.5rem 0;
        font-size: 0.875rem;
    }
}"""