"""E2E tests for galleria CLI serve command."""

import subprocess
import time

import pytest
import requests


class TestGalleriaServeE2E:
    """E2E tests for galleria serve command."""

    @pytest.mark.skip("Implementation not ready - orchestrator pattern not yet built")
    def test_galleria_serve_cli_integration(
        self,
        temp_filesystem,
        fake_image_factory,
        config_file_factory,
        file_factory
    ):
        """E2E: Test CLI starts server, serves files, handles shutdown.

        Test complete serve workflow:
        1. CLI argument parsing (--config, --port, --host, --verbose)
        2. Configuration file loading and validation
        3. Generate command execution (cascading pattern)
        4. HTTP server startup and gallery serving
        5. Basic HTTP response validation
        6. Clean shutdown handling
        """
        # Arrange: Create test photos using fake_image_factory
        test_photos = []
        for i in range(2):  # Small set for faster testing
            photo_path = fake_image_factory(
                f"test_{i:03d}.jpg",
                directory="source_photos",
                color=(255 - i * 50, i * 50, 100 + i * 30),
                size=(200, 150)
            )
            test_photos.append(str(photo_path))

        # Create NormPic manifest using file_factory
        manifest_data = {
            "version": "0.1.0",
            "collection_name": "test_photos",
            "pics": [
                {
                    "source_path": test_photos[0],
                    "dest_path": "test_001.jpg",
                    "hash": "hash001",
                    "size_bytes": 2048,
                    "mtime": 1234567890
                },
                {
                    "source_path": test_photos[1],
                    "dest_path": "test_002.jpg",
                    "hash": "hash002",
                    "size_bytes": 2048,
                    "mtime": 1234567891
                }
            ]
        }
        manifest_path = file_factory("manifest.json", json_content=manifest_data)

        # Create galleria config using config_file_factory with custom overrides
        galleria_config_content = {
            "input": {"manifest_path": str(manifest_path)},
            "output": {"directory": str(temp_filesystem / "gallery_output")},
            "pipeline": {
                "provider": {"plugin": "normpic-provider", "config": {}},
                "processor": {"plugin": "thumbnail-processor", "config": {"thumbnail_size": 200}},
                "transform": {"plugin": "basic-pagination", "config": {"page_size": 2}},
                "template": {"plugin": "basic-template", "config": {"theme": "minimal"}},
                "css": {"plugin": "basic-css", "config": {"theme": "light"}}
            }
        }
        config_path = config_file_factory("galleria", galleria_config_content)

        test_port = 8001
        output_dir = temp_filesystem / "gallery_output"

        # Act: Execute galleria serve command in subprocess
        serve_process = subprocess.Popen([
            "python", "-m", "galleria", "serve",
            "--config", str(config_path),
            "--port", str(test_port),
            "--verbose"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        try:
            # Wait for server to start with timeout
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
            assert output_dir.exists(), "Output directory was not created by generate"
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

        finally:
            # Cleanup: Terminate server process
            serve_process.terminate()
            try:
                serve_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                serve_process.kill()
                serve_process.wait()

    @pytest.mark.skip("Implementation not ready - file watcher not yet built")
    def test_serve_file_watching_workflow(
        self,
        temp_filesystem,
        fake_image_factory,
        config_file_factory,
        file_factory
    ):
        """E2E: Test config/manifest changes trigger rebuilds.

        Test hot reload functionality:
        1. Start serve command with file watching enabled
        2. Verify initial gallery generation and serving
        3. Modify configuration file (change theme)
        4. Verify file watcher detects change
        5. Verify gallery regeneration occurs
        6. Verify updated content is served
        """
        # Arrange: Create test photo
        photo_path = fake_image_factory(
            "test.jpg",
            directory="source_photos",
            color="blue",
            size=(100, 100)
        )

        # Create manifest
        manifest_data = {
            "version": "0.1.0",
            "collection_name": "watch_test",
            "pics": [{
                "source_path": str(photo_path),
                "dest_path": "test.jpg",
                "hash": "hash001",
                "size_bytes": 2048,
                "mtime": 1234567890
            }]
        }
        manifest_path = file_factory("manifest.json", json_content=manifest_data)

        # Create initial config with "minimal" theme
        config_content = {
            "input": {"manifest_path": str(manifest_path)},
            "output": {"directory": str(temp_filesystem / "output")},
            "pipeline": {
                "provider": {"plugin": "normpic-provider", "config": {}},
                "processor": {"plugin": "thumbnail-processor", "config": {"thumbnail_size": 200}},
                "transform": {"plugin": "basic-pagination", "config": {"page_size": 1}},
                "template": {"plugin": "basic-template", "config": {"theme": "minimal"}},
                "css": {"plugin": "basic-css", "config": {"theme": "light"}}
            }
        }
        config_path = config_file_factory("galleria", config_content)
        test_port = 8002

        # Act: Start serve command with watching enabled
        serve_process = subprocess.Popen([
            "python", "-m", "galleria", "serve",
            "--config", str(config_path),
            "--port", str(test_port),
            "--verbose"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        try:
            # Wait for initial server startup and generation
            time.sleep(3)

            # Verify initial content
            response = requests.get(f"http://localhost:{test_port}/page_1.html", timeout=2)
            assert response.status_code == 200, "Initial server not responding"
            initial_content = response.text
            assert "minimal" in initial_content, "Initial theme not applied"

            # Modify config to change theme (trigger hot reload)
            config_content["pipeline"]["template"]["config"]["theme"] = "elegant"
            file_factory(
                "config/galleria.json",
                json_content=config_content
            )

            # Wait for hot reload to detect change and regenerate
            time.sleep(4)

            # Verify updated content is served
            response = requests.get(f"http://localhost:{test_port}/page_1.html", timeout=2)
            assert response.status_code == 200, "Server not responding after hot reload"
            updated_content = response.text

            # Content should be different after hot reload
            assert len(updated_content) > 100, "Page content should still be substantial"

        finally:
            serve_process.terminate()
            try:
                serve_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                serve_process.kill()

    @pytest.mark.skip("Implementation not ready - HTTP server not yet built")
    def test_serve_static_file_serving(
        self,
        temp_filesystem,
        fake_image_factory,
        config_file_factory,
        file_factory
    ):
        """E2E: Test HTTP requests return correct gallery files.

        Test static file serving functionality:
        1. Generate gallery with multiple photos and pages
        2. Start serve command
        3. Test serving of HTML pages with correct content-type
        4. Test serving of CSS files with correct content-type
        5. Test serving of thumbnail images with correct content-type
        6. Test root path redirect to page_1.html
        7. Test 404 handling for missing files
        """
        # Arrange: Create multiple test photos for comprehensive test
        test_photos = []
        for i in range(3):
            photo_path = fake_image_factory(
                f"photo_{i:03d}.jpg",
                directory="photos",
                color=(255 - i * 60, i * 80, 100 + i * 40),
                size=(300, 200)
            )
            test_photos.append(str(photo_path))

        # Create manifest with multiple photos
        manifest_data = {
            "version": "0.1.0",
            "collection_name": "serving_test",
            "pics": [
                {"source_path": test_photos[0], "dest_path": "photo_001.jpg", "hash": "h001", "size_bytes": 4096, "mtime": 1000000},
                {"source_path": test_photos[1], "dest_path": "photo_002.jpg", "hash": "h002", "size_bytes": 4096, "mtime": 1000001},
                {"source_path": test_photos[2], "dest_path": "photo_003.jpg", "hash": "h003", "size_bytes": 4096, "mtime": 1000002}
            ]
        }
        manifest_path = file_factory("manifest.json", json_content=manifest_data)

        # Create config with pagination to generate multiple pages
        config_content = {
            "input": {"manifest_path": str(manifest_path)},
            "output": {"directory": str(temp_filesystem / "output")},
            "pipeline": {
                "provider": {"plugin": "normpic-provider", "config": {}},
                "processor": {"plugin": "thumbnail-processor", "config": {"thumbnail_size": 150}},
                "transform": {"plugin": "basic-pagination", "config": {"page_size": 2}},
                "template": {"plugin": "basic-template", "config": {"theme": "elegant"}},
                "css": {"plugin": "basic-css", "config": {"theme": "dark"}}
            }
        }
        config_path = config_file_factory("galleria", config_content)
        test_port = 8003

        # Act: Start serve command
        serve_process = subprocess.Popen([
            "python", "-m", "galleria", "serve",
            "--config", str(config_path),
            "--port", str(test_port),
            "--verbose"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        try:
            # Wait for complete startup
            time.sleep(4)

            # Assert: Test various file serving scenarios
            output_dir = temp_filesystem / "output"
            assert output_dir.exists(), "Output directory not created"
            assert (output_dir / "page_1.html").exists(), "Page 1 not generated"
            assert (output_dir / "page_2.html").exists(), "Page 2 not generated"
            assert (output_dir / "gallery.css").exists(), "Gallery CSS not generated"
            assert (output_dir / "thumbnails").exists(), "Thumbnails directory not created"

            # Test root redirect to page_1.html
            response = requests.get(f"http://localhost:{test_port}/", timeout=2)
            assert response.status_code == 200, "Root redirect failed"

            # Test HTML serving with correct content-type
            response = requests.get(f"http://localhost:{test_port}/page_1.html", timeout=2)
            assert response.status_code == 200, "Page 1 not served"
            assert "serving_test" in response.text, "Collection name missing"

            response = requests.get(f"http://localhost:{test_port}/page_2.html", timeout=2)
            assert response.status_code == 200, "Page 2 not served"

            # Test CSS serving with correct content-type
            response = requests.get(f"http://localhost:{test_port}/gallery.css", timeout=2)
            assert response.status_code == 200, "CSS not served"
            assert "text/css" in response.headers.get("content-type", ""), "CSS content type incorrect"

            # Test thumbnail serving with correct content-type
            thumbnails = list((output_dir / "thumbnails").glob("*.webp"))
            assert len(thumbnails) == 3, f"Expected 3 thumbnails, found {len(thumbnails)}"

            for thumb in thumbnails:
                thumb_response = requests.get(f"http://localhost:{test_port}/thumbnails/{thumb.name}", timeout=2)
                assert thumb_response.status_code == 200, f"Thumbnail {thumb.name} not served"
                assert "image" in thumb_response.headers.get("content-type", ""), "Thumbnail content type incorrect"

            # Test 404 handling
            response = requests.get(f"http://localhost:{test_port}/nonexistent.html", timeout=2)
            assert response.status_code == 404, "Should return 404 for missing files"

        finally:
            serve_process.terminate()
            try:
                serve_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                serve_process.kill()
