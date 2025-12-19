"""Shared asset manager for downloading and managing external dependencies.

NOTE: Current implementation downloads latest versions without pinning.
This is acceptable for MVP but should be enhanced post-MVP for reproducible builds.
See TODO.md Medium-term Features for version pinning implementation.
"""

from pathlib import Path
from typing import Literal

import requests

from defaults import get_shared_css_paths

AssetType = Literal["css", "js"]
AssetName = Literal["pico"]


class AssetManager:
    """Manages external asset downloads and URL generation."""

    # Asset URLs - currently using latest versions (no version pinning for MVP)
    ASSET_URLS: dict[AssetName, dict[AssetType, str]] = {
        "pico": {
            "css": "https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css",
            "js": "https://cdn.jsdelivr.net/npm/@picocss/pico@2/js/pico.min.js",
        }
    }

    def __init__(self, output_dir: Path):
        """Initialize asset manager with output directory.

        Args:
            output_dir: Base output directory where assets will be stored
        """
        self.output_dir = Path(output_dir)
        self.css_dir = self.output_dir / "css"
        self.js_dir = self.output_dir / "js"

    def ensure_asset(self, asset_name: AssetName, file_type: AssetType) -> Path:
        """Ensure asset is available locally, downloading if necessary.

        Args:
            asset_name: Name of the asset (e.g., "pico")
            file_type: Type of file (css, js)

        Returns:
            Path to the local asset file

        Raises:
            ValueError: If asset name or file type is unknown
            Exception: If download fails
        """
        if asset_name not in self.ASSET_URLS:
            raise ValueError(f"Unknown asset: {asset_name}")

        if file_type not in self.ASSET_URLS[asset_name]:
            raise ValueError(f"Unknown file type: {file_type}")

        # Determine target path
        target_dir = self.css_dir if file_type == "css" else self.js_dir
        filename = f"{asset_name}.min.{file_type}"
        target_path = target_dir / filename

        # Skip download if file already exists
        if target_path.exists():
            return target_path

        # Create directories if needed
        target_dir.mkdir(parents=True, exist_ok=True)

        # Download asset
        url = self.ASSET_URLS[asset_name][file_type]
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Write to file
            target_path.write_text(response.text)

            return target_path

        except Exception as e:
            raise Exception(f"Failed to download asset {asset_name} from {url}: {e}") from e

    def get_asset_url(self, asset_name: AssetName, file_type: AssetType) -> str:
        """Get the relative URL path for an asset.

        Args:
            asset_name: Name of the asset (e.g., "pico")
            file_type: Type of file (css, js)

        Returns:
            Relative URL path (e.g., "/css/pico.min.css")
        """
        if asset_name not in self.ASSET_URLS:
            raise ValueError(f"Unknown asset: {asset_name}")

        if file_type not in self.ASSET_URLS[asset_name]:
            raise ValueError(f"Unknown file type: {file_type}")

        filename = f"{asset_name}.min.{file_type}"
        return f"/{file_type}/{filename}"

    def get_shared_css_files(self) -> list[Path]:
        """Get list of all shared CSS files from default paths.

        Returns:
            List of Path objects for shared CSS files
        """
        css_files = []

        for css_dir in get_shared_css_paths():
            if css_dir.exists() and css_dir.is_dir():
                # Find all CSS files in the directory
                css_files.extend(css_dir.glob("*.css"))

        return css_files

    def copy_shared_css_files(self) -> list[Path]:
        """Copy shared CSS files to output directory.

        Returns:
            List of Path objects for copied CSS files in output directory
        """
        copied_files = []
        self.css_dir.mkdir(parents=True, exist_ok=True)

        for css_file in self.get_shared_css_files():
            target_path = self.css_dir / css_file.name
            target_path.write_text(css_file.read_text())
            copied_files.append(target_path)

        return copied_files
