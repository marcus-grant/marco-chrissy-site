"""Base plugin interface for Galleria plugin system."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


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


@dataclass
class PluginContext:
    """Context data passed to plugin execution.

    Contains all input data and configuration needed for plugin execution,
    along with shared metadata that can be passed between plugins in the pipeline.
    """

    input_data: Any
    """The input data for the plugin (varies by plugin type)."""

    config: dict[str, Any]
    """Plugin-specific configuration settings."""

    output_dir: Path
    """Directory where plugin should write output files."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Shared metadata that can be passed between plugins."""


@dataclass
class PluginResult:
    """Result data returned from plugin execution.

    Contains execution status, output data, and any errors or metadata
    generated during plugin processing.
    """

    success: bool
    """Whether plugin execution completed successfully."""

    output_data: Any
    """The output data produced by the plugin (varies by plugin type)."""

    errors: list[str] = field(default_factory=list)
    """List of error messages if execution failed."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Additional metadata about the execution (timing, stats, etc.)."""
