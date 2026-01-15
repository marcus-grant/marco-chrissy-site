"""Unit tests for BunnyCdn API client."""

import os
from unittest.mock import Mock, patch

import pytest
import requests

from deploy.bunny_cdn_client import BunnyCdnClient, create_cdn_client_from_config


class TestBunnyCdnClient:
    """Test BunnyCdn API client functionality."""

    def test_client_initialization(self):
        """Test client initializes with correct base URL."""
        client = BunnyCdnClient("test-api-key", "123456")

        assert client.base_url == "https://api.bunny.net"
        assert client.pullzone_id == "123456"

    @patch("requests.post")
    def test_purge_pullzone_success_204(self, mock_post):
        """Test purge_pullzone returns True on 204 No Content."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response

        client = BunnyCdnClient("test-api-key", "123456")
        result = client.purge_pullzone()

        assert result is True
        mock_post.assert_called_once_with(
            "https://api.bunny.net/pullzone/123456/purgeCache",
            headers={
                "AccessKey": "test-api-key",
                "Content-Type": "application/json",
            },
        )

    @patch("requests.post")
    def test_purge_pullzone_success_200(self, mock_post):
        """Test purge_pullzone returns True on 200 OK."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        client = BunnyCdnClient("test-api-key", "123456")
        result = client.purge_pullzone()

        assert result is True

    @patch("requests.post")
    def test_purge_pullzone_failure_401(self, mock_post):
        """Test purge_pullzone returns False on 401 Unauthorized."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        client = BunnyCdnClient("invalid-api-key", "123456")
        result = client.purge_pullzone()

        assert result is False

    @patch("requests.post")
    def test_purge_pullzone_failure_404(self, mock_post):
        """Test purge_pullzone returns False on 404 Not Found."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_post.return_value = mock_response

        client = BunnyCdnClient("test-api-key", "invalid-zone")
        result = client.purge_pullzone()

        assert result is False

    @patch("requests.post")
    def test_purge_pullzone_network_error(self, mock_post):
        """Test purge_pullzone returns False on network error."""
        mock_post.side_effect = requests.ConnectionError("Network error")

        client = BunnyCdnClient("test-api-key", "123456")
        result = client.purge_pullzone()

        assert result is False


class TestCreateCdnClientFromConfig:
    """Test CDN client factory function."""

    def test_create_cdn_client_from_config_success(self):
        """Test creating CDN client from config with env vars set."""
        deploy_config = {
            "cdn_api_key_env_var": "TEST_CDN_API_KEY",
            "site_pullzone_id_env_var": "TEST_PULLZONE_ID",
        }

        with patch.dict(
            os.environ,
            {
                "TEST_CDN_API_KEY": "test-api-key-value",
                "TEST_PULLZONE_ID": "123456",
            },
        ):
            client = create_cdn_client_from_config(deploy_config)

            assert isinstance(client, BunnyCdnClient)
            assert client.pullzone_id == "123456"

    def test_create_cdn_client_from_config_missing_api_key_fails(self):
        """Test that missing API key env var raises ValueError."""
        deploy_config = {
            "cdn_api_key_env_var": "MISSING_CDN_API_KEY",
            "site_pullzone_id_env_var": "TEST_PULLZONE_ID",
        }

        with patch.dict(
            os.environ,
            {"TEST_PULLZONE_ID": "123456"},
            clear=True,
        ):
            with pytest.raises(ValueError, match="Missing.*MISSING_CDN_API_KEY"):
                create_cdn_client_from_config(deploy_config)

    def test_create_cdn_client_from_config_missing_pullzone_id_fails(self):
        """Test that missing pullzone ID env var raises ValueError."""
        deploy_config = {
            "cdn_api_key_env_var": "TEST_CDN_API_KEY",
            "site_pullzone_id_env_var": "MISSING_PULLZONE_ID",
        }

        with patch.dict(
            os.environ,
            {"TEST_CDN_API_KEY": "test-api-key-value"},
            clear=True,
        ):
            with pytest.raises(ValueError, match="Missing.*MISSING_PULLZONE_ID"):
                create_cdn_client_from_config(deploy_config)
