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
        print("DEBUG: CSS plugin started")
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
            print(f"DEBUG: Processing {len(html_files)} HTML files for collection '{collection_name}'")

            # Generate CSS files
            css_files = []

            # Main gallery CSS (needs layout from template config)
            print("DEBUG: Generating gallery CSS...")
            gallery_css = self._generate_gallery_css(template_config)
            print(f"DEBUG: Gallery CSS generated, size: {len(gallery_css)} bytes")
            css_files.append({
                "filename": "gallery.css",
                "content": gallery_css,
                "type": "gallery"
            })

            # Theme-specific CSS if theme is specified
            if theme:
                print(f"DEBUG: Generating theme CSS for '{theme}'...")
                theme_css = self._generate_theme_css(theme, context.config)
                print(f"DEBUG: Theme CSS generated, size: {len(theme_css)} bytes")
                css_files.append({
                    "filename": f"theme-{theme}.css",
                    "content": theme_css,
                    "type": "theme"
                })

            # Responsive CSS if enabled
            if css_config.get("responsive", True):
                print("DEBUG: Generating responsive CSS...")
                responsive_css = self._generate_responsive_css(css_config)
                print(f"DEBUG: Responsive CSS generated, size: {len(responsive_css)} bytes")
                css_files.append({
                    "filename": "responsive.css",
                    "content": responsive_css,
                    "type": "responsive"
                })

            print(f"DEBUG: CSS generation complete. Created {len(css_files)} CSS files.")
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
            pass
        else:
            # Default to flexbox layout
            pass


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
        # Add content size check to prevent infinite content generation
        css_content = """/* Responsive Design */

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

        # Validate content size before returning
        if len(css_content) > 1_000_000:  # 1MB limit
            raise ValueError(f"CSS content too large: {len(css_content)} bytes")

        return css_content
