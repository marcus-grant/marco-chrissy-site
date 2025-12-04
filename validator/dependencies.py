"""Dependency validation functionality."""

import importlib
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of validation operation."""

    success: bool
    errors: list[str]


class DependencyValidator:
    """Validates required dependencies are available."""

    def __init__(self):
        """Initialize dependency validator."""
        # Core dependencies that must be available
        self.required_dependencies = [
            "pelican",
            "PIL",  # Pillow imports as PIL
            "click",
            "jinja2",
            "jsonschema",
            "normpic",
        ]

    def validate_dependencies(self) -> ValidationResult:
        """Validate that all required dependencies are importable."""
        errors = []

        for dependency in self.required_dependencies:
            try:
                importlib.import_module(dependency)
            except ImportError:
                errors.append(f"Missing required dependency: {dependency}")
            except Exception as e:
                errors.append(f"Error importing {dependency}: {e}")

        return ValidationResult(success=len(errors) == 0, errors=errors)
