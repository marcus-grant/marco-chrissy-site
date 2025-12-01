"""JSON configuration loader with schema validation."""

import json
from pathlib import Path
from typing import Any

try:
    import jsonschema

    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False

from .exceptions import ConfigLoadError, ConfigValidationError


class JsonConfigLoader:
    """Loads and validates JSON configuration files."""

    def __init__(self, schema: dict[str, Any] | None = None):
        """Initialize JSON config loader.

        Args:
            schema: Optional JSON schema for validation
        """
        self.schema = schema

        if schema and not JSONSCHEMA_AVAILABLE:
            raise ImportError(
                "jsonschema library is required for schema validation. "
                "Install with: uv add jsonschema"
            )

    def load_config(self, config_path: Path) -> dict[str, Any]:
        """Load and validate configuration from JSON file.

        Args:
            config_path: Path to JSON config file

        Returns:
            Loaded and validated configuration data

        Raises:
            ConfigLoadError: If file cannot be loaded or parsed
            ConfigValidationError: If config fails schema validation
        """
        # Check if file exists
        if not config_path.exists():
            raise ConfigLoadError(config_path, "Configuration file not found")

        # Load JSON content
        try:
            with open(config_path, encoding="utf-8") as f:
                content = f.read().strip()

            # Handle empty files
            if not content:
                raise ConfigLoadError(config_path, "Configuration file is empty")

            config_data = json.loads(content)

        except json.JSONDecodeError as e:
            raise ConfigLoadError(config_path, f"Failed to parse JSON: {e}") from e
        except OSError as e:
            raise ConfigLoadError(config_path, f"Failed to read file: {e}") from e

        # Validate against schema if provided
        if self.schema:
            self._validate_schema(config_path, config_data)

        return config_data

    def _validate_schema(self, config_path: Path, config_data: Any) -> None:
        """Validate config data against JSON schema.

        Args:
            config_path: Path to config file (for error context)
            config_data: Loaded config data to validate

        Raises:
            ConfigValidationError: If validation fails
        """
        try:
            jsonschema.validate(config_data, self.schema)
        except jsonschema.ValidationError as e:
            # Extract meaningful error message
            error_msg = e.message
            if e.absolute_path:
                field_path = ".".join(str(part) for part in e.absolute_path)
                error_msg = f"Field '{field_path}': {error_msg}"

            raise ConfigValidationError(
                config_path, f"Schema validation failed - {error_msg}"
            ) from e
        except jsonschema.SchemaError as e:
            # This shouldn't happen in production, indicates bug in schema definition
            raise ConfigValidationError(
                config_path, f"Invalid schema definition: {e.message}"
            ) from e
