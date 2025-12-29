"""Unit tests for BunnyNet API client."""

import os
from unittest.mock import patch

import pytest

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

    def test_upload_file_not_implemented(self):
        """Test upload_file raises NotImplementedError (stub implementation)."""
        client = BunnyNetClient("test-password", "")

        with pytest.raises(NotImplementedError, match="Upload functionality not implemented"):
            client.upload_file("local.jpg", "remote.jpg", "test-zone")

    def test_download_file_not_implemented(self):
        """Test download_file raises NotImplementedError (stub implementation)."""
        client = BunnyNetClient("test-password", "")

        with pytest.raises(NotImplementedError, match="Download functionality not implemented"):
            client.download_file("remote.jpg", "test-zone")

    def test_list_directory_not_implemented(self):
        """Test list_directory raises NotImplementedError (stub implementation)."""
        client = BunnyNetClient("test-password", "")

        with pytest.raises(NotImplementedError, match="Directory listing not implemented"):
            client.list_directory("remote/path", "test-zone")
