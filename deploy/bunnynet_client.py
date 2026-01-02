"""Bunny.net storage API client for file uploads and downloads."""

import os
from pathlib import Path

import requests


class BunnyNetClient:
    """Minimal Bunny.net storage API client for deployment operations."""

    def __init__(self, storage_password: str, region: str = ""):
        """Initialize client with storage credentials.

        Args:
            storage_password: Storage zone password (NEVER inspect this value)
            region: Storage region (empty for Frankfurt, 'uk' for London, 'ny' for NY)
        """
        self.storage_password = storage_password
        self.region = region
        self.base_url = self._build_base_url()

    def _build_base_url(self) -> str:
        """Build base URL for storage API based on region."""
        if self.region:
            return f"https://{self.region}.storage.bunnycdn.com"
        return "https://storage.bunnycdn.com"

    def upload_file(self, local_path: Path, remote_path: str, zone_name: str) -> bool:
        """Upload a file to bunny.net storage zone.

        Args:
            local_path: Path to local file to upload
            remote_path: Remote path within the storage zone
            zone_name: Name of the storage zone

        Returns:
            True if upload successful, False otherwise
        """
        url = f"{self.base_url}/{zone_name}/{remote_path}"
        headers = {"AccessKey": self.storage_password}

        try:
            with open(local_path, "rb") as file:
                file_data = file.read()

            response = requests.put(url, data=file_data, headers=headers)
            return response.status_code == 201

        except Exception:
            return False

    def download_file(self, remote_path: str, zone_name: str) -> bytes | None:
        """Download a file from bunny.net storage zone.

        Args:
            remote_path: Remote path within the storage zone
            zone_name: Name of the storage zone

        Returns:
            File contents as bytes, or None if not found/error
        """
        url = f"{self.base_url}/{zone_name}/{remote_path}"
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


def create_client_from_env() -> BunnyNetClient:
    """Create client from environment variables.

    Returns:
        Configured BunnyNetClient

    Raises:
        ValueError: If required environment variables are missing
    """
    storage_password = os.getenv("BUNNYNET_STORAGE_PASSWORD")
    if not storage_password:
        raise ValueError("Missing BUNNYNET_STORAGE_PASSWORD environment variable")

    region = os.getenv("BUNNYNET_REGION", "")

    return BunnyNetClient(storage_password, region)
