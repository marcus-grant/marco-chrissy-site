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
                    errors=["MISSING_COLLECTION_NAME: collection_name required"],
                )

            if "html_files" not in context.input_data:
                return PluginResult(
                    success=False,
                    output_data={},
                    errors=["MISSING_HTML_FILES: html_files required"],
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
                    errors=[f"INVALID_THEME: Unknown theme: {theme}"],
                )

            collection_name = context.input_data["collection_name"]
            html_files = context.input_data["html_files"]

            # Check if theme path is configured
            theme_path = context.config.get("theme_path")
            if theme_path:
                css_files = self._read_theme_css_files(theme_path, css_config)
            else:
                # Generate CSS files using hardcoded implementation
                css_files = []

                # Main gallery CSS (needs layout from template config)
                gallery_css = self._generate_gallery_css(template_config)
                css_files.append(
                    {"filename": "gallery.css", "content": gallery_css, "type": "gallery"}
                )

            # Theme-specific CSS if theme is specified
            if theme:
                theme_css = self._generate_theme_css(theme, context.config)
                css_files.append(
                    {
                        "filename": f"theme-{theme}.css",
                        "content": theme_css,
                        "type": "theme",
                    }
                )

            # Shared CSS files if shared theme path is configured
            shared_theme_path = css_config.get("shared_theme_path")
            if shared_theme_path:
                shared_css_files = self._read_shared_css_files(shared_theme_path)
                css_files.extend(shared_css_files)

            # Responsive CSS if enabled
            if css_config.get("responsive", True):
                responsive_css = self._generate_responsive_css(css_config)
                css_files.append(
                    {
                        "filename": "responsive.css",
                        "content": responsive_css,
                        "type": "responsive",
                    }
                )

            return PluginResult(
                success=True,
                output_data={
                    "css_files": css_files,
                    "html_files": html_files,  # Pass through from input
                    "collection_name": collection_name,
                    "css_count": len(css_files),
                },
            )

        except Exception as e:
            return PluginResult(
                success=False, output_data={}, errors=[f"CSS_ERROR: {str(e)}"]
            )

    def _generate_gallery_css(self, config: dict) -> str:
        """Generate base gallery CSS styles."""
        layout = config.get("layout", "grid")

        if layout == "grid":
            return """/* Grid Layout Gallery Styles */
.gallery.layout-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    padding: 1rem;
    max-width: 1200px;
    margin: 0 auto;
}

.gallery.layout-grid .photo-item {
    position: relative;
    overflow: hidden;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.gallery.layout-grid .photo-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.gallery.layout-grid .photo-item img {
    width: 100%;
    height: auto;
    display: block;
}

/* Base Gallery Styles */
header {
    text-align: center;
    padding: 2rem 0;
    border-bottom: 1px solid #eee;
    margin-bottom: 2rem;
}

header h1 {
    margin: 0;
    font-size: 2.5rem;
    color: #333;
    font-weight: 300;
}

.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    padding: 2rem 0;
    border-top: 1px solid #eee;
    margin-top: 2rem;
}

.pagination a {
    text-decoration: none;
    padding: 0.5rem 1rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    color: #007bff;
    background: #fff;
    transition: background-color 0.2s ease;
}

.pagination a:hover {
    background-color: #f8f9fa;
}

.pagination span {
    font-weight: 500;
    color: #666;
}

footer {
    text-align: center;
    padding: 2rem 0;
    color: #666;
    font-size: 0.875rem;
}

.empty-message {
    text-align: center;
    color: #666;
    font-style: italic;
    padding: 3rem 0;
}"""
        else:
            # Default to flexbox layout
            return """/* Flexbox Layout Gallery Styles */
.gallery {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    padding: 1rem;
    max-width: 1200px;
    margin: 0 auto;
}

.gallery .photo-item {
    flex: 1 1 200px;
    max-width: 300px;
    position: relative;
    overflow: hidden;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.gallery .photo-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.gallery .photo-item img {
    width: 100%;
    height: auto;
    display: block;
}

/* Base Gallery Styles */
header {
    text-align: center;
    padding: 2rem 0;
    border-bottom: 1px solid #eee;
    margin-bottom: 2rem;
}

header h1 {
    margin: 0;
    font-size: 2.5rem;
    color: #333;
    font-weight: 300;
}

.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    padding: 2rem 0;
    border-top: 1px solid #eee;
    margin-top: 2rem;
}

.pagination a {
    text-decoration: none;
    padding: 0.5rem 1rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    color: #007bff;
    background: #fff;
    transition: background-color 0.2s ease;
}

.pagination a:hover {
    background-color: #f8f9fa;
}

.pagination span {
    font-weight: 500;
    color: #666;
}

footer {
    text-align: center;
    padding: 2rem 0;
    color: #666;
    font-size: 0.875rem;
}

.empty-message {
    text-align: center;
    color: #666;
    font-style: italic;
    padding: 3rem 0;
}"""

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

    def _read_theme_css_files(self, theme_path: str, css_config: dict) -> list[dict]:
        """Read CSS files from theme directory.

        Args:
            theme_path: Path to theme directory
            css_config: CSS configuration

        Returns:
            List of CSS file dictionaries
        """
        from pathlib import Path

        css_files = []
        theme_css_dir = Path(theme_path) / "static" / "css"

        if not theme_css_dir.exists():
            return css_files

        # Read all CSS files, with custom.css loaded last for highest priority
        css_file_paths = list(theme_css_dir.glob("*.css"))
        css_file_paths.sort(key=lambda p: (p.name == "custom.css", p.name))

        for css_file_path in css_file_paths:
            try:
                css_content = css_file_path.read_text(encoding="utf-8")
                css_files.append({
                    "filename": css_file_path.name,
                    "content": css_content,
                    "type": "theme"
                })
            except (OSError, UnicodeDecodeError):
                # Skip files that can't be read
                continue

        return css_files

    def _read_shared_css_files(self, shared_theme_path: str) -> list[dict]:
        """Read CSS files from shared theme directory.
        
        Args:
            shared_theme_path: Path to shared theme directory
            
        Returns:
            List of CSS file dictionaries
        """
        from pathlib import Path
        
        css_files = []
        shared_css_dir = Path(shared_theme_path) / "static" / "css"
        
        if not shared_css_dir.exists():
            return css_files
        
        # Read all shared CSS files
        for css_file_path in shared_css_dir.glob("*.css"):
            try:
                content = css_file_path.read_text(encoding='utf-8')
                css_files.append({
                    "filename": css_file_path.name,
                    "content": content,
                    "type": "shared"
                })
            except (OSError, UnicodeDecodeError):
                # Skip files that can't be read
                continue
        
        return css_files
