"""E2E tests for site deploy command."""

import subprocess
import pytest


class TestSiteDeploy:
    """Test the site deploy command functionality."""

    @pytest.mark.skip(reason="Deploy command functionality not yet implemented")
    def test_deploy_uploads_to_bunny_cdn(self):
        """Test that deploy command uploads to Bunny CDN."""
        result = subprocess.run(
            ["uv", "run", "site", "deploy"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "bunny" in result.stdout.lower() or "cdn" in result.stdout.lower()

    @pytest.mark.skip(reason="Deploy command functionality not yet implemented")
    def test_deploy_uses_dual_cdn_strategy(self):
        """Test that deploy uses separate buckets for photos vs site content."""
        result = subprocess.run(
            ["uv", "run", "site", "deploy"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        # Should upload pics/ to photos CDN, everything else to site CDN
        assert "photos" in result.stdout.lower()

    @pytest.mark.skip(reason="Deploy command functionality not yet implemented")
    def test_deploy_calls_build_automatically(self):
        """Test that deploy automatically calls build if needed."""
        result = subprocess.run(
            ["uv", "run", "site", "deploy"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        # Should see evidence that build was called
        assert "build" in result.stdout.lower()

    @pytest.mark.skip(reason="Deploy command functionality not yet implemented")
    def test_deploy_is_idempotent(self):
        """Test that deploy skips upload if files unchanged."""
        pass

    @pytest.mark.skip(reason="Deploy command functionality not yet implemented")
    def test_deploy_complete_pipeline_integration(self):
        """Test that deploy runs complete pipeline end-to-end."""
        # This is the ultimate E2E test - validate → organize → build → deploy
        result = subprocess.run(
            ["uv", "run", "site", "deploy"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        # Should see evidence of all stages
        assert "validate" in result.stdout.lower()
        assert "organize" in result.stdout.lower()  
        assert "build" in result.stdout.lower()
        assert "deploy" in result.stdout.lower()