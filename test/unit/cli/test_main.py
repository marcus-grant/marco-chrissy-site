"""Unit tests for CLI main entry point."""

import pytest
from unittest.mock import patch, MagicMock


class TestCLIMain:
    """Test the main CLI entry point and command discovery."""

    def test_main_function_exists(self):
        """Test that main CLI function can be imported."""
        from cli.main import main
        assert callable(main)

    def test_main_creates_click_group(self):
        """Test that main function creates Click command group."""
        from cli.main import main
        
        # Should be a Click group with commands
        assert hasattr(main, 'commands')
        assert 'validate' in main.commands
        assert 'organize' in main.commands  
        assert 'build' in main.commands
        assert 'deploy' in main.commands

    def test_validate_command_exists(self):
        """Test that validate command can be imported and called."""
        from cli.commands.validate import validate
        assert callable(validate)

    def test_organize_command_exists(self):
        """Test that organize command can be imported and called."""
        from cli.commands.organize import organize
        assert callable(organize)

    def test_build_command_exists(self):
        """Test that build command can be imported and called."""
        from cli.commands.build import build
        assert callable(build)

    def test_deploy_command_exists(self):
        """Test that deploy command can be imported and called."""
        from cli.commands.deploy import deploy
        assert callable(deploy)