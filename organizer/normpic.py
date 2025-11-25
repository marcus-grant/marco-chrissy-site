"""NormPic integration functionality."""

import json
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path

try:
    from normpic import organize_photos, Manifest, Pic, Config
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
    errors: List[str]
    manifest_path: Optional[str] = None
    pics_processed: int = 0


class NormPicOrganizer:
    """Organizes photos using NormPic tool."""
    
    def __init__(self, 
                 config_dir: Path = None,
                 source_dir: Path = None,
                 dest_dir: Path = None, 
                 collection_name: str = None,
                 create_symlinks: bool = None):
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
        self.source_dir = source_dir or Path(config.get("source_dir", "~/Pictures/wedding/full")).expanduser()
        self.dest_dir = dest_dir or Path(config.get("dest_dir", "output/pics/full"))
        self.collection_name = collection_name or config.get("collection_name", "wedding")
        self.create_symlinks = create_symlinks if create_symlinks is not None else config.get("create_symlinks", True)
    
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
                    errors=[f"Source directory does not exist: {self.source_dir}"]
                )
            
            # Create destination directory if it doesn't exist
            self.dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Call NormPic's organize_photos function
            # Note: create_symlinks is not a parameter, symlinks are created by default
            manifest = organize_photos(
                source_dir=self.source_dir,
                dest_dir=self.dest_dir,
                collection_name=self.collection_name,
                collection_description=f"Photo collection: {self.collection_name}"
            )
            
            # Determine manifest path
            manifest_path = self.dest_dir / "manifest.json"
            
            # Check for errors in manifest
            errors = []
            if hasattr(manifest, 'errors') and manifest.errors:
                errors.extend([error.get('message', str(error)) for error in manifest.errors])
            
            # Check processing status
            success = True
            if hasattr(manifest, 'processing_status'):
                status = manifest.processing_status.get('status', 'unknown')
                if status == 'failed':
                    success = False
                    errors.append(f"Photo organization failed with status: {status}")
            
            return OrganizeResult(
                success=success,
                errors=errors,
                manifest_path=str(manifest_path),
                pics_processed=len(manifest.pics) if hasattr(manifest, 'pics') else 0
            )
            
        except Exception as e:
            return OrganizeResult(
                success=False,
                errors=[f"Photo organization failed: {e}"]
            )
    
    def _load_config(self) -> dict:
        """Load NormPic configuration from config file.
        
        Returns:
            Configuration dictionary
        """
        config_file = self.config_dir / "normpic.json"
        
        if not config_file.exists():
            return {}
        
        try:
            with open(config_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}