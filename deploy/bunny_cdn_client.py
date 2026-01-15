"""Bunny.net CDN API client for cache operations."""

import os

import requests


class BunnyCdnClient:
    """Bunny.net CDN API client for cache purging operations."""

    def __init__(self, api_key: str, pullzone_id: str):
        """Initialize client with CDN API credentials.

        Args:
            api_key: Account API key (NEVER inspect this value)
            pullzone_id: Pullzone ID for cache operations
        """
        self.api_key = api_key
        self.pullzone_id = pullzone_id
        self.base_url = "https://api.bunny.net"

    def purge_pullzone(self) -> bool:
        """Purge entire pullzone cache.

        Returns:
            True if purge successful, False otherwise
        """
        url = f"{self.base_url}/pullzone/{self.pullzone_id}/purgeCache"
        headers = {
            "AccessKey": self.api_key,
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(url, headers=headers)
            # Bunny.net returns 204 No Content on successful purge
            return response.status_code in (200, 204)

        except Exception:
            return False


def create_cdn_client_from_config(config: dict) -> BunnyCdnClient:
    """Create CDN client from deploy configuration.

    Args:
        config: Deploy configuration dict with env var names

    Returns:
        BunnyCdnClient configured for cache operations

    Raises:
        ValueError: If required environment variables are missing
    """
    # Read environment variable names from config
    api_key_env_var = config["cdn_api_key_env_var"]
    pullzone_id_env_var = config["site_pullzone_id_env_var"]

    # Get actual values from environment using config-specified names
    api_key = os.getenv(api_key_env_var)
    if not api_key:
        raise ValueError(f"Missing {api_key_env_var} environment variable")

    pullzone_id = os.getenv(pullzone_id_env_var)
    if not pullzone_id:
        raise ValueError(f"Missing {pullzone_id_env_var} environment variable")

    return BunnyCdnClient(api_key, pullzone_id)
