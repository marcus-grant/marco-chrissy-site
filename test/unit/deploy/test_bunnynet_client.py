"""Unit tests for BunnyNet API client."""

import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests

from deploy.bunnynet_client import BunnyNetClient, create_client_from_env


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

    def test_create_client_from_env_success(self):
        """Test creating client from environment variables succeeds."""
        # NEVER inspect these env var values - just test they work
        with patch.dict(os.environ, {
            "BUNNYNET_STORAGE_PASSWORD": "test-password",
            "BUNNYNET_REGION": "uk"
        }):
            client = create_client_from_env()

            assert isinstance(client, BunnyNetClient)
            assert client.region == "uk"
            assert client.base_url == "https://uk.storage.bunnycdn.com"

    def test_create_client_from_env_default_region(self):
        """Test creating client with default region when BUNNYNET_REGION not set."""
        with patch.dict(os.environ, {
            "BUNNYNET_STORAGE_PASSWORD": "test-password"
        }, clear=True):
            client = create_client_from_env()

            assert isinstance(client, BunnyNetClient)
            assert client.region == ""
            assert client.base_url == "https://storage.bunnycdn.com"

    def test_create_client_from_env_missing_password_fails(self):
        """Test creating client fails when BUNNYNET_STORAGE_PASSWORD missing."""
        # Clear all BUNNYNET env vars to test missing password
        env_vars_to_clear = {k: v for k, v in os.environ.items()
                           if not k.startswith("BUNNYNET")}

        with patch.dict(os.environ, env_vars_to_clear, clear=True):
            with pytest.raises(ValueError, match="Missing BUNNYNET_STORAGE_PASSWORD"):
                create_client_from_env()

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
            headers={"AccessKey": "test-password"}
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
            headers={"AccessKey": "test-password"}
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
