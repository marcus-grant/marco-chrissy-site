# Testing Guide

## Overview

This project uses a nested TDD approach with comprehensive E2E and unit tests. Tests are organized to drive development workflow and ensure reliable functionality.

**CRITICAL: All tests must use isolation patterns to prevent contamination between test runs. Direct filesystem access is prohibited in tests.**

**CRITICAL: All tests must use the current unified config format. Never hardcode nested config structures in tests.**

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

### Theme Testing Fixtures

**`shared_theme_dirs`** - Create shared theme directory structure:
```python
def test_shared_templates(self, shared_theme_dirs):
    """Test shared theme directory structure creation."""
    # Returns dict with standardized paths
    shared_templates = shared_theme_dirs["shared_templates"]
    galleria_templates = shared_theme_dirs["galleria_templates"]
    
    # Create and test shared templates
    template_path = shared_templates / "navigation.html"
    template_path.write_text("<nav>Shared Navigation</nav>")
    
    assert template_path.exists()
    assert shared_templates.exists()
    assert galleria_templates.exists()
```

**Fixture Benefits**:
- Replaces repeated directory creation in 4+ tests
- Provides standardized shared theme structure
- Returns consistent path dictionary for easy access
- Integrates with temp_filesystem for proper isolation

**Usage Pattern**:
```python
def test_template_loading(self, shared_theme_dirs):
    """Test template loading from shared directories."""
    from themes.shared.utils.template_loader import GalleriaSharedTemplateLoader
    
    # Use fixture paths
    config = {
        "theme": {
            "external_templates": [str(shared_theme_dirs["shared_templates"])]
        }
    }
    
    loader = GalleriaSharedTemplateLoader(config, shared_theme_dirs["galleria_templates"])
    # Test template loading functionality
```

## Test Isolation Patterns

### CRITICAL: No Direct Filesystem Access

**❌ PROHIBITED PATTERNS:**
```python
# NEVER do direct filesystem access in tests
thumbnails = list((output_dir / "thumbnails").glob("*.webp"))  # NO!
schema = loader.load_config(Path("config/schema/file.json"))   # NO!
os.chdir(str(temp_directory))  # NO!
shutil.copy("real/file.json", temp_dir)  # NO!
```

**✅ REQUIRED PATTERNS:**

### Mock Schemas Instead of Real Files
```python
# Use inline mock schemas
file_factory("config/schema/normpic.json", json_content={
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object", 
    "required": ["source_dir", "dest_dir"],
    "properties": {
        "source_dir": {"type": "string"},
        "dest_dir": {"type": "string"}
    }
})
```

### HTTP Testing Instead of Filesystem Inspection
```python
# Test via HTTP interface, not filesystem counting
for i in range(1, expected_count + 1):
    response = requests.get(f"http://localhost:{port}/file_{i}.html")
    assert response.status_code == 200
```

### Dependency Injection for Paths
```python
# Use configurable base paths instead of os.chdir()
validator = ConfigValidator(base_path=temp_filesystem)
result = validator.validate_config_files()
```

### Isolation Principles

1. **Each test runs in completely isolated temporary directory**
2. **No shared state between tests** 
3. **All data generated fresh per test run**
4. **Test behavior via public interfaces (HTTP, API calls)**
5. **Mock all external dependencies**

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

## Galleria-Specific Fixtures

Galleria has its own comprehensive fixture ecosystem for serve command testing and general galleria development. These fixtures are duplicated for independence to support future extraction as a standalone package.

See: [Galleria Testing Fixtures Guide](modules/galleria/testing-fixtures.md)

**Key Galleria Fixtures:**
- `complete_serving_scenario` - End-to-end serve command scenarios
- `gallery_output_factory` - Realistic gallery structures with HTML/CSS/thumbnails  
- `manifest_factory` - Normpic manifests with customizable photo collections
- `free_port` - Dynamic port allocation for HTTP testing
- `file_watcher_scenario` - Hot reload and file watching test scenarios

**Usage Example:**
```python
def test_serve_command(complete_serving_scenario):
    scenario = complete_serving_scenario(num_photos=6, photos_per_page=3)
    # All components ready: config, manifest, output, port allocation
    assert scenario["num_pages"] == 2  # Calculated automatically
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

## Config Format Testing Patterns

**RULE: Always use flat config format in tests. Never hardcode nested format.**

### Correct Config Format in Tests

**✅ CORRECT - Flat format:**
```python
config_data = {
    "manifest_path": str(manifest_path),
    "output_dir": str(tmp_path / "output"),
    "thumbnail_size": 400,
    "theme": "minimal"
}
```

**❌ INCORRECT - Old nested format:**
```python
# NEVER USE THIS - causes test failures
config_data = {
    "input": {"manifest_path": str(manifest_path)},
    "output": {"directory": str(tmp_path / "output")},
    "pipeline": {...}
}
```

### Prevention Strategy

1. **Use config fixtures**: Always use `galleria_config_factory` fixture instead of hardcoding
2. **Review config examples**: Ensure all documentation shows flat format
3. **Test config loading**: Verify `GalleriaConfig.from_file()` works with your test config
4. **Follow TDD**: Write tests first using current config format, then implement

## Build Module Testing Patterns

The build module uses simplified testing patterns enabled by the orchestrator architecture.

### Orchestrator Testing Strategy

**Before (Complex Mocking):**
```python
@patch('cli.commands.build.organize')
@patch('cli.commands.build.JsonConfigLoader') 
@patch('cli.commands.build.PipelineManager')
@patch('cli.commands.build.pelican')
def test_build_complex(mock_pelican, mock_pipeline, mock_config, mock_organize):
    # Setup 4+ mocks with complex interactions
    mock_organize.return_value = Mock(exit_code=0)
    mock_config.return_value.load_config.side_effect = [config1, config2, config3]
    mock_pipeline.return_value.execute_stages.return_value = Mock(success=True)
    mock_pelican.Pelican.return_value = Mock()
```

**After (Simple Orchestrator Mocking):**
```python
@patch('cli.commands.build.organize')
@patch('cli.commands.build.BuildOrchestrator')
def test_build_simple(mock_orchestrator_class, mock_organize):
    # Mock only the orchestrator - much simpler
    mock_organize.return_value = Mock(exit_code=0)
    mock_orchestrator = Mock()
    mock_orchestrator_class.return_value = mock_orchestrator
    mock_orchestrator.execute.return_value = True
    
    result = runner.invoke(build)
    assert result.exit_code == 0
```

### Business Logic Testing

Each builder component can be tested independently:

**ConfigManager Testing:**
```python
def test_config_manager_loads_site_config(temp_filesystem, config_file_factory):
    config_manager = ConfigManager(temp_filesystem)
    config_file_factory("site.json", {"output_dir": "test"})
    
    config = config_manager.load_site_config()
    assert config["output_dir"] == "test"
```

**GalleriaBuilder Testing:**
```python
@patch('build.galleria_builder.PipelineManager')
def test_galleria_builder_success(mock_pipeline_manager):
    mock_pipeline = Mock()
    mock_pipeline_manager.return_value = mock_pipeline
    mock_pipeline.execute_stages.return_value = Mock(success=True)
    
    builder = GalleriaBuilder()
    success = builder.build(galleria_config)
    assert success is True
```

### Testing Benefits

**Reduced Complexity:**
- Test business logic classes directly instead of through CLI
- Mock 1 orchestrator instead of 4+ dependencies
- Clear separation between CLI and business logic testing

**Better Test Organization:**
- `test/unit/cli/` - Tests CLI command behavior (simple orchestrator mocking)
- `test/unit/build/` - Tests business logic classes (focused responsibility testing)
- `test/e2e/` - Tests complete workflow integration

**Maintainable Tests:**
- Changes to internal implementation don't break CLI tests
- Business logic tests focus on specific functionality
- Clear test boundaries match architectural boundaries

## HTTP Handler Testing Patterns

The site serve functionality includes HTTP request handling that requires special testing patterns.

### HTTP Handler Testing Strategy

HTTP handlers inherit from `BaseHTTPRequestHandler` which makes testing challenging. Use the `__new__` pattern to avoid constructor issues:

**✅ CORRECT - Using __new__ pattern:**
```python
def test_proxy_handler_routing():
    from cli.commands.serve import ProxyHTTPHandler
    
    # Create handler without calling constructor 
    handler = ProxyHTTPHandler.__new__(ProxyHTTPHandler)
    handler.path = "/galleries/wedding/page_1.html"
    handler.proxy = SiteServeProxy(8001, 8002, "/pics")
    
    # Mock methods that would send HTTP responses
    handler.forward_to_server = Mock()
    
    # Test the routing logic
    handler.do_GET()
    
    # Assert correct routing decision
    handler.forward_to_server.assert_called_once_with("127.0.0.1", 8001, "/galleries/wedding/page_1.html")
```

**❌ INCORRECT - Direct construction:**
```python
# This triggers HTTP request handling and fails
handler = ProxyHTTPHandler(request, address, server)  # Don't do this
```

### HTTP Request Forwarding Tests

Test request forwarding by mocking the HTTP client:

```python
@patch('cli.commands.serve.http.client.HTTPConnection')
def test_forward_to_server_makes_http_request(mock_http_connection):
    # Mock successful HTTP response
    mock_conn = Mock()
    mock_response = Mock()
    mock_response.status = 200
    mock_response.read.return_value = b"<html>Content</html>"
    
    mock_conn.getresponse.return_value = mock_response
    mock_http_connection.return_value = mock_conn
    
    handler = ProxyHTTPHandler.__new__(ProxyHTTPHandler)
    handler.send_response = Mock()
    handler.wfile = Mock()
    
    # Test request forwarding
    handler.forward_to_server("127.0.0.1", 8001, "/galleries/page_1.html")
    
    # Verify HTTP connection and response handling
    mock_http_connection.assert_called_once_with("127.0.0.1", 8001)
    mock_conn.request.assert_called_once_with("GET", "/galleries/page_1.html")
    handler.wfile.write.assert_called_once_with(b"<html>Content</html>")
```

### Static File Serving Tests

Mock filesystem operations for static file tests:

```python
@patch('cli.commands.serve.mimetypes.guess_type')
@patch('cli.commands.serve.Path')
def test_serve_static_file(mock_path_class, mock_guess_type):
    # Mock file operations
    mock_file_path = Mock()
    mock_file_path.exists.return_value = True
    mock_file_path.read_bytes.return_value = b"fake jpg data"
    
    # Mock Path constructor and division operator
    mock_path_instance = Mock()
    mock_path_instance.__truediv__ = Mock(return_value=mock_file_path)
    mock_path_class.return_value = mock_path_instance
    
    # Mock content type detection
    mock_guess_type.return_value = ("image/jpeg", None)
    
    handler = ProxyHTTPHandler.__new__(ProxyHTTPHandler)
    handler.send_response = Mock()
    handler.send_header = Mock()
    handler.wfile = Mock()
    
    # Test static file serving
    handler.serve_static_file("/path/to/pics", "/pics/full/photo1.jpg")
    
    # Verify correct response
    handler.send_response.assert_called_once_with(200)
    handler.send_header.assert_any_call("Content-Type", "image/jpeg")
    handler.wfile.write.assert_called_once_with(b"fake jpg data")
```

### Error Handling Tests

Test error conditions with appropriate mock exceptions:

```python
@patch('cli.commands.serve.http.client.HTTPConnection')
def test_forward_to_server_handles_connection_error(mock_http_connection):
    # Mock connection failure
    mock_http_connection.side_effect = OSError("Connection refused")
    
    handler = ProxyHTTPHandler.__new__(ProxyHTTPHandler)
    handler.send_error = Mock()
    
    # Test error handling
    handler.forward_to_server("127.0.0.1", 8001, "/galleries/page_1.html")
    
    # Verify 502 Bad Gateway response
    handler.send_error.assert_called_once_with(502, "Bad Gateway - Target server unreachable")
```

### Key HTTP Testing Principles

1. **Use `__new__` pattern** to avoid BaseHTTPRequestHandler constructor issues
2. **Mock HTTP responses** instead of making real network calls
3. **Mock filesystem operations** for static file tests  
4. **Test error conditions** with appropriate exception mocking
5. **Verify HTTP status codes and headers** are set correctly