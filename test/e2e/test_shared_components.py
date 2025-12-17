"""E2E tests for shared theme component system integration."""


import pytest


class TestSharedComponentSystem:
    """Test shared component system integration across Pelican and Galleria."""

    @pytest.mark.skip("Shared component system not implemented")
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

        # Test Pelican can load shared templates
        from pelican.settings import read_settings
        pelican_settings = read_settings(pelican_config)

        # Pelican Jinja2 environment should include shared templates
        assert str(shared_dir / "templates") in pelican_settings.get("TEMPLATE_DIRS", [])

        # Test Galleria can load shared templates
        from galleria.theme.loader import TemplateLoader
        galleria_loader = TemplateLoader(galleria_config)

        # Should be able to load shared template
        shared_template_path = shared_dir / "templates" / "test.html"
        shared_template_path.write_text("<nav>Shared Navigation</nav>")

        template = galleria_loader.load_template("test.html")
        assert template is not None, "Galleria should load shared template"

        # Test both systems generate consistent output
        # This ensures shared assets are properly integrated

        # Build with Pelican
        from cli.commands.build import BuildCommand
        build_cmd = BuildCommand()
        pelican_result = build_cmd._run_pelican(str(config_dir))
        assert pelican_result.success, "Pelican build should succeed with shared assets"

        # Build with Galleria
        from galleria.cli.commands.generate import GenerateCommand
        galleria_cmd = GenerateCommand()
        galleria_result = galleria_cmd.execute({
            "config_file": str(galleria_config),
            "output_dir": str(output_dir / "galleries")
        })
        assert galleria_result.success, "Galleria build should succeed with shared assets"

        # Verify both systems reference same CSS file
        pelican_index = output_dir / "index.html"
        galleria_index = output_dir / "galleries" / "wedding" / "index.html"

        if pelican_index.exists():
            pelican_content = pelican_index.read_text()
            assert "/css/pico.min.css" in pelican_content, "Pelican should reference shared CSS"

        if galleria_index.exists():
            galleria_content = galleria_index.read_text()
            assert "/css/pico.min.css" in galleria_content, "Galleria should reference shared CSS"

    @pytest.mark.skip("Shared component system not implemented")
    def test_shared_template_inclusion_from_both_systems(self, temp_filesystem):
        """Test that both Pelican and Galleria can include shared template components."""
        # This test will verify context adapters and template inclusion
        # Implementation will be added when context adapters are built
        pass

    @pytest.mark.skip("Shared component system not implemented")
    def test_pico_css_loads_consistently_across_page_types(self, temp_filesystem):
        """Test PicoCSS loads with same URL across static and gallery pages."""
        # This test will verify asset URL consistency
        # Implementation will be added when asset manager is built
        pass
