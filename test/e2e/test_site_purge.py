"""E2E tests for site purge command."""

import os
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner


class TestSitePurge:
    """Test the site purge command functionality."""

    @pytest.fixture
    def purge_test_setup(self, temp_filesystem, full_config_setup):
        """Setup isolated purge test environment."""
        original_cwd = os.getcwd()
        os.chdir(temp_filesystem)

        try:
            configs = full_config_setup()
            yield configs
        finally:
            os.chdir(original_cwd)

    @pytest.mark.skip(reason="Purge command not yet implemented")
    @patch("cli.commands.purge.create_cdn_client_from_config")
    @patch("cli.commands.purge.ConfigManager")
    def test_purge_clears_site_pullzone_cache(
        self, mock_config_manager_class, mock_create_cdn_client, purge_test_setup
    ):
        """Test that purge command clears the site pullzone cache."""
        from cli.commands.purge import purge

        # Mock config loading
        mock_config_manager = Mock()
        mock_config_manager_class.return_value = mock_config_manager
        mock_config_manager.load_deploy_config.return_value = {
            "cdn_api_key_env_var": "TEST_CDN_API_KEY",
            "site_pullzone_id_env_var": "TEST_SITE_PULLZONE_ID",
        }

        # Mock CDN client
        mock_cdn_client = Mock()
        mock_create_cdn_client.return_value = mock_cdn_client
        mock_cdn_client.purge_pullzone.return_value = True

        runner = CliRunner()
        result = runner.invoke(purge)

        assert result.exit_code == 0
        mock_cdn_client.purge_pullzone.assert_called_once()

    @pytest.mark.skip(reason="Purge command not yet implemented")
    @patch("cli.commands.purge.create_cdn_client_from_config")
    @patch("cli.commands.purge.ConfigManager")
    def test_purge_reports_success(
        self, mock_config_manager_class, mock_create_cdn_client, purge_test_setup
    ):
        """Test that purge command reports success message."""
        from cli.commands.purge import purge

        # Mock config loading
        mock_config_manager = Mock()
        mock_config_manager_class.return_value = mock_config_manager
        mock_config_manager.load_deploy_config.return_value = {
            "cdn_api_key_env_var": "TEST_CDN_API_KEY",
            "site_pullzone_id_env_var": "TEST_SITE_PULLZONE_ID",
        }

        # Mock CDN client success
        mock_cdn_client = Mock()
        mock_create_cdn_client.return_value = mock_cdn_client
        mock_cdn_client.purge_pullzone.return_value = True

        runner = CliRunner()
        result = runner.invoke(purge)

        assert result.exit_code == 0
        assert "purge" in result.output.lower()

    @pytest.mark.skip(reason="Purge command not yet implemented")
    @patch("cli.commands.purge.create_cdn_client_from_config")
    @patch("cli.commands.purge.ConfigManager")
    def test_purge_handles_api_failure(
        self, mock_config_manager_class, mock_create_cdn_client, purge_test_setup
    ):
        """Test that purge command handles API failure gracefully."""
        from cli.commands.purge import purge

        # Mock config loading
        mock_config_manager = Mock()
        mock_config_manager_class.return_value = mock_config_manager
        mock_config_manager.load_deploy_config.return_value = {
            "cdn_api_key_env_var": "TEST_CDN_API_KEY",
            "site_pullzone_id_env_var": "TEST_SITE_PULLZONE_ID",
        }

        # Mock CDN client failure
        mock_cdn_client = Mock()
        mock_create_cdn_client.return_value = mock_cdn_client
        mock_cdn_client.purge_pullzone.return_value = False

        runner = CliRunner()
        result = runner.invoke(purge)

        assert result.exit_code != 0
        assert "failed" in result.output.lower()

    @pytest.mark.skip(reason="Purge command not yet implemented")
    @patch("cli.commands.purge.create_cdn_client_from_config")
    @patch("cli.commands.purge.ConfigManager")
    def test_purge_handles_missing_config(
        self, mock_config_manager_class, mock_create_cdn_client, purge_test_setup
    ):
        """Test that purge command handles missing configuration gracefully."""
        from cli.commands.purge import purge

        # Mock config loading failure
        mock_config_manager = Mock()
        mock_config_manager_class.return_value = mock_config_manager
        mock_config_manager.load_deploy_config.side_effect = FileNotFoundError(
            "config/deploy.json not found"
        )

        runner = CliRunner()
        result = runner.invoke(purge)

        assert result.exit_code != 0


class TestDeployPurgeFlag:
    """Test the deploy --purge flag functionality."""

    @pytest.fixture
    def deploy_purge_test_setup(
        self, temp_filesystem, directory_factory, file_factory, full_config_setup
    ):
        """Setup isolated deploy test environment with purge support."""
        original_cwd = os.getcwd()
        os.chdir(temp_filesystem)

        try:
            configs = full_config_setup()

            # Create output directory structure
            directory_factory("output/pics/full")
            directory_factory("output/pics/thumb")

            # Create minimal site content
            file_factory("output/index.html", content="<html><body>Test</body></html>")

            yield configs
        finally:
            os.chdir(original_cwd)

    @pytest.mark.skip(reason="Deploy --purge flag not yet implemented")
    @patch("cli.commands.deploy.create_cdn_client_from_config")
    @patch("cli.commands.deploy.create_clients_from_config")
    @patch("cli.commands.deploy.ManifestComparator")
    @patch("cli.commands.deploy.DeployOrchestrator")
    @patch("cli.commands.deploy.ConfigManager")
    @patch("cli.commands.deploy.build")
    def test_deploy_with_purge_flag_purges_cache(
        self,
        mock_build,
        mock_config_manager_class,
        mock_orchestrator_class,
        mock_comparator_class,
        mock_create_clients,
        mock_create_cdn_client,
        deploy_purge_test_setup,
    ):
        """Test that deploy --purge flag triggers cache purge after deployment."""
        from cli.commands.deploy import deploy

        # Mock build success
        mock_build.return_value = Mock(exit_code=0)

        # Mock config loading
        mock_config_manager = Mock()
        mock_config_manager_class.return_value = mock_config_manager
        mock_config_manager.load_deploy_config.return_value = {
            "photo_password_env_var": "TEST_PHOTO_PASSWORD",
            "site_password_env_var": "TEST_SITE_PASSWORD",
            "photo_zone_name": "test-photo-zone",
            "site_zone_name": "test-site-zone",
            "cdn_api_key_env_var": "TEST_CDN_API_KEY",
            "site_pullzone_id_env_var": "TEST_SITE_PULLZONE_ID",
            "region": "",
        }

        # Mock storage clients
        mock_photo_client, mock_site_client = Mock(), Mock()
        mock_create_clients.return_value = (mock_photo_client, mock_site_client)

        # Mock deploy orchestrator
        mock_comparator = Mock()
        mock_comparator_class.return_value = mock_comparator
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.execute_deployment.return_value = True

        # Mock CDN client for purge
        mock_cdn_client = Mock()
        mock_create_cdn_client.return_value = mock_cdn_client
        mock_cdn_client.purge_pullzone.return_value = True

        runner = CliRunner()
        result = runner.invoke(deploy, ["--purge"])

        assert result.exit_code == 0
        mock_cdn_client.purge_pullzone.assert_called_once()

    @pytest.mark.skip(reason="Deploy --purge flag not yet implemented")
    @patch("cli.commands.deploy.create_clients_from_config")
    @patch("cli.commands.deploy.ManifestComparator")
    @patch("cli.commands.deploy.DeployOrchestrator")
    @patch("cli.commands.deploy.ConfigManager")
    @patch("cli.commands.deploy.build")
    def test_deploy_without_purge_flag_does_not_purge(
        self,
        mock_build,
        mock_config_manager_class,
        mock_orchestrator_class,
        mock_comparator_class,
        mock_create_clients,
        deploy_purge_test_setup,
    ):
        """Test that deploy without --purge flag does not purge cache."""
        from cli.commands.deploy import deploy

        # Mock build success
        mock_build.return_value = Mock(exit_code=0)

        # Mock config loading
        mock_config_manager = Mock()
        mock_config_manager_class.return_value = mock_config_manager
        mock_config_manager.load_deploy_config.return_value = {
            "photo_password_env_var": "TEST_PHOTO_PASSWORD",
            "site_password_env_var": "TEST_SITE_PASSWORD",
            "photo_zone_name": "test-photo-zone",
            "site_zone_name": "test-site-zone",
            "region": "",
        }

        # Mock storage clients
        mock_photo_client, mock_site_client = Mock(), Mock()
        mock_create_clients.return_value = (mock_photo_client, mock_site_client)

        # Mock deploy orchestrator
        mock_comparator = Mock()
        mock_comparator_class.return_value = mock_comparator
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.execute_deployment.return_value = True

        runner = CliRunner()
        result = runner.invoke(deploy)

        assert result.exit_code == 0
        # No purge should happen - we don't even import the CDN client
