# Galleria Test Fixtures Guide

## Overview

Galleria has a comprehensive test fixture ecosystem designed for serve command testing and general galleria development. These fixtures are duplicated from the main project fixtures to ensure galleria's independence and support future extraction as a standalone package.

## Fixture Location

All galleria-specific fixtures are defined in:
```
test/galleria/conftest.py
```

## Core Fixtures

### Filesystem Management

**`galleria_temp_filesystem`** - Isolated temporary directory:
```python
def test_with_filesystem(galleria_temp_filesystem):
    assert galleria_temp_filesystem.exists()
    # Path object for galleria-specific testing
```

**`galleria_file_factory`** - Create files with content:
```python
def test_file_creation(galleria_file_factory):
    # Text file
    path = galleria_file_factory("test.txt", content="Hello galleria")
    
    # JSON file
    path = galleria_file_factory("config.json", json_content={"key": "value"})
```

**`galleria_image_factory`** - Create fake images for testing:
```python
def test_image_generation(galleria_image_factory):
    # Basic image
    image_path = galleria_image_factory("test.jpg")
    
    # Custom image with color and size
    image_path = galleria_image_factory(
        "custom.jpg",
        directory="photos",
        color=(255, 128, 0),  # RGB tuple or color name
        size=(1200, 800)
    )
```

### Configuration Management

**`galleria_config_factory`** - Galleria config files with defaults:
```python
def test_config_creation(galleria_config_factory):
    # Default galleria config
    config_path = galleria_config_factory()
    
    # Custom configuration
    custom_config = {
        "manifest_path": "custom.json",
        "pipeline": {
            "processor": {"plugin": "thumbnail-processor", "config": {"thumbnail_size": 300}}
        }
    }
    config_path = galleria_config_factory("custom", custom_config)
```

**Default Config Structure:**
```json
{
  "manifest_path": "manifest.json",
  "output_dir": "gallery_output",
  "pipeline": {
    "provider": {"plugin": "normpic-provider", "config": {}},
    "processor": {"plugin": "thumbnail-processor", "config": {"thumbnail_size": 200}},
    "transform": {"plugin": "basic-pagination", "config": {"page_size": 10}},
    "template": {"plugin": "basic-template", "config": {"theme": "minimal"}},
    "css": {"plugin": "basic-css", "config": {"theme": "light"}}
  }
}
```

## Data Factory Fixtures

### Manifest Creation

**`manifest_factory`** - Create normpic manifests:
```python
def test_manifest_creation(manifest_factory):
    # Default manifest with 2 photos
    manifest_path = manifest_factory()
    
    # Custom collection with specific photos
    photos = [
        {
            "source_path": "photo1.jpg",
            "dest_path": "img1.jpg",
            "hash": "abc123",
            "size_bytes": 1000000,
            "mtime": 1234567890
        }
    ]
    manifest_path = manifest_factory(
        collection_name="wedding_photos",
        photos=photos,
        filename="custom_manifest.json"
    )
```

### Gallery Output Creation

**`gallery_output_factory`** - Create realistic gallery directory structures:
```python
def test_gallery_output(gallery_output_factory):
    # Basic gallery with 2 pages, 2 photos per page
    output_path = gallery_output_factory()
    
    # Custom gallery structure
    output_path = gallery_output_factory(
        output_dir="custom_gallery",
        collection_name="vacation_photos",
        num_pages=3,
        photos_per_page=4,
        include_css=True,
        include_thumbnails=True
    )
    
    # Verify structure
    assert (output_path / "page_1.html").exists()
    assert (output_path / "gallery.css").exists()
    assert (output_path / "thumbnails").exists()
```

**Generated Structure:**
- HTML pages with realistic pagination and navigation
- CSS files with grid layouts and responsive design  
- Thumbnail images with visual variety (different colors)
- Proper cross-references between pages and assets

## HTTP Testing Fixtures

### Port Management

**`free_port`** - Allocate available ports:
```python
def test_server_startup(free_port):
    port = free_port()
    # Start server on dynamically allocated port
    server = start_test_server(port)
    assert server.is_running
```

**`mock_http_server`** - Mock server with request tracking:
```python
def test_http_requests(mock_http_server):
    server = mock_http_server(port=8080)
    
    # Mock requests
    server.handle_request("/test", "GET")
    
    # Verify tracking
    assert len(server.requests) == 1
    assert server.requests[0]["path"] == "/test"
```

## Complete Scenario Fixtures

### End-to-End Testing

**`complete_serving_scenario`** - Full serve command scenarios:
```python
def test_serve_workflow(complete_serving_scenario):
    scenario = complete_serving_scenario(
        collection_name="wedding_photos",
        num_photos=6,
        photos_per_page=3
    )
    
    # All components ready for testing
    assert scenario["config_path"].exists()
    assert scenario["manifest_path"].exists()
    assert scenario["output_path"].exists()
    assert len(scenario["source_photos"]) == 6
    assert scenario["num_pages"] == 2  # 6 photos, 3 per page = 2 pages
    
    # Use in serve command testing
    port = scenario["port"]
    config_path = scenario["config_path"]
```

**Scenario Components:**
- Source images with realistic metadata
- Normpic manifest with photo collection
- Galleria configuration file
- Generated gallery output structure
- Allocated port for HTTP testing
- Calculated pagination and metadata

### File Watching Testing

**`file_watcher_scenario`** - Files for hot reload testing:
```python
def test_file_watching(file_watcher_scenario, galleria_file_factory):
    scenario = file_watcher_scenario()
    
    # Initial files created
    config_path = scenario["config_path"]
    manifest_path = scenario["manifest_path"]
    
    # Modify config to trigger hot reload
    modified_config = scenario["initial_config"].copy()
    modified_config["pipeline"]["template"]["config"]["theme"] = "elegant"
    
    galleria_file_factory(
        str(config_path.relative_to(config_path.parent.parent)),
        json_content=modified_config
    )
    
    # Test file watcher detects changes
```

## Usage Examples

### Basic Test Setup

```python
def test_simple_gallery(complete_serving_scenario):
    """Test with minimal setup."""
    scenario = complete_serving_scenario(num_photos=2, photos_per_page=2)
    
    # Ready to test serve functionality
    assert scenario["num_pages"] == 1
    assert len(scenario["source_photos"]) == 2
```

### Custom Test Data

```python
def test_large_gallery(
    manifest_factory, 
    galleria_config_factory, 
    gallery_output_factory
):
    """Test with custom data creation."""
    # Create large photo collection
    photos = []
    for i in range(50):
        photos.append({
            "source_path": f"photo_{i:03d}.jpg",
            "dest_path": f"img_{i:03d}.jpg", 
            "hash": f"hash{i:03d}",
            "size_bytes": 2000000 + i * 1000,
            "mtime": 1234567890 + i
        })
    
    manifest_path = manifest_factory("large_collection", photos)
    config_path = galleria_config_factory()
    output_path = gallery_output_factory(num_pages=10, photos_per_page=5)
    
    # Test with large dataset
```

### HTTP Server Testing

```python
def test_server_integration(complete_serving_scenario):
    """Test HTTP server with realistic data."""
    scenario = complete_serving_scenario(num_photos=4, photos_per_page=2)
    
    # Start server on allocated port
    server = GalleriaHTTPServer(scenario["output_path"], port=scenario["port"])
    
    with server:
        # Test HTTP requests
        response = requests.get(f"http://localhost:{scenario['port']}/")
        assert response.status_code == 200
```

## Benefits

### Independence
- Galleria fixtures are completely independent of parent project
- Ready for extraction as standalone galleria package
- No dependencies on site-level fixtures

### Comprehensive Coverage
- Realistic test data with proper relationships
- Complete end-to-end scenarios
- HTTP testing infrastructure
- File watching simulation

### Developer Experience
- Simplified test setup (from ~40 lines to ~4 lines)
- Consistent test data across tests
- Easy customization for specific test needs
- Clear separation between test concerns

### Maintainability
- Fixtures handle complex setup logic
- Tests focus on behavior rather than setup
- Centralized test data management
- Easy to extend for new testing scenarios

## Migration from Old Fixtures

**Before (Manual Setup):**
```python
def test_old_way(temp_filesystem, fake_image_factory, file_factory, config_file_factory):
    # 40+ lines of manual setup
    photos = []
    for i in range(4):
        photo_path = fake_image_factory(f"img_{i}.jpg", "source", (255-i*50, i*50, 100))
        photos.append({"source_path": str(photo_path), ...})
    
    manifest_data = {"version": "0.1.0", "collection_name": "test", "pics": photos}
    manifest_path = file_factory("manifest.json", json_content=manifest_data)
    
    config_content = {"manifest_path": str(manifest_path), ...}
    config_path = config_file_factory("galleria", config_content)
    # ... more setup
```

**After (Fixture-Based):**
```python
def test_new_way(complete_serving_scenario):
    # 4 lines of setup
    scenario = complete_serving_scenario(
        collection_name="test",
        num_photos=4,
        photos_per_page=2
    )
    # Everything ready for testing
```

This fixture ecosystem enables comprehensive testing of galleria serve functionality while maintaining clean, readable test code.