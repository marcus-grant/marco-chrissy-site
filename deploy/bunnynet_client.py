"""Bunny.net storage API client for file uploads and downloads."""

import os
from pathlib import Path

import requests


class BunnyNetClient:
    """Minimal Bunny.net storage API client for deployment operations."""

    def __init__(self, storage_password: str, zone_name: str, region: str = ""):
        """Initialize client with storage credentials.

        Args:
            storage_password: Storage zone password (NEVER inspect this value)
            zone_name: Name of the storage zone this client will operate on
            region: Storage region (empty for Frankfurt, 'uk' for London, 'ny' for NY)
        """
        self.storage_password = storage_password
        self.zone_name = zone_name
        self.region = region
        self.base_url = self._build_base_url()

    def _build_base_url(self) -> str:
        """Build base URL for storage API based on region."""
        if self.region:
            return f"https://{self.region}.storage.bunnycdn.com"
        return "https://storage.bunnycdn.com"

    def upload_file(self, local_path: Path, remote_path: str) -> bool:
        """Upload a file to bunny.net storage zone.

        Args:
            local_path: Path to local file to upload
            remote_path: Remote path within the storage zone

        Returns:
            True if upload successful, False otherwise
        """
        url = f"{self.base_url}/{self.zone_name}/{remote_path}"
        headers = {
            "AccessKey": self.storage_password,
            "Content-Type": "application/octet-stream"
        }

        try:
            with open(local_path, "rb") as file:
                file_data = file.read()

            response = requests.put(url, data=file_data, headers=headers)
            return response.status_code == 201

        except Exception:
            return False

    def download_file(self, remote_path: str) -> bytes | None:
        """Download a file from bunny.net storage zone.

        Args:
            remote_path: Remote path within the storage zone

        Returns:
            File contents as bytes, or None if not found/error
        """
        url = f"{self.base_url}/{self.zone_name}/{remote_path}"
        headers = {"AccessKey": self.storage_password}

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.content
            return None

        except Exception:
            return None

    def list_directory(self, remote_path: str, zone_name: str) -> list[str] | None:
        """List files in a storage zone directory.

        Args:
            remote_path: Remote directory path within the storage zone
            zone_name: Name of the storage zone

        Returns:
            List of filenames, or None if error
        """
        # Stub implementation - will be implemented in TDD cycle
        raise NotImplementedError("Directory listing not implemented yet")


def create_clients_from_config(config: dict) -> tuple[BunnyNetClient, BunnyNetClient]:
    """Create dual clients from deploy configuration.

    Args:
        config: Deploy configuration dict with env var names and zone settings

    Returns:
        Tuple of (photo_client, site_client) configured for their zones

    Raises:
        ValueError: If required environment variables are missing
    """
    # Read environment variable names from config
    photo_password_env_var = config["photo_password_env_var"]
    site_password_env_var = config["site_password_env_var"]
    region = config.get("region", "")

    # Get actual passwords from environment using config-specified names
    photo_password = os.getenv(photo_password_env_var)
    if not photo_password:
        raise ValueError(f"Missing {photo_password_env_var} environment variable")

    site_password = os.getenv(site_password_env_var)
    if not site_password:
        raise ValueError(f"Missing {site_password_env_var} environment variable")

    # Create separate clients for each zone with zone names
    photo_zone_name = config["photo_zone_name"]
    site_zone_name = config["site_zone_name"]

    photo_client = BunnyNetClient(photo_password, photo_zone_name, region)
    site_client = BunnyNetClient(site_password, site_zone_name, region)

    return photo_client, site_client
