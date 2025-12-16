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
