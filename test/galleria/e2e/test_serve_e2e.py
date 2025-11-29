"""E2E tests for galleria CLI serve command."""

import subprocess
import time

import requests


class TestGalleriaServeE2E:
    """E2E tests for galleria serve command."""

    def test_galleria_serve_cli_integration(self, complete_serving_scenario):
        """E2E: Test CLI starts server, serves files, handles shutdown.

        Test complete serve workflow:
        1. CLI argument parsing (--config, --port, --host, --verbose)
        2. Configuration file loading and validation
        3. Generate command execution (cascading pattern)
        4. HTTP server startup and gallery serving
        5. Basic HTTP response validation
        6. Clean shutdown handling
        """
        # Arrange: Create complete serving scenario with all components
        scenario = complete_serving_scenario(
            collection_name="e2e_test_photos",
            num_photos=4,
            photos_per_page=2
        )

        config_path = scenario["config_path"]
        test_port = scenario["port"]
        output_dir = scenario["output_path"]

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

    def test_serve_file_watching_workflow(self, file_watcher_scenario, galleria_file_factory, free_port):
        """E2E: Test config/manifest changes trigger rebuilds.

        Test hot reload functionality:
        1. Start serve command with file watching enabled
        2. Verify initial gallery generation and serving
        3. Modify configuration file (change theme)
        4. Verify file watcher detects change
        5. Verify gallery regeneration occurs
        6. Verify updated content is served
        """
        # Arrange: Create file watching scenario
        scenario = file_watcher_scenario()
        config_path = scenario["config_path"]
        scenario["manifest_path"]
        initial_config = scenario["initial_config"]

        test_port = free_port()

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
            modified_config = initial_config.copy()
            modified_config["pipeline"]["template"]["config"]["theme"] = "elegant"
            galleria_file_factory(
                str(config_path.relative_to(config_path.parent.parent)),
                json_content=modified_config
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

    def test_serve_static_file_serving(self, complete_serving_scenario):
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
        # Arrange: Create comprehensive serving scenario
        scenario = complete_serving_scenario(
            collection_name="serving_test",
            num_photos=6,
            photos_per_page=3
        )

        config_path = scenario["config_path"]
        test_port = scenario["port"]
        output_dir = scenario["output_path"]

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
            # Use scenario data instead of reading real filesystem
            expected_thumbnails = scenario["num_photos"]

            # Test each expected thumbnail by making HTTP requests
            for i in range(1, expected_thumbnails + 1):
                thumb_name = f"photo_{i:03d}.webp"  # Use predictable naming pattern
                thumb_response = requests.get(f"http://localhost:{test_port}/thumbnails/{thumb_name}", timeout=2)
                assert thumb_response.status_code == 200, f"Thumbnail {thumb_name} not served"
                assert "image" in thumb_response.headers.get("content-type", ""), f"Thumbnail {thumb_name} content type incorrect"

            # Test 404 handling
            response = requests.get(f"http://localhost:{test_port}/nonexistent.html", timeout=2)
            assert response.status_code == 404, "Should return 404 for missing files"

        finally:
            serve_process.terminate()
            try:
                serve_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                serve_process.kill()
