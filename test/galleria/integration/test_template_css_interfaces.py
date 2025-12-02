"""Integration tests for Template and CSS plugin interfaces."""

from galleria.plugins import PluginContext, PluginResult


class TestTemplateCSSIntegration:
    """Integration tests for Transform ↔ Template ↔ CSS plugin interaction."""

    def test_template_plugin_generates_html_from_transform_data(self, tmp_path):
        """Template plugin should generate HTML structure from Transform output.

        This test defines the contract between Transform and Template:
        - Transform outputs: {"pages": [...], "collection_name": str}
        - Template expects: pages data with photo information
        - Template outputs: HTML files with structured markup
        """
        from galleria.plugins.interfaces import TemplatePlugin

        # Arrange: Create a concrete TemplatePlugin implementation
        class TestGalleryTemplate(TemplatePlugin):
            @property
            def name(self) -> str:
                return "test-gallery-template"

            @property
            def version(self) -> str:
                return "1.0.0"

            def generate_html(self, context: PluginContext) -> PluginResult:
                """Generate HTML files from paginated photo data."""
                pages = context.input_data["pages"]
                collection_name = context.input_data["collection_name"]

                # Mock HTML generation
                html_files = []
                for page in pages:
                    page_num = page["page_number"]
                    html_filename = f"page_{page_num}.html"

                    # Generate mock HTML content
                    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{collection_name} - Page {page_num}</title>
    <link rel="stylesheet" href="gallery.css">
</head>
<body>
    <div class="gallery-container">
"""

                    for photo in page["photos"]:
                        html_content += f"""        <div class="photo-item">
            <img src="{photo["thumbnail_path"]}" alt="Photo">
        </div>
"""

                    html_content += """    </div>
</body>
</html>"""

                    html_files.append(
                        {
                            "filename": html_filename,
                            "content": html_content,
                            "page_number": page_num,
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

        # Create template and test it with Transform output data
        template = TestGalleryTemplate()

        # Mock Transform output as Template input
        transform_output = {
            "pages": [
                {
                    "page_number": 1,
                    "photos": [
                        {
                            "source_path": "/source/photos/IMG_001.jpg",
                            "dest_path": "wedding/IMG_001.jpg",
                            "thumbnail_path": "thumbnails/IMG_001_thumb.webp",
                            "thumbnail_size": (300, 200),
                        },
                        {
                            "source_path": "/source/photos/IMG_002.jpg",
                            "dest_path": "wedding/IMG_002.jpg",
                            "thumbnail_path": "thumbnails/IMG_002_thumb.webp",
                            "thumbnail_size": (300, 200),
                        },
                    ],
                    "photo_count": 2,
                },
                {
                    "page_number": 2,
                    "photos": [
                        {
                            "source_path": "/source/photos/IMG_003.jpg",
                            "dest_path": "wedding/IMG_003.jpg",
                            "thumbnail_path": "thumbnails/IMG_003_thumb.webp",
                            "thumbnail_size": (300, 200),
                        }
                    ],
                    "photo_count": 1,
                },
            ],
            "collection_name": "wedding_photos",
            "page_count": 2,
            "total_photos": 3,
        }

        context = PluginContext(
            input_data=transform_output,
            config={"theme": "minimal"},
            output_dir=tmp_path / "output",
        )

        # Act: Execute template
        result = template.generate_html(context)

        # Assert: Template output includes HTML files
        assert result.success
        assert "html_files" in result.output_data
        assert "file_count" in result.output_data
        assert result.output_data["file_count"] == 2

        # Verify HTML file structure
        html_files = result.output_data["html_files"]
        assert len(html_files) == 2
        assert html_files[0]["filename"] == "page_1.html"
        assert html_files[0]["page_number"] == 1
        assert html_files[1]["filename"] == "page_2.html"
        assert html_files[1]["page_number"] == 2

        # Verify HTML content contains photo data
        page1_html = html_files[0]["content"]
        assert "wedding_photos - Page 1" in page1_html
        assert "thumbnails/IMG_001_thumb.webp" in page1_html
        assert "thumbnails/IMG_002_thumb.webp" in page1_html
        assert "gallery-container" in page1_html

    def test_css_plugin_generates_stylesheets_from_template_data(self, tmp_path):
        """CSS plugin should generate stylesheets from Template output.

        This test defines the contract between Template and CSS:
        - Template outputs: {"html_files": [...], "collection_name": str}
        - CSS expects: HTML file information and collection metadata
        - CSS outputs: CSS files with styling for template structures
        """
        from galleria.plugins.interfaces import CSSPlugin

        # Arrange: Create a concrete CSSPlugin implementation
        class TestResponsiveCSS(CSSPlugin):
            @property
            def name(self) -> str:
                return "test-responsive-css"

            @property
            def version(self) -> str:
                return "1.0.0"

            def generate_css(self, context: PluginContext) -> PluginResult:
                """Generate CSS files for template HTML structures."""
                html_files = context.input_data["html_files"]
                collection_name = context.input_data["collection_name"]
                theme = context.config.get("theme", "default")

                # Mock CSS generation
                css_files = []

                # Generate main gallery CSS
                gallery_css = (
                    """/* Gallery styles for """
                    + collection_name
                    + """ */
.gallery-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
    padding: 1rem;
}

.photo-item {
    border: 1px solid #ddd;
    border-radius: 4px;
    overflow: hidden;
    transition: transform 0.3s ease;
}

.photo-item:hover {
    transform: scale(1.05);
}

.photo-item img {
    width: 100%;
    height: auto;
    display: block;
}

@media (max-width: 768px) {
    .gallery-container {
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 0.5rem;
        padding: 0.5rem;
    }
}
"""
                )

                css_files.append(
                    {
                        "filename": "gallery.css",
                        "content": gallery_css,
                        "type": "gallery",
                    }
                )

                # Generate theme CSS if specified
                if theme != "default":
                    theme_css = f"""/* Theme styles: {theme} */
body {{
    font-family: 'Arial', sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f5f5f5;
}}

h1 {{
    text-align: center;
    color: #333;
    margin-bottom: 2rem;
}}
"""
                    css_files.append(
                        {
                            "filename": f"theme-{theme}.css",
                            "content": theme_css,
                            "type": "theme",
                        }
                    )

                return PluginResult(
                    success=True,
                    output_data={
                        "css_files": css_files,
                        "html_files": html_files,  # Pass through for next stage
                        "collection_name": collection_name,
                        "css_count": len(css_files),
                    },
                )

        # Create CSS plugin with Template output data
        css_plugin = TestResponsiveCSS()

        # Mock Template output as CSS input
        template_output = {
            "html_files": [
                {
                    "filename": "page_1.html",
                    "content": "<html>...</html>",
                    "page_number": 1,
                },
                {
                    "filename": "page_2.html",
                    "content": "<html>...</html>",
                    "page_number": 2,
                },
            ],
            "collection_name": "wedding_photos",
            "file_count": 2,
        }

        context = PluginContext(
            input_data=template_output,
            config={"theme": "minimal"},
            output_dir=tmp_path / "output",
        )

        # Act: Execute CSS plugin
        result = css_plugin.generate_css(context)

        # Assert: CSS output includes stylesheets
        assert result.success
        assert "css_files" in result.output_data
        assert "css_count" in result.output_data
        assert result.output_data["css_count"] == 2

        # Verify CSS file structure
        css_files = result.output_data["css_files"]
        assert len(css_files) == 2
        assert css_files[0]["filename"] == "gallery.css"
        assert css_files[0]["type"] == "gallery"
        assert css_files[1]["filename"] == "theme-minimal.css"
        assert css_files[1]["type"] == "theme"

        # Verify CSS content is appropriate
        gallery_css = css_files[0]["content"]
        assert "gallery-container" in gallery_css
        assert "photo-item" in gallery_css
        assert "@media" in gallery_css  # Responsive styles
        assert "wedding_photos" in gallery_css  # Collection-specific comment

        # Verify HTML files are passed through
        assert "html_files" in result.output_data
        assert len(result.output_data["html_files"]) == 2

    def test_transform_to_template_to_css_pipeline_integration(self, tmp_path):
        """Test complete Transform → Template → CSS pipeline integration.

        This test verifies the data flow works end-to-end:
        1. Transform provides paginated photo data
        2. Template receives Transform output and generates HTML
        3. CSS receives Template output and generates stylesheets
        4. Pipeline produces final output with HTML and CSS files
        """
        from galleria.plugins.interfaces import (
            CSSPlugin,
            TemplatePlugin,
            TransformPlugin,
        )

        # Use simplified test implementations
        class TestPaginationTransform(TransformPlugin):
            @property
            def name(self) -> str:
                return "test-pagination-transform"

            @property
            def version(self) -> str:
                return "1.0.0"

            def transform_data(self, context: PluginContext) -> PluginResult:
                photos = context.input_data["photos"]
                pages = []
                for i in range(0, len(photos), 2):
                    pages.append(
                        {"page_number": len(pages) + 1, "photos": photos[i : i + 2]}
                    )

                return PluginResult(
                    success=True,
                    output_data={
                        "pages": pages,
                        "collection_name": context.input_data["collection_name"],
                        "page_count": len(pages),
                    },
                )

        class TestGalleryTemplate(TemplatePlugin):
            @property
            def name(self) -> str:
                return "test-gallery-template"

            @property
            def version(self) -> str:
                return "1.0.0"

            def generate_html(self, context: PluginContext) -> PluginResult:
                pages = context.input_data["pages"]
                html_files = []

                for page in pages:
                    html_files.append(
                        {
                            "filename": f"page_{page['page_number']}.html",
                            "page_number": page["page_number"],
                        }
                    )

                return PluginResult(
                    success=True,
                    output_data={
                        "html_files": html_files,
                        "collection_name": context.input_data["collection_name"],
                    },
                )

        class TestResponsiveCSS(CSSPlugin):
            @property
            def name(self) -> str:
                return "test-responsive-css"

            @property
            def version(self) -> str:
                return "1.0.0"

            def generate_css(self, context: PluginContext) -> PluginResult:
                css_files = [
                    {"filename": "gallery.css", "type": "gallery"},
                    {"filename": "responsive.css", "type": "responsive"},
                ]

                return PluginResult(
                    success=True,
                    output_data={
                        "css_files": css_files,
                        "html_files": context.input_data["html_files"],
                        "collection_name": context.input_data["collection_name"],
                    },
                )

        # Arrange: Create output directory
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Act: Execute Transform → Template → CSS pipeline
        transform = TestPaginationTransform()
        template = TestGalleryTemplate()
        css_plugin = TestResponsiveCSS()

        # Stage 1: Transform (mock Processor output)
        transform_context = PluginContext(
            input_data={
                "photos": [
                    {"thumbnail_path": "thumbnails/IMG_001.webp"},
                    {"thumbnail_path": "thumbnails/IMG_002.webp"},
                    {"thumbnail_path": "thumbnails/IMG_003.webp"},
                ],
                "collection_name": "test_photos",
            },
            config={"photos_per_page": 2},
            output_dir=output_dir,
        )
        transform_result = transform.transform_data(transform_context)

        # Stage 2: Template (uses Transform output as input)
        template_context = PluginContext(
            input_data=transform_result.output_data,
            config={"theme": "minimal"},
            output_dir=output_dir,
        )
        template_result = template.generate_html(template_context)

        # Stage 3: CSS (uses Template output as input)
        css_context = PluginContext(
            input_data=template_result.output_data,
            config={"theme": "minimal"},
            output_dir=output_dir,
        )
        css_result = css_plugin.generate_css(css_context)

        # Assert: End-to-end pipeline success
        assert transform_result.success
        assert template_result.success
        assert css_result.success

        # Verify data flow through pipeline
        assert transform_result.output_data["collection_name"] == "test_photos"
        assert template_result.output_data["collection_name"] == "test_photos"
        assert css_result.output_data["collection_name"] == "test_photos"

        # Verify final output contains all expected components
        final_output = css_result.output_data
        assert "html_files" in final_output
        assert "css_files" in final_output
        assert len(final_output["html_files"]) == 2  # 3 photos / 2 per page = 2 pages
        assert len(final_output["css_files"]) == 2  # gallery.css + responsive.css

        # Verify template operations
        html_files = final_output["html_files"]
        assert html_files[0]["filename"] == "page_1.html"
        assert html_files[1]["filename"] == "page_2.html"

        # Verify CSS operations
        css_files = final_output["css_files"]
        assert css_files[0]["filename"] == "gallery.css"
        assert css_files[1]["filename"] == "responsive.css"
