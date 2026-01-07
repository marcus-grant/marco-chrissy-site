"""Unit tests for deploy command."""

from unittest.mock import Mock, patch

from click.testing import CliRunner

from cli.commands.deploy import deploy


class TestDeployCommand:
    """Test deploy command functionality."""

    @patch("cli.commands.deploy.build")
    @patch("cli.commands.deploy.DeployOrchestrator")
    @patch("cli.commands.deploy.create_clients_from_config")
    @patch("cli.commands.deploy.ManifestComparator")
    @patch("cli.commands.deploy.Path")
    @patch("cli.commands.deploy.ConfigManager")
    def test_deploy_calls_build_cascade(self, mock_config_manager_class, mock_path_class, mock_manifest_comp_class,
                                      mock_client_factory, mock_orchestrator_class, mock_build):
        """Test that deploy calls build (which calls organize and validate)."""
        # Mock config loading
        mock_config_manager = Mock()
        mock_config_manager_class.return_value = mock_config_manager
        deploy_config = {"test": "config"}
        mock_config_manager.load_deploy_config.return_value = deploy_config

        # Mock dual client creation
        mock_photo_client = Mock()
        mock_site_client = Mock()
        mock_client_factory.return_value = (mock_photo_client, mock_site_client)

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
    @patch("cli.commands.deploy.create_clients_from_config")
    @patch("cli.commands.deploy.ManifestComparator")
    @patch("cli.commands.deploy.Path")
    @patch("cli.commands.deploy.ConfigManager")
    def test_deploy_fails_if_build_fails(self, mock_config_manager_class, mock_path_class, mock_manifest_comp_class,
                                       mock_client_factory, mock_orchestrator_class, mock_build):
        """Test that deploy fails if build step fails."""
        # Mock config loading
        mock_config_manager = Mock()
        mock_config_manager_class.return_value = mock_config_manager
        mock_config_manager.load_deploy_config.return_value = {"test": "config"}

        mock_build.return_value = Mock(exit_code=1)

        # Orchestrator should not be called if build fails
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator

        # Mock dual client creation
        mock_client_factory.return_value = (Mock(), Mock())

        runner = CliRunner()
        result = runner.invoke(deploy)

        assert result.exit_code != 0
        assert "build failed" in result.output.lower()
        mock_orchestrator.execute_deployment.assert_not_called()

    @patch("cli.commands.deploy.build")
    @patch("cli.commands.deploy.DeployOrchestrator")
    @patch("cli.commands.deploy.create_clients_from_config")
    @patch("cli.commands.deploy.ManifestComparator")
    @patch("cli.commands.deploy.Path")
    @patch("cli.commands.deploy.ConfigManager")
    def test_deploy_fails_if_output_missing(self, mock_config_manager_class, mock_path_class, mock_manifest_comp_class,
                                          mock_client_factory, mock_orchestrator_class, mock_build):
        """Test that deploy fails if output directory doesn't exist."""
        # Mock config loading
        mock_config_manager = Mock()
        mock_config_manager_class.return_value = mock_config_manager
        mock_config_manager.load_deploy_config.return_value = {"test": "config"}

        # Mock dual client creation
        mock_client_factory.return_value = (Mock(), Mock())

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
    @patch("cli.commands.deploy.create_clients_from_config")
    @patch("cli.commands.deploy.ManifestComparator")
    @patch("cli.commands.deploy.Path")
    @patch("cli.commands.deploy.ConfigManager")
    def test_deploy_creates_orchestrator_with_dependencies(self, mock_config_manager_class, mock_path_class,
                                                         mock_manifest_comp_class,
                                                         mock_client_factory,
                                                         mock_orchestrator_class, mock_build):
        """Test that deploy creates orchestrator with proper dependencies."""
        # Mock config loading
        mock_config_manager = Mock()
        mock_config_manager_class.return_value = mock_config_manager
        mock_config_manager.load_deploy_config.return_value = {"test": "config"}

        mock_build.return_value = Mock(exit_code=0)

        # Mock output directory exists
        mock_output_dir = Mock()
        mock_output_dir.exists.return_value = True
        mock_path_class.return_value = mock_output_dir

        # Mock dual client creation
        mock_photo_client = Mock()
        mock_site_client = Mock()
        mock_client_factory.return_value = (mock_photo_client, mock_site_client)
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
        # Verify orchestrator was created with dual clients and manifest comparator
        mock_orchestrator_class.assert_called_once_with(
            mock_photo_client,
            mock_site_client,
            mock_manifest_comp
        )

    @patch("cli.commands.deploy.build")
    @patch("cli.commands.deploy.DeployOrchestrator")
    @patch("cli.commands.deploy.create_clients_from_config")
    @patch("cli.commands.deploy.ManifestComparator")
    @patch("cli.commands.deploy.Path")
    @patch("cli.commands.deploy.ConfigManager")
    def test_deploy_fails_if_orchestrator_fails(self, mock_config_manager_class, mock_path_class, mock_manifest_comp_class,
                                               mock_client_factory, mock_orchestrator_class, mock_build):
        """Test that deploy fails if orchestrator deployment fails."""
        # Mock config loading
        mock_config_manager = Mock()
        mock_config_manager_class.return_value = mock_config_manager
        mock_config_manager.load_deploy_config.return_value = {"test": "config"}

        # Mock dual client creation
        mock_client_factory.return_value = (Mock(), Mock())

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
    @patch("cli.commands.deploy.create_clients_from_config")
    @patch("cli.commands.deploy.ManifestComparator")
    @patch("cli.commands.deploy.Path")
    @patch("cli.commands.deploy.ConfigManager")
    def test_deploy_handles_exceptions(self, mock_config_manager_class, mock_path_class, mock_manifest_comp_class,
                                     mock_client_factory, mock_orchestrator_class, mock_build):
        """Test that deploy handles exceptions gracefully."""
        # Mock config loading
        mock_config_manager = Mock()
        mock_config_manager_class.return_value = mock_config_manager
        mock_config_manager.load_deploy_config.return_value = {"test": "config"}

        # Mock dual client creation
        mock_client_factory.return_value = (Mock(), Mock())

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
    @patch("cli.commands.deploy.create_clients_from_config")
    @patch("cli.commands.deploy.ManifestComparator")
    @patch("cli.commands.deploy.Path")
    @patch("cli.commands.deploy.ConfigManager")
    def test_deploy_shows_progress_output(self, mock_config_manager_class, mock_path_class, mock_manifest_comp_class,
                                        mock_client_factory, mock_orchestrator_class, mock_build):
        """Test that deploy shows progress information to user."""
        # Mock config loading
        mock_config_manager = Mock()
        mock_config_manager_class.return_value = mock_config_manager
        mock_config_manager.load_deploy_config.return_value = {"test": "config"}

        # Mock dual client creation
        mock_client_factory.return_value = (Mock(), Mock())

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

    @patch("cli.commands.deploy.build")
    @patch("cli.commands.deploy.DeployOrchestrator")
    @patch("cli.commands.deploy.create_clients_from_config")
    @patch("cli.commands.deploy.ManifestComparator")
    @patch("cli.commands.deploy.Path")
    @patch("cli.commands.deploy.ConfigManager")
    def test_deploy_loads_config_and_creates_dual_clients(self, mock_config_manager_class, mock_path_class, mock_manifest_comp_class,
                                                     mock_client_factory, mock_orchestrator_class, mock_build):
        """Test that deploy loads config and creates dual clients."""
        # Mock config loading with specific deploy config
        mock_config_manager = Mock()
        mock_config_manager_class.return_value = mock_config_manager
        deploy_config = {
            "photo_password_env_var": "TEST_PHOTO_PASS",
            "site_password_env_var": "TEST_SITE_PASS",
            "photo_zone_name": "test-photo-zone",
            "site_zone_name": "test-site-zone",
            "region": "uk"
        }
        mock_config_manager.load_deploy_config.return_value = deploy_config

        mock_build.return_value = Mock(exit_code=0)

        # Mock output directory exists
        mock_output_dir = Mock()
        mock_output_dir.exists.return_value = True
        mock_path_class.return_value = mock_output_dir

        # Mock dual client creation
        mock_photo_client = Mock()
        mock_site_client = Mock()
        mock_client_factory.return_value = (mock_photo_client, mock_site_client)
        mock_manifest_comp = Mock()
        mock_manifest_comp_class.return_value = mock_manifest_comp

        # Mock orchestrator success
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.execute_deployment.return_value = True

        runner = CliRunner()
        result = runner.invoke(deploy)

        assert result.exit_code == 0

        # Verify config was loaded
        mock_config_manager.load_deploy_config.assert_called_once()

        # Verify clients were created from config
        mock_client_factory.assert_called_once_with(deploy_config)

        # Verify orchestrator was created with dual clients
        mock_orchestrator_class.assert_called_once_with(
            mock_photo_client,
            mock_site_client,
            mock_manifest_comp
        )

    @patch("cli.commands.deploy.build")
    @patch("cli.commands.deploy.create_clients_from_config")
    @patch("cli.commands.deploy.ConfigManager")
    def test_deploy_fails_if_client_creation_fails(self, mock_config_manager_class, mock_client_factory, mock_build):
        """Test that deploy fails gracefully if client creation fails."""
        # Mock config loading
        mock_config_manager = Mock()
        mock_config_manager_class.return_value = mock_config_manager
        mock_config_manager.load_deploy_config.return_value = {"test": "config"}

        # Mock client creation failure (e.g., missing env vars)
        mock_client_factory.side_effect = ValueError("Missing TEST_PASSWORD environment variable")

        mock_build.return_value = Mock(exit_code=0)

        runner = CliRunner()
        result = runner.invoke(deploy)

        assert result.exit_code != 0
        assert "missing test_password" in result.output.lower()

        # Verify client factory was called
        mock_client_factory.assert_called_once()
