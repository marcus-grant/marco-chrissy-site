"""Unit tests for shared CSS variables and responsive design tokens."""

import re
from pathlib import Path

# Path to the shared CSS file
SHARED_CSS_PATH = Path(__file__).parent.parent.parent / "themes/shared/static/css/shared.css"


class TestResponsiveBreakpointVariables:
    """Test CSS custom properties for responsive breakpoints."""

    def test_shared_css_file_exists(self):
        """Verify shared.css file exists at expected location."""
        assert SHARED_CSS_PATH.exists(), f"shared.css not found at {SHARED_CSS_PATH}"

    def test_has_root_block(self):
        """Verify shared.css has a :root block for CSS custom properties."""
        css_content = SHARED_CSS_PATH.read_text()
        assert ":root" in css_content, "shared.css should have :root block for CSS variables"

    def test_breakpoint_sm_variable(self):
        """Verify --breakpoint-sm: 480px for mobile landscape."""
        css_content = SHARED_CSS_PATH.read_text()
        assert "--breakpoint-sm: 480px" in css_content, \
            "Missing --breakpoint-sm: 480px (mobile landscape)"

    def test_breakpoint_md_variable(self):
        """Verify --breakpoint-md: 768px for tablet portrait."""
        css_content = SHARED_CSS_PATH.read_text()
        assert "--breakpoint-md: 768px" in css_content, \
            "Missing --breakpoint-md: 768px (tablet portrait)"

    def test_breakpoint_lg_variable(self):
        """Verify --breakpoint-lg: 1024px for tablet landscape."""
        css_content = SHARED_CSS_PATH.read_text()
        assert "--breakpoint-lg: 1024px" in css_content, \
            "Missing --breakpoint-lg: 1024px (tablet landscape)"

    def test_breakpoint_xl_variable(self):
        """Verify --breakpoint-xl: 1200px for desktop."""
        css_content = SHARED_CSS_PATH.read_text()
        assert "--breakpoint-xl: 1200px" in css_content, \
            "Missing --breakpoint-xl: 1200px (desktop)"


class TestTouchTargetVariables:
    """Test CSS custom properties for touch target accessibility."""

    def test_touch_target_min_variable(self):
        """Verify --touch-target-min: 44px per WCAG 2.1 AAA guidelines."""
        css_content = SHARED_CSS_PATH.read_text()
        assert "--touch-target-min: 44px" in css_content, \
            "Missing --touch-target-min: 44px (WCAG touch target minimum)"


class TestSpacingVariables:
    """Test CSS custom properties for spacing scale."""

    def test_spacing_xs_variable(self):
        """Verify --spacing-xs exists for extra small spacing."""
        css_content = SHARED_CSS_PATH.read_text()
        # Match --spacing-xs with any value
        assert re.search(r"--spacing-xs:\s*[^;]+;", css_content), \
            "Missing --spacing-xs variable"

    def test_spacing_sm_variable(self):
        """Verify --spacing-sm exists for small spacing."""
        css_content = SHARED_CSS_PATH.read_text()
        assert re.search(r"--spacing-sm:\s*[^;]+;", css_content), \
            "Missing --spacing-sm variable"

    def test_spacing_md_variable(self):
        """Verify --spacing-md exists for medium spacing."""
        css_content = SHARED_CSS_PATH.read_text()
        assert re.search(r"--spacing-md:\s*[^;]+;", css_content), \
            "Missing --spacing-md variable"

    def test_spacing_lg_variable(self):
        """Verify --spacing-lg exists for large spacing."""
        css_content = SHARED_CSS_PATH.read_text()
        assert re.search(r"--spacing-lg:\s*[^;]+;", css_content), \
            "Missing --spacing-lg variable"


class TestCSSVariableOrganization:
    """Test CSS variable organization and structure."""

    def test_variables_in_root_block(self):
        """Verify all responsive variables are within :root block."""
        css_content = SHARED_CSS_PATH.read_text()

        # Extract :root block content
        root_match = re.search(r":root\s*\{([^}]+)\}", css_content)
        assert root_match, ":root block not found or malformed"

        root_content = root_match.group(1)

        # Check all breakpoint variables are in :root
        assert "--breakpoint-sm" in root_content, "--breakpoint-sm should be in :root"
        assert "--breakpoint-md" in root_content, "--breakpoint-md should be in :root"
        assert "--breakpoint-lg" in root_content, "--breakpoint-lg should be in :root"
        assert "--breakpoint-xl" in root_content, "--breakpoint-xl should be in :root"
        assert "--touch-target-min" in root_content, "--touch-target-min should be in :root"

    def test_breakpoints_in_ascending_order(self):
        """Verify breakpoint values are in logical ascending order."""
        css_content = SHARED_CSS_PATH.read_text()

        # Extract numeric values
        sm_match = re.search(r"--breakpoint-sm:\s*(\d+)px", css_content)
        md_match = re.search(r"--breakpoint-md:\s*(\d+)px", css_content)
        lg_match = re.search(r"--breakpoint-lg:\s*(\d+)px", css_content)
        xl_match = re.search(r"--breakpoint-xl:\s*(\d+)px", css_content)

        assert all([sm_match, md_match, lg_match, xl_match]), \
            "All breakpoint variables must be defined with px values"

        sm = int(sm_match.group(1))
        md = int(md_match.group(1))
        lg = int(lg_match.group(1))
        xl = int(xl_match.group(1))

        assert sm < md < lg < xl, \
            f"Breakpoints should be ascending: sm({sm}) < md({md}) < lg({lg}) < xl({xl})"
