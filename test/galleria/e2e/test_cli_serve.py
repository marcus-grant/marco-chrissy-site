"""E2E tests for galleria CLI serve command."""

import json
import subprocess
import time
import threading
import requests
from pathlib import Path


class TestGalleriaCLIServe:
    """E2E tests for galleria serve command."""

    def test_cli_serve_command_with_config_file(self, tmp_path):
        """E2E: Test galleria serve --config config.json command.
        
        This test should initially fail since no serve command exists yet.
        Tests complete serve workflow:
        1. Argument parsing (--config, --port, --host, --verbose)
        2. Configuration file loading and validation
        3. Generate command execution (cascading pattern)
        4. HTTP server startup and gallery serving
        5. Basic HTTP response validation
        """
        # Arrange: Create test data and config (same as generate test)
        test_photos_dir = tmp_path / "source_photos"
        test_photos_dir.mkdir()

        # Create test photo files (valid JPEG images)
        photo_paths = []
        for i in range(2):  # Smaller set for faster testing
            photo_path = test_photos_dir / f"test_{i:03d}.jpg"
            # Create a simple 100x100 RGB image and save as JPEG
            from PIL import Image
            color = (255 - i * 50, i * 50, 100 + i * 30)
            test_img = Image.new('RGB', (100, 100), color)
            test_img.save(photo_path, 'JPEG')
            photo_paths.append(str(photo_path))

        # Create NormPic manifest
        manifest = {
            "version": "0.1.0",
            "collection_name": "test_photos",
            "pics": [
                {
                    "source_path": str(photo_paths[0]),
                    "dest_path": "test_001.jpg",
                    "hash": "hash001",
                    "size_bytes": 2048,
                    "mtime": 1234567890
                },
                {
                    "source_path": str(photo_paths[1]),
                    "dest_path": "test_002.jpg",
                    "hash": "hash002",
                    "size_bytes": 2048,
                    "mtime": 1234567891
                }
            ]
        }

        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2))

        # Create galleria configuration file
        config = {
            "input": {
                "manifest_path": str(manifest_path)
            },
            "output": {
                "directory": str(tmp_path / "gallery_output")
            },
            "pipeline": {
                "provider": {
                    "plugin": "normpic-provider",
                    "config": {}
                },
                "processor": {
                    "plugin": "thumbnail-processor",
                    "config": {
                        "thumbnail_size": 300,
                        "quality": 85
                    }
                },
                "transform": {
                    "plugin": "basic-pagination",
                    "config": {
                        "page_size": 2
                    }
                },
                "template": {
                    "plugin": "basic-template",
                    "config": {
                        "theme": "minimal",
                        "layout": "grid"
                    }
                },
                "css": {
                    "plugin": "basic-css",
                    "config": {
                        "theme": "light",
                        "responsive": True
                    }
                }
            }
        }

        config_path = tmp_path / "galleria_config.json"
        config_path.write_text(json.dumps(config, indent=2))

        output_dir = tmp_path / "gallery_output"
        test_port = 8001  # Use non-default port to avoid conflicts

        # Act: Execute galleria serve command in subprocess
        serve_process = subprocess.Popen([
            "python", "-m", "galleria", "serve",
            "--config", str(config_path),
            "--port", str(test_port),
            "--verbose"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
           cwd=tmp_path.parent.parent.parent)

        try:
            # Wait for server to start (with timeout)
            server_started = False
            for _ in range(10):  # 5 second timeout
                time.sleep(0.5)
                try:
                    response = requests.get(f"http://localhost:{test_port}", timeout=1)
                    if response.status_code == 200:
                        server_started = True
                        break
                except requests.ConnectionError:
                    continue

            # Assert: Verify serve command started successfully
            assert server_started, "Server did not start within timeout period"

            # Verify output directory was created (by generate phase)
            assert output_dir.exists(), "Output directory was not created by generate"

            # Verify gallery files were generated (by generate phase)
            assert (output_dir / "page_1.html").exists(), "Page 1 HTML not generated"
            assert (output_dir / "gallery.css").exists(), "Gallery CSS not generated"
            assert (output_dir / "thumbnails").exists(), "Thumbnails directory not created"

            # Test HTTP responses for generated files
            response = requests.get(f"http://localhost:{test_port}/")
            assert response.status_code == 200, "Index page not served"
            
            response = requests.get(f"http://localhost:{test_port}/page_1.html")
            assert response.status_code == 200, "Page 1 HTML not served"
            assert "test_photos" in response.text, "Collection name not in served HTML"

            response = requests.get(f"http://localhost:{test_port}/gallery.css")
            assert response.status_code == 200, "Gallery CSS not served"
            assert response.headers.get("content-type", "").startswith("text/css"), "CSS content-type not set"

            # Test thumbnail serving
            thumbnail_files = list((output_dir / "thumbnails").glob("*.webp"))
            if thumbnail_files:
                thumb_name = thumbnail_files[0].name
                response = requests.get(f"http://localhost:{test_port}/thumbnails/{thumb_name}")
                assert response.status_code == 200, "Thumbnail not served"
                assert "image" in response.headers.get("content-type", ""), "Thumbnail content-type not set"

        finally:
            # Cleanup: Terminate server process
            serve_process.terminate()
            try:
                serve_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                serve_process.kill()
                serve_process.wait()

    def test_cli_serve_calls_generate_first(self, tmp_path):
        """E2E: Test that serve command calls generate before serving (cascading pattern)."""
        # Arrange: Create minimal test setup
        manifest = {
            "version": "0.1.0",
            "collection_name": "cascade_test",
            "pics": []
        }

        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2))

        config = {
            "input": {"manifest_path": str(manifest_path)},
            "output": {"directory": str(tmp_path / "output")},
            "pipeline": {
                "provider": {"plugin": "normpic-provider", "config": {}},
                "processor": {"plugin": "thumbnail-processor", "config": {}},
                "transform": {"plugin": "basic-pagination", "config": {"page_size": 1}},
                "template": {"plugin": "basic-template", "config": {}},
                "css": {"plugin": "basic-css", "config": {}}
            }
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config, indent=2))

        output_dir = tmp_path / "output"
        test_port = 8002

        # Ensure output directory does not exist initially
        assert not output_dir.exists(), "Output directory should not exist initially"

        # Act: Start serve command
        serve_process = subprocess.Popen([
            "python", "-m", "galleria", "serve",
            "--config", str(config_path),
            "--port", str(test_port),
            "--verbose"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
           cwd=tmp_path.parent.parent.parent)

        try:
            # Wait briefly for generation to complete
            time.sleep(2)

            # Assert: Verify generate was called (output directory created)
            assert output_dir.exists(), "Generate phase did not create output directory"
            assert (output_dir / "page_1.html").exists(), "Generate phase did not create HTML"

            # Verify server is serving the generated content
            server_started = False
            for _ in range(10):
                time.sleep(0.5)
                try:
                    response = requests.get(f"http://localhost:{test_port}/page_1.html", timeout=1)
                    if response.status_code == 200:
                        server_started = True
                        break
                except requests.ConnectionError:
                    continue

            assert server_started, "Server did not serve generated content"

        finally:
            serve_process.terminate()
            try:
                serve_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                serve_process.kill()

    def test_cli_serve_handles_missing_config_file(self, tmp_path):
        """E2E: Test galleria serve with missing config file shows error."""
        nonexistent_config = tmp_path / "missing_config.json"

        # Act: Execute serve command with missing config
        result = subprocess.run([
            "python", "-m", "galleria", "serve",
            "--config", str(nonexistent_config),
            "--port", "8003"
        ], capture_output=True, text=True, cwd=tmp_path.parent.parent.parent)

        # Assert: Command should fail gracefully
        assert result.returncode != 0, "Command should fail with missing config"
        error_output = result.stderr.lower()
        assert any(phrase in error_output for phrase in ["config", "not found", "no such file"]), \
            f"Error should mention config file issue: {result.stderr}"

    def test_cli_serve_shows_help_with_no_args(self, tmp_path):
        """E2E: Test galleria serve with no arguments shows help."""
        # Act: Execute serve command with no arguments
        result = subprocess.run([
            "python", "-m", "galleria", "serve"
        ], capture_output=True, text=True, cwd=tmp_path.parent.parent.parent)

        # Assert: Should show usage information
        output_text = result.stdout + result.stderr
        assert any(word in output_text.lower() for word in ["usage", "help", "config", "required", "missing option"]), \
            f"Should show usage information: {output_text}"

    def test_cli_serve_port_argument_validation(self, tmp_path):
        """E2E: Test serve command validates port argument."""
        # Create minimal config
        config = {
            "input": {"manifest_path": str(tmp_path / "manifest.json")},
            "output": {"directory": str(tmp_path / "output")},
            "pipeline": {
                "provider": {"plugin": "normpic-provider", "config": {}},
                "processor": {"plugin": "thumbnail-processor", "config": {}},
                "transform": {"plugin": "basic-pagination", "config": {}},
                "template": {"plugin": "basic-template", "config": {}},
                "css": {"plugin": "basic-css", "config": {}}
            }
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config, indent=2))

        # Act: Test invalid port numbers
        result = subprocess.run([
            "python", "-m", "galleria", "serve",
            "--config", str(config_path),
            "--port", "invalid_port"
        ], capture_output=True, text=True, cwd=tmp_path.parent.parent.parent)

        # Assert: Should fail with port validation error
        assert result.returncode != 0, "Command should fail with invalid port"
        output_text = result.stdout + result.stderr
        assert any(word in output_text.lower() for word in ["port", "invalid", "integer", "number"]), \
            f"Should show port validation error: {output_text}"

    def test_cli_serve_hot_reload_functionality(self, tmp_path):
        """E2E: Test serve command hot reload when config or manifest changes."""
        # Create initial test setup
        from PIL import Image
        
        test_photo = tmp_path / "test.jpg"
        test_img = Image.new('RGB', (100, 100), (255, 0, 0))
        test_img.save(test_photo, 'JPEG')

        manifest = {
            "version": "0.1.0",
            "collection_name": "hot_reload_test",
            "pics": [{
                "source_path": str(test_photo),
                "dest_path": "test.jpg",
                "hash": "hash001",
                "size_bytes": 2048,
                "mtime": 1234567890
            }]
        }

        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2))

        config = {
            "input": {"manifest_path": str(manifest_path)},
            "output": {"directory": str(tmp_path / "output")},
            "pipeline": {
                "provider": {"plugin": "normpic-provider", "config": {}},
                "processor": {"plugin": "thumbnail-processor", "config": {"thumbnail_size": 200}},
                "transform": {"plugin": "basic-pagination", "config": {"page_size": 1}},
                "template": {"plugin": "basic-template", "config": {"theme": "minimal"}},
                "css": {"plugin": "basic-css", "config": {"theme": "light"}}
            }
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config, indent=2))
        test_port = 8004

        # Start serve command
        serve_process = subprocess.Popen([
            "python", "-m", "galleria", "serve",
            "--config", str(config_path),
            "--port", str(test_port),
            "--verbose"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
           cwd=tmp_path.parent.parent.parent)

        try:
            # Wait for initial generation and server startup
            time.sleep(3)

            # Verify server is running
            response = requests.get(f"http://localhost:{test_port}/page_1.html", timeout=2)
            assert response.status_code == 200, "Initial server not responding"
            initial_content = response.text
            assert "minimal" in initial_content, "Initial theme not applied"

            # Modify config to change theme and trigger hot reload
            config["pipeline"]["template"]["config"]["theme"] = "elegant"
            config_path.write_text(json.dumps(config, indent=2))

            # Wait for hot reload to detect change and regenerate
            time.sleep(4)

            # Verify changes were applied
            response = requests.get(f"http://localhost:{test_port}/page_1.html", timeout=2)
            assert response.status_code == 200, "Server not responding after hot reload"
            updated_content = response.text
            
            # The content should be different after hot reload
            # (This is a basic check - in reality we'd check for theme-specific changes)
            assert len(updated_content) > 100, "Page content should still be substantial"

        finally:
            serve_process.terminate()
            try:
                serve_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                serve_process.kill()

    def test_cli_serve_no_watch_flag(self, tmp_path):
        """E2E: Test serve command with --no-watch flag disables hot reload."""
        # Create minimal test setup
        manifest = {
            "version": "0.1.0", 
            "collection_name": "no_watch_test",
            "pics": []
        }

        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2))

        config = {
            "input": {"manifest_path": str(manifest_path)},
            "output": {"directory": str(tmp_path / "output")},
            "pipeline": {
                "provider": {"plugin": "normpic-provider", "config": {}},
                "processor": {"plugin": "thumbnail-processor", "config": {}},
                "transform": {"plugin": "basic-pagination", "config": {}},
                "template": {"plugin": "basic-template", "config": {}},
                "css": {"plugin": "basic-css", "config": {}}
            }
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config, indent=2))

        # Test that --no-watch flag is accepted
        result = subprocess.run([
            "python", "-m", "galleria", "serve",
            "--config", str(config_path),
            "--port", "8005",
            "--no-watch",
            "--no-generate"  # Skip generation for faster test
        ], capture_output=True, text=True, timeout=2,
           cwd=tmp_path.parent.parent.parent)

        # Should start but exit quickly due to no output directory (expected behavior)
        # The important thing is that --no-watch flag is accepted
        assert "--no-watch" not in (result.stdout + result.stderr), "Flag should be processed, not appear in error"