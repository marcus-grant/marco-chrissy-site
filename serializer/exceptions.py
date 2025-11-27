"""Exception classes for config serialization and validation."""


class ConfigError(Exception):
    """Base exception for configuration-related errors."""
    pass


class ConfigLoadError(ConfigError):
    """Exception raised when config file cannot be loaded."""

    def __init__(self, file_path, message):
        self.file_path = file_path
        super().__init__(f"Failed to load config from {file_path}: {message}")


class ConfigValidationError(ConfigError):
    """Exception raised when config fails schema validation."""

    def __init__(self, file_path, message):
        self.file_path = file_path
        super().__init__(f"Config validation failed for {file_path}: {message}")

