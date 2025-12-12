"""Unit tests for TemplateLoader."""

import jinja2
import pytest

from galleria.theme.loader import TemplateLoader


class TestTemplateLoader:
    """Test TemplateLoader functionality."""

    def test_load_template_with_existing_file(self, temp_filesystem):
        """TemplateLoader should load existing template files."""
        # Create theme structure with template
        theme_dir = temp_filesystem / "themes" / "basic"
        templates_dir = theme_dir / "templates"
        templates_dir.mkdir(parents=True)

        template_content = """<html>
<head><title>{{ title }}</title></head>
<body><h1>{{ collection_name }}</h1></body>
</html>"""
        (templates_dir / "gallery.j2.html").write_text(template_content)

        # Test template loading
        loader = TemplateLoader(str(theme_dir))
        template = loader.load_template("gallery.j2.html")

        # Should return Jinja2 template
        assert isinstance(template, jinja2.Template)

        # Should render with context
        rendered = template.render(title="Test Gallery", collection_name="Wedding")
        assert "Test Gallery" in rendered
        assert "Wedding" in rendered

    def test_load_template_with_missing_file(self, temp_filesystem):
        """TemplateLoader should raise error for missing template files."""
        theme_dir = temp_filesystem / "themes" / "basic"
        templates_dir = theme_dir / "templates"
        templates_dir.mkdir(parents=True)

        loader = TemplateLoader(str(theme_dir))

        with pytest.raises((jinja2.TemplateNotFound, FileNotFoundError)):
            loader.load_template("nonexistent.j2.html")

    def test_load_template_with_template_inheritance(self, temp_filesystem):
        """TemplateLoader should support Jinja2 template inheritance."""
        theme_dir = temp_filesystem / "themes" / "basic"
        templates_dir = theme_dir / "templates"
        templates_dir.mkdir(parents=True)

        # Create base template
        base_content = """<html>
<head><title>{% block title %}Default{% endblock %}</title></head>
<body>{% block content %}{% endblock %}</body>
</html>"""
        (templates_dir / "base.j2.html").write_text(base_content)

        # Create child template
        child_content = """{% extends "base.j2.html" %}
{% block title %}{{ collection_name }}{% endblock %}
{% block content %}<h1>Gallery</h1>{% endblock %}"""
        (templates_dir / "gallery.j2.html").write_text(child_content)

        loader = TemplateLoader(str(theme_dir))
        template = loader.load_template("gallery.j2.html")

        rendered = template.render(collection_name="Wedding")
        assert "<title>Wedding</title>" in rendered
        assert "<h1>Gallery</h1>" in rendered
