"""BuildOrchestrator for coordinating the complete build process."""

from pathlib import Path

from .config_manager import ConfigManager
from .galleria_builder import GalleriaBuilder
from .pelican_builder import PelicanBuilder
from .exceptions import BuildError


class BuildOrchestrator:
    """Orchestrates the complete site build process."""

    def __init__(self):
        """Initialize BuildOrchestrator."""
        self.config_manager = ConfigManager()
        self.galleria_builder = GalleriaBuilder()
        self.pelican_builder = PelicanBuilder()

    def execute(self, config_dir: Path = None, base_dir: Path = None) -> bool:
        """Execute the complete build process.
        
        Args:
            config_dir: Directory containing config files (optional)
            base_dir: Base directory for resolving paths (optional)
            
        Returns:
            True if successful
            
        Raises:
            BuildError: If any step of the build fails
        """
        try:
            # Set defaults
            if config_dir is None:
                config_dir = Path("config")
            if base_dir is None:
                base_dir = Path.cwd()

            # Initialize config manager with custom directory if provided
            if config_dir != Path("config"):
                self.config_manager = ConfigManager(config_dir)

            # Load all configurations
            site_config = self.config_manager.load_site_config()
            galleria_config = self.config_manager.load_galleria_config()
            pelican_config = self.config_manager.load_pelican_config()

            # Execute galleria build
            self.galleria_builder.build(galleria_config, base_dir)

            # Execute pelican build
            self.pelican_builder.build(site_config, pelican_config, base_dir)

            return True

        except Exception as e:
            raise BuildError(f"Build orchestration failed: {e}") from e