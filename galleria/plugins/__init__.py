"""Galleria plugin system."""

from .base import BasePlugin, PluginContext, PluginResult
from .exceptions import (
    PluginDependencyError,
    PluginError,
    PluginExecutionError,
    PluginValidationError,
)

__all__ = [
    "BasePlugin",
    "PluginContext",
    "PluginResult",
    "PluginError",
    "PluginValidationError",
    "PluginExecutionError",
    "PluginDependencyError",
]
