"""Exception hierarchy for Galleria plugin system."""


class PluginError(Exception):
    """Base exception for all plugin-related errors.

    All plugin-specific exceptions inherit from this base class to enable
    consistent error handling across the plugin system.
    """

    def __init__(self, message: str, plugin_name: str = None):
        """Initialize plugin error with message and optional plugin name.

        Args:
            message: Error message describing what went wrong
            plugin_name: Name of the plugin that caused the error (optional)
        """
        self.plugin_name = plugin_name
        super().__init__(message)


class PluginValidationError(PluginError):
    """Raised when plugin context or configuration is invalid.

    This exception is raised when plugin input validation fails, such as:
    - Invalid configuration parameters
    - Missing required context fields
    - Invalid input data format
    """

    pass


class PluginExecutionError(PluginError):
    """Raised when plugin execution fails at runtime.

    This exception is raised when plugin execution encounters errors during
    processing, such as:
    - File system errors
    - Image processing failures
    - Network connectivity issues
    """

    def __init__(
        self, message: str, plugin_name: str = None, original_error: Exception = None
    ):
        """Initialize execution error with optional original exception.

        Args:
            message: Error message describing the execution failure
            plugin_name: Name of the plugin that failed (optional)
            original_error: The original exception that caused the failure (optional)
        """
        self.original_error = original_error
        super().__init__(message, plugin_name)


class PluginDependencyError(PluginError):
    """Raised when plugin dependencies are missing or incompatible.

    This exception is raised when plugin dependency checks fail, such as:
    - Missing required Python packages
    - Incompatible plugin versions
    - Missing system dependencies
    """

    def __init__(
        self, message: str, plugin_name: str = None, missing_deps: list[str] = None
    ):
        """Initialize dependency error with optional missing dependencies list.

        Args:
            message: Error message describing the dependency issue
            plugin_name: Name of the plugin with missing dependencies (optional)
            missing_deps: List of missing dependency names (optional)
        """
        self.missing_deps = missing_deps or []
        super().__init__(message, plugin_name)
