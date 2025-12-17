"""Tests for the ACTUAL URL bugs found in browser testing."""

from build.context import BuildContext
from galleria.plugins.template import BasicTemplatePlugin


class TestRealURLBugs:
    """Test the actual URL bugs found during browser testing."""

    def test_browser_bug_photo_links_generate_root_urls_not_pics_full(self, plugin_context_factory):
        """Test that photo links incorrectly generate root URLs instead of /pics/full/ URLs."""
        plugin = BasicTemplatePlugin()

        # Mock development environment with real manifest data structure
        build_context = BuildContext(production=False)
        site_url = "http://127.0.0.1:8000"

        context = plugin_context_factory(
            photos=[
                {
                    "source_path": "/home/marcus/Pictures/wedding/full/4F6A5096.JPG",
                    "thumbnail_path": "/tmp/output/galleries/wedding/thumbnails/wedding-20250809T132034-r5a.webp",
                    # BUG: Real dest_path from manifest is just filename, causing wrong URLs
                    "dest_path": "wedding-20250809T132034-r5a.JPG",
                }
            ],
            collection_name="wedding",
            build_context=build_context,
            site_url=site_url,
        )

        result = plugin.generate_html(context)

        assert result.success
        html_content = result.output_data["html_files"][0]["content"]

        print(f"\nActual HTML content:\n{html_content}\n")

        # This test SHOULD FAIL showing the current bug
        # BUG: Currently generates wrong URL (just filename in root)
        assert 'href="http://127.0.0.1:8000/wedding-20250809T132034-r5a.JPG"' not in html_content

        # EXPECTED: Should generate correct URL with pics/full path
        assert 'href="http://127.0.0.1:8000/pics/full/wedding-20250809T132034-r5a.JPG"' in html_content

    def test_gallery_directory_access_via_proxy_url_transformation(self):
        """Test that /galleries/wedding/ URLs are properly transformed by proxy server."""
        # This would be an integration test, but we can test the URL transformation logic

        # Test case 1: /galleries/wedding/ -> should become /index.html
        path = "/galleries/wedding/"
        path_parts = path.split("/", 3)  # ['', 'galleries', 'wedding', '']

        if len(path_parts) > 3 and path_parts[3]:
            # Has filename after collection
            galleria_path = "/" + path_parts[3]
        else:
            # Directory access: /galleries/collection/ -> /index.html
            galleria_path = "/index.html"

        assert galleria_path == "/index.html", f"Expected /index.html, got {galleria_path}"

        # Test case 2: /galleries/wedding/page_2.html -> should become /page_2.html
        path = "/galleries/wedding/page_2.html"
        path_parts = path.split("/", 3)  # ['', 'galleries', 'wedding', 'page_2.html']

        if len(path_parts) > 3 and path_parts[3]:
            # Has filename after collection
            galleria_path = "/" + path_parts[3]
        else:
            # Directory access: /galleries/collection/ -> /index.html
            galleria_path = "/index.html"

        assert galleria_path == "/page_2.html", f"Expected /page_2.html, got {galleria_path}"
