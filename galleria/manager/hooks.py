"""Plugin hook system for Galleria."""

from collections.abc import Callable

from galleria.plugins import PluginContext, PluginResult


class PluginHookManager:
    """Manages plugin hooks for extensibility points in the pipeline.

    Provides registration and execution of hooks at specific stages
    of the plugin pipeline workflow.
    """

    def __init__(self):
        """Initialize hook manager with empty hook storage."""
        self._hooks: dict[str, list[Callable[[PluginContext], PluginResult]]] = {}

    def register_hook(
        self,
        name: str,
        callback: Callable[[PluginContext], PluginResult]
    ) -> None:
        """Register a callback function for a specific hook.

        Args:
            name: Hook name (e.g., "before_provider", "after_processor")
            callback: Function that takes PluginContext and returns PluginResult
        """
        if name not in self._hooks:
            self._hooks[name] = []
        self._hooks[name].append(callback)

    def execute_hook(self, name: str, context: PluginContext) -> list[PluginResult]:
        """Execute all callbacks registered for a hook.

        Args:
            name: Hook name to execute
            context: PluginContext to pass to hook callbacks

        Returns:
            List of PluginResult objects from all hook callbacks
        """
        if name not in self._hooks:
            return []

        results = []
        for callback in self._hooks[name]:
            result = callback(context)
            results.append(result)

        return results

    def list_hooks(self) -> list[str]:
        """List all registered hook names.

        Returns:
            List of hook names that have registered callbacks
        """
        return list(self._hooks.keys())
