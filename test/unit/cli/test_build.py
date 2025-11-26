"""Unit tests for build command."""

import subprocess
from unittest.mock import Mock, call, patch

from click.testing import CliRunner

from cli.commands.build import build


class TestBuildCommand:
    """Test build command functionality."""

    @patch('cli.commands.build.organize')
    def test_build_calls_organize_cascade(self, mock_organize):
        """Test that build calls organize (which calls validate)."""
        mock_organize.return_value = Mock(exit_code=0)
        
        with patch('cli.commands.build.subprocess.run') as mock_subprocess:
            # Mock successful galleria and pelican runs
            mock_subprocess.return_value = Mock(returncode=0, stdout="success", stderr="")
            
            runner = CliRunner()
            result = runner.invoke(build)

            assert result.exit_code == 0
            mock_organize.assert_called_once()

    @patch('cli.commands.build.organize')
    @patch('cli.commands.build.subprocess.run')
    def test_build_runs_galleria_generation(self, mock_subprocess, mock_organize):
        """Test that build runs galleria generation via CLI."""
        mock_organize.return_value = Mock(exit_code=0)
        mock_subprocess.return_value = Mock(returncode=0, stdout="Gallery generated", stderr="")
        
        runner = CliRunner()
        result = runner.invoke(build)

        assert result.exit_code == 0
        
        # Should call galleria generate command
        galleria_calls = [call for call in mock_subprocess.call_args_list 
                         if 'galleria' in str(call)]
        assert len(galleria_calls) >= 1, "Should call galleria generate"

    @patch('cli.commands.build.organize')
    @patch('cli.commands.build.subprocess.run')
    def test_build_runs_pelican_generation(self, mock_subprocess, mock_organize):
        """Test that build runs pelican generation via CLI."""
        mock_organize.return_value = Mock(exit_code=0)
        mock_subprocess.return_value = Mock(returncode=0, stdout="Site generated", stderr="")
        
        runner = CliRunner()
        result = runner.invoke(build)

        assert result.exit_code == 0
        
        # Should call pelican command
        pelican_calls = [call for call in mock_subprocess.call_args_list 
                        if 'pelican' in str(call)]
        assert len(pelican_calls) >= 1, "Should call pelican generate"

    @patch('cli.commands.build.organize')
    def test_build_fails_if_organize_fails(self, mock_organize):
        """Test that build fails if organize step fails."""
        mock_organize.return_value = Mock(exit_code=1)
        
        runner = CliRunner()
        result = runner.invoke(build)

        assert result.exit_code != 0
        assert "organize failed" in result.output.lower()

    @patch('cli.commands.build.organize')
    @patch('cli.commands.build.subprocess.run')
    def test_build_fails_if_galleria_fails(self, mock_subprocess, mock_organize):
        """Test that build fails if galleria generation fails."""
        mock_organize.return_value = Mock(exit_code=0)
        mock_subprocess.return_value = Mock(returncode=1, stdout="", stderr="Galleria error")
        
        runner = CliRunner()
        result = runner.invoke(build)

        assert result.exit_code != 0
        assert "galleria" in result.output.lower()

    @patch('cli.commands.build.organize')
    @patch('cli.commands.build.subprocess.run')  
    def test_build_shows_progress_output(self, mock_subprocess, mock_organize):
        """Test that build shows progress information to user."""
        mock_organize.return_value = Mock(exit_code=0)
        mock_subprocess.return_value = Mock(returncode=0, stdout="success", stderr="")
        
        runner = CliRunner()
        result = runner.invoke(build)

        assert result.exit_code == 0
        assert "building site" in result.output.lower() or "build" in result.output.lower()
        assert "galleria" in result.output.lower()
        assert "pelican" in result.output.lower()

    @patch('cli.commands.build.organize')
    @patch('cli.commands.build.os.path.exists')
    @patch('cli.commands.build.subprocess.run')
    def test_build_idempotent_behavior(self, mock_subprocess, mock_exists, mock_organize):
        """Test that build skips work if output already exists and is up to date."""
        mock_organize.return_value = Mock(exit_code=0)
        
        # Mock that output directories already exist 
        mock_exists.return_value = True
        
        runner = CliRunner()
        result = runner.invoke(build)

        assert result.exit_code == 0
        # Should either skip work or show it's up to date
        output_lower = result.output.lower()
        idempotent_indicators = ["already built", "up to date", "skipping", "no changes"]
        assert any(indicator in output_lower for indicator in idempotent_indicators)