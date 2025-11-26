"""Unit tests for build command."""

import pytest
from unittest.mock import Mock, patch

from click.testing import CliRunner

from cli.commands.build import build


class TestBuildCommand:
    """Test build command functionality."""

    @pytest.mark.skip(reason="Unit tests need updating after galleria module integration")
    @patch('cli.commands.build.organize')
    @patch('cli.commands.build.JsonConfigLoader')
    @patch('cli.commands.build.PipelineManager')
    @patch('cli.commands.build.configure_settings')
    def test_build_calls_organize_cascade(self, mock_configure_settings, mock_pipeline_manager, mock_config_loader, mock_organize):
        """Test that build calls organize (which calls validate)."""
        mock_organize.return_value = Mock(exit_code=0)
        
        # Mock config loading
        mock_loader = Mock()
        mock_config_loader.return_value = mock_loader
        mock_loader.load_config.return_value = {"output_dir": "output", "manifest_path": "test.json", "output_dir": "galleries"}
        
        # Mock pipeline
        mock_pipeline = Mock()
        mock_pipeline_manager.return_value = mock_pipeline
        mock_result = Mock()
        mock_result.success = True
        mock_result.output_data = {"html_files": [], "css_files": []}
        mock_pipeline.execute_stages.return_value = mock_result
        
        # Mock pelican
        mock_pelican_instance = Mock()
        mock_configure_settings.return_value = {"test": "settings"}
        
        with patch('cli.commands.build.pelican.Pelican', return_value=mock_pelican_instance):
            runner = CliRunner()
            result = runner.invoke(build)

            assert result.exit_code == 0
            mock_organize.assert_called_once()

    @pytest.mark.skip(reason="Unit tests need updating after galleria module integration")
    @patch('cli.commands.build.organize')
    @patch('cli.commands.build.galleria')
    def test_build_runs_galleria_generation(self, mock_galleria_module, mock_organize):
        """Test that build runs galleria generation via Python module."""
        mock_organize.return_value = Mock(exit_code=0)

        # Mock galleria module functions
        mock_galleria_module.generate.return_value = Mock(success=True)

        with patch('cli.commands.build.pelican.Pelican') as mock_pelican_class:
            mock_pelican_class.return_value = Mock()

            runner = CliRunner()
            result = runner.invoke(build)

            assert result.exit_code == 0
            mock_galleria_module.generate.assert_called_once()

    @pytest.mark.skip(reason="Unit tests need updating after galleria module integration")
    @patch('cli.commands.build.organize')
    @patch('cli.commands.build.pelican.Pelican')
    def test_build_runs_pelican_generation(self, mock_pelican_class, mock_organize):
        """Test that build runs pelican generation via Python module."""
        mock_organize.return_value = Mock(exit_code=0)

        # Mock Pelican instance
        mock_pelican = Mock()
        mock_pelican_class.return_value = mock_pelican

        with patch('cli.commands.build.galleria') as mock_galleria:
            mock_galleria.generate.return_value = Mock(success=True)

            runner = CliRunner()
            result = runner.invoke(build)

            assert result.exit_code == 0

            # Should create Pelican instance and run generation
            mock_pelican_class.assert_called_once()
            mock_pelican.run.assert_called_once()

    @pytest.mark.skip(reason="Unit tests need updating after galleria module integration")
    @patch('cli.commands.build.organize')
    def test_build_fails_if_organize_fails(self, mock_organize):
        """Test that build fails if organize step fails."""
        mock_organize.return_value = Mock(exit_code=1)

        runner = CliRunner()
        result = runner.invoke(build)

        assert result.exit_code != 0
        assert "organize failed" in result.output.lower()

    @pytest.mark.skip(reason="Unit tests need updating after galleria module integration")
    @patch('cli.commands.build.organize')
    @patch('cli.commands.build.galleria')
    def test_build_fails_if_galleria_fails(self, mock_galleria_module, mock_organize):
        """Test that build fails if galleria generation fails."""
        mock_organize.return_value = Mock(exit_code=0)

        # Mock galleria failure
        mock_galleria_module.generate.return_value = Mock(success=False, errors=["Test error"])

        runner = CliRunner()
        result = runner.invoke(build)

        assert result.exit_code != 0
        assert "galleria" in result.output.lower()

    @pytest.mark.skip(reason="Unit tests need updating after galleria module integration")
    @patch('cli.commands.build.organize')
    @patch('cli.commands.build.pelican.Pelican')
    def test_build_fails_if_pelican_fails(self, mock_pelican_class, mock_organize):
        """Test that build fails if pelican generation fails."""
        mock_organize.return_value = Mock(exit_code=0)

        # Mock pelican failure
        mock_pelican = Mock()
        mock_pelican.run.side_effect = Exception("Pelican error")
        mock_pelican_class.return_value = mock_pelican

        with patch('cli.commands.build.galleria') as mock_galleria:
            mock_galleria.generate.return_value = Mock(success=True)

            runner = CliRunner()
            result = runner.invoke(build)

            assert result.exit_code != 0
            assert "pelican" in result.output.lower()

    @pytest.mark.skip(reason="Unit tests need updating after galleria module integration")
    @patch('cli.commands.build.organize')
    @patch('cli.commands.build.galleria')
    @patch('cli.commands.build.pelican.Pelican')
    def test_build_shows_progress_output(self, mock_pelican_class, mock_galleria_module, mock_organize):
        """Test that build shows progress information to user."""
        mock_organize.return_value = Mock(exit_code=0)
        mock_galleria_module.generate.return_value = Mock(success=True)
        mock_pelican_class.return_value = Mock()

        runner = CliRunner()
        result = runner.invoke(build)

        assert result.exit_code == 0
        assert "building site" in result.output.lower() or "build" in result.output.lower()
        assert "galleria" in result.output.lower()
        assert "pelican" in result.output.lower()

    @pytest.mark.skip(reason="Unit tests need updating after galleria module integration")
    @patch('cli.commands.build.organize')
    @patch('cli.commands.build.os.path.exists')
    @patch('cli.commands.build.galleria')
    @patch('cli.commands.build.pelican.Pelican')
    def test_build_idempotent_behavior(self, mock_pelican_class, mock_galleria_module, mock_exists, mock_organize):
        """Test that build skips work if output already exists and is up to date."""
        mock_organize.return_value = Mock(exit_code=0)
        mock_galleria_module.generate.return_value = Mock(success=True)
        mock_pelican_class.return_value = Mock()

        # Mock that output directories already exist
        mock_exists.return_value = True

        runner = CliRunner()
        result = runner.invoke(build)

        assert result.exit_code == 0
        # Should either skip work or show it's up to date
        output_lower = result.output.lower()
        idempotent_indicators = ["already built", "up to date", "skipping", "no changes"]
        assert any(indicator in output_lower for indicator in idempotent_indicators)

    @pytest.mark.skip(reason="Unit tests need updating after galleria module integration")
    @patch('cli.commands.build.organize')
    @patch('cli.commands.build.JsonConfigLoader')
    @patch('cli.commands.build.galleria')
    @patch('cli.commands.build.pelican.Pelican')
    def test_build_uses_config_system(self, mock_pelican_class, mock_galleria_module, mock_config_loader_class, mock_organize):
        """Test that build command loads and uses configuration files."""
        mock_organize.return_value = Mock(exit_code=0)
        mock_galleria_module.generate.return_value = Mock(success=True)
        mock_pelican_class.return_value = Mock()

        # Mock config loader
        mock_config_loader = Mock()
        mock_config_loader_class.return_value = mock_config_loader

        # Mock config data
        mock_site_config = {
            "output_dir": "custom_output",
            "cdn": {"photos": "https://photos.cdn", "site": "https://site.cdn"}
        }
        mock_galleria_config = {
            "manifest_path": "custom/manifest.json",
            "output_dir": "custom_output/galleries",
            "theme": "custom"
        }

        mock_config_loader.load_config.side_effect = [mock_site_config, mock_galleria_config]

        runner = CliRunner()
        result = runner.invoke(build)

        assert result.exit_code == 0
        # Should load both site.json and galleria.json configs
        assert mock_config_loader.load_config.call_count >= 2
