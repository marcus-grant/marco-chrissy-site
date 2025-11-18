"""Unit tests for serializer exception classes."""

import pytest


class TestExceptionClasses:
    """Unit tests for exception classes."""

    def test_manifest_not_found_error_inheritance(self):
        """Test ManifestNotFoundError inherits from Exception."""
        from galleria.serializer.exceptions import ManifestNotFoundError

        error = ManifestNotFoundError("Test message")

        assert isinstance(error, Exception)
        assert str(error) == "Test message"

    def test_manifest_not_found_error_with_custom_message(self):
        """Test ManifestNotFoundError with custom message."""
        from galleria.serializer.exceptions import ManifestNotFoundError

        message = "Manifest file not found: /path/to/nonexistent.json"
        error = ManifestNotFoundError(message)

        assert str(error) == message

    def test_manifest_validation_error_inheritance(self):
        """Test ManifestValidationError inherits from Exception."""
        from galleria.serializer.exceptions import ManifestValidationError

        error = ManifestValidationError("Test validation message")

        assert isinstance(error, Exception)
        assert str(error) == "Test validation message"

    def test_manifest_validation_error_with_custom_message(self):
        """Test ManifestValidationError with custom message."""
        from galleria.serializer.exceptions import ManifestValidationError

        message = "Missing required field: collection_name"
        error = ManifestValidationError(message)

        assert str(error) == message

    def test_exceptions_can_be_raised_and_caught(self):
        """Test exceptions can be properly raised and caught."""
        from galleria.serializer.exceptions import (
            ManifestNotFoundError,
            ManifestValidationError,
        )

        # Test ManifestNotFoundError
        with pytest.raises(ManifestNotFoundError) as exc_info:
            raise ManifestNotFoundError("File not found")

        assert "File not found" in str(exc_info.value)

        # Test ManifestValidationError
        with pytest.raises(ManifestValidationError) as exc_info:
            raise ManifestValidationError("Invalid data")

        assert "Invalid data" in str(exc_info.value)

    def test_exceptions_are_distinct_types(self):
        """Test that exception types are distinct and don't interfere."""
        from galleria.serializer.exceptions import (
            ManifestNotFoundError,
            ManifestValidationError,
        )

        not_found = ManifestNotFoundError("Not found")
        validation = ManifestValidationError("Invalid")

        assert type(not_found) is not type(validation)
        assert not isinstance(not_found, ManifestValidationError)
        assert not isinstance(validation, ManifestNotFoundError)
