"""Configuration file validation functionality."""

from dataclasses import dataclass
from pathlib import Path

from serializer.json import JsonConfigLoader
from serializer.exceptions import ConfigError


@dataclass
class ValidationResult:
    """Result of validation operation."""
    success: bool
    errors: list[str]


class ConfigValidator:
    """Validates configuration files and directories."""

    def __init__(self):
        """Initialize config validator."""
        self.config_schemas = {
            "config/site.json": "config/schema/site.json",
            "config/normpic.json": "config/schema/normpic.json",
            "config/pelican.json": "config/schema/pelican.json",
            "config/galleria.json": "config/schema/galleria.json"
        }

    def validate_config_files(self) -> ValidationResult:
        """Validate config files exist and have valid content against schemas."""
        errors = []

        for config_file, schema_file in self.config_schemas.items():
            config_path = Path(config_file)
            schema_path = Path(schema_file)
            
            # Check if config file exists
            if not config_path.exists():
                errors.append(f"Missing required config file: {config_file}")
                continue
                
            # Check if schema exists
            if not schema_path.exists():
                # If no schema, just check file existence (backward compatibility)
                continue
                
            # Validate content against schema
            try:
                # Load schema
                schema_loader = JsonConfigLoader()
                schema = schema_loader.load_config(schema_path)
                
                # Validate config against schema
                config_loader = JsonConfigLoader(schema=schema)
                config_loader.load_config(config_path)
                
            except ConfigError as e:
                errors.append(f"Config validation error in {config_file}: {e}")
            except Exception as e:
                errors.append(f"Unexpected error validating {config_file}: {e}")

        return ValidationResult(
            success=len(errors) == 0,
            errors=errors
        )
