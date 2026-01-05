"""E2E tests for site deploy command."""

import os
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from cli.commands.deploy import deploy


class TestSiteDeploy:
    """Test the site deploy command functionality."""

    @pytest.fixture
    def deploy_test_setup(self, temp_filesystem, directory_factory, file_factory, fake_image_factory, full_config_setup):
        """Setup isolated deploy test environment."""
        # Change to temp directory for complete isolation
        original_cwd = os.getcwd()
        os.chdir(temp_filesystem)

        try:
            # Create minimal config setup
            configs = full_config_setup()

            # Create output directory structure matching galleria output
            directory_factory("output/pics/full")
            directory_factory("output/pics/thumb")

            # Create minimal test files
            fake_image_factory("photo1.jpg", "output/pics/full")
            fake_image_factory("photo1.jpg", "output/pics/thumb", size=(300, 200))

            # Create manifest.json in full directory
            manifest_data = {
                "photos": [{"filename": "photo1.jpg", "hash": "abc123"}]
            }
            file_factory("output/pics/full/manifest.json", json_content=manifest_data)

            # Create minimal site content
            file_factory("output/index.html", content="<html><body>Test</body></html>")

            yield configs
        finally:
            os.chdir(original_cwd)

    @pytest.mark.skip(reason="Deploy command functionality not yet implemented")
    @patch("cli.commands.deploy.DeployOrchestrator")
    @patch("cli.commands.deploy.build")
    def test_deploy_uploads_to_bunny_cdn(self, mock_build, mock_orchestrator_class, deploy_test_setup):
        """Test that deploy command uploads to Bunny CDN."""
        # Mock build success
        mock_build.return_value = Mock(exit_code=0)

        # Mock deploy orchestrator success
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.deploy.return_value = True

        # Run with test environment variables (NEVER inspect these values)
        with patch.dict(os.environ, {
            "BUNNYNET_STORAGE_PASSWORD": "test-password",
            "BUNNYNET_PHOTO_ZONE_NAME": "test-photos",
            "BUNNYNET_SITE_ZONE_NAME": "test-site"
        }):
            runner = CliRunner()
            result = runner.invoke(deploy)

        assert result.exit_code == 0
        assert "bunny" in result.output.lower() or "cdn" in result.output.lower()

    @pytest.mark.skip(reason="Deploy command functionality not yet implemented")
    @patch("cli.commands.deploy.DeployOrchestrator")
    @patch("cli.commands.deploy.build")
    def test_deploy_uses_dual_zone_strategy(self, mock_build, mock_orchestrator_class, deploy_test_setup):
        """Test that deploy uses separate zones for photos vs site content."""
        # Mock build success
        mock_build.return_value = Mock(exit_code=0)

        # Mock deploy orchestrator success
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.deploy.return_value = True

        with patch.dict(os.environ, {
            "BUNNYNET_STORAGE_PASSWORD": "test-password",
            "BUNNYNET_PHOTO_ZONE_NAME": "test-photos",
            "BUNNYNET_SITE_ZONE_NAME": "test-site"
        }):
            runner = CliRunner()
            result = runner.invoke(deploy)

        assert result.exit_code == 0
        # Should mention dual zone strategy
        assert "photo" in result.output.lower() or "site" in result.output.lower()

    @pytest.mark.skip(reason="Deploy command functionality not yet implemented")
    @patch("cli.commands.deploy.DeployOrchestrator")
    @patch("cli.commands.deploy.build")
    def test_deploy_calls_build_automatically(self, mock_build, mock_orchestrator_class, deploy_test_setup):
        """Test that deploy automatically calls build if needed."""
        # Mock build success
        mock_build.return_value = Mock(exit_code=0)

        # Mock deploy orchestrator success
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.deploy.return_value = True

        with patch.dict(os.environ, {
            "BUNNYNET_STORAGE_PASSWORD": "test-password",
            "BUNNYNET_PHOTO_ZONE_NAME": "test-photos",
            "BUNNYNET_SITE_ZONE_NAME": "test-site"
        }):
            runner = CliRunner()
            result = runner.invoke(deploy)

        assert result.exit_code == 0
        # Should call build command
        mock_build.assert_called_once()

    @pytest.mark.skip(reason="Deploy command functionality not yet implemented")
    @patch("cli.commands.deploy.DeployOrchestrator")
    @patch("cli.commands.deploy.build")
    def test_deploy_manifest_comparison_incremental_uploads(self, mock_build, mock_orchestrator_class, deploy_test_setup):
        """Test that deploy compares manifests and only uploads changed files."""
        # Mock build success
        mock_build.return_value = Mock(exit_code=0)

        # Mock deploy orchestrator with manifest comparison
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.deploy.return_value = True

        with patch.dict(os.environ, {
            "BUNNYNET_STORAGE_PASSWORD": "test-password",
            "BUNNYNET_PHOTO_ZONE_NAME": "test-photos",
            "BUNNYNET_SITE_ZONE_NAME": "test-site"
        }):
            runner = CliRunner()
            result = runner.invoke(deploy)

        assert result.exit_code == 0
        # Should mention manifest comparison or incremental behavior
        assert "manifest" in result.output.lower() or "incremental" in result.output.lower()

    @pytest.mark.skip(reason="Deploy command functionality not yet implemented")
    @patch("cli.commands.deploy.DeployOrchestrator")
    @patch("cli.commands.deploy.build")
    def test_deploy_complete_pipeline_integration(self, mock_build, mock_orchestrator_class, deploy_test_setup):
        """Test that deploy runs complete pipeline end-to-end."""
        # Mock build success (which cascades to organize and validate)
        mock_build.return_value = Mock(exit_code=0)

        # Mock deploy orchestrator success
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.deploy.return_value = True

        with patch.dict(os.environ, {
            "BUNNYNET_STORAGE_PASSWORD": "test-password",
            "BUNNYNET_PHOTO_ZONE_NAME": "test-photos",
            "BUNNYNET_SITE_ZONE_NAME": "test-site"
        }):
            runner = CliRunner()
            result = runner.invoke(deploy)

        assert result.exit_code == 0
        # Should call build (which handles validate→organize→build cascade)
        mock_build.assert_called_once()
        # Should call deploy orchestrator
        mock_orchestrator.deploy.assert_called_once()

    @pytest.mark.skip(reason="Deploy command functionality not yet implemented")
    @patch("cli.commands.deploy.DeployOrchestrator")
    @patch("cli.commands.deploy.build")
    def test_deploy_fails_gracefully_on_build_failure(self, mock_build, mock_orchestrator_class, deploy_test_setup):
        """Test that deploy fails gracefully if build step fails."""
        # Mock build failure
        mock_build.return_value = Mock(exit_code=1)

        # Deploy orchestrator should not be called if build fails
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator

        with patch.dict(os.environ, {
            "BUNNYNET_STORAGE_PASSWORD": "test-password",
            "BUNNYNET_PHOTO_ZONE_NAME": "test-photos",
            "BUNNYNET_SITE_ZONE_NAME": "test-site"
        }):
            runner = CliRunner()
            result = runner.invoke(deploy)

        assert result.exit_code != 0
        assert "build failed" in result.output.lower()
        mock_orchestrator.deploy.assert_not_called()

    @patch("cli.commands.deploy.create_clients_from_config")
    @patch("cli.commands.deploy.build")
    def test_deploy_instantiates_bunnynet_clients_correctly(self, mock_build, mock_create_clients, deploy_test_setup):
        """Test that deploy command creates dual BunnyNetClients with proper config."""
        # Mock build success
        mock_build.return_value = Mock(exit_code=0)

        # Mock dual client creation - this should succeed
        mock_photo_client = Mock()
        mock_site_client = Mock()
        mock_create_clients.return_value = (mock_photo_client, mock_site_client)

        # Mock config loading, orchestrator and comparator to focus on client instantiation
        with patch("cli.commands.deploy.ManifestComparator") as mock_comparator_class, \
             patch("cli.commands.deploy.DeployOrchestrator") as mock_orchestrator_class, \
             patch("cli.commands.deploy.ConfigManager") as mock_config_manager_class:
            # Mock config loading
            mock_config_manager = Mock()
            mock_config_manager_class.return_value = mock_config_manager
            deploy_config = {
                "photo_password_env_var": "TEST_PHOTO_PASSWORD",
                "site_password_env_var": "TEST_SITE_PASSWORD",
                "photo_zone_name": "test-photo-zone",
                "site_zone_name": "test-site-zone",
                "region": ""
            }
            mock_config_manager.get_deploy_config.return_value = deploy_config

            mock_comparator = Mock()
            mock_comparator_class.return_value = mock_comparator
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator
            mock_orchestrator.execute_deployment.return_value = True

            runner = CliRunner()
            result = runner.invoke(deploy)

        # Should succeed with correct dual client instantiation
        assert result.exit_code == 0
        mock_create_clients.assert_called_once_with(deploy_config)
        mock_orchestrator_class.assert_called_once_with(
            mock_photo_client,
            mock_site_client,
            mock_comparator
        )
        mock_orchestrator.execute_deployment.assert_called_once()

    @pytest.mark.skip(reason="Deploy command functionality not yet implemented")
    @patch("cli.commands.deploy.DeployOrchestrator")
    @patch("cli.commands.deploy.build")
    def test_deploy_handles_missing_env_vars(self, mock_build, mock_orchestrator_class, deploy_test_setup):
        """Test that deploy handles missing environment variables gracefully."""
        # Mock build success
        mock_build.return_value = Mock(exit_code=0)

        # Mock deploy orchestrator failure due to missing env vars
        Mock()
        mock_orchestrator_class.side_effect = ValueError("Missing BUNNYNET_STORAGE_PASSWORD")

        # Run without setting env vars to test error handling
        runner = CliRunner()
        result = runner.invoke(deploy)

        assert result.exit_code != 0
        assert "environment" in result.output.lower() or "missing" in result.output.lower()

