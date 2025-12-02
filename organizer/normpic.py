"""NormPic integration functionality."""

import json
from dataclasses import dataclass
from pathlib import Path

from serializer.exceptions import ConfigLoadError, ConfigValidationError
from serializer.json import JsonConfigLoader

try:
    from normpic import Config, Manifest, Pic, organize_photos

    NORMPIC_AVAILABLE = True
except ImportError as e:
    organize_photos = None
    Manifest = None
    Pic = None
    Config = None
    NORMPIC_AVAILABLE = False
    IMPORT_ERROR = str(e)


@dataclass
class OrganizeResult:
    """Result of photo organization operation."""

    success: bool
    errors: list[str]
    manifest_path: str | None = None
    pics_processed: int = 0


class NormPicOrganizer:
    """Organizes photos using NormPic tool."""

    def __init__(
        self,
        config_dir: Path = None,
        source_dir: Path = None,
        dest_dir: Path = None,
        collection_name: str = None,
        create_symlinks: bool = None,
    ):
        """Initialize NormPic organizer.

        Args:
            config_dir: Path to config directory (defaults to ./config)
            source_dir: Override source directory from config
            dest_dir: Override destination directory from config
            collection_name: Override collection name from config
            create_symlinks: Override symlink setting from config
        """
        if not NORMPIC_AVAILABLE:
            raise ImportError(f"Failed to import NormPic: {IMPORT_ERROR}")

        self.config_dir = config_dir or Path("config")

        # Load config from file
        config = self._load_config()

        # Use provided values or fall back to config, then defaults
        self.source_dir = (
            source_dir
            or Path(config.get("source_dir", "~/Pictures/wedding/full")).expanduser()
        )
        self.dest_dir = dest_dir or Path(config.get("dest_dir", "output/pics/full"))
        self.collection_name = collection_name or config.get(
            "collection_name", "wedding"
        )
        self.create_symlinks = (
            create_symlinks
            if create_symlinks is not None
            else config.get("create_symlinks", True)
        )

    def is_already_organized(self) -> bool:
        """Check if photos are already organized for current configuration.

        Returns:
            True if manifest exists and is up to date, False otherwise
        """
        manifest_path = self.dest_dir / "manifest.json"

        # If manifest doesn't exist, not organized
        if not manifest_path.exists():
            return False

        try:
            # Load and validate manifest
            with open(manifest_path) as f:
                manifest_data = json.load(f)

            # Check if manifest has expected structure
            if "collection_name" not in manifest_data or "pics" not in manifest_data:
                return False

            # Check if collection name matches current config
            if manifest_data["collection_name"] != self.collection_name:
                return False

            # Check if all expected symlinks still exist
            pics = manifest_data.get("pics", [])
            for pic in pics:
                if "dest_path" in pic:
                    symlink_path = self.dest_dir / pic["dest_path"]
                    if not symlink_path.exists():
                        return False

            return True

        except (OSError, json.JSONDecodeError, KeyError):
            return False

    def organize_photos(self) -> OrganizeResult:
        """Orchestrate NormPic to organize photos.

        Returns:
            OrganizeResult with success status and any errors
        """
        try:
            # Ensure directories exist
            if not self.source_dir.exists():
                return OrganizeResult(
                    success=False,
                    errors=[f"Source directory does not exist: {self.source_dir}"],
                )

            # Create destination directory if it doesn't exist
            self.dest_dir.mkdir(parents=True, exist_ok=True)

            # Call NormPic's organize_photos function
            # Note: create_symlinks is not a parameter, symlinks are created by default
            manifest = organize_photos(
                source_dir=self.source_dir,
                dest_dir=self.dest_dir,
                collection_name=self.collection_name,
                collection_description=f"Photo collection: {self.collection_name}",
            )

            # Determine manifest path
            manifest_path = self.dest_dir / "manifest.json"

            # Check for errors in manifest
            errors = []
            if hasattr(manifest, "errors") and manifest.errors:
                errors.extend(
                    [error.get("message", str(error)) for error in manifest.errors]
                )

            # Check processing status
            success = True
            if hasattr(manifest, "processing_status"):
                status = manifest.processing_status.get("status", "unknown")
                if status == "failed":
                    success = False
                    errors.append(f"Photo organization failed with status: {status}")

            return OrganizeResult(
                success=success,
                errors=errors,
                manifest_path=str(manifest_path),
                pics_processed=len(manifest.pics) if hasattr(manifest, "pics") else 0,
            )

        except Exception as e:
            return OrganizeResult(
                success=False, errors=[f"Photo organization failed: {e}"]
            )

    def _load_config(self) -> dict:
        """Load NormPic configuration using unified config system.

        Returns:
            Configuration dictionary with schema validation
        """
        config_file = self.config_dir / "normpic.json"

        # Load schema for validation
        schema_file = Path("config/schema/normpic.json")
        try:
            schema_loader = JsonConfigLoader()
            schema = schema_loader.load_config(schema_file)
        except ConfigLoadError:
            # Fall back to no schema validation if schema file missing
            schema = None

        # Load config with schema validation
        try:
            config_loader = JsonConfigLoader(schema=schema)
            return config_loader.load_config(config_file)
        except ConfigLoadError:
            # Config file doesn't exist, return defaults
            return {}
        except ConfigValidationError:
            # Config file exists but is invalid, re-raise for caller to handle
            raise
