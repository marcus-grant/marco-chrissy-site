# Validator Module

## Overview

The validator module provides comprehensive validation functionality for the site build system. It includes config file validation, dependency checking, and permission verification.

## ConfigValidator API

### Constructor

```python
ConfigValidator(base_path=None)
```

**Parameters:**
- `base_path` (Path, optional): Base directory for resolving config and schema paths. Defaults to `Path.cwd()`.

**Breaking Change (2025-11-29):** Added `base_path` parameter for dependency injection and test isolation.

### Methods

#### validate_config_files()

```python
def validate_config_files(self) -> ValidationResult
```

Validates all required config files exist and have valid content against their schemas.

**Returns:** `ValidationResult` with `success: bool` and `errors: list[str]`

**Validated Files:**
- `config/site.json` → `config/schema/site.json`
- `config/normpic.json` → `config/schema/normpic.json` 
- `config/pelican.json` → `config/schema/pelican.json`
- `config/galleria.json` → `config/schema/galleria.json`

## Usage Examples

### Production Usage
```python
from validator.config import ConfigValidator

# Uses current working directory
validator = ConfigValidator()
result = validator.validate_config_files()

if not result.success:
    for error in result.errors:
        print(f"Validation error: {error}")
```

### Testing Usage
```python
# Use dependency injection for isolated testing
validator = ConfigValidator(base_path=temp_filesystem)
result = validator.validate_config_files()
```

## Architecture Notes

### Path Resolution

All config and schema paths are resolved relative to `base_path`:
- **Before:** Hardcoded relative paths from current working directory
- **After:** Configurable base path enables dependency injection

### Test Isolation

The `base_path` parameter enables:
- **Testing:** Each test gets isolated temporary directory
- **Deployment:** Different path structures for different environments
- **Development:** Local vs production path configurations

## Migration Guide

### Production Code
No changes required. `ConfigValidator()` continues to work with current working directory.

### Test Code
```python
# OLD (contaminated global state)
original_cwd = os.getcwd()
try:
    os.chdir(str(temp_filesystem))
    validator = ConfigValidator()
    result = validator.validate_config_files()
finally:
    os.chdir(original_cwd)

# NEW (isolated)
validator = ConfigValidator(base_path=temp_filesystem)
result = validator.validate_config_files()
```

## DependencyValidator API

### Constructor

```python
DependencyValidator()
```

No parameters required. Validates a predefined set of core dependencies.

### Methods

#### validate_dependencies()

```python
def validate_dependencies(self) -> ValidationResult
```

Validates that all required Python dependencies are importable.

**Returns:** `ValidationResult` with `success: bool` and `errors: list[str]`

**Validated Dependencies:**
- `pelican` - Static site generator
- `PIL` (Pillow) - Image processing
- `click` - CLI framework
- `jinja2` - Template engine
- `jsonschema` - Config validation
- `normpic` - Photo organization tool

### Usage Example

```python
from validator.dependencies import DependencyValidator

validator = DependencyValidator()
result = validator.validate_dependencies()

if not result.success:
    for error in result.errors:
        print(f"Dependency error: {error}")
```

## PermissionValidator API

### Constructor

```python
PermissionValidator(base_path=None)
```

**Parameters:**
- `base_path` (Path, optional): Base directory for resolving paths. Defaults to `Path.cwd()`.

### Methods

#### validate_output_permissions()

```python
def validate_output_permissions(self) -> ValidationResult
```

Validates write permissions for required output directories.

**Returns:** `ValidationResult` with `success: bool` and `errors: list[str]`

**Validated Directories:**
- `output/` - Main output directory for generated site
- `temp/` - Temporary directory for build operations

### Usage Example

```python
from validator.permissions import PermissionValidator

validator = PermissionValidator()
result = validator.validate_output_permissions()

if not result.success:
    for error in result.errors:
        print(f"Permission error: {error}")
```

## ValidationResult Common Interface

All validators return a consistent `ValidationResult` object:

```python
@dataclass
class ValidationResult:
    success: bool      # True if all checks passed
    errors: list[str]  # List of error messages (empty if success=True)
```

## Future Enhancements

### Post-MVP: PathConfig Integration
The `base_path` parameter is a stepping stone to full path configuration:

```python
# Future: Centralized path configuration
path_config = PathConfig.from_config("config/site.json")
validator = ConfigValidator(path_config=path_config)
```

This will enable:
- Docker volume mounting flexibility
- Development vs production path differences  
- CDN integration path configuration
- Deployment environment customization