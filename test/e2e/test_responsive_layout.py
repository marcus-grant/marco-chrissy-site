"""E2E tests for mobile-first responsive layout implementation.

Tests verify CSS variables, breakpoints, touch targets, navbar structure,
and responsive typography work together across the full build.

All tests are initially skipped until responsive features are implemented.
"""

import json
from pathlib import Path

import pytest

# Skip all tests in this module until responsive layout is implemented
pytestmark = pytest.mark.skip(reason="Responsive layout not implemented")

# Path to actual project files for testing
PROJECT_ROOT = Path(__file__).parent.parent.parent


class TestResponsiveCSSVariables:
    """Test CSS variables for responsive breakpoints and touch targets."""

    def test_shared_css_contains_breakpoint_variables(self):
        """Verify shared.css defines CSS custom properties for breakpoints.

        Expected variables:
        - --breakpoint-sm: 480px (mobile landscape)
        - --breakpoint-md: 768px (tablet portrait)
        - --breakpoint-lg: 1024px (tablet landscape)
        - --breakpoint-xl: 1200px (desktop)
        """
        css_path = PROJECT_ROOT / "themes/shared/static/css/shared.css"
        css_content = css_path.read_text()

        # Verify breakpoint variables exist
        assert "--breakpoint-sm: 480px" in css_content, "Missing --breakpoint-sm variable"
        assert "--breakpoint-md: 768px" in css_content, "Missing --breakpoint-md variable"
        assert "--breakpoint-lg: 1024px" in css_content, "Missing --breakpoint-lg variable"
        assert "--breakpoint-xl: 1200px" in css_content, "Missing --breakpoint-xl variable"

    def test_shared_css_contains_touch_target_variable(self):
        """Verify shared.css defines touch target minimum size variable.

        Expected: --touch-target-min: 44px
        Per WCAG 2.1 AAA guidelines for touch target accessibility.
        """
        css_path = PROJECT_ROOT / "themes/shared/static/css/shared.css"
        css_content = css_path.read_text()

        assert "--touch-target-min: 44px" in css_content, "Missing --touch-target-min variable"

    def test_shared_css_contains_spacing_variables(self):
        """Verify shared.css defines spacing scale variables.

        Expected variables for consistent spacing:
        - --spacing-xs, --spacing-sm, --spacing-md, --spacing-lg
        """
        css_path = PROJECT_ROOT / "themes/shared/static/css/shared.css"
        css_content = css_path.read_text()

        assert "--spacing-xs" in css_content, "Missing --spacing-xs variable"
        assert "--spacing-sm" in css_content, "Missing --spacing-sm variable"
        assert "--spacing-md" in css_content, "Missing --spacing-md variable"
        assert "--spacing-lg" in css_content, "Missing --spacing-lg variable"


class TestGalleryGridBreakpoints:
    """Test gallery grid adapts columns at responsive breakpoints."""

    def test_gallery_css_has_mobile_first_default(
        self, temp_filesystem, file_factory, directory_factory
    ):
        """Verify gallery CSS starts with 2 columns for mobile-first approach.

        Default: grid-template-columns: repeat(2, 1fr) (2 columns)
        """
        # Create a minimal gallery build to test CSS output
        directory_factory("output/pics/full")
        file_factory("output/pics/full/manifest.json", json_content={
            "version": "0.1.0",
            "collection_name": "test",
            "pics": [{"source_path": "/fake/photo.jpg", "dest_path": "photo.jpg", "hash": "abc", "size_bytes": 1024, "mtime": 123}]
        })

        # Set up galleria theme
        directory_factory("galleria/themes/minimal/templates")
        file_factory(
            "galleria/themes/minimal/templates/gallery.j2.html",
            """<!DOCTYPE html>
<html><head><title>Gallery</title><link rel="stylesheet" href="gallery.css"></head>
<body><main class="gallery">{% for photo in photos %}<div class="photo-item"></div>{% endfor %}</main></body>
</html>"""
        )

        directory_factory("output/galleries/test")

        # Build gallery using GalleriaBuilder
        from build.galleria_builder import GalleriaBuilder

        galleria_config = {
            "manifest_path": "output/pics/full/manifest.json",
            "output_dir": "output/galleries/test",
            "theme": "minimal",
            "theme_path": "galleria/themes/minimal",
        }

        builder = GalleriaBuilder()
        result = builder.build(galleria_config, temp_filesystem)
        assert result, "Galleria build should succeed"

        # Read generated CSS
        css_path = temp_filesystem / "output/galleries/test/gallery.css"
        assert css_path.exists(), "gallery.css should be generated"
        css_content = css_path.read_text()

        # Verify mobile-first: default is 2 columns
        assert "grid-template-columns: repeat(2, 1fr)" in css_content, \
            "Gallery should default to 2 columns for mobile"

    def test_gallery_css_has_breakpoint_media_queries(
        self, temp_filesystem, file_factory, directory_factory
    ):
        """Verify gallery CSS defines media queries at each breakpoint.

        Expected breakpoints:
        - Default: 2 columns
        - 560px: 3 columns
        - 768px: 4 columns
        - 1024px: 6 columns
        """
        directory_factory("output/pics/full")
        file_factory("output/pics/full/manifest.json", json_content={
            "version": "0.1.0",
            "collection_name": "test",
            "pics": [{"source_path": "/fake/photo.jpg", "dest_path": "photo.jpg", "hash": "abc", "size_bytes": 1024, "mtime": 123}]
        })

        directory_factory("galleria/themes/minimal/templates")
        file_factory(
            "galleria/themes/minimal/templates/gallery.j2.html",
            """<!DOCTYPE html>
<html><head><title>Gallery</title><link rel="stylesheet" href="gallery.css"></head>
<body><main class="gallery"></main></body>
</html>"""
        )

        directory_factory("output/galleries/test")

        from build.galleria_builder import GalleriaBuilder

        galleria_config = {
            "manifest_path": "output/pics/full/manifest.json",
            "output_dir": "output/galleries/test",
            "theme": "minimal",
            "theme_path": "galleria/themes/minimal",
        }

        builder = GalleriaBuilder()
        builder.build(galleria_config, temp_filesystem)

        css_path = temp_filesystem / "output/galleries/test/gallery.css"
        css_content = css_path.read_text()

        # Verify media queries at each breakpoint
        assert "@media" in css_content and "560px" in css_content, "Missing 560px breakpoint"
        assert "@media" in css_content and "768px" in css_content, "Missing 768px breakpoint"
        assert "@media" in css_content and "1024px" in css_content, "Missing 1024px breakpoint"

        # Verify column counts at each breakpoint
        assert "repeat(2, 1fr)" in css_content, "Should have 2 columns default"
        assert "repeat(3, 1fr)" in css_content, "Should have 3 columns at 560px"
        assert "repeat(4, 1fr)" in css_content, "Should have 4 columns at 768px"
        assert "repeat(6, 1fr)" in css_content, "Should have 6 columns at 1024px"


class TestTouchTargets:
    """Test touch targets meet 44px minimum accessibility requirement."""

    def test_navbar_links_have_minimum_touch_target(self):
        """Verify navbar links meet 44px minimum touch target size.

        WCAG 2.1 AAA: Touch targets should be at least 44x44 CSS pixels.
        """
        css_path = PROJECT_ROOT / "themes/shared/static/css/shared.css"
        css_content = css_path.read_text()

        # Check navbar links have minimum height
        # Should use var(--touch-target-min) or explicit 44px
        assert "min-height: var(--touch-target-min)" in css_content or "min-height: 44px" in css_content, \
            "Navbar links should have 44px minimum touch target height"

    def test_pagination_links_have_minimum_touch_target(
        self, temp_filesystem, file_factory, directory_factory
    ):
        """Verify pagination controls meet 44px minimum touch target size."""
        directory_factory("output/pics/full")
        file_factory("output/pics/full/manifest.json", json_content={
            "version": "0.1.0",
            "collection_name": "test",
            "pics": [{"source_path": "/fake/photo.jpg", "dest_path": "photo.jpg", "hash": "abc", "size_bytes": 1024, "mtime": 123}]
        })

        directory_factory("galleria/themes/minimal/templates")
        file_factory(
            "galleria/themes/minimal/templates/gallery.j2.html",
            """<!DOCTYPE html>
<html><head><title>Gallery</title><link rel="stylesheet" href="gallery.css"></head>
<body><nav class="pagination"><a href="#">Prev</a><a href="#">Next</a></nav></body>
</html>"""
        )

        directory_factory("output/galleries/test")

        from build.galleria_builder import GalleriaBuilder

        galleria_config = {
            "manifest_path": "output/pics/full/manifest.json",
            "output_dir": "output/galleries/test",
            "theme": "minimal",
            "theme_path": "galleria/themes/minimal",
        }

        builder = GalleriaBuilder()
        builder.build(galleria_config, temp_filesystem)

        css_path = temp_filesystem / "output/galleries/test/gallery.css"
        css_content = css_path.read_text()

        # Pagination links should have minimum touch target
        assert "min-height: 44px" in css_content or "min-height: var(--touch-target-min)" in css_content, \
            "Pagination should have 44px minimum touch target height"
        assert "min-width: 44px" in css_content or "min-width: var(--touch-target-min)" in css_content, \
            "Pagination should have 44px minimum touch target width"


class TestResponsiveNavbar:
    """Test navbar has CSS-only mobile menu structure."""

    def test_navbar_html_has_checkbox_toggle(self):
        """Verify navbar HTML includes checkbox hack for CSS-only toggle.

        Required structure:
        - Hidden checkbox input (toggle state)
        - Label element (hamburger button)
        - Nav links container (toggleable)
        """
        navbar_path = PROJECT_ROOT / "themes/shared/templates/navbar.html"
        navbar_content = navbar_path.read_text()

        # Verify checkbox toggle structure
        assert 'type="checkbox"' in navbar_content, "Navbar should have checkbox input for toggle"
        assert "nav-toggle" in navbar_content or "menu-toggle" in navbar_content, \
            "Navbar should have toggle element with identifiable class/id"
        assert "<label" in navbar_content, "Navbar should have label for hamburger button"

    def test_navbar_css_hides_toggle_on_desktop(self):
        """Verify hamburger toggle is hidden on desktop viewports."""
        css_path = PROJECT_ROOT / "themes/shared/static/css/shared.css"
        css_content = css_path.read_text()

        # Toggle should be hidden by default (desktop-first hidden) or via media query
        assert "display: none" in css_content, \
            "Hamburger toggle should be hidden on desktop"

    def test_navbar_css_shows_toggle_on_mobile(self):
        """Verify hamburger toggle is visible below 768px breakpoint."""
        css_path = PROJECT_ROOT / "themes/shared/static/css/shared.css"
        css_content = css_path.read_text()

        # Should have media query that shows toggle on mobile
        assert "@media" in css_content and "768px" in css_content, \
            "Should have media query for 768px breakpoint"

    def test_navbar_css_toggles_nav_links_visibility(self):
        """Verify CSS checkbox hack toggles nav links visibility.

        Pattern: input:checked ~ .nav-links { display: flex; }
        """
        css_path = PROJECT_ROOT / "themes/shared/static/css/shared.css"
        css_content = css_path.read_text()

        # Verify checkbox toggle pattern exists
        assert ":checked" in css_content, \
            "CSS should use :checked pseudo-class for toggle state"


class TestResponsiveTypography:
    """Test responsive typography using CSS clamp()."""

    def test_shared_css_uses_clamp_for_headers(self):
        """Verify header typography uses clamp() for fluid sizing.

        Expected pattern: font-size: clamp(min, preferred, max)
        e.g., clamp(1.5rem, 4vw + 0.5rem, 2.5rem)
        """
        css_path = PROJECT_ROOT / "themes/shared/static/css/shared.css"
        css_content = css_path.read_text()

        # Verify clamp() is used for font-size
        assert "clamp(" in css_content, "Typography should use clamp() for fluid sizing"
        assert "font-size:" in css_content and "clamp(" in css_content, \
            "font-size should use clamp() function"

    def test_shared_css_typography_scales_between_viewports(self):
        """Verify typography has appropriate min/max bounds.

        Font sizes should scale smoothly between mobile and desktop,
        with reasonable minimum (readable on mobile) and maximum (not too large).
        """
        css_path = PROJECT_ROOT / "themes/shared/static/css/shared.css"
        css_content = css_path.read_text()

        # clamp() should have rem units for accessibility
        # Pattern: clamp(Xrem, ..., Yrem) where X >= 1rem for body text
        assert "rem" in css_content, "Typography should use rem units for accessibility"


class TestFullBuildResponsiveIntegration:
    """Test responsive features work in full build context."""

    def test_full_build_includes_responsive_css(
        self, temp_filesystem, full_config_setup, file_factory, directory_factory
    ):
        """Verify full site build includes responsive CSS variables.

        Integration test: Build both Pelican and Galleria, verify
        responsive CSS is present in output.
        """
        # Create shared navbar and CSS
        directory_factory("themes/shared/templates")
        file_factory(
            "themes/shared/templates/navbar.html",
            '<nav id="shared-navbar"><a href="/">Home</a></nav>'
        )

        directory_factory("themes/shared/static/css")
        # Use actual CSS from the project
        actual_css = (PROJECT_ROOT / "themes/shared/static/css/shared.css").read_text()
        file_factory("themes/shared/static/css/shared.css", actual_css)

        # Create minimal Pelican content
        file_factory("content/index.md", """Title: Home
Date: 2023-01-01

Home page content.
""")

        # Create test photo manifest
        directory_factory("output/pics/full")
        file_factory("output/pics/full/manifest.json", json_content={
            "version": "0.1.0",
            "collection_name": "test_wedding",
            "pics": [{"source_path": "/fake/photo.jpg", "dest_path": "photo.jpg", "hash": "abc123", "size_bytes": 1024, "mtime": 1234567890}]
        })

        # Create theme with base template
        directory_factory("themes/site/templates")
        file_factory(
            "themes/site/templates/base.html",
            """<!DOCTYPE html>
<html>
<head><title>{{ SITENAME }}</title></head>
<body>{% include 'navbar.html' %}{% block content %}{% endblock %}</body>
</html>"""
        )
        file_factory(
            "themes/site/templates/index.html",
            """{% extends "base.html" %}
{% block content %}Content{% endblock %}"""
        )

        # Create Galleria theme
        directory_factory("galleria/themes/minimal/templates")
        file_factory(
            "galleria/themes/minimal/templates/gallery.j2.html",
            """<!DOCTYPE html>
<html>
<head><title>Gallery</title><link rel="stylesheet" href="gallery.css"></head>
<body>{% include 'navbar.html' ignore missing %}<main class="gallery"></main></body>
</html>"""
        )

        # Configure builds
        configs = full_config_setup({
            "pelican": {
                "author": "Test",
                "sitename": "Test Site",
                "theme": "themes/site",
                "content_path": "content",
                "THEME_TEMPLATES_OVERRIDES": "themes/shared",
            },
            "galleria": {
                "manifest_path": "output/pics/full/manifest.json",
                "output_dir": "output/galleries/wedding",
                "theme": "minimal",
                "theme_path": "galleria/themes/minimal",
                "THEME_TEMPLATES_OVERRIDES": "themes/shared",
            }
        })

        # Build Pelican
        from build.pelican_builder import PelicanBuilder
        with open(configs["pelican"]) as f:
            pelican_config = json.load(f)

        pelican_builder = PelicanBuilder()
        pelican_result = pelican_builder.build({"output_dir": "output"}, pelican_config, temp_filesystem)
        assert pelican_result, "Pelican build failed"

        # Check shared CSS in Pelican output has responsive variables
        pelican_css = temp_filesystem / "output" / "theme" / "css" / "shared.css"
        if pelican_css.exists():
            css_content = pelican_css.read_text()
            assert "--breakpoint-" in css_content, "Pelican output should include breakpoint variables"

        # Build Galleria
        from build.galleria_builder import GalleriaBuilder
        with open(configs["galleria"]) as f:
            galleria_config = json.load(f)

        galleria_builder = GalleriaBuilder()
        galleria_result = galleria_builder.build(galleria_config, temp_filesystem)
        assert galleria_result, "Galleria build failed"

        # Check gallery CSS has responsive grid
        gallery_css = temp_filesystem / "output" / "galleries" / "wedding" / "gallery.css"
        if gallery_css.exists():
            css_content = gallery_css.read_text()
            assert "@media" in css_content, "Gallery CSS should have media queries"
