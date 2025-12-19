"""Integration tests for theme system with plugin pipeline."""



class TestThemeSystemIntegration:
    """Test theme file loading and integration with plugin pipeline."""

    def test_theme_directory_loading_and_template_rendering(self, temp_filesystem, config_file_factory):
        """Test loading theme files and rendering through plugin pipeline.

        Integration test covering:
        - Theme directory structure validation
        - Jinja2 template loading from theme files
        - CSS file reading from theme static directory
        - Template plugin using theme files instead of hardcoded strings
        - CSS plugin using theme files instead of hardcoded strings
        - Full pipeline: theme files → plugin processing → output validation
        """
        from pathlib import Path

        from galleria.plugins.css import BasicCSSPlugin
        from galleria.plugins.template import BasicTemplatePlugin
        from galleria.theme.loader import TemplateLoader
        from galleria.theme.validator import ThemeValidator

        # Create theme directory structure
        theme_dir = temp_filesystem / "themes" / "basic"
        theme_dir.mkdir(parents=True)

        # Create theme.json
        theme_config = {
            "name": "Basic Theme",
            "version": "1.0.0",
            "templates": ["gallery.html", "page.html"],
            "css": ["gallery.css"]
        }
        config_file_factory(theme_dir / "theme.json", theme_config)

        # Create template files
        templates_dir = theme_dir / "templates"
        templates_dir.mkdir()

        gallery_template = '''<!DOCTYPE html>
<html>
<head><title>{{ collection_name }}</title></head>
<body>
    <h1>{{ collection_name }}</h1>
    <div class="gallery">
        {% for photo in photos %}
        <div class="photo">
            <a href="{{ photo.photo_url }}">
                <img src="{{ photo.thumb_url }}" alt="Photo from {{ photo.collection_name }}" loading="lazy">
            </a>
        </div>
        {% endfor %}
    </div>
</body>
</html>'''
        (templates_dir / "gallery.j2.html").write_text(gallery_template)

        # Create CSS files
        css_dir = theme_dir / "static" / "css"
        css_dir.mkdir(parents=True)

        gallery_css = '''.gallery { display: grid; }
.photo { border: 1px solid #ccc; }'''
        (css_dir / "gallery.css").write_text(gallery_css)

        # Test theme validation
        validator = ThemeValidator()
        assert validator.validate_theme_directory(theme_dir)

        # Test template loading
        loader = TemplateLoader(theme_dir)
        loader.load_template("gallery.j2.html")

        # Test template rendering through plugin
        from galleria.plugins.base import PluginContext

        plugin_config = {"theme_path": str(theme_dir)}
        test_data = {
            "collection_name": "Test Gallery",
            "photos": [
                {"filename": "photo1.jpg", "dest_path": "photos/photo1.jpg", "thumbnail_path": "thumbnails/photo1.webp"},
                {"filename": "photo2.jpg", "dest_path": "photos/photo2.jpg", "thumbnail_path": "thumbnails/photo2.webp"}
            ]
        }

        context = PluginContext(
            input_data=test_data,
            config=plugin_config,
            output_dir=Path(temp_filesystem),
            metadata={}
        )

        template_plugin = BasicTemplatePlugin()
        result = template_plugin.generate_html(context)

        assert result.success
        assert "html_files" in result.output_data
        html_files = result.output_data["html_files"]
        assert len(html_files) > 0

        html_content = html_files[0]["content"]
        assert "Test Gallery" in html_content
        assert "photo1" in html_content
        assert "photo2" in html_content

        # Test CSS loading through plugin
        css_plugin = BasicCSSPlugin()

        # CSS plugin expects HTML files in input data
        css_context = PluginContext(
            input_data={
                "collection_name": "Test Gallery",
                "html_files": result.output_data["html_files"]
            },
            config=plugin_config,
            output_dir=Path(temp_filesystem),
            metadata={}
        )

        css_result = css_plugin.generate_css(css_context)

        assert css_result.success
        assert "css_files" in css_result.output_data
        css_files = css_result.output_data["css_files"]
        assert len(css_files) > 0

        # Check theme CSS file is loaded correctly
        theme_css_file = next((f for f in css_files if f["filename"] == "gallery.css"), None)
        assert theme_css_file is not None
        assert ".gallery { display: grid; }" in theme_css_file["content"]
        assert ".photo { border: 1px solid #ccc; }" in theme_css_file["content"]

