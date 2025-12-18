"""Template plugin implementations for HTML generation."""

from typing import Any

from .base import PluginContext, PluginResult
from .interfaces import TemplatePlugin


class BasicTemplatePlugin(TemplatePlugin):
    """Basic template plugin for generating simple HTML gallery pages."""

    @property
    def name(self) -> str:
        return "basic-template"

    @property
    def version(self) -> str:
        return "1.0.0"

    def generate_html(self, context: PluginContext) -> PluginResult:
        """Generate HTML files from transformed photo data."""
        try:
            # Validate input data
            if "collection_name" not in context.input_data:
                return PluginResult(
                    success=False,
                    output_data={},
                    errors=["MISSING_COLLECTION_NAME: collection_name required"],
                )

            collection_name = context.input_data["collection_name"]

            # Handle different input formats
            html_files = []

            if "pages" in context.input_data:
                # Pagination transform input
                pages = context.input_data["pages"]
                for page_num, photos in enumerate(pages, 1):
                    html_content = self._generate_page_html(
                        photos, collection_name, page_num, len(pages), context
                    )
                    html_files.append(
                        {
                            "filename": f"page_{page_num}.html",
                            "content": html_content,
                            "page_number": page_num,
                        }
                    )

                # Generate index.html that redirects to first page for direct directory access
                if pages:
                    index_content = self._generate_gallery_index_html(collection_name)
                    html_files.append(
                        {
                            "filename": "index.html",
                            "content": index_content,
                            "page_number": 0,  # Special marker for index page
                        }
                    )
            elif "photos" in context.input_data:
                # Direct photos input (no pagination)
                photos = context.input_data["photos"]
                html_content = self._generate_gallery_html(
                    photos, collection_name, context
                )
                html_files.append(
                    {
                        "filename": "index.html",
                        "content": html_content,
                        "page_number": 1,
                    }
                )
            else:
                # No photos data
                html_files.append(
                    {
                        "filename": "index.html",
                        "content": self._generate_empty_gallery_html(collection_name),
                        "page_number": 1,
                    }
                )

            return PluginResult(
                success=True,
                output_data={
                    "html_files": html_files,
                    "collection_name": collection_name,
                    "file_count": len(html_files),
                },
            )

        except Exception as e:
            return PluginResult(
                success=False, output_data={}, errors=[f"TEMPLATE_ERROR: {str(e)}"]
            )

    def _generate_page_html(
        self,
        photos: list[dict[str, Any]],
        collection_name: str,
        page_num: int,
        total_pages: int,
        context: PluginContext,
    ) -> str:
        """Generate HTML for a single page of photos."""
        # Check if theme path is configured
        theme_path = context.config.get("theme_path")
        if not theme_path and "template" in context.config:
            theme_path = context.config["template"].get("theme_path")
        if theme_path:
            return self._render_theme_template(
                photos, collection_name, page_num, total_pages, context, theme_path
            )

        # Fallback to original hardcoded implementation
        return self._generate_hardcoded_html(
            photos, collection_name, page_num, total_pages, context
        )

    def _generate_gallery_html(
        self, photos: list[dict[str, Any]], collection_name: str, context: PluginContext
    ) -> str:
        """Generate HTML for complete gallery (no pagination)."""
        return self._generate_page_html(photos, collection_name, 1, 1, context)

    def _generate_empty_gallery_html(self, collection_name: str) -> str:
        """Generate HTML for empty gallery."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{collection_name}</title>
    <link rel="stylesheet" href="gallery.css">
</head>
<body>
    <header>
        <h1>{collection_name}</h1>
    </header>

    <main class="gallery">
        <p class="empty-message">No photos found in this collection.</p>
    </main>

    <footer>
        <p>Generated with Galleria</p>
    </footer>
</body>
</html>"""

    def _generate_gallery_index_html(self, collection_name: str) -> str:
        """Generate index.html that redirects to first page for gallery directory access."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="0; url=page_1.html">
    <title>{collection_name}</title>
    <link rel="stylesheet" href="gallery.css">
</head>
<body>
    <header>
        <h1>{collection_name}</h1>
    </header>

    <main class="gallery">
        <p>Redirecting to gallery... If you are not redirected, <a href="page_1.html">click here</a>.</p>
    </main>

    <footer>
        <p>Generated with Galleria</p>
    </footer>
</body>
</html>"""

    def _make_url(self, path: str, context: PluginContext) -> str:
        """Convert path to URL using BuildContext and site_url from metadata.

        Args:
            path: File path to convert to URL
            context: Plugin context containing metadata with build_context and site_url

        Returns:
            Full URL if BuildContext available, otherwise relative path
        """
        if not path:
            return path

        # Check if BuildContext is available in metadata
        build_context = context.metadata.get("build_context")
        site_url = context.metadata.get("site_url", "")

        if build_context is not None and site_url:
            # Use context-aware URL filter (import locally to avoid circular import)
            from ..template.filters import full_url
            return full_url(path, build_context, site_url)
        else:
            # Fallback to original relative path method
            return self._make_relative_path(path)

    def _make_relative_path(self, path: str) -> str:
        """Convert absolute filesystem path to relative web path.

        Args:
            path: Absolute filesystem path (e.g., /abs/path/to/output/galleries/wedding/thumbnails/img.webp)

        Returns:
            Relative web path (e.g., thumbnails/img.webp)
        """
        if not path:
            return path

        # Extract the filename
        import os

        filename = os.path.basename(path)

        # Determine relative path based on file location or type
        if "thumbnails" in path:
            return f"thumbnails/{filename}"
        elif "pics" in path or path.endswith((".jpg", ".jpeg", ".JPG", ".JPEG")):
            # For full-size photos, we want to link to the CDN or pics directory
            return f"../pics/full/{filename}"
        elif path.endswith((".webp", ".WEBP")):
            # For thumbnails (webp files), they should be in thumbnails directory
            return f"thumbnails/{filename}"
        else:
            # Fallback to just the filename
            return filename

    def _render_theme_template(
        self,
        photos: list[dict[str, Any]],
        collection_name: str,
        page_num: int,
        total_pages: int,
        context: PluginContext,
        theme_path: str,
    ) -> str:
        """Render HTML using theme template files."""
        from ..theme.loader import TemplateLoader

        # Get shared theme path from config
        shared_theme_path = context.config.get("shared_theme_path")
        if not shared_theme_path and "template" in context.config:
            shared_theme_path = context.config["template"].get("shared_theme_path")
        loader = TemplateLoader(theme_path, shared_theme_path)

        # Prepare photo data for template
        template_photos = []
        for photo in photos:
            thumb_path = photo.get("thumbnail_path", photo.get("dest_path", ""))
            photo_path = photo.get("dest_path", "")

            template_photos.append({
                "thumb_url": self._make_url(thumb_path, context),
                "photo_url": self._make_url(photo_path, context),
                "collection_name": collection_name,
            })

        # Get shared CSS files from context if available
        css_files = context.input_data.get("css_files", [])
        shared_css_files = [f for f in css_files if f.get("type") == "shared"]

        # Load and render gallery template
        template = loader.load_template("gallery.j2.html")
        return template.render(
            collection_name=collection_name,
            photos=template_photos,
            page_num=page_num,
            total_pages=total_pages,
            shared_css_files=shared_css_files,
        )

    def _generate_hardcoded_html(
        self,
        photos: list[dict[str, Any]],
        collection_name: str,
        page_num: int,
        total_pages: int,
        context: PluginContext,
    ) -> str:
        """Generate HTML using original hardcoded implementation."""
        # Support both nested and direct config patterns
        config = context.config
        if "template" in config:
            template_config = config["template"]
        else:
            template_config = config

        theme = template_config.get("theme", "minimal")
        layout = template_config.get("layout", "grid")

        # Build photo gallery HTML
        photo_html = ""
        for photo in photos:
            thumb_path = photo.get("thumbnail_path", photo.get("dest_path", ""))
            photo_path = photo.get("dest_path", "")

            # Convert paths to URLs using context-aware filter
            thumb_url = self._make_url(thumb_path, context)
            photo_url = self._make_url(photo_path, context)

            photo_html += f"""
            <div class="photo-item">
                <a href="{photo_url}">
                    <img src="{thumb_url}" alt="Photo from {collection_name}" loading="lazy">
                </a>
            </div>"""

        # Build pagination navigation
        nav_html = ""
        if total_pages > 1:
            nav_html = '<nav class="pagination">'
            if page_num > 1:
                nav_html += f'<a href="page_{page_num - 1}.html">← Previous</a>'
            nav_html += f"<span>Page {page_num} of {total_pages}</span>"
            if page_num < total_pages:
                nav_html += f'<a href="page_{page_num + 1}.html">Next →</a>'
            nav_html += "</nav>"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{collection_name} - Page {page_num}</title>
    <link rel="stylesheet" href="gallery.css">
</head>
<body class="theme-{theme}">
    <header>
        <h1>{collection_name}</h1>
    </header>

    <main class="gallery layout-{layout}">
        {photo_html}
    </main>

    {nav_html}

    <footer>
        <p>Generated with Galleria</p>
    </footer>
</body>
</html>"""
