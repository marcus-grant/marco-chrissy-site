"""Galleria plugin system."""

from .base import BasePlugin, PluginContext, PluginResult
from .exceptions import (
    PluginDependencyError,
    PluginError,
    PluginExecutionError,
    PluginValidationError,
)
from .interfaces import ProcessorPlugin, ProviderPlugin, TransformPlugin

__all__ = [
    "BasePlugin",
    "PluginContext",
    "PluginResult",
    "PluginError",
    "PluginValidationError",
    "PluginExecutionError",
    "PluginDependencyError",
    "ProviderPlugin",
    "ProcessorPlugin",
    "TransformPlugin",
]
