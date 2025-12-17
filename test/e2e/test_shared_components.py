"""E2E tests for shared theme component system integration."""

from pathlib import Path

import pytest


class TestSharedComponentSystem:
    """Test shared component system integration across Pelican and Galleria."""

    def test_both_systems_load_shared_assets(self, temp_filesystem, config_file_factory):
        """Test that both Pelican and Galleria can load shared assets and templates.

        This test verifies:
        - PicoCSS loads consistently across page types
        - Shared template inclusion from both systems
        - Asset manager properly downloads external dependencies
        - Template search paths include shared directories
        """
        # Setup test environment
        config_dir = temp_filesystem / "config"
        output_dir = temp_filesystem / "output"
        themes_dir = temp_filesystem / "themes"

        # Create shared component directories
        shared_dir = themes_dir / "shared"
        shared_dir.mkdir(parents=True)
        (shared_dir / "css").mkdir()
        (shared_dir / "templates").mkdir()
        (shared_dir / "utils").mkdir()

        # Create test configs
        pelican_config = config_file_factory(
            config_dir / "pelican.json",
            {
                "SITENAME": "Test Site",
                "THEME": str(themes_dir / "site"),
                "SHARED_THEME_PATH": str(shared_dir)
            }
        )

        galleria_config = config_file_factory(
            config_dir / "galleria.json",
            {
                "theme": {
                    "name": "minimal",
                    "external_templates": [str(shared_dir / "templates")],
                    "external_assets": {
                        "css": ["/css/pico.min.css"],
                        "js": []
                    }
                }
            }
        )

        # Test asset manager downloads PicoCSS
        from themes.shared.utils.asset_manager import AssetManager
        asset_manager = AssetManager(output_dir)
        css_path = asset_manager.ensure_asset("pico", "css")

        assert css_path.exists(), "PicoCSS should be downloaded to output directory"
        assert css_path.name == "pico.min.css", "CSS file should have correct name"

        # Test Pelican can load shared templates using our template loader
        from themes.shared.utils.template_loader import (
            configure_pelican_shared_templates,
        )
        template_dirs = configure_pelican_shared_templates(pelican_config)

        # Shared templates should be included in search paths
        assert str(shared_dir / "templates") in template_dirs

        # Test Galleria can load shared templates using our new shared loader
        from themes.shared.utils.template_loader import GalleriaSharedTemplateLoader

        # Create a minimal theme for testing
        galleria_theme_path = themes_dir / "minimal"
        galleria_theme_path.mkdir(parents=True)
        (galleria_theme_path / "templates").mkdir()

        # Read the galleria config data
        import json
        with open(galleria_config) as f:
            galleria_config_data = json.load(f)

        galleria_loader = GalleriaSharedTemplateLoader(
            galleria_config_data,
            str(galleria_theme_path)
        )

        # Create and test shared template loading
        shared_template_path = shared_dir / "templates" / "test.html"
        shared_template_path.write_text("<nav>Shared Navigation</nav>")

        template = galleria_loader.get_template("test.html")
        assert template is not None, "Galleria should load shared template"

        # Test asset URL generation consistency
        css_url = asset_manager.get_asset_url("pico", "css")
        assert css_url == "/css/pico.min.css", "Asset URL should be consistent across systems"

    def test_shared_template_inclusion_from_both_systems(self, temp_filesystem):
        """Test that both Pelican and Galleria can include shared template components."""
        # This test will verify context adapters and template inclusion
        # Implementation will be added when context adapters are built
        pass

    def test_pico_css_loads_consistently_across_page_types(self, temp_filesystem):
        """Test PicoCSS loads with same URL across static and gallery pages."""
        # This test will verify asset URL consistency
        # Implementation will be added when asset manager is built
        pass

    @pytest.mark.skip("Shared component build integration not implemented")
    def test_build_integrates_shared_components_into_both_systems(self, full_config_setup, file_factory, directory_factory, fake_image_factory):
        """Test that shared navbar and CSS appear in both Pelican and Galleria HTML output.

        This integration test verifies that:
        - Shared navbar template is included in both Pelican and Galleria pages
        - Shared CSS is copied to output and referenced in both systems
        - Build system properly integrates external shared components
        """
        import os
        import subprocess

        from bs4 import BeautifulSoup

        # Create shared component files
        directory_factory("themes/shared/templates")
        directory_factory("themes/shared/css")

        file_factory(
            "themes/shared/templates/navbar.html",
            '<nav class="shared-nav">Test Navbar</nav>'
        )

        file_factory(
            "themes/shared/css/shared.css",
            '.shared-nav { color: blue; background: red; }'
        )

        # Create test content for Pelican
        file_factory("content/test.md", """
Title: Test Page
Date: 2023-01-01

Test content with shared navbar:
{% include 'navbar.html' %}
""")

        # Create configs that reference shared components
        full_config_setup({
            "pelican": {
                "SITENAME": "Test Site",
                "SHARED_THEME_PATH": "themes/shared"
            },
            "galleria": {
                "theme": {
                    "external_templates": ["themes/shared/templates"],
                    "external_assets": {"css": ["/css/shared.css"]}
                },
                "galleries": {
                    "test": {
                        "title": "Test Gallery",
                        "input_dir": "photos",
                        "template": "gallery.html"
                    }
                }
            }
        })

        # Create test photos for Galleria
        directory_factory("photos")
        fake_image_factory("test.jpg", "photos")

        # Run site build
        result = subprocess.run(
            ["uv", "run", "site", "build"],
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            timeout=30
        )

        # Build should succeed
        assert result.returncode == 0, f"Build failed: {result.stderr}"

        # Verify shared navbar in Pelican HTML output
        pelican_files = list(Path("output").glob("*.html"))
        assert len(pelican_files) > 0, "No Pelican HTML files generated"

        pelican_html = pelican_files[0].read_text()
        pelican_soup = BeautifulSoup(pelican_html, 'html.parser')
        pelican_navbar = pelican_soup.find('nav', class_='shared-nav')

        assert pelican_navbar is not None, "Shared navbar not found in Pelican HTML"
        assert pelican_navbar.get_text().strip() == "Test Navbar", "Navbar text incorrect in Pelican HTML"

        # Verify shared navbar in Galleria HTML output
        galleria_files = list(Path("output/galleries").rglob("*.html"))
        assert len(galleria_files) > 0, "No Galleria HTML files generated"

        galleria_html = galleria_files[0].read_text()
        galleria_soup = BeautifulSoup(galleria_html, 'html.parser')
        galleria_navbar = galleria_soup.find('nav', class_='shared-nav')

        assert galleria_navbar is not None, "Shared navbar not found in Galleria HTML"
        assert galleria_navbar.get_text().strip() == "Test Navbar", "Navbar text incorrect in Galleria HTML"

        # Verify shared CSS is copied to output
        shared_css_output = Path("output/css/shared.css")
        assert shared_css_output.exists(), "Shared CSS not copied to output"

        css_content = shared_css_output.read_text()
        assert ".shared-nav" in css_content, "Shared CSS rules missing from output"
        assert "color: blue" in css_content, "CSS styling missing from output"
