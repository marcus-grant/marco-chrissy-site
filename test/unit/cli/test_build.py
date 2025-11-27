"""Unit tests for build command."""

from unittest.mock import Mock, patch

from click.testing import CliRunner

from cli.commands.build import build


class TestBuildCommand:
    """Test build command functionality."""

    @patch('cli.commands.build.organize')
    @patch('cli.commands.build.BuildOrchestrator')
    def test_build_calls_organize_cascade(self, mock_orchestrator_class, mock_organize):
        """Test that build calls organize (which calls validate)."""
        # Mock organize success
        mock_organize.return_value = Mock(exit_code=0)

        # Mock orchestrator success
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.execute.return_value = True

        runner = CliRunner()
        result = runner.invoke(build)

        assert result.exit_code == 0
        mock_organize.assert_called_once()
        mock_orchestrator.execute.assert_called_once()

    @patch('cli.commands.build.organize')
    @patch('cli.commands.build.BuildOrchestrator')
    def test_build_runs_orchestrator_execution(self, mock_orchestrator_class, mock_organize):
        """Test that build runs the orchestrator to coordinate galleria and pelican."""
        mock_organize.return_value = Mock(exit_code=0)

        # Mock orchestrator success
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.execute.return_value = True

        runner = CliRunner()
        result = runner.invoke(build)

        assert result.exit_code == 0
        mock_orchestrator.execute.assert_called_once()

    @patch('cli.commands.build.organize')
    @patch('cli.commands.build.BuildOrchestrator')
    def test_build_fails_if_organize_fails(self, mock_orchestrator_class, mock_organize):
        """Test that build fails if organize step fails."""
        mock_organize.return_value = Mock(exit_code=1)

        # Orchestrator should not be called if organize fails
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator

        runner = CliRunner()
        result = runner.invoke(build)

        assert result.exit_code != 0
        assert "organize failed" in result.output.lower()
        mock_orchestrator.execute.assert_not_called()

    @patch('cli.commands.build.organize')
    @patch('cli.commands.build.BuildOrchestrator')
    def test_build_fails_if_orchestrator_fails(self, mock_orchestrator_class, mock_organize):
        """Test that build fails if orchestrator step fails."""
        mock_organize.return_value = Mock(exit_code=0)

        # Mock orchestrator failure - raises BuildError
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        from build.exceptions import BuildError
        mock_orchestrator.execute.side_effect = BuildError("Test orchestrator failure")

        runner = CliRunner()
        result = runner.invoke(build)

        assert result.exit_code != 0
        assert "build failed" in result.output.lower()

    @patch('cli.commands.build.organize')
    @patch('cli.commands.build.BuildOrchestrator')
    def test_build_shows_progress_output(self, mock_orchestrator_class, mock_organize):
        """Test that build shows progress information to user."""
        mock_organize.return_value = Mock(exit_code=0)

        # Mock orchestrator success
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.execute.return_value = True

        runner = CliRunner()
        result = runner.invoke(build)

        assert result.exit_code == 0
        assert "building site" in result.output.lower()
        assert "organization" in result.output.lower()
        assert "generating galleries" in result.output.lower()

    @patch('cli.commands.build.organize')
    @patch('cli.commands.build.BuildOrchestrator')
    def test_build_orchestrator_success_message(self, mock_orchestrator_class, mock_organize):
        """Test that build shows success message when orchestrator succeeds."""
        mock_organize.return_value = Mock(exit_code=0)

        # Mock orchestrator success
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.execute.return_value = True

        runner = CliRunner()
        result = runner.invoke(build)

        assert result.exit_code == 0
        assert "completed successfully" in result.output.lower()

    @patch('cli.commands.build.organize')
    @patch('cli.commands.build.BuildOrchestrator')
    def test_build_organize_cascade_result_handling(self, mock_orchestrator_class, mock_organize):
        """Test that build properly handles organize result with exit_code attribute."""
        # Test that organize result with exit_code=0 allows build to proceed
        mock_organize.return_value = Mock(exit_code=0)

        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.execute.return_value = True

        runner = CliRunner()
        result = runner.invoke(build)

        assert result.exit_code == 0
        mock_orchestrator.execute.assert_called_once()

        # Test that organize result without exit_code also works
        mock_organize.reset_mock()
        mock_orchestrator.execute.reset_mock()
        mock_organize.return_value = Mock(spec=[])  # No exit_code attribute

        result = runner.invoke(build)
        assert result.exit_code == 0
        mock_orchestrator.execute.assert_called_once()

    @patch('cli.commands.build.organize')
    @patch('cli.commands.build.BuildOrchestrator')
    def test_build_orchestrator_delegates_idempotency(self, mock_orchestrator_class, mock_organize):
        """Test that build delegates idempotency logic to orchestrator."""
        mock_organize.return_value = Mock(exit_code=0)

        # Mock orchestrator success - idempotency is handled by orchestrator internally
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.execute.return_value = True

        runner = CliRunner()
        result = runner.invoke(build)

        assert result.exit_code == 0
        # Build command trusts orchestrator to handle idempotency
        mock_orchestrator.execute.assert_called_once()

    @patch('cli.commands.build.organize')
    @patch('cli.commands.build.BuildOrchestrator')
    def test_build_orchestrator_handles_config_loading(self, mock_orchestrator_class, mock_organize):
        """Test that build delegates config handling to orchestrator."""
        mock_organize.return_value = Mock(exit_code=0)

        # Mock orchestrator success - config loading is handled by orchestrator internally
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.execute.return_value = True

        runner = CliRunner()
        result = runner.invoke(build)

        assert result.exit_code == 0
        # Build command delegates config loading to orchestrator
        mock_orchestrator_class.assert_called_once()
        mock_orchestrator.execute.assert_called_once()
