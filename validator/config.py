"""Configuration file validation functionality."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ValidationResult:
    """Result of validation operation."""
    success: bool
    errors: list[str]


class ConfigValidator:
    """Validates configuration files and directories."""

    def __init__(self):
        """Initialize config validator."""
        self.required_config_files = [
            "config/site.json",
            "config/normpic.json",
            "config/pelican.json",
            "config/galleria.json"
        ]

    def validate_config_files(self) -> ValidationResult:
        """Validate that all required config files exist."""
        errors = []

        for config_file in self.required_config_files:
            config_path = Path(config_file)
            if not config_path.exists():
                errors.append(f"Missing required config file: {config_file}")

        return ValidationResult(
            success=len(errors) == 0,
            errors=errors
        )
