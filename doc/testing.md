# Testing Guide

## Overview

This project uses a nested TDD approach with comprehensive E2E and unit tests. Tests are organized to drive development workflow and ensure reliable functionality.

## Test Organization

### Directory Structure

```
test/
├── e2e/                    # End-to-end tests (outer TDD cycle)
├── unit/                   # Unit tests (inner TDD cycle)
└── conftest.py            # Shared fixtures
```

### E2E Tests (Outer Cycle)

E2E tests define desired functionality and drive development:

**Site Command Tests:**
- `test_site_command.py` - Basic CLI discovery and help
- `test_site_validate.py` - Config validation functionality
- `test_site_organize.py` - Photo organization workflow  
- `test_site_build.py` - Gallery and site generation
- `test_site_deploy.py` - CDN upload and complete pipeline

**Test Pattern:**
```python
def test_site_validate_checks_config_files(self, temp_filesystem, full_config_setup):
    """Test that validate command finds required config files."""
    full_config_setup()  # Use fixtures for setup
    
    result = subprocess.run(["uv", "run", "site", "validate"], 
                          capture_output=True, cwd=str(temp_filesystem))
    
    assert result.returncode == 0
    assert "config files found" in result.stdout.lower()
```

## Test Fixtures

### Filesystem Fixtures

**`temp_filesystem`** - Temporary directory for test isolation:
```python
def test_something(self, temp_filesystem):
    assert temp_filesystem.exists()  # Path object
```

**`file_factory`** - Create files with content:
```python
def test_file_creation(self, file_factory):
    # Text file
    path = file_factory("test.txt", content="Hello")
    
    # JSON file  
    path = file_factory("data.json", json_content={"key": "value"})
```

**`directory_factory`** - Create directory structures:
```python
def test_directories(self, directory_factory):
    path = directory_factory("deep/nested/dirs")
    assert path.exists()
```

### Config Fixtures

**`config_file_factory`** - Create config files with defaults:
```python
def test_config(self, config_file_factory):
    # Uses built-in defaults for site config
    site_config = config_file_factory("site")
    
    # Custom content
    custom_config = config_file_factory("site", {"custom": "value"})
```

**`full_config_setup`** - Complete config environment:
```python
def test_full_setup(self, full_config_setup):
    configs = full_config_setup()  # Creates all 4 required configs
    assert "site" in configs
    assert configs["site"].exists()
```

### Custom Config Example

```python
def test_custom_configs(self, full_config_setup):
    custom_configs = {
        "site": {"base_url": "https://test.example.com"},
        "normpic": {"input_dir": "custom_photos"}
    }
    configs = full_config_setup(custom_configs)
```

## Running Tests

### Basic Commands

```bash
# All tests
uv run pytest

# Specific test file
uv run pytest test/unit/validator/test_config.py -v

# E2E tests only
uv run pytest test/e2e/ -v

# Stop on first failure
uv run pytest -x
```

### Test Categories

```bash
# Unit tests for specific module
uv run pytest test/unit/validator/ -v

# All site command E2E tests
uv run pytest test/e2e/test_site_*.py -v
```

## Writing New Tests

### E2E Test Pattern

1. **Use fixtures** for setup
2. **Call actual commands** via subprocess  
3. **Test real behavior** not implementation
4. **Start with skip** to keep suite green

```python
@pytest.mark.skip(reason="Feature not yet implemented")
def test_new_functionality(self, temp_filesystem, full_config_setup):
    full_config_setup()
    
    result = subprocess.run(["uv", "run", "site", "new-command"],
                          capture_output=True, cwd=str(temp_filesystem))
    
    assert result.returncode == 0
    assert "expected output" in result.stdout
```

### Unit Test Pattern

1. **Test specific functions/classes**
2. **Use fixtures** for realistic setup
3. **Focus on single responsibility**
4. **Keep tests small and fast**

```python
def test_validator_function(self, temp_filesystem, file_factory):
    config_file = file_factory("config/test.json", json_content={"valid": True})
    
    from module import validator_function
    result = validator_function(config_file)
    
    assert result.success is True
```

## Test Development Workflow

1. **Write E2E test** for new feature (skipped)
2. **Run test** - should be skipped, suite stays green
3. **Write unit tests** for missing pieces
4. **Implement functionality** to pass unit tests
5. **Unskip E2E test** when ready
6. **Verify E2E test passes**
7. **Commit and move to next feature**

This ensures continuous progress while maintaining a passing test suite.