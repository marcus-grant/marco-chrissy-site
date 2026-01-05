"""Configuration manager for unified config loading."""

from pathlib import Path

from serializer.json import JsonConfigLoader
from serializer.exceptions import ConfigLoadError, ConfigValidationError
from .exceptions import ConfigError


class ConfigManager:
    """Manages loading and validation of all project configuration files."""

    def __init__(self, config_dir: str | Path = "config"):
        """Initialize ConfigManager.
        
        Args:
            config_dir: Directory containing config files (default: "config")
        """
        self.config_dir = Path(config_dir)
        self.loader = JsonConfigLoader()

    def load_site_config(self) -> dict:
        """Load site configuration from site.json.
        
        Returns:
            Site configuration data
            
        Raises:
            ConfigError: If config cannot be loaded or is invalid
        """
        config_path = self.config_dir / "site.json"
        try:
            return self.loader.load_config(config_path)
        except (ConfigLoadError, ConfigValidationError) as e:
            raise ConfigError(f"Failed to load site configuration: {e}") from e

    def load_galleria_config(self, config_path: str | Path | None = None) -> dict:
        """Load galleria configuration from galleria.json or specified path.
        
        Args:
            config_path: Path to galleria config file, defaults to config_dir/galleria.json
        
        Returns:
            Galleria configuration data
            
        Raises:
            ConfigError: If config cannot be loaded or is invalid
        """
        if config_path is None:
            config_path = self.config_dir / "galleria.json"
        else:
            config_path = Path(config_path)
            
        try:
            return self.loader.load_config(config_path)
        except (ConfigLoadError, ConfigValidationError) as e:
            raise ConfigError(f"Failed to load galleria configuration: {e}") from e

    def load_pelican_config(self) -> dict:
        """Load pelican configuration from pelican.json.
        
        Returns:
            Pelican configuration data
            
        Raises:
            ConfigError: If config cannot be loaded or is invalid
        """
        config_path = self.config_dir / "pelican.json"
        try:
            return self.loader.load_config(config_path)
        except (ConfigLoadError, ConfigValidationError) as e:
            raise ConfigError(f"Failed to load pelican configuration: {e}") from e

    def load_normpic_config(self) -> dict:
        """Load normpic configuration from normpic.json.
        
        Returns:
            Normpic configuration data
            
        Raises:
            ConfigError: If config cannot be loaded or is invalid
        """
        config_path = self.config_dir / "normpic.json"
        try:
            return self.loader.load_config(config_path)
        except (ConfigLoadError, ConfigValidationError) as e:
            raise ConfigError(f"Failed to load normpic configuration: {e}") from e

    def load_deploy_config(self) -> dict:
        """Load deploy configuration from deploy.json.
        
        Returns:
            Deploy configuration data with env var names and zone settings
            
        Raises:
            ConfigError: If config cannot be loaded or is invalid
        """
        config_path = self.config_dir / "deploy.json"
        try:
            return self.loader.load_config(config_path)
        except (ConfigLoadError, ConfigValidationError) as e:
            raise ConfigError(f"Failed to load deploy configuration: {e}") from e