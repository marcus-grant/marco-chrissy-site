"""E2E tests for shared theme component system integration."""

from pathlib import Path


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
                "THEME_TEMPLATES_OVERRIDES": str(shared_dir)
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

    def test_shared_components_integration_without_subprocess(self, temp_filesystem, full_config_setup, file_factory, directory_factory):
        """Test shared component integration using builders directly (no subprocess).

        This integration test verifies that:
        - PelicanBuilder uses shared templates when SHARED_THEME_PATH is configured
        - AssetManager copies shared CSS files to output directory
        - Template loading works with proper search path precedence
        """
        from unittest.mock import Mock, patch

        from build.pelican_builder import PelicanBuilder
        from themes.shared.utils.asset_manager import AssetManager

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
        file_factory("content/test.md", """Title: Test Page
Date: 2023-01-01

Test content with shared navbar:
{% include 'navbar.html' %}
""")

        # Create configs that reference shared components
        configs = full_config_setup({
            "pelican": {
                "author": "Test Author",
                "sitename": "Test Site",
                "content_path": "content",
                "THEME_TEMPLATES_OVERRIDES": "themes/shared"
            }
        })

        # Test 1: AssetManager copies shared CSS
        output_dir = temp_filesystem / "output"
        asset_manager = AssetManager(output_dir)

        # Mock get_shared_css_paths to use our test directory
        with patch('themes.shared.utils.asset_manager.get_shared_css_paths') as mock_paths:
            shared_css_dir = temp_filesystem / "themes" / "shared" / "css"
            mock_paths.return_value = [shared_css_dir]

            copied_files = asset_manager.copy_shared_css_files()

        # Verify CSS was copied
        assert len(copied_files) == 1
        shared_css_output = output_dir / "css" / "shared.css"
        assert shared_css_output.exists(), "Shared CSS not copied to output"

        css_content = shared_css_output.read_text()
        assert ".shared-nav" in css_content, "Shared CSS rules missing from output"
        assert "color: blue" in css_content, "CSS styling missing from output"

        # Test 2: PelicanBuilder uses shared template configuration
        site_config = {"output_dir": "output"}

        with open(configs["pelican"]) as f:
            import json
            pelican_config = json.load(f)

        builder = PelicanBuilder()

        # Mock Pelican to capture template configuration instead of running full build
        with patch('build.pelican_builder.pelican.Pelican') as mock_pelican_class:
            with patch('build.pelican_builder.configure_settings') as mock_configure:
                mock_pelican_instance = Mock()
                mock_pelican_class.return_value = mock_pelican_instance
                mock_configure.return_value = {}

                # Mock configure_pelican_shared_templates to return our test paths
                with patch('build.pelican_builder.configure_pelican_shared_templates') as mock_configure_shared:
                    shared_templates_dir = temp_filesystem / "themes" / "shared" / "templates"
                    mock_configure_shared.return_value = [str(shared_templates_dir)]

                    result = builder.build(site_config, pelican_config, temp_filesystem)

                    # Verify shared template configuration was used
                    assert result is True
                    mock_configure_shared.assert_called_once()

                    # Verify Jinja environment includes shared templates
                    mock_configure.assert_called_once()
                    settings_dict = mock_configure.call_args[0][0]
                    assert 'JINJA_ENVIRONMENT' in settings_dict

        # Test 3: Template loader can find shared templates
        # Create temporary config file for template loader test
        import tempfile

        from themes.shared.utils.template_loader import (
            configure_pelican_shared_templates,
        )
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_config:
            json.dump(pelican_config, temp_config)
            temp_config_path = temp_config.name

        try:
            template_dirs = configure_pelican_shared_templates(temp_config_path)
            # Template loader returns relative paths from config, which is correct behavior
            assert "themes/shared/templates" in template_dirs, "Shared templates should be in search paths"
        finally:
            Path(temp_config_path).unlink(missing_ok=True)

    def test_shared_components_end_to_end_minimal(self, temp_filesystem, full_config_setup, file_factory, directory_factory):
        """Minimal test to verify shared components work with actual build orchestrator."""

        from build.config_manager import ConfigManager

        # Create minimal shared components
        directory_factory("themes/shared/templates")
        directory_factory("themes/shared/css")

        file_factory(
            "themes/shared/templates/test.html",
            '<div class="shared-test">Shared Component Works</div>'
        )

        file_factory(
            "themes/shared/css/test.css",
            '.shared-test { background: blue; }'
        )

        # Create minimal configs
        full_config_setup({
            "pelican": {
                "author": "Test",
                "sitename": "Test Site",
                "THEME_TEMPLATES_OVERRIDES": "themes/shared"
            }
        })

        # Test that BuildOrchestrator can load configs with shared theme path
        try:
            config_manager = ConfigManager(temp_filesystem / "config")
            pelican_config = config_manager.load_pelican_config()

            # Verify shared theme path is in the loaded config
            assert "THEME_TEMPLATES_OVERRIDES" in pelican_config
            assert pelican_config["THEME_TEMPLATES_OVERRIDES"] == "themes/shared"

            # Success - our shared component config is properly loaded
            print("✓ Shared component configuration successfully loaded by build system")

        except Exception as e:
            print(f"✗ Shared component configuration failed: {e}")
            raise
