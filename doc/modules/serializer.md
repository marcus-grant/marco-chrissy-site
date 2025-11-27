# Serializer Module Documentation

## Overview

The serializer module provides unified JSON configuration loading with schema validation support.

## Components

### JsonConfigLoader

Core configuration loader with optional schema validation:

```python
from serializer.json import JsonConfigLoader
from pathlib import Path

# Basic usage without schema
loader = JsonConfigLoader()
config = loader.load_config(Path("config/site.json"))

# Usage with schema validation
schema_loader = JsonConfigLoader()
schema = schema_loader.load_config(Path("config/schema/site.json"))
config_loader = JsonConfigLoader(schema=schema)
config = config_loader.load_config(Path("config/site.json"))
```

**Methods:**
- `load_config(config_path: Path) -> dict[str, Any]`: Load and validate configuration

**Parameters:**
- `schema: dict[str, Any] | None`: Optional JSON schema for validation

**Exceptions:**
- `ConfigLoadError`: File loading or JSON parsing errors
- `ConfigValidationError`: Schema validation failures

### Configuration Exceptions

Structured exception hierarchy for configuration errors:

```python
from serializer.exceptions import ConfigError, ConfigLoadError, ConfigValidationError

try:
    config = loader.load_config(Path("config/invalid.json"))
except ConfigLoadError as e:
    print(f"Failed to load {e.config_path}: {e}")
except ConfigValidationError as e:
    print(f"Validation failed for {e.config_path}: {e}")
except ConfigError as e:
    print(f"General config error: {e}")
```

**Exception Types:**
- `ConfigError`: Base exception for all configuration errors
- `ConfigLoadError`: File not found, permission errors, JSON parsing errors
- `ConfigValidationError`: Schema validation failures with field context

## Dependencies

- `jsonschema`: Required for schema validation (optional dependency)
- `pathlib`: File path handling

## Design Principles

### Schema Validation

- Uses JSON Schema draft-07 standard
- Provides detailed error messages with field paths
- Graceful degradation when jsonschema library not available
- Backward compatibility when schema files missing

### Error Handling

- Comprehensive exception chaining preserves original error context
- Meaningful error messages for user-facing validation failures
- Structured exception types for programmatic error handling

### Extensibility

- Pluggable schema validation system
- Support for multiple configuration formats (currently JSON)
- Designed for future extension to YAML, TOML, etc.

## Integration

The serializer module is used throughout the configuration system:

- **ConfigValidator**: Uses JsonConfigLoader for schema validation
- **Build Command**: Loads site.json and galleria.json configurations  
- **Organize Command**: Loads normpic.json through NormPicOrganizer
- **Validate Command**: Validates all config files through ConfigValidator

## Testing

Comprehensive test coverage includes:

- Unit tests for JsonConfigLoader with valid/invalid configs
- Schema validation success and failure scenarios  
- Error handling for missing files, malformed JSON, schema violations
- Exception hierarchy and error message validation