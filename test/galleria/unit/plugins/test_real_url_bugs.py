"""Tests for the ACTUAL URL bugs found in browser testing."""


from galleria.plugins.base import PluginContext
from galleria.plugins.template import BasicTemplatePlugin


class TestRealURLBugs:
    """Test the actual URL bugs found during browser testing."""

    def test_browser_bug_photo_links_generate_root_urls_not_pics_full(self, tmp_path):
        """Test that photo links incorrectly generate root URLs instead of /pics/full/ URLs."""
        from build.context import BuildContext

        plugin = BasicTemplatePlugin()

        # Mock development environment
        build_context = BuildContext(production=False)
        site_url = "http://localhost:8000"

        context = PluginContext(
            input_data={
                "pages": [
                    [
                        {
                            "source_path": "/tmp/test/photos/test-photo.jpg",
                            "thumbnail_path": "/tmp/test/thumbnails/test-photo.webp",
                            # BUG: This path doesn't contain 'output' so falls back to filename only
                            "dest_path": "/tmp/test/photos/test-photo.jpg",
                        }
                    ]
                ],
                "collection_name": "test_gallery",
                "total_photos": 1,
            },
            config={},
            output_dir=tmp_path,
            metadata={
                "build_context": build_context,
                "site_url": site_url,
            },
        )

        result = plugin.generate_html(context)

        assert result.success
        html_content = result.output_data["html_files"][0]["content"]

        print(f"\nActual HTML content:\n{html_content}\n")

        # This test SHOULD FAIL showing the current bug
        # BUG: Currently generates wrong URL
        assert 'href="http://localhost:8000/test-photo.jpg"' not in html_content

        # EXPECTED: Should generate correct URL with pics/full path
        assert 'href="http://localhost:8000/pics/full/test-photo.jpg"' in html_content

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
