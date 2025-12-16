"""Unit tests for template plugin URL generation bugs."""


from galleria.plugins.base import PluginContext
from galleria.plugins.template import BasicTemplatePlugin


class TestBasicTemplatePluginURLBugs:
    """Test BasicTemplatePlugin URL generation bugs discovered in MVP testing."""

    def test_photo_links_should_point_to_pics_full_not_root(self, tmp_path):
        """Photo links should point to /pics/full/{filename}, not /{filename} (502 bug)."""
        plugin = BasicTemplatePlugin()

        # Create mock data as it would come from processor
        context = PluginContext(
            input_data={
                "pages": [
                    [
                        {
                            "source_path": "/home/user/photos/wedding-20250809T132034-r5a.JPG",
                            "thumbnail_path": "/absolute/path/to/output/galleries/wedding/thumbnails/wedding-20250809T132034-r5a.webp",
                            "dest_path": "/absolute/path/to/output/pics/full/wedding-20250809T132034-r5a.JPG",
                        }
                    ]
                ],
                "collection_name": "wedding",
                "total_photos": 1,
            },
            config={},
            output_dir=tmp_path,
        )

        result = plugin.generate_html(context)

        assert result.success
        html_content = result.output_data["html_files"][0]["content"]

        # EXPECTED: Links should point to /pics/full/wedding-20250809T132034-r5a.JPG
        assert 'href="../pics/full/wedding-20250809T132034-r5a.JPG"' in html_content
        assert 'href="/wedding-20250809T132034-r5a.JPG"' not in html_content
        assert 'href="wedding-20250809T132034-r5a.JPG"' not in html_content

    def test_production_photo_links_should_point_to_full_pics_url_not_root(self, tmp_path):
        """Production photo links should point to full CDN URLs for pics, not root URLs (502 bug)."""
        from build.context import BuildContext

        plugin = BasicTemplatePlugin()

        # Create production BuildContext - this might be where the bug occurs
        build_context = BuildContext(production=True)
        site_url = "https://cdn.example.com"

        context = PluginContext(
            input_data={
                "pages": [
                    [
                        {
                            "source_path": "/home/user/photos/wedding-20250809T132034-r5a.JPG",
                            "thumbnail_path": "/absolute/path/to/output/galleries/wedding/thumbnails/wedding-20250809T132034-r5a.webp",
                            "dest_path": "/absolute/path/to/output/pics/full/wedding-20250809T132034-r5a.JPG",
                        }
                    ]
                ],
                "collection_name": "wedding",
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

        # Debug: Print actual HTML content to understand current behavior
        print(f"\nProduction HTML content:\n{html_content}\n")

        # EXPECTED: Should use full CDN URLs that include /pics/full/ path
        assert 'href="https://cdn.example.com/pics/full/wedding-20250809T132034-r5a.JPG"' in html_content
        # BUG: Should NOT point to root domain without pics/full path
        assert 'href="https://cdn.example.com/wedding-20250809T132034-r5a.JPG"' not in html_content

    def test_gallery_directory_should_generate_index_html_for_direct_access(self, tmp_path):
        """Gallery directories should have index.html to handle /galleries/wedding/ URLs (404 bug)."""
        plugin = BasicTemplatePlugin()

        context = PluginContext(
            input_data={
                "pages": [
                    [
                        {
                            "source_path": "/home/user/photos/wedding-photo.JPG",
                            "thumbnail_path": "/absolute/path/to/output/galleries/wedding/thumbnails/wedding-photo.webp",
                            "dest_path": "/absolute/path/to/output/pics/full/wedding-photo.JPG",
                        }
                    ]
                ],
                "collection_name": "wedding",
                "total_photos": 1,
            },
            config={},
            output_dir=tmp_path,
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
