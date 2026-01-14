"""Unit tests for template URL filters."""


from build.context import BuildContext


class TestTemplateURLFilters:
    """Test template URL filters for context-aware URL generation."""

    def test_full_url_filter_with_production_context(self):
        """full_url filter should generate relative URLs in production context."""
        # This test will fail until we implement relative URL generation
        from galleria.template.filters import full_url

        context = BuildContext(production=True)
        site_url = "https://marco-chrissy.com"

        result = full_url("gallery.css", context, site_url)
        assert result == "/gallery.css"

    def test_full_url_filter_with_development_context(self):
        """full_url filter should generate relative URLs in development context."""
        from galleria.template.filters import full_url

        context = BuildContext(production=False)
        site_url = "http://127.0.0.1:8000"

        result = full_url("gallery.css", context, site_url)
        assert result == "/gallery.css"

    def test_full_url_filter_handles_relative_paths(self):
        """full_url filter should convert relative paths to absolute relative URLs."""
        from galleria.template.filters import full_url

        context = BuildContext(production=True)
        site_url = "https://marco-chrissy.com"

        result = full_url("galleries/wedding/thumbnails/photo.webp", context, site_url)
        assert result == "/galleries/wedding/thumbnails/photo.webp"

    def test_full_url_filter_handles_absolute_paths(self):
        """full_url filter should convert absolute paths to relative URLs."""
        from galleria.template.filters import full_url

        context = BuildContext(production=True)
        site_url = "https://marco-chrissy.com"

        # Absolute path should be converted to relative
        abs_path = "/abs/path/to/output/galleries/wedding/thumbnails/photo.webp"
        result = full_url(abs_path, context, site_url)
        assert result == "/galleries/wedding/thumbnails/photo.webp"

    def test_full_url_filter_handles_pics_directory(self):
        """full_url filter should generate relative URLs for pics directory."""
        from galleria.template.filters import full_url

        context = BuildContext(production=True)
        site_url = "https://marco-chrissy.com"

        abs_path = "/abs/path/to/output/pics/full/photo.jpg"
        result = full_url(abs_path, context, site_url)
        assert result == "/pics/full/photo.jpg"

    def test_full_url_filter_with_empty_path(self):
        """full_url filter should handle empty paths gracefully."""
        from galleria.template.filters import full_url

        context = BuildContext(production=True)
        site_url = "https://marco-chrissy.com"

        result = full_url("", context, site_url)
        assert result == ""

    def test_full_url_filter_without_leading_slash_in_site_url(self):
        """full_url filter should generate relative URLs regardless of site URL format."""
        from galleria.template.filters import full_url

        context = BuildContext(production=True)
        site_url = "https://marco-chrissy.com"  # No trailing slash

        result = full_url("gallery.css", context, site_url)
        assert result == "/gallery.css"

    def test_full_url_filter_strips_output_from_relative_paths(self):
        """full_url filter should strip output/ prefix from relative paths.

        The output/ directory IS the web root, so paths like
        output/galleries/wedding/thumbnails/photo.webp should become
        /galleries/wedding/thumbnails/photo.webp (not /output/galleries/...).
        """
        from galleria.template.filters import full_url

        context = BuildContext(production=True)
        site_url = "https://marco-chrissy.com"

        # Relative path starting with output/ - this is the bug case
        result = full_url("output/galleries/wedding/thumbnails/photo.webp", context, site_url)
        assert result == "/galleries/wedding/thumbnails/photo.webp"
