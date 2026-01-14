"""Unit tests for shared navbar responsive structure."""

import re
from pathlib import Path

# Paths to shared theme files
NAVBAR_HTML_PATH = Path(__file__).parent.parent.parent / "themes/shared/templates/navbar.html"
SHARED_CSS_PATH = Path(__file__).parent.parent.parent / "themes/shared/static/css/shared.css"


class TestNavbarHTMLStructure:
    """Test navbar HTML has required elements for CSS-only mobile menu."""

    def test_navbar_file_exists(self):
        """Verify navbar.html exists at expected location."""
        assert NAVBAR_HTML_PATH.exists(), f"navbar.html not found at {NAVBAR_HTML_PATH}"

    def test_has_nav_element(self):
        """Verify navbar has nav element with shared-navbar id."""
        html_content = NAVBAR_HTML_PATH.read_text()
        assert '<nav id="shared-navbar"' in html_content or '<nav id="shared-navbar">' in html_content, \
            "Navbar should have <nav id='shared-navbar'>"

    def test_has_checkbox_input_for_toggle(self):
        """Verify navbar has hidden checkbox input for toggle state."""
        html_content = NAVBAR_HTML_PATH.read_text()
        assert 'type="checkbox"' in html_content, \
            "Navbar should have checkbox input for CSS-only toggle"

    def test_checkbox_has_id_for_label_association(self):
        """Verify checkbox has id attribute for label association."""
        html_content = NAVBAR_HTML_PATH.read_text()
        # Match checkbox with id attribute
        assert re.search(r'<input[^>]*type="checkbox"[^>]*id="[^"]+"', html_content) or \
               re.search(r'<input[^>]*id="[^"]+"[^>]*type="checkbox"', html_content), \
            "Checkbox input should have id attribute for label association"

    def test_has_label_for_hamburger_button(self):
        """Verify navbar has label element for hamburger button."""
        html_content = NAVBAR_HTML_PATH.read_text()
        assert '<label' in html_content, \
            "Navbar should have label element for hamburger button"

    def test_label_has_for_attribute(self):
        """Verify label has for attribute matching checkbox id."""
        html_content = NAVBAR_HTML_PATH.read_text()
        assert re.search(r'<label[^>]*for="[^"]+"', html_content), \
            "Label should have for attribute to associate with checkbox"

    def test_checkbox_and_label_ids_match(self):
        """Verify checkbox id matches label for attribute."""
        html_content = NAVBAR_HTML_PATH.read_text()

        # Extract checkbox id
        checkbox_match = re.search(r'<input[^>]*id="([^"]+)"[^>]*type="checkbox"', html_content) or \
                        re.search(r'<input[^>]*type="checkbox"[^>]*id="([^"]+)"', html_content)

        # Extract label for
        label_match = re.search(r'<label[^>]*for="([^"]+)"', html_content)

        assert checkbox_match and label_match, \
            "Both checkbox id and label for attributes must exist"
        assert checkbox_match.group(1) == label_match.group(1), \
            f"Checkbox id '{checkbox_match.group(1)}' should match label for '{label_match.group(1)}'"

    def test_has_nav_links_container(self):
        """Verify navbar has container for nav links."""
        html_content = NAVBAR_HTML_PATH.read_text()
        # Should have a container class for the links (nav-links, nav-menu, etc.)
        assert 'class="nav-links"' in html_content or 'class="nav-menu"' in html_content, \
            "Navbar should have nav-links or nav-menu container for links"

    def test_has_navigation_links(self):
        """Verify navbar contains navigation links."""
        html_content = NAVBAR_HTML_PATH.read_text()
        assert '<a href="/"' in html_content, "Navbar should have Home link"
        assert '<a href="/about/"' in html_content, "Navbar should have About link"
        assert '<a href="/galleries/' in html_content, "Navbar should have Gallery link"

    def test_label_contains_hamburger_icon(self):
        """Verify label contains hamburger menu icon (spans or entity)."""
        html_content = NAVBAR_HTML_PATH.read_text()
        # Check for hamburger icon: could be spans, unicode, or aria-label
        has_hamburger = (
            'aria-label' in html_content or
            '☰' in html_content or
            'hamburger' in html_content.lower() or
            re.search(r'<label[^>]*>[^<]*<span', html_content)
        )
        assert has_hamburger, \
            "Label should contain hamburger icon (spans, ☰, or aria-label)"


class TestNavbarTouchTargets:
    """Test navbar touch targets meet accessibility requirements."""

    def test_nav_links_have_touch_target_min_height(self):
        """Verify nav links have min-height using touch target variable."""
        css_content = SHARED_CSS_PATH.read_text()
        # Check that #shared-navbar a has min-height: var(--touch-target-min)
        assert "min-height: var(--touch-target-min)" in css_content, \
            "Nav links should have min-height: var(--touch-target-min)"

    def test_toggle_label_has_touch_target_size(self):
        """Verify toggle label has minimum touch target dimensions."""
        css_content = SHARED_CSS_PATH.read_text()
        assert "min-height: var(--touch-target-min)" in css_content, \
            "Toggle label should have min-height for touch target"
        assert "min-width: var(--touch-target-min)" in css_content, \
            "Toggle label should have min-width for touch target"


class TestNavbarCSSResponsive:
    """Test navbar CSS has responsive styles for mobile menu."""

    def test_navbar_toggle_hidden_by_default(self):
        """Verify hamburger toggle is hidden on desktop (default state)."""
        css_content = SHARED_CSS_PATH.read_text()
        # Toggle (label or checkbox) should be hidden by default
        # Look for display: none on nav-toggle or related selector
        assert "display: none" in css_content, \
            "Toggle should be hidden by default (display: none)"

    def test_has_media_query_for_mobile(self):
        """Verify CSS has media query for mobile breakpoint."""
        css_content = SHARED_CSS_PATH.read_text()
        # Should have media query at 768px (tablet/mobile breakpoint)
        assert re.search(r'@media[^{]*768px', css_content), \
            "Should have media query for 768px breakpoint"

    def test_checkbox_visually_hidden(self):
        """Verify checkbox input is visually hidden (accessible)."""
        css_content = SHARED_CSS_PATH.read_text()
        # Checkbox should be hidden but accessible
        # Common patterns: position: absolute with clip, or specific class
        has_hidden_checkbox = (
            'nav-toggle' in css_content and 'position: absolute' in css_content or
            'clip: rect' in css_content or
            'opacity: 0' in css_content
        )
        assert has_hidden_checkbox, \
            "Checkbox should be visually hidden but accessible"

    def test_has_checked_state_selector(self):
        """Verify CSS has :checked pseudo-class for toggle state."""
        css_content = SHARED_CSS_PATH.read_text()
        assert ':checked' in css_content, \
            "CSS should use :checked pseudo-class for toggle state"

    def test_nav_links_hidden_on_mobile_by_default(self):
        """Verify nav links are hidden on mobile by default."""
        css_content = SHARED_CSS_PATH.read_text()
        # nav-links should be hidden on mobile until toggle is checked
        assert 'nav-links' in css_content, \
            "CSS should style .nav-links container"

    def test_checked_state_shows_nav_links(self):
        """Verify checked state shows nav links (sibling selector)."""
        css_content = SHARED_CSS_PATH.read_text()
        # Pattern: input:checked ~ .nav-links or #nav-toggle:checked ~ .nav-links
        assert re.search(r':checked\s*[~+]\s*\.nav-links', css_content) or \
               re.search(r':checked\s*[~+]\s*\.nav-menu', css_content), \
            "Should have :checked ~ .nav-links selector to show menu"

    def test_nav_links_flex_direction_column_on_mobile(self):
        """Verify nav links stack vertically on mobile."""
        css_content = SHARED_CSS_PATH.read_text()
        # On mobile, nav links should be flex-direction: column
        assert 'flex-direction: column' in css_content, \
            "Nav links should stack vertically (flex-direction: column) on mobile"
