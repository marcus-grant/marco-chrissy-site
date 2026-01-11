"""E2E tests for site command functionality."""

import subprocess


class TestSiteCommand:
    """Test the basic site command interface and subcommands."""

    def test_site_command_exists(self):
        """Test that 'uv run site' command is discoverable."""
        result = subprocess.run(
            ["uv", "run", "site", "--help"], capture_output=True, text=True
        )
        assert result.returncode == 0, f"site command not found: {result.stderr}"
        assert "usage:" in result.stdout.lower()

    def test_site_validate_subcommand_exists(self):
        """Test that 'site validate' subcommand exists."""
        result = subprocess.run(
            ["uv", "run", "site", "validate", "--help"], capture_output=True, text=True
        )
        assert result.returncode == 0, f"validate subcommand not found: {result.stderr}"
        assert "validate" in result.stdout.lower()

    def test_site_organize_subcommand_exists(self):
        """Test that 'site organize' subcommand exists."""
        result = subprocess.run(
            ["uv", "run", "site", "organize", "--help"], capture_output=True, text=True
        )
        assert result.returncode == 0, f"organize subcommand not found: {result.stderr}"
        assert "organize" in result.stdout.lower()

    def test_site_build_subcommand_exists(self):
        """Test that 'site build' subcommand exists."""
        result = subprocess.run(
            ["uv", "run", "site", "build", "--help"], capture_output=True, text=True
        )
        assert result.returncode == 0, f"build subcommand not found: {result.stderr}"
        assert "build" in result.stdout.lower()

    def test_site_deploy_subcommand_exists(self):
        """Test that 'site deploy' subcommand exists."""
        result = subprocess.run(
            ["uv", "run", "site", "deploy", "--help"], capture_output=True, text=True
        )
        assert result.returncode == 0, f"deploy subcommand not found: {result.stderr}"
        assert "deploy" in result.stdout.lower()

