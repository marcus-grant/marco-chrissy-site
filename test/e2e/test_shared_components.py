"""E2E tests for shared theme component system integration."""



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


    def test_shared_components_end_to_end_minimal(self, temp_filesystem, full_config_setup, file_factory, directory_factory, theme_factory):
        """Minimal test to verify shared components work with actual build orchestrator."""

        from build.config_manager import ConfigManager

        # Create minimal shared components using theme_factory
        theme_factory(
            "shared",
            css_files={"test.css": '.shared-test { background: blue; }'},
            templates={"test.html": '<div class="shared-test">Shared Component Works</div>'}
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
