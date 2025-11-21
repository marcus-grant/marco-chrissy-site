"""E2E tests for site organize command."""

import subprocess
import pytest


class TestSiteOrganize:
    """Test the site organize command functionality."""

    @pytest.mark.skip(reason="Organize command functionality not yet implemented")
    def test_organize_calls_normpic(self):
        """Test that organize command orchestrates NormPic."""
        result = subprocess.run(
            ["uv", "run", "site", "organize"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "normpic" in result.stdout.lower()

    @pytest.mark.skip(reason="Organize command functionality not yet implemented")
    def test_organize_generates_manifest(self):
        """Test that organize command generates photo manifest."""
        result = subprocess.run(
            ["uv", "run", "site", "organize"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "manifest" in result.stdout.lower()

    @pytest.mark.skip(reason="Organize command functionality not yet implemented")
    def test_organize_calls_validate_automatically(self):
        """Test that organize automatically calls validate if needed."""
        result = subprocess.run(
            ["uv", "run", "site", "organize"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        # Should see evidence that validate was called
        assert "validate" in result.stdout.lower()

    @pytest.mark.skip(reason="Organize command functionality not yet implemented")
    def test_organize_is_idempotent(self):
        """Test that organize skips work if already done."""
        # Run twice, second should be faster/skip work
        pass