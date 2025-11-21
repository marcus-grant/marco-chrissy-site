"""E2E tests for site build command."""

import subprocess
import pytest


class TestSiteBuild:
    """Test the site build command functionality."""

    @pytest.mark.skip(reason="Build command functionality not yet implemented")
    def test_build_generates_galleries(self):
        """Test that build command generates galleries with Galleria."""
        result = subprocess.run(
            ["uv", "run", "site", "build"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "gallery" in result.stdout.lower()

    @pytest.mark.skip(reason="Build command functionality not yet implemented")
    def test_build_generates_site_pages(self):
        """Test that build command generates site pages with Pelican."""
        result = subprocess.run(
            ["uv", "run", "site", "build"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "pelican" in result.stdout.lower()

    @pytest.mark.skip(reason="Build command functionality not yet implemented")
    def test_build_calls_organize_automatically(self):
        """Test that build automatically calls organize if needed."""
        result = subprocess.run(
            ["uv", "run", "site", "build"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        # Should see evidence that organize was called
        assert "organize" in result.stdout.lower()

    @pytest.mark.skip(reason="Build command functionality not yet implemented")
    def test_build_creates_output_structure(self):
        """Test that build creates proper output directory structure."""
        result = subprocess.run(
            ["uv", "run", "site", "build"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        # Should create output/pics/, output/galleries/, etc.
        pass

    @pytest.mark.skip(reason="Build command functionality not yet implemented")
    def test_build_is_idempotent(self):
        """Test that build skips work if already done."""
        pass