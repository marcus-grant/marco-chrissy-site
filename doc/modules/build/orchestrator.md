# BuildOrchestrator

## Overview

The BuildOrchestrator is the main coordination class that executes the complete site build process. It manages the build workflow by delegating to specialized builder components while handling configuration loading and error coordination.

## Class Design

```python
class BuildOrchestrator:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.galleria_builder = GalleriaBuilder()
        self.pelican_builder = PelicanBuilder()
    
    def execute(self, config_dir: Path = None, base_dir: Path = None) -> bool:
        # Executes complete build workflow
```

## Key Features

### Configuration Management
- Automatically initializes ConfigManager with default or custom config directory
- Loads all required configurations (site.json, galleria.json, pelican.json)
- Provides unified error handling for configuration issues

### Build Coordination
- Executes galleria build first (generates galleries and thumbnails)
- Executes pelican build second (generates site pages)
- Maintains proper dependency order between build steps

### Error Handling
- Catches all exceptions and wraps them in BuildError
- Provides clear error messages with exception chaining
- Returns boolean success indicator for simple integration

## API Reference

### `__init__()`
Initializes orchestrator with default builder components.

### `execute(config_dir: Path = None, base_dir: Path = None) -> bool`

**Parameters:**
- `config_dir`: Directory containing config files (defaults to "config")
- `base_dir`: Base directory for resolving relative paths (defaults to current directory)

**Returns:**
- `True` if build completed successfully
- Raises `BuildError` if any step fails

**Raises:**
- `BuildError`: If configuration loading or any build step fails

## Usage Patterns

### Basic Usage
```python
from build.orchestrator import BuildOrchestrator

orchestrator = BuildOrchestrator()
try:
    success = orchestrator.execute()
    print("Build completed successfully!")
except BuildError as e:
    print(f"Build failed: {e}")
```

### Custom Configuration
```python
from pathlib import Path
from build.orchestrator import BuildOrchestrator

orchestrator = BuildOrchestrator()
success = orchestrator.execute(
    config_dir=Path("custom/configs"),
    base_dir=Path("/project/root")
)
```

### Integration in CLI Commands
```python
@click.command()
def build():
    try:
        orchestrator = BuildOrchestrator()
        orchestrator.execute()
        click.echo("✓ Build completed successfully!")
    except BuildError as e:
        click.echo(f"✗ Build failed: {e}")
        ctx.exit(1)
```

## Testing

The BuildOrchestrator is designed for easy testing with minimal mocking:

```python
@patch('cli.commands.build.BuildOrchestrator')
def test_build_success(mock_orchestrator_class):
    mock_orchestrator = Mock()
    mock_orchestrator_class.return_value = mock_orchestrator
    mock_orchestrator.execute.return_value = True
    
    result = runner.invoke(build)
    assert result.exit_code == 0
```

## Design Benefits

### Separation of Concerns
- Business logic completely separated from CLI presentation
- Each builder has single responsibility (gallery vs site generation)
- Configuration loading centralized and reusable

### Testability
- Single class to mock instead of multiple dependencies
- Clear success/failure interface
- Exception chaining preserves debugging information

### Reusability
- Can be called from CLI, API, scripts, or other contexts
- No CLI dependencies in core logic
- Configurable paths for different environments