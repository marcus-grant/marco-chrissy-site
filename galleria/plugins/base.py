"""Base plugin interface for Galleria plugin system."""

from abc import ABC, abstractmethod


class BasePlugin(ABC):
    """Abstract base class for all Galleria plugins.

    All plugins must inherit from this class and implement the required
    abstract methods to define their name and version.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name identifier.

        Returns:
            Unique string identifier for the plugin.
        """

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin semantic version.

        Returns:
            Version string following semantic versioning (e.g., "1.0.0").
        """
