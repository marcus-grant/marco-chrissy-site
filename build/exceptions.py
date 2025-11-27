"""Build-related exceptions."""


class BuildError(Exception):
    """Base exception for build-related errors."""
    pass


class ConfigError(BuildError):
    """Exception raised when configuration loading or validation fails."""
    pass


class GalleriaError(BuildError):
    """Exception raised when galleria generation fails."""
    pass


class PelicanError(BuildError):
    """Exception raised when pelican site generation fails."""
    pass