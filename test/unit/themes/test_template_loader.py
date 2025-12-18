"""Unit tests for shared template loader configuration."""


import pytest


class TestSharedTemplateLoader:
    """Test shared template loader functionality."""

    def test_pelican_template_loader_includes_shared_paths(self, temp_filesystem, config_file_factory):
        """Test Pelican Jinja2 environment includes shared template directories."""
        from themes.shared.utils.template_loader import (
            configure_pelican_shared_templates,
        )

        # Setup directories
        shared_templates = temp_filesystem / "themes" / "shared" / "templates"
        shared_templates.mkdir(parents=True)
        pelican_templates = temp_filesystem / "themes" / "site" / "templates"
        pelican_templates.mkdir(parents=True)

        # Create test shared template
        (shared_templates / "shared_nav.html").write_text("<nav>Shared Navigation</nav>")

        # Create Pelican config
        config = config_file_factory(
            temp_filesystem / "pelican.json",
            {
                "SITENAME": "Test Site",
                "THEME": str(pelican_templates.parent),
                "THEME_TEMPLATE_OVERRIDES": str(shared_templates.parent)
            }
        )

        # Configure shared template paths
        template_dirs = configure_pelican_shared_templates(config)

        # Verify shared templates directory is included
        assert str(shared_templates) in template_dirs
        assert str(pelican_templates) in template_dirs

    def test_galleria_template_loader_includes_shared_paths(self, shared_theme_dirs):
        """Test Galleria template system includes shared template directories."""
        from themes.shared.utils.template_loader import GalleriaSharedTemplateLoader

        # Setup directories
        dirs = shared_theme_dirs()
        shared_templates = dirs["shared_templates"]
        galleria_templates = dirs["galleria_templates"]

        # Create test shared template
        (shared_templates / "shared_nav.html").write_text("<nav>Shared Navigation</nav>")

        # Create Galleria config
        config = {
            "theme": {
                "name": "minimal",
                "external_templates": [str(shared_templates)],
                "external_assets": {"css": [], "js": []}
            }
        }

        # Create loader
        loader = GalleriaSharedTemplateLoader(config, str(galleria_templates.parent))

        # Verify loader can find shared template
        template = loader.get_template("shared_nav.html")
        assert template is not None
        rendered = template.render()
        assert "Shared Navigation" in rendered

    def test_shared_template_search_path_precedence(self, shared_theme_dirs):
        """Test template search path precedence (theme-specific overrides shared)."""
        from themes.shared.utils.template_loader import GalleriaSharedTemplateLoader

        # Setup directories
        dirs = shared_theme_dirs()
        shared_templates = dirs["shared_templates"]
        galleria_templates = dirs["galleria_templates"]

        # Create same template in both locations (theme should override shared)
        (shared_templates / "nav.html").write_text("<nav>Shared Navigation</nav>")
        (galleria_templates / "nav.html").write_text("<nav>Theme-Specific Navigation</nav>")

        config = {
            "theme": {
                "name": "minimal",
                "external_templates": [str(shared_templates)],
                "external_assets": {"css": [], "js": []}
            }
        }

        loader = GalleriaSharedTemplateLoader(config, str(galleria_templates.parent))

        # Should get theme-specific version (higher precedence)
        template = loader.get_template("nav.html")
        rendered = template.render()
        assert "Theme-Specific Navigation" in rendered
        assert "Shared Navigation" not in rendered

    def test_shared_template_inclusion_from_theme_template(self, shared_theme_dirs):
        """Test theme template can include shared template via Jinja2 include."""
        from themes.shared.utils.template_loader import GalleriaSharedTemplateLoader

        # Setup directories
        dirs = shared_theme_dirs()
        shared_templates = dirs["shared_templates"]
        galleria_templates = dirs["galleria_templates"]

        # Create shared component
        (shared_templates / "navigation.html").write_text('<nav class="shared">Shared Nav</nav>')

        # Create theme template that includes shared component
        (galleria_templates / "page.html").write_text('''
<html>
<head><title>Gallery Page</title></head>
<body>
    {% include "navigation.html" %}
    <main>Gallery content</main>
</body>
</html>
        '''.strip())

        config = {
            "theme": {
                "name": "minimal",
                "external_templates": [str(shared_templates)],
                "external_assets": {"css": [], "js": []}
            }
        }

        loader = GalleriaSharedTemplateLoader(config, str(galleria_templates.parent))

        # Should be able to render theme template with shared include
        template = loader.get_template("page.html")
        rendered = template.render()
        assert "Shared Nav" in rendered
        assert "Gallery content" in rendered
        assert '<nav class="shared">' in rendered

    def test_missing_shared_template_raises_appropriate_error(self, temp_filesystem):
        """Test missing shared template raises clear error message."""
        from themes.shared.utils.template_loader import GalleriaSharedTemplateLoader

        # Setup with no templates
        galleria_templates = temp_filesystem / "galleria" / "themes" / "minimal" / "templates"
        galleria_templates.mkdir(parents=True)

        config = {
            "theme": {
                "name": "minimal",
                "external_templates": [],
                "external_assets": {"css": [], "js": []}
            }
        }

        loader = GalleriaSharedTemplateLoader(config, str(galleria_templates.parent))

        # Should raise clear error for missing template
        with pytest.raises(Exception) as exc_info:
            loader.get_template("nonexistent.html")

        # Error should mention template name
        assert "nonexistent.html" in str(exc_info.value)

    def test_create_shared_template_example(self, temp_filesystem):
        """Test creating and verifying example shared template functionality."""
        from themes.shared.utils.template_loader import create_example_shared_template

        # Setup shared templates directory
        shared_templates = temp_filesystem / "themes" / "shared" / "templates"
        shared_templates.mkdir(parents=True)

        # Create example template
        template_path = create_example_shared_template(shared_templates)

        # Verify template was created
        assert template_path.exists()
        assert template_path.name == "example.html"

        # Verify content is reasonable
        content = template_path.read_text()
        assert "example" in content.lower()
        assert "<" in content and ">" in content  # Has HTML tags
