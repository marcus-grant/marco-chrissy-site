"""Unit tests for BunnyNet API client."""

import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests

from deploy.bunnynet_client import BunnyNetClient, create_clients_from_config


class TestBunnyNetClient:
    """Test BunnyNet API client functionality."""

    def test_client_initialization_frankfurt_region(self):
        """Test client initializes with Frankfurt region (default)."""
        # NEVER inspect env var values during testing
        client = BunnyNetClient("test-password", "")

        assert client.base_url == "https://storage.bunnycdn.com"
        assert client.region == ""

    def test_client_initialization_london_region(self):
        """Test client initializes with London region."""
        client = BunnyNetClient("test-password", "uk")

        assert client.base_url == "https://uk.storage.bunnycdn.com"
        assert client.region == "uk"

    def test_client_initialization_new_york_region(self):
        """Test client initializes with New York region."""
        client = BunnyNetClient("test-password", "ny")

        assert client.base_url == "https://ny.storage.bunnycdn.com"
        assert client.region == "ny"

    def test_create_clients_from_config_with_region(self):
        """Test creating dual clients from config with specified region."""
        # Use arbitrary test env var names - NEVER production names
        deploy_config = {
            "photo_password_env_var": "TEST_PHOTO_PASSWORD",
            "site_password_env_var": "TEST_SITE_PASSWORD",
            "region": "uk"
        }

        # Mock environment variables with test values
        with patch.dict(os.environ, {
            "TEST_PHOTO_PASSWORD": "test-photo-pass",
            "TEST_SITE_PASSWORD": "test-site-pass"
        }):
            photo_client, site_client = create_clients_from_config(deploy_config)

            # Verify both clients are properly configured with UK region
            assert isinstance(photo_client, BunnyNetClient)
            assert isinstance(site_client, BunnyNetClient)
            assert photo_client.region == "uk"
            assert site_client.region == "uk"
            assert photo_client.base_url == "https://uk.storage.bunnycdn.com"
            assert site_client.base_url == "https://uk.storage.bunnycdn.com"

    def test_create_clients_from_config_default_region(self):
        """Test creating dual clients with default region when not specified."""
        deploy_config = {
            "photo_password_env_var": "TEST_PHOTO_PASSWORD",
            "site_password_env_var": "TEST_SITE_PASSWORD"
            # region not specified - should default to ""
        }

        with patch.dict(os.environ, {
            "TEST_PHOTO_PASSWORD": "test-photo-pass",
            "TEST_SITE_PASSWORD": "test-site-pass"
        }, clear=True):
            photo_client, site_client = create_clients_from_config(deploy_config)

            assert isinstance(photo_client, BunnyNetClient)
            assert isinstance(site_client, BunnyNetClient)
            assert photo_client.region == ""
            assert site_client.region == ""
            assert photo_client.base_url == "https://storage.bunnycdn.com"
            assert site_client.base_url == "https://storage.bunnycdn.com"

    def test_list_directory_not_implemented(self):
        """Test list_directory raises NotImplementedError (stub implementation)."""
        client = BunnyNetClient("test-password", "")

        with pytest.raises(NotImplementedError, match="Directory listing not implemented"):
            client.list_directory("remote/path", "test-zone")

    @patch("requests.put")
    def test_upload_file_success(self, mock_put):
        """Test file upload sends correct request and returns True on success."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 201
        mock_put.return_value = mock_response

        client = BunnyNetClient("test-password", "uk")
        local_path = Path("/tmp/test.jpg")

        # Mock file content
        with patch("builtins.open", create=True) as mock_open:
            mock_file = Mock()
            mock_file.read.return_value = b"test-content"
            mock_open.return_value.__enter__.return_value = mock_file

            # Execute
            result = client.upload_file(local_path, "photos/test.jpg", "my-zone")

        # Verify
        assert result is True
        mock_put.assert_called_once_with(
            "https://uk.storage.bunnycdn.com/my-zone/photos/test.jpg",
            data=b"test-content",
            headers={
                "AccessKey": "test-password",
                "Content-Type": "application/octet-stream"
            }
        )

    @patch("requests.put")
    def test_upload_file_failure(self, mock_put):
        """Test file upload returns False on HTTP error."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 400
        mock_put.return_value = mock_response

        client = BunnyNetClient("test-password", "")
        local_path = Path("/tmp/test.jpg")

        # Mock file content
        with patch("builtins.open", create=True) as mock_open:
            mock_file = Mock()
            mock_file.read.return_value = b"test-content"
            mock_open.return_value.__enter__.return_value = mock_file

            # Execute
            result = client.upload_file(local_path, "photos/test.jpg", "my-zone")

        # Verify
        assert result is False
        mock_put.assert_called_once_with(
            "https://storage.bunnycdn.com/my-zone/photos/test.jpg",
            data=b"test-content",
            headers={
                "AccessKey": "test-password",
                "Content-Type": "application/octet-stream"
            }
        )

    @patch("requests.get")
    def test_download_file_success(self, mock_get):
        """Test file download returns content on success."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"manifest-content"
        mock_get.return_value = mock_response

        client = BunnyNetClient("test-password", "ny")

        # Execute
        result = client.download_file("manifest.json", "my-zone")

        # Verify
        assert result == b"manifest-content"
        mock_get.assert_called_once_with(
            "https://ny.storage.bunnycdn.com/my-zone/manifest.json",
            headers={"AccessKey": "test-password"}
        )

    @patch("requests.get")
    def test_download_file_not_found(self, mock_get):
        """Test file download returns None on 404."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        client = BunnyNetClient("test-password", "")

        # Execute
        result = client.download_file("missing.json", "my-zone")

        # Verify
        assert result is None
        mock_get.assert_called_once_with(
            "https://storage.bunnycdn.com/my-zone/missing.json",
            headers={"AccessKey": "test-password"}
        )

    @patch("requests.put")
    def test_upload_file_network_error(self, mock_put):
        """Test file upload returns False on network/connection error."""
        # Setup - raise requests exception
        mock_put.side_effect = requests.ConnectionError("Network error")

        client = BunnyNetClient("test-password", "")
        local_path = Path("/tmp/test.jpg")

        # Mock file content
        with patch("builtins.open", create=True) as mock_open:
            mock_file = Mock()
            mock_file.read.return_value = b"test-content"
            mock_open.return_value.__enter__.return_value = mock_file

            # Execute
            result = client.upload_file(local_path, "photos/test.jpg", "my-zone")

        # Verify
        assert result is False

    @patch("requests.get")
    def test_download_file_network_error(self, mock_get):
        """Test file download returns None on network/connection error."""
        # Setup - raise requests exception
        mock_get.side_effect = requests.ConnectionError("Network error")

        client = BunnyNetClient("test-password", "")

        # Execute
        result = client.download_file("manifest.json", "my-zone")

        # Verify
        assert result is None

    def test_create_clients_from_config_returns_dual_clients(self):
        """Test creating dual clients from config with arbitrary env var names."""
        # Use arbitrary test env var names - NEVER production names
        deploy_config = {
            "photo_password_env_var": "TEST_PHOTO_PASSWORD",
            "site_password_env_var": "TEST_SITE_PASSWORD",
            "photo_zone_name": "test-photo-zone",
            "site_zone_name": "test-site-zone",
            "region": "uk"
        }

        # Mock environment variables with test values
        with patch.dict(os.environ, {
            "TEST_PHOTO_PASSWORD": "test-photo-pass",
            "TEST_SITE_PASSWORD": "test-site-pass"
        }):
            from deploy.bunnynet_client import create_clients_from_config

            photo_client, site_client = create_clients_from_config(deploy_config)

            # Verify both clients are BunnyNetClient instances
            assert isinstance(photo_client, BunnyNetClient)
            assert isinstance(site_client, BunnyNetClient)

            # Verify both clients use the same region from config
            assert photo_client.region == "uk"
            assert site_client.region == "uk"
            assert photo_client.base_url == "https://uk.storage.bunnycdn.com"
            assert site_client.base_url == "https://uk.storage.bunnycdn.com"

    def test_create_clients_from_config_missing_photo_password_fails(self):
        """Test that missing photo password env var raises ValueError."""
        deploy_config = {
            "photo_password_env_var": "MISSING_PHOTO_PASSWORD",
            "site_password_env_var": "TEST_SITE_PASSWORD",
            "photo_zone_name": "test-photo-zone",
            "site_zone_name": "test-site-zone",
            "region": ""
        }

        # Only set site password, not photo password
        with patch.dict(os.environ, {
            "TEST_SITE_PASSWORD": "test-site-pass"
        }, clear=True):
            from deploy.bunnynet_client import create_clients_from_config

            with pytest.raises(ValueError, match="Missing.*MISSING_PHOTO_PASSWORD"):
                create_clients_from_config(deploy_config)

    def test_create_clients_from_config_missing_site_password_fails(self):
        """Test that missing site password env var raises ValueError."""
        deploy_config = {
            "photo_password_env_var": "TEST_PHOTO_PASSWORD",
            "site_password_env_var": "MISSING_SITE_PASSWORD",
            "photo_zone_name": "test-photo-zone",
            "site_zone_name": "test-site-zone",
            "region": ""
        }

        # Only set photo password, not site password
        with patch.dict(os.environ, {
            "TEST_PHOTO_PASSWORD": "test-photo-pass"
        }, clear=True):
            from deploy.bunnynet_client import create_clients_from_config

            with pytest.raises(ValueError, match="Missing.*MISSING_SITE_PASSWORD"):
                create_clients_from_config(deploy_config)
