"""Permission validation functionality."""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ValidationResult:
    """Result of validation operation."""

    success: bool
    errors: list[str]


class PermissionValidator:
    """Validates directory permissions for site operations."""

    def __init__(self, base_path=None):
        """Initialize permission validator."""
        self.base_path = Path(base_path) if base_path else Path.cwd()

    def validate_output_permissions(self) -> ValidationResult:
        """Validate that output directory can be created and written to."""
        errors = []
        output_dir = self.base_path / "output"

        # Check if output directory exists and is writable
        if output_dir.exists():
            if not os.access(output_dir, os.W_OK):
                errors.append("Output directory exists but is not writable")
        else:
            # Check if parent directory allows creating output directory
            parent_dir = output_dir.parent
            if not os.access(parent_dir, os.W_OK):
                errors.append("Cannot create output directory - parent not writable")

        # Check temp directory permissions (needed for building)
        temp_dir = self.base_path / "temp"
        if temp_dir.exists():
            if not os.access(temp_dir, os.W_OK):
                errors.append("Temp directory exists but is not writable")
        else:
            # Check if we can create temp directory
            if not os.access(self.base_path, os.W_OK):
                errors.append("Cannot create temp directory - base path not writable")

        return ValidationResult(success=len(errors) == 0, errors=errors)
