# Build Exceptions

## Overview

The build module provides a comprehensive exception hierarchy for handling all types of build-related errors. This system enables precise error handling, clear error messages, and proper exception chaining for debugging.

## Exception Hierarchy

```
BuildError (base exception)
├── ConfigError (configuration issues)
├── GalleriaError (gallery generation issues)
└── PelicanError (site generation issues)
```

## Exception Classes

### `BuildError`

Base exception for all build-related errors.

```python
class BuildError(Exception):
    """Base exception for build system errors."""
    pass
```

**Usage:**
- Catch-all for any build system error
- Base class for specific error types
- Used by orchestrator for general failures

### `ConfigError`

Raised when configuration loading or validation fails.

```python
class ConfigError(BuildError):
    """Configuration loading or validation error."""
    pass
```

**Common Scenarios:**
- Missing configuration files
- Invalid JSON in config files
- Schema validation failures
- Required configuration fields missing

### `GalleriaError`

Raised when gallery generation fails.

```python
class GalleriaError(BuildError):
    """Gallery generation error."""
    pass
```

**Common Scenarios:**
- Plugin registration failures
- Plugin execution errors
- Missing photo manifest files
- Thumbnail generation failures

### `PelicanError`

Raised when static site generation fails.

```python
class PelicanError(BuildError):
    """Pelican site generation error."""
    pass
```

**Common Scenarios:**
- Pelican configuration errors
- Content processing failures
- Theme validation issues
- Output directory creation failures

## Usage Patterns

### Specific Exception Handling
```python
from build.orchestrator import BuildOrchestrator
from build.exceptions import ConfigError, GalleriaError, PelicanError

orchestrator = BuildOrchestrator()
try:
    orchestrator.execute()
except ConfigError as e:
    print(f"Configuration error: {e}")
except GalleriaError as e:
    print(f"Gallery generation failed: {e}")
except PelicanError as e:
    print(f"Site generation failed: {e}")
```

### General Error Handling
```python
from build.orchestrator import BuildOrchestrator
from build.exceptions import BuildError

orchestrator = BuildOrchestrator()
try:
    orchestrator.execute()
except BuildError as e:
    print(f"Build failed: {e}")
```

### Exception Chaining
```python
from build.exceptions import GalleriaError

try:
    # Gallery generation code
    pass
except Exception as e:
    raise GalleriaError(f"Gallery generation failed: {e}") from e
```

## Error Message Guidelines

### Clear and Actionable
- Describe what went wrong
- Include relevant file paths or configuration keys
- Suggest possible solutions when appropriate

### Examples
```python
# Good error messages
raise ConfigError("Failed to load site configuration: config/site.json not found")
raise GalleriaError("Plugin execution failed: missing manifest file at photos/manifest.json")
raise PelicanError("Theme validation failed: theme 'custom' directory not found")

# Poor error messages  
raise ConfigError("Config error")
raise GalleriaError("Something went wrong")
```

## Exception Chaining

All build exceptions support proper exception chaining to preserve debugging information:

```python
try:
    # Lower-level operation
    data = json.load(config_file)
except JSONDecodeError as e:
    # Chain the exception to preserve stack trace
    raise ConfigError(f"Invalid JSON in {config_file}: {e}") from e
```

This preserves the original exception while providing build-specific context.

## Testing Exception Handling

### Testing Specific Exceptions
```python
from build.config_manager import ConfigManager
from build.exceptions import ConfigError

def test_config_manager_missing_file_raises_config_error():
    config_manager = ConfigManager(Path("/nonexistent"))
    
    with pytest.raises(ConfigError) as exc_info:
        config_manager.load_site_config()
    
    assert "config/site.json not found" in str(exc_info.value)
```

### Testing Exception Chaining
```python
def test_exception_chaining_preserves_original():
    with pytest.raises(ConfigError) as exc_info:
        # Code that raises ConfigError from JSONDecodeError
        pass
    
    assert exc_info.value.__cause__ is not None
    assert isinstance(exc_info.value.__cause__, JSONDecodeError)
```

## Integration with Build Components

### ConfigManager
```python
try:
    config_data = self.loader.load_config(config_path)
except Exception as e:
    raise ConfigError(f"Failed to load {config_path}: {e}") from e
```

### GalleriaBuilder
```python
try:
    result = pipeline.execute_stages()
except Exception as e:
    raise GalleriaError(f"Gallery pipeline failed: {e}") from e
```

### PelicanBuilder
```python
try:
    pelican_instance.run()
except Exception as e:
    raise PelicanError(f"Pelican generation failed: {e}") from e
```

### BuildOrchestrator
```python
try:
    # Execute build steps
    pass
except (ConfigError, GalleriaError, PelicanError):
    # Re-raise specific build errors
    raise
except Exception as e:
    # Wrap unexpected errors
    raise BuildError(f"Build orchestration failed: {e}") from e
```

## Design Benefits

### Precise Error Handling
- Different error types can be handled differently
- CLI can provide specific user guidance based on error type
- Logging can categorize errors for monitoring

### Debugging Support
- Exception chaining preserves full stack traces
- Clear error messages reduce debugging time
- Consistent error format across all components

### Error Recovery
- Specific exceptions enable targeted retry logic
- Different error types can trigger different fallback strategies
- Clear error boundaries between components