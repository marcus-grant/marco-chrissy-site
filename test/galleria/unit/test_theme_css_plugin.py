"""Unit tests for theme-based BasicCSSPlugin."""


from galleria.plugins.base import PluginContext
from galleria.plugins.css import BasicCSSPlugin


class TestThemeBasedCSSPlugin:
    """Test BasicCSSPlugin with theme system integration."""

    def test_generate_css_with_theme_files(self, temp_filesystem):
        """BasicCSSPlugin should read CSS files from theme directory."""
        # Create theme structure
        theme_dir = temp_filesystem / "themes" / "basic"
        css_dir = theme_dir / "static" / "css"
        css_dir.mkdir(parents=True)

        # Create theme.json
        (theme_dir / "theme.json").write_text('{"name": "basic", "version": "1.0.0"}')

        # Create custom CSS file
        custom_css = """/* Custom gallery styles */
.gallery {
    max-width: 1200px;
    margin: 0 auto;
}

.photo-item {
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}"""
        (css_dir / "custom.css").write_text(custom_css)

        # Create additional CSS files
        layout_css = """/* Layout specific styles */
.gallery-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}"""
        (css_dir / "layout.css").write_text(layout_css)

        # Test plugin with theme configuration
        plugin = BasicCSSPlugin()
        context = PluginContext(
            input_data={
                "collection_name": "Wedding",
                "html_files": [
                    {"filename": "index.html", "content": "<html></html>", "page_number": 1}
                ]
            },
            config={"theme_path": str(theme_dir)},
            output_dir=str(temp_filesystem / "output"),
            metadata={}
        )

        result = plugin.generate_css(context)

        # Should succeed and use theme CSS files
        assert result.success is True
        assert "css_files" in result.output_data
        css_files = result.output_data["css_files"]

        # Should have CSS files from theme directory
        assert len(css_files) >= 2  # At least custom.css and layout.css

        # Find custom.css file (should load last for highest priority)
        custom_css_file = None
        for css_file in css_files:
            if css_file["filename"] == "custom.css":
                custom_css_file = css_file
                break

        assert custom_css_file is not None
        assert "Custom gallery styles" in custom_css_file["content"]
        assert ".photo-item" in custom_css_file["content"]

        # Should pass through HTML files
        assert "html_files" in result.output_data
        assert len(result.output_data["html_files"]) == 1

    def test_generate_css_fallback_to_hardcoded_without_theme(self, temp_filesystem):
        """BasicCSSPlugin should fallback to hardcoded CSS when no theme configured."""
        plugin = BasicCSSPlugin()
        context = PluginContext(
            input_data={
                "collection_name": "Wedding",
                "html_files": [
                    {"filename": "index.html", "content": "<html></html>", "page_number": 1}
                ]
            },
            config={},  # No theme_path
            output_dir=str(temp_filesystem / "output"),
            metadata={}
        )

        result = plugin.generate_css(context)

        # Should still succeed with fallback behavior
        assert result.success is True
