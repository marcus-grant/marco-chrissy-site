# ConfigManager

## Overview

The ConfigManager provides unified configuration loading for all build-related configuration files. It centralizes config file access and validation, replacing scattered configuration loading throughout the codebase.

## Class Design

```python
class ConfigManager:
    def __init__(self, config_dir: Path = Path("config")):
        self.config_dir = config_dir
        self.loader = JsonConfigLoader()
    
    def load_site_config(self) -> dict
    def load_galleria_config(self) -> dict  
    def load_pelican_config(self) -> dict
    def load_normpic_config(self) -> dict
```

## Key Features

### Unified Configuration Loading
- Single point of access for all configuration files
- Consistent error handling across all config types
- Uses JsonConfigLoader with schema validation support

### Configuration Files Managed
- **site.json**: Orchestration settings, output paths, CDN deployment
- **galleria.json**: Gallery generation settings, manifest paths, themes
- **pelican.json**: Site generation settings, themes, content configuration
- **normpic.json**: Photo organization settings, source/destination paths

### Error Handling
- Wraps JsonConfigLoader exceptions in ConfigError
- Provides clear error messages for missing or invalid config files
- Maintains exception chaining for debugging

## API Reference

### `__init__(config_dir: Path = Path("config"))`
Initialize ConfigManager with custom config directory.

**Parameters:**
- `config_dir`: Directory containing configuration files

### `load_site_config() -> dict`
Load site orchestration configuration.

**Returns:** Dictionary with site configuration data
**Raises:** `ConfigError` if config file missing or invalid

### `load_galleria_config() -> dict`
Load gallery generation configuration.

**Returns:** Dictionary with galleria configuration data
**Raises:** `ConfigError` if config file missing or invalid

### `load_pelican_config() -> dict`
Load static site generation configuration.

**Returns:** Dictionary with pelican configuration data
**Raises:** `ConfigError` if config file missing or invalid

### `load_normpic_config() -> dict`
Load photo organization configuration.

**Returns:** Dictionary with normpic configuration data
**Raises:** `ConfigError` if config file missing or invalid

## Usage Patterns

### Basic Usage
```python
from build.config_manager import ConfigManager

config_manager = ConfigManager()
site_config = config_manager.load_site_config()
galleria_config = config_manager.load_galleria_config()
```

### Custom Config Directory
```python
from pathlib import Path
from build.config_manager import ConfigManager

config_manager = ConfigManager(Path("custom/configs"))
pelican_config = config_manager.load_pelican_config()
```

### Error Handling
```python
from build.config_manager import ConfigManager
from build.exceptions import ConfigError

config_manager = ConfigManager()
try:
    site_config = config_manager.load_site_config()
except ConfigError as e:
    print(f"Configuration error: {e}")
```

## Integration with JsonConfigLoader

ConfigManager builds on the JsonConfigLoader foundation:

```python
# ConfigManager internally uses:
self.loader = JsonConfigLoader()
config_data = self.loader.load_config(config_path, schema_path)
```

This provides:
- JSON schema validation when schemas are available
- Consistent error handling and messaging
- Support for schema-less loading when schemas missing

## Configuration File Locations

Default configuration file locations:
```
config/
├── site.json          # Site orchestration settings
├── galleria.json      # Gallery generation settings  
├── pelican.json       # Static site generation settings
└── normpic.json       # Photo organization settings
```

## Testing

ConfigManager is tested with comprehensive unit tests covering:

```python
def test_load_site_config(self, temp_filesystem, config_file_factory):
    config_manager = ConfigManager(temp_filesystem.name)
    config_file_factory("site.json", {"output_dir": "output"})
    
    config = config_manager.load_site_config()
    assert config["output_dir"] == "output"

def test_load_config_missing_file_raises_config_error(self, temp_filesystem):
    config_manager = ConfigManager(temp_filesystem.name)
    
    with pytest.raises(ConfigError):
        config_manager.load_site_config()
```

## Design Benefits

### Centralized Configuration
- Single source of truth for configuration loading logic
- Consistent error handling across all config types
- Easy to add new configuration files

### Schema Integration
- Built-in support for JSON schema validation
- Graceful fallback when schemas not available
- Clear validation error messages

### Testability
- Simple mocking of configuration data in tests
- Isolated testing of configuration logic
- Support for temporary filesystem testing