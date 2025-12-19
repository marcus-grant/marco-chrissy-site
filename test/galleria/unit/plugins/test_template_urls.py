"""Unit tests for template plugin URL generation bugs."""

from build.context import BuildContext
from galleria.plugins.template import BasicTemplatePlugin


class TestBasicTemplatePluginURLBugs:
    """Test BasicTemplatePlugin URL generation bugs discovered in MVP testing."""

    def test_development_urls_use_relative_paths(self, plugin_context_factory):
        """Development mode should generate relative URLs without full domain."""
        plugin = BasicTemplatePlugin()

        context = plugin_context_factory(
            photos=[
                {
                    "source_path": "/fake/source/wedding-photo.JPG",
                    "thumbnail_path": "/fake/thumbnails/wedding-photo.webp",
                    "dest_path": "wedding-photo.JPG",  # Real manifest data
                }
            ],
            collection_name="wedding",
        )

        result = plugin.generate_html(context)

        assert result.success
        html_content = result.output_data["html_files"][0]["content"]

        # EXPECTED: Links should point to /pics/full/wedding-photo.JPG without domain
        assert 'href="../pics/full/wedding-photo.JPG"' in html_content
        assert 'href="/wedding-photo.JPG"' not in html_content
        assert 'href="wedding-photo.JPG"' not in html_content

    def test_production_urls_use_full_domain_paths(self, plugin_context_factory):
        """Production mode should generate full CDN URLs with domain."""
        plugin = BasicTemplatePlugin()

        # Create production BuildContext
        build_context = BuildContext(production=True)
        site_url = "https://cdn.example.com"

        context = plugin_context_factory(
            photos=[
                {
                    "source_path": "/fake/source/wedding-photo.JPG",
                    "thumbnail_path": "/fake/thumbnails/wedding-photo.webp",
                    "dest_path": "wedding-photo.JPG",  # Real manifest data
                }
            ],
            collection_name="wedding",
            build_context=build_context,
            site_url=site_url,
        )

        result = plugin.generate_html(context)

        assert result.success
        html_content = result.output_data["html_files"][0]["content"]

        # EXPECTED: Should use full CDN URLs that include /pics/full/ path
        assert 'href="https://cdn.example.com/pics/full/wedding-photo.JPG"' in html_content
        # Should NOT point to root domain without pics/full path
        assert 'href="https://cdn.example.com/wedding-photo.JPG"' not in html_content

    def test_gallery_directory_should_generate_index_html_for_direct_access(
        self, plugin_context_factory
    ):
        """Gallery directories should have index.html to handle /galleries/wedding/ URLs (404 bug)."""
        plugin = BasicTemplatePlugin()

        context = plugin_context_factory(
            photos=[
                {
                    "source_path": "/fake/source/wedding-photo.JPG",
                    "thumbnail_path": "/fake/thumbnails/wedding-photo.webp",
                    "dest_path": "wedding-photo.JPG",
                }
            ],
            collection_name="wedding",
        )

        result = plugin.generate_html(context)

        assert result.success
        html_files = result.output_data["html_files"]

        # ISSUE: Currently only generates page_1.html
        # EXPECTED: Should also generate index.html that redirects or serves first page content
        filenames = [html_file["filename"] for html_file in html_files]
        print(f"\nGenerated HTML files: {filenames}\n")

        # This test should fail - we expect index.html but probably only get page_1.html
        assert "index.html" in filenames, f"Expected index.html in {filenames} for gallery directory access"

    def test_empty_photo_paths_should_fail_gracefully(self, plugin_context_factory):
        """Template plugin should handle empty dest_path and thumbnail_path gracefully.

        This reproduces the regression where all thumbnail links are empty href=\"\"
        because photo data contains empty strings instead of valid paths.
        """
        plugin = BasicTemplatePlugin()

        # This simulates the actual bug - empty paths from broken photo processing
        context = plugin_context_factory(
            photos=[
                {
                    "source_path": "/fake/source/wedding-photo.JPG",
                    "thumbnail_path": "",  # EMPTY - this is the bug
                    "dest_path": "",       # EMPTY - this is the bug
                }
            ],
            collection_name="wedding",
        )

        result = plugin.generate_html(context)
        assert result.success
        html_content = result.output_data["html_files"][0]["content"]

        # Template should handle empty paths gracefully with placeholder
        assert 'href=""' not in html_content, "Found empty href attributes - should use placeholder"
        assert 'src=""' not in html_content, "Found empty src attributes - should use placeholder"
        assert 'href="#missing-photo-path"' in html_content, "Should use placeholder for missing photo path"
        assert 'src="#missing-photo-path"' in html_content, "Should use placeholder for missing thumbnail path"

    def test_template_includes_shared_css_when_shared_theme_configured(self, plugin_context_factory, temp_filesystem):
        """Template plugin should directly read and link shared CSS files when shared_theme_path is configured.

        This tests the pipeline order issue fix - template needs to include shared CSS
        even when CSS plugin hasn't run yet.
        """

        # Create shared theme with CSS file
        shared_dir = temp_filesystem / "themes" / "shared"
        shared_css_dir = shared_dir / "static" / "css"
        shared_css_dir.mkdir(parents=True)

        shared_css_file = shared_css_dir / "shared.css"
        shared_css_file.write_text("#shared-navbar { background: red; }")

        # Create minimal theme directory and template
        theme_dir = temp_filesystem / "galleria" / "themes" / "minimal" / "templates"
        theme_dir.mkdir(parents=True)

        # Create minimal gallery template that includes shared CSS
        gallery_template = theme_dir / "gallery.j2.html"
        gallery_template.write_text("""<!DOCTYPE html>
<html>
<head>
    <title>{{ collection_name }}</title>
    <link rel="stylesheet" href="gallery.css">
    {% if shared_css_files %}{% for css_file in shared_css_files %}<link rel="stylesheet" href="{{ css_file.filename }}">
    {% endfor %}{% endif %}
</head>
<body>
    {% for photo in photos %}
    <a href="{{ photo.photo_url }}"><img src="{{ photo.thumb_url }}"></a>
    {% endfor %}
</body>
</html>""")

        plugin = BasicTemplatePlugin()

        context = plugin_context_factory(
            photos=[
                {
                    "source_path": "/fake/source/wedding-photo.JPG",
                    "thumbnail_path": "/fake/thumbnails/wedding-photo.webp",
                    "dest_path": "wedding-photo.JPG",
                }
            ],
            collection_name="wedding",
            config={
                "template": {
                    "theme_path": str(temp_filesystem / "galleria" / "themes" / "minimal"),
                    "THEME_TEMPLATES_OVERRIDES": str(shared_dir)
                }
            }
        )

        result = plugin.generate_html(context)
        assert result.success
        html_content = result.output_data["html_files"][0]["content"]

        # Template should include shared CSS link
        assert 'shared.css' in html_content, "Template should link to shared CSS file"
        assert '<link rel="stylesheet" href="shared.css">' in html_content, "Template should have proper shared CSS link tag"
