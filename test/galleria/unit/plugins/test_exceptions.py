"""Unit tests for plugin exception hierarchy."""

import pytest

from galleria.plugins.exceptions import (
    PluginDependencyError,
    PluginError,
    PluginExecutionError,
    PluginValidationError,
)


class TestPluginError:
    """Tests for base PluginError exception."""

    def test_plugin_error_is_exception_subclass(self):
        """PluginError should inherit from Exception."""
        assert issubclass(PluginError, Exception)

    def test_plugin_error_with_message_only(self):
        """PluginError can be created with just a message."""
        error = PluginError("Something went wrong")

        assert str(error) == "Something went wrong"
        assert error.plugin_name is None

    def test_plugin_error_with_message_and_plugin_name(self):
        """PluginError can be created with message and plugin name."""
        error = PluginError("Something went wrong", plugin_name="test-plugin")

        assert str(error) == "Something went wrong"
        assert error.plugin_name == "test-plugin"

    def test_plugin_error_can_be_raised_and_caught(self):
        """PluginError can be raised and caught like any exception."""
        with pytest.raises(PluginError) as exc_info:
            raise PluginError("Test error", plugin_name="test-plugin")

        assert str(exc_info.value) == "Test error"
        assert exc_info.value.plugin_name == "test-plugin"


class TestPluginValidationError:
    """Tests for PluginValidationError exception."""

    def test_plugin_validation_error_inherits_from_plugin_error(self):
        """PluginValidationError should inherit from PluginError."""
        assert issubclass(PluginValidationError, PluginError)

    def test_plugin_validation_error_with_message(self):
        """PluginValidationError can be created with message."""
        error = PluginValidationError("Invalid configuration")

        assert str(error) == "Invalid configuration"
        assert error.plugin_name is None

    def test_plugin_validation_error_with_plugin_name(self):
        """PluginValidationError can be created with plugin name."""
        error = PluginValidationError("Invalid config", plugin_name="validator")

        assert str(error) == "Invalid config"
        assert error.plugin_name == "validator"

    def test_plugin_validation_error_can_be_caught_as_plugin_error(self):
        """PluginValidationError can be caught as base PluginError."""
        with pytest.raises(PluginError) as exc_info:
            raise PluginValidationError("Validation failed")

        assert isinstance(exc_info.value, PluginValidationError)
        assert str(exc_info.value) == "Validation failed"


class TestPluginExecutionError:
    """Tests for PluginExecutionError exception."""

    def test_plugin_execution_error_inherits_from_plugin_error(self):
        """PluginExecutionError should inherit from PluginError."""
        assert issubclass(PluginExecutionError, PluginError)

    def test_plugin_execution_error_with_message_only(self):
        """PluginExecutionError can be created with just message."""
        error = PluginExecutionError("Execution failed")

        assert str(error) == "Execution failed"
        assert error.plugin_name is None
        assert error.original_error is None

    def test_plugin_execution_error_with_original_error(self):
        """PluginExecutionError can wrap an original exception."""
        original = ValueError("Original error")
        error = PluginExecutionError(
            "Plugin failed",
            plugin_name="processor",
            original_error=original
        )

        assert str(error) == "Plugin failed"
        assert error.plugin_name == "processor"
        assert error.original_error is original

    def test_plugin_execution_error_preserves_original_error_chain(self):
        """PluginExecutionError should preserve exception chaining."""
        original = FileNotFoundError("File not found")

        try:
            raise original
        except FileNotFoundError as e:
            execution_error = PluginExecutionError(
                "Failed to process file",
                plugin_name="file-processor",
                original_error=e
            )

        assert execution_error.original_error is original
        assert isinstance(execution_error.original_error, FileNotFoundError)


class TestPluginDependencyError:
    """Tests for PluginDependencyError exception."""

    def test_plugin_dependency_error_inherits_from_plugin_error(self):
        """PluginDependencyError should inherit from PluginError."""
        assert issubclass(PluginDependencyError, PluginError)

    def test_plugin_dependency_error_with_message_only(self):
        """PluginDependencyError can be created with just message."""
        error = PluginDependencyError("Missing dependencies")

        assert str(error) == "Missing dependencies"
        assert error.plugin_name is None
        assert error.missing_deps == []

    def test_plugin_dependency_error_with_missing_dependencies(self):
        """PluginDependencyError can track missing dependencies."""
        missing_deps = ["pillow", "requests"]
        error = PluginDependencyError(
            "Required dependencies not found",
            plugin_name="image-processor",
            missing_deps=missing_deps
        )

        assert str(error) == "Required dependencies not found"
        assert error.plugin_name == "image-processor"
        assert error.missing_deps == missing_deps

    def test_plugin_dependency_error_defaults_empty_missing_deps(self):
        """PluginDependencyError missing_deps defaults to empty list."""
        error = PluginDependencyError("Dependency error", plugin_name="test")

        assert error.missing_deps == []
        assert isinstance(error.missing_deps, list)


class TestExceptionHierarchy:
    """Tests for overall exception hierarchy behavior."""

    def test_all_plugin_exceptions_inherit_from_plugin_error(self):
        """All plugin-specific exceptions should inherit from PluginError."""
        exceptions = [
            PluginValidationError,
            PluginExecutionError,
            PluginDependencyError
        ]

        for exc_class in exceptions:
            assert issubclass(exc_class, PluginError)

    def test_all_plugin_exceptions_inherit_from_base_exception(self):
        """All plugin exceptions should ultimately inherit from Exception."""
        exceptions = [
            PluginError,
            PluginValidationError,
            PluginExecutionError,
            PluginDependencyError
        ]

        for exc_class in exceptions:
            assert issubclass(exc_class, Exception)

    def test_exception_types_are_distinct(self):
        """Each exception type should be distinct from others."""
        exceptions = [
            PluginError,
            PluginValidationError,
            PluginExecutionError,
            PluginDependencyError
        ]

        # Test that no exception class is the same as another
        for i, exc1 in enumerate(exceptions):
            for j, exc2 in enumerate(exceptions):
                if i != j:
                    assert exc1 is not exc2

    def test_can_catch_specific_exception_types(self):
        """Each exception type can be caught specifically."""
        # Test PluginValidationError
        with pytest.raises(PluginValidationError):
            raise PluginValidationError("validation error")

        # Test PluginExecutionError
        with pytest.raises(PluginExecutionError):
            raise PluginExecutionError("execution error")

        # Test PluginDependencyError
        with pytest.raises(PluginDependencyError):
            raise PluginDependencyError("dependency error")

    def test_can_catch_all_plugin_exceptions_with_base_class(self):
        """All plugin exceptions can be caught using base PluginError."""
        exceptions_to_test = [
            PluginValidationError("validation"),
            PluginExecutionError("execution"),
            PluginDependencyError("dependency")
        ]

        for exception in exceptions_to_test:
            with pytest.raises(PluginError):
                raise exception
