"""Unit tests for ThemeValidator."""


from galleria.theme.validator import ThemeValidator


class TestThemeValidator:
    """Test ThemeValidator functionality."""

    def test_validate_theme_directory_with_complete_structure(self, temp_filesystem):
        """ThemeValidator should validate complete theme directory structure."""
        # Create complete theme structure
        theme_dir = temp_filesystem / "themes" / "basic"
        theme_dir.mkdir(parents=True)

        # Create theme.json
        (theme_dir / "theme.json").write_text('{"name": "basic", "version": "1.0.0"}')

        # Create template directory and files
        templates_dir = theme_dir / "templates"
        templates_dir.mkdir()
        (templates_dir / "base.j2.html").write_text("<html></html>")
        (templates_dir / "gallery.j2.html").write_text("<div>Gallery</div>")
        (templates_dir / "empty.j2.html").write_text("<div>Empty</div>")

        # Create static CSS directory and file
        css_dir = theme_dir / "static" / "css"
        css_dir.mkdir(parents=True)
        (css_dir / "custom.css").write_text("body { margin: 0; }")

        # Test validation
        validator = ThemeValidator()
        result = validator.validate_theme_directory(str(theme_dir))

        # Should pass validation
        assert result["valid"] is True
        assert "errors" not in result or len(result["errors"]) == 0

    def test_validate_theme_directory_with_missing_theme_json(self, temp_filesystem):
        """ThemeValidator should fail when theme.json is missing."""
        theme_dir = temp_filesystem / "themes" / "basic"
        theme_dir.mkdir(parents=True)

        validator = ThemeValidator()
        result = validator.validate_theme_directory(str(theme_dir))

        assert result["valid"] is False
        assert "theme.json missing" in str(result.get("errors", []))

    def test_validate_theme_directory_with_missing_templates(self, temp_filesystem):
        """ThemeValidator should fail when template files are missing."""
        theme_dir = temp_filesystem / "themes" / "basic"
        theme_dir.mkdir(parents=True)
        (theme_dir / "theme.json").write_text('{"name": "basic"}')

        validator = ThemeValidator()
        result = validator.validate_theme_directory(str(theme_dir))

        assert result["valid"] is False
        assert any("template" in str(error).lower() for error in result.get("errors", []))
