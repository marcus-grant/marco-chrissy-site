"""Unit tests for theme-based BasicTemplatePlugin."""


from galleria.plugins.base import PluginContext
from galleria.plugins.template import BasicTemplatePlugin


class TestThemeBasedTemplatePlugin:
    """Test BasicTemplatePlugin with theme system integration."""

    def test_generate_html_with_theme_files(self, temp_filesystem):
        """BasicTemplatePlugin should use theme files instead of hardcoded HTML."""
        # Create theme structure
        theme_dir = temp_filesystem / "themes" / "basic"
        templates_dir = theme_dir / "templates"
        templates_dir.mkdir(parents=True)

        # Create theme.json
        (theme_dir / "theme.json").write_text('{"name": "basic", "version": "1.0.0"}')

        # Create base template with PicoCSS
        base_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Gallery{% endblock %}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@1/css/pico.min.css">
    <link rel="stylesheet" href="custom.css">
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>"""
        (templates_dir / "base.j2.html").write_text(base_template)

        # Create gallery template
        gallery_template = """{% extends "base.j2.html" %}
{% block title %}{{ collection_name }}{% endblock %}
{% block content %}
<header><h1>{{ collection_name }}</h1></header>
<main class="gallery">
{% for photo in photos %}
    <div class="photo-item">
        <a href="{{ photo.photo_url }}">
            <img src="{{ photo.thumb_url }}" alt="Photo from {{ collection_name }}" loading="lazy">
        </a>
    </div>
{% endfor %}
</main>
{% endblock %}"""
        (templates_dir / "gallery.j2.html").write_text(gallery_template)

        # Create empty gallery template
        empty_template = """{% extends "base.j2.html" %}
{% block title %}{{ collection_name }}{% endblock %}
{% block content %}
<header><h1>{{ collection_name }}</h1></header>
<main class="gallery">
    <p class="empty-message">No photos found in this collection.</p>
</main>
{% endblock %}"""
        (templates_dir / "empty.j2.html").write_text(empty_template)

        # Test plugin with theme configuration
        plugin = BasicTemplatePlugin()
        context = PluginContext(
            input_data={
                "collection_name": "Wedding",
                "photos": [
                    {"thumbnail_path": "thumbnails/img1.webp", "dest_path": "../pics/img1.jpg"},
                    {"thumbnail_path": "thumbnails/img2.webp", "dest_path": "../pics/img2.jpg"},
                ]
            },
            config={"theme_path": str(theme_dir)},
            output_dir=str(temp_filesystem / "output"),
            metadata={}
        )

        result = plugin.generate_html(context)

        # Should succeed and use theme templates
        assert result.success is True
        assert "html_files" in result.output_data
        html_files = result.output_data["html_files"]
        assert len(html_files) == 1

        # Generated HTML should use theme templates
        html_content = html_files[0]["content"]
        assert "Wedding" in html_content  # Collection name
        assert "pico.min.css" in html_content  # PicoCSS from base template
        assert "custom.css" in html_content  # Custom CSS link
        assert "photo-item" in html_content  # Template structure
        assert "thumbnails/img1.webp" in html_content  # Photo data

    def test_generate_html_fallback_to_hardcoded_without_theme(self, temp_filesystem):
        """BasicTemplatePlugin should fallback to hardcoded HTML when no theme configured."""
        plugin = BasicTemplatePlugin()
        context = PluginContext(
            input_data={
                "collection_name": "Wedding",
                "photos": [{"thumbnail_path": "thumbnails/img1.webp", "dest_path": "../pics/img1.jpg"}]
            },
            config={},  # No theme_path
            output_dir=str(temp_filesystem / "output"),
            metadata={}
        )

        result = plugin.generate_html(context)

        # Should still succeed with fallback behavior
        assert result.success is True
        # This test will initially fail because fallback isn't implemented yet
