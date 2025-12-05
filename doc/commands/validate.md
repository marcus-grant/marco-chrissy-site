# Validate Command

## Overview

The validate command performs comprehensive pre-flight checks to ensure all requirements are met before running any site operations. It is the foundation command that all others cascade through.

## Usage

```bash
uv run site validate
```

## Validation Checks

The validate command performs three categories of validation:

### 1. Configuration Files
- Verifies existence of required config files:
  - `config/site.json`
  - `config/normpic.json`
  - `config/pelican.json`
  - `config/galleria.json`
- Validates config content against JSON schemas (when schemas exist)
- Reports specific missing files or schema validation errors

### 2. Dependencies
- Checks that all required Python dependencies are importable:
  - `pelican` - Static site generator
  - `PIL` (Pillow) - Image processing
  - `click` - CLI framework
  - `jinja2` - Template engine
  - `jsonschema` - Config validation
  - `normpic` - Photo organization tool
- Reports any missing or unimportable dependencies

### 3. Permissions
- Verifies write permissions for required directories:
  - `output/` directory (or ability to create it)
  - `temp/` directory (or ability to create it)
- Ensures the build process can write generated files

## Exit Codes

- **0**: All validations passed successfully
- **1**: One or more validation checks failed

## Output Examples

### Success
```
Running validation checks...
✓ Config files found
✓ Dependencies available  
✓ Permissions verified
Validation completed successfully!
```

### Failure
```
Running validation checks...
✗ Config validation failed:
  - Missing required config file: config/site.json
  - Missing required config file: config/galleria.json
```

## Command Pipeline Position

The validate command is the base of the cascading pipeline:
```
deploy → build → organize → validate
```

All other commands automatically call validate through the cascade, ensuring consistent pre-flight checks.

## Architecture

The validate command uses three specialized validator classes:

- **ConfigValidator** (`validator/config.py`) - Config file validation
- **DependencyValidator** (`validator/dependencies.py`) - Python dependency checks
- **PermissionValidator** (`validator/permissions.py`) - Directory permission checks

Each validator follows the same pattern:
- Returns `ValidationResult(success: bool, errors: list[str])`
- Supports dependency injection for testing isolation
- Provides clear, actionable error messages

## Testing

The validate command has comprehensive E2E test coverage:
- `test_validate_checks_config_files_exist` - Config validation
- `test_validate_checks_dependencies` - Dependency validation  
- `test_validate_checks_output_permissions` - Permission validation
- `test_validate_fails_on_missing_requirements` - Failure scenarios

All validators support test isolation through dependency injection.

## Troubleshooting

### Common Issues

**Missing config files:**
- Create config files from examples or run `site init` (if available)
- Check file paths are relative to project root

**Import errors:**
- Run `uv sync` to ensure dependencies are installed
- Check virtual environment activation

**Permission errors:**  
- Verify write permissions on project directory
- Check for read-only filesystem mounts
- Ensure user has necessary file system permissions

**Exit code 1 in CI:**
- Validate command properly returns non-zero exit codes on failure
- Use this for build pipeline failure detection