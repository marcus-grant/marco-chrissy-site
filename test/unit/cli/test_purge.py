"""Unit tests for purge CLI command."""

from unittest.mock import Mock, patch

from click.testing import CliRunner

from cli.commands.purge import purge


class TestPurgeCommand:
    """Test purge command functionality."""

    @patch("cli.commands.purge.create_cdn_client_from_config")
    @patch("cli.commands.purge.ConfigManager")
    def test_purge_success(self, mock_config_manager_class, mock_create_cdn_client):
        """Test purge command succeeds when API call succeeds."""
        # Mock config loading
        mock_config_manager = Mock()
        mock_config_manager_class.return_value = mock_config_manager
        mock_config_manager.load_deploy_config.return_value = {
            "cdn_api_key_env_var": "TEST_CDN_API_KEY",
            "site_pullzone_id_env_var": "TEST_PULLZONE_ID",
        }

        # Mock CDN client success
        mock_cdn_client = Mock()
        mock_create_cdn_client.return_value = mock_cdn_client
        mock_cdn_client.purge_pullzone.return_value = True

        runner = CliRunner()
        result = runner.invoke(purge)

        assert result.exit_code == 0
        assert "purged successfully" in result.output.lower()
        mock_cdn_client.purge_pullzone.assert_called_once()

    @patch("cli.commands.purge.create_cdn_client_from_config")
    @patch("cli.commands.purge.ConfigManager")
    def test_purge_api_failure(self, mock_config_manager_class, mock_create_cdn_client):
        """Test purge command fails when API call fails."""
        # Mock config loading
        mock_config_manager = Mock()
        mock_config_manager_class.return_value = mock_config_manager
        mock_config_manager.load_deploy_config.return_value = {
            "cdn_api_key_env_var": "TEST_CDN_API_KEY",
            "site_pullzone_id_env_var": "TEST_PULLZONE_ID",
        }

        # Mock CDN client failure
        mock_cdn_client = Mock()
        mock_create_cdn_client.return_value = mock_cdn_client
        mock_cdn_client.purge_pullzone.return_value = False

        runner = CliRunner()
        result = runner.invoke(purge)

        assert result.exit_code != 0
        assert "failed" in result.output.lower()

    @patch("cli.commands.purge.ConfigManager")
    def test_purge_missing_config(self, mock_config_manager_class):
        """Test purge command handles missing config file."""
        # Mock config loading failure
        mock_config_manager = Mock()
        mock_config_manager_class.return_value = mock_config_manager
        mock_config_manager.load_deploy_config.side_effect = FileNotFoundError(
            "config/deploy.json not found"
        )

        runner = CliRunner()
        result = runner.invoke(purge)

        assert result.exit_code != 0
        assert "not found" in result.output.lower()

    @patch("cli.commands.purge.create_cdn_client_from_config")
    @patch("cli.commands.purge.ConfigManager")
    def test_purge_missing_env_var(
        self, mock_config_manager_class, mock_create_cdn_client
    ):
        """Test purge command handles missing environment variable."""
        # Mock config loading
        mock_config_manager = Mock()
        mock_config_manager_class.return_value = mock_config_manager
        mock_config_manager.load_deploy_config.return_value = {
            "cdn_api_key_env_var": "MISSING_CDN_API_KEY",
            "site_pullzone_id_env_var": "TEST_PULLZONE_ID",
        }

        # Mock client creation failure due to missing env var
        mock_create_cdn_client.side_effect = ValueError(
            "Missing MISSING_CDN_API_KEY environment variable"
        )

        runner = CliRunner()
        result = runner.invoke(purge)

        assert result.exit_code != 0
        assert "configuration error" in result.output.lower()
