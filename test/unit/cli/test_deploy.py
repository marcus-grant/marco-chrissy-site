"""Unit tests for deploy command."""

from unittest.mock import Mock, patch

from click.testing import CliRunner

from cli.commands.deploy import deploy


class TestDeployCommand:
    """Test deploy command functionality."""

    @patch("cli.commands.deploy.build")
    @patch("cli.commands.deploy.DeployOrchestrator")
    @patch("cli.commands.deploy.create_client_from_env")
    @patch("cli.commands.deploy.ManifestComparator")
    @patch("cli.commands.deploy.Path")
    def test_deploy_calls_build_cascade(self, mock_path_class, mock_manifest_comp_class,
                                      mock_client_factory, mock_orchestrator_class, mock_build):
        """Test that deploy calls build (which calls organize and validate)."""
        # Mock build success
        mock_build.return_value = Mock(exit_code=0)

        # Mock output directory exists
        mock_output_dir = Mock()
        mock_output_dir.exists.return_value = True
        mock_path_class.return_value = mock_output_dir

        # Mock orchestrator success
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.execute_deployment.return_value = True

        runner = CliRunner()
        result = runner.invoke(deploy)

        assert result.exit_code == 0
        mock_build.assert_called_once()
        mock_orchestrator.execute_deployment.assert_called_once_with(mock_output_dir)

    @patch("cli.commands.deploy.build")
    @patch("cli.commands.deploy.DeployOrchestrator")
    @patch("cli.commands.deploy.create_client_from_env")
    @patch("cli.commands.deploy.ManifestComparator")
    @patch("cli.commands.deploy.Path")
    def test_deploy_fails_if_build_fails(self, mock_path_class, mock_manifest_comp_class,
                                       mock_client_factory, mock_orchestrator_class, mock_build):
        """Test that deploy fails if build step fails."""
        mock_build.return_value = Mock(exit_code=1)

        # Orchestrator should not be called if build fails
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator

        runner = CliRunner()
        result = runner.invoke(deploy)

        assert result.exit_code != 0
        assert "build failed" in result.output.lower()
        mock_orchestrator.execute_deployment.assert_not_called()

    @patch("cli.commands.deploy.build")
    @patch("cli.commands.deploy.DeployOrchestrator")
    @patch("cli.commands.deploy.create_client_from_env")
    @patch("cli.commands.deploy.ManifestComparator")
    @patch("cli.commands.deploy.Path")
    def test_deploy_fails_if_output_missing(self, mock_path_class, mock_manifest_comp_class,
                                          mock_client_factory, mock_orchestrator_class, mock_build):
        """Test that deploy fails if output directory doesn't exist."""
        mock_build.return_value = Mock(exit_code=0)

        # Mock output directory doesn't exist
        mock_output_dir = Mock()
        mock_output_dir.exists.return_value = False
        mock_path_class.return_value = mock_output_dir

        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator

        runner = CliRunner()
        result = runner.invoke(deploy)

        assert result.exit_code != 0
        assert "output directory not found" in result.output.lower()
        mock_orchestrator.execute_deployment.assert_not_called()

    @patch("cli.commands.deploy.build")
    @patch("cli.commands.deploy.DeployOrchestrator")
    @patch("cli.commands.deploy.create_client_from_env")
    @patch("cli.commands.deploy.ManifestComparator")
    @patch("cli.commands.deploy.Path")
    def test_deploy_creates_orchestrator_with_dependencies(self, mock_path_class,
                                                         mock_manifest_comp_class,
                                                         mock_client_factory,
                                                         mock_orchestrator_class, mock_build):
        """Test that deploy creates orchestrator with proper dependencies."""
        mock_build.return_value = Mock(exit_code=0)

        # Mock output directory exists
        mock_output_dir = Mock()
        mock_output_dir.exists.return_value = True
        mock_path_class.return_value = mock_output_dir

        # Mock component creation
        mock_client = Mock()
        mock_client_factory.return_value = mock_client
        mock_manifest_comp = Mock()
        mock_manifest_comp_class.return_value = mock_manifest_comp

        # Mock orchestrator success
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.execute_deployment.return_value = True

        runner = CliRunner()
        result = runner.invoke(deploy)

        assert result.exit_code == 0
        # Verify components were created
        mock_client_factory.assert_called_once()
        mock_manifest_comp_class.assert_called_once()
        # Verify orchestrator was created with dependencies
        mock_orchestrator_class.assert_called_once_with(mock_client, mock_manifest_comp)

    @patch("cli.commands.deploy.build")
    @patch("cli.commands.deploy.DeployOrchestrator")
    @patch("cli.commands.deploy.create_client_from_env")
    @patch("cli.commands.deploy.ManifestComparator")
    @patch("cli.commands.deploy.Path")
    def test_deploy_fails_if_orchestrator_fails(self, mock_path_class, mock_manifest_comp_class,
                                               mock_client_factory, mock_orchestrator_class, mock_build):
        """Test that deploy fails if orchestrator deployment fails."""
        mock_build.return_value = Mock(exit_code=0)

        # Mock output directory exists
        mock_output_dir = Mock()
        mock_output_dir.exists.return_value = True
        mock_path_class.return_value = mock_output_dir

        # Mock orchestrator failure
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.execute_deployment.return_value = False

        runner = CliRunner()
        result = runner.invoke(deploy)

        assert result.exit_code != 0
        assert "deploy failed" in result.output.lower()

    @patch("cli.commands.deploy.build")
    @patch("cli.commands.deploy.DeployOrchestrator")
    @patch("cli.commands.deploy.create_client_from_env")
    @patch("cli.commands.deploy.ManifestComparator")
    @patch("cli.commands.deploy.Path")
    def test_deploy_handles_exceptions(self, mock_path_class, mock_manifest_comp_class,
                                     mock_client_factory, mock_orchestrator_class, mock_build):
        """Test that deploy handles exceptions gracefully."""
        mock_build.return_value = Mock(exit_code=0)

        # Mock output directory exists
        mock_output_dir = Mock()
        mock_output_dir.exists.return_value = True
        mock_path_class.return_value = mock_output_dir

        # Mock orchestrator exception
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.execute_deployment.side_effect = Exception("Test deploy error")

        runner = CliRunner()
        result = runner.invoke(deploy)

        assert result.exit_code != 0
        assert "deploy failed" in result.output.lower()
        assert "test deploy error" in result.output.lower()

    @patch("cli.commands.deploy.build")
    @patch("cli.commands.deploy.DeployOrchestrator")
    @patch("cli.commands.deploy.create_client_from_env")
    @patch("cli.commands.deploy.ManifestComparator")
    @patch("cli.commands.deploy.Path")
    def test_deploy_shows_progress_output(self, mock_path_class, mock_manifest_comp_class,
                                        mock_client_factory, mock_orchestrator_class, mock_build):
        """Test that deploy shows progress information to user."""
        mock_build.return_value = Mock(exit_code=0)

        # Mock output directory exists
        mock_output_dir = Mock()
        mock_output_dir.exists.return_value = True
        mock_path_class.return_value = mock_output_dir

        # Mock orchestrator success
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.execute_deployment.return_value = True

        runner = CliRunner()
        result = runner.invoke(deploy)

        assert result.exit_code == 0
        assert "deploying site" in result.output.lower()
        assert "running build" in result.output.lower()
        assert "uploading to cdn" in result.output.lower()
        assert "dual zone strategy" in result.output.lower()
        assert "completed successfully" in result.output.lower()
