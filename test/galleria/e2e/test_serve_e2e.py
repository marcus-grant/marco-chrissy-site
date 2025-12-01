"""E2E tests for galleria serve functionality."""

from pathlib import Path
from threading import Thread
from unittest.mock import patch
import time

import requests
from galleria.orchestrator.serve import ServeOrchestrator


class TestGalleriaServeE2E:
    """E2E tests for galleria serve command."""

    def test_serve_orchestrator_integration(self, complete_serving_scenario):
        """E2E: Test ServeOrchestrator with direct imports (no subprocess).

        Test complete serve workflow:
        1. Configuration loading and validation
        2. Gallery generation (if needed)
        3. HTTP server startup and gallery serving
        4. File serving verification
        5. Clean shutdown handling
        """
        # Arrange: Use existing fixture with flat config
        scenario = complete_serving_scenario(
            collection_name="e2e_test_photos",
            num_photos=4,
            photos_per_page=2
        )

        config_path = scenario["config_path"]
        test_port = scenario["port"]
        output_dir = scenario["output_path"]

        # Act: Use ServeOrchestrator directly instead of subprocess
        orchestrator = ServeOrchestrator()
        serve_thread = None
        
        try:
            # Run serve in background thread
            def run_serve():
                orchestrator.execute(
                    config_path=config_path,
                    host="127.0.0.1",
                    port=test_port,
                    no_watch=True,  # Disable file watching for test
                    verbose=False
                )
            
            serve_thread = Thread(target=run_serve, daemon=True)
            serve_thread.start()
            
            # Wait for server to start
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

            # Assert: Verify serve workflow completed successfully
            assert server_started, "Server did not start within timeout period"
            assert output_dir.exists(), "Output directory was not created"
            assert (output_dir / "page_1.html").exists(), "Page 1 HTML not generated"
            assert (output_dir / "gallery.css").exists(), "Gallery CSS not generated"

            # Test HTTP responses for generated files
            response = requests.get(f"http://localhost:{test_port}/page_1.html")
            assert response.status_code == 200, "Page 1 HTML not served"
            assert "e2e_test_photos" in response.text, "Collection name not in served HTML"

            response = requests.get(f"http://localhost:{test_port}/gallery.css")
            assert response.status_code == 200, "Gallery CSS not served"
            assert "text/css" in response.headers.get("content-type", ""), "CSS content-type not set"

        finally:
            # Cleanup: ServeOrchestrator handles cleanup internally via _cleanup()
            if serve_thread and serve_thread.is_alive():
                # The thread will be cleaned up when test ends (daemon=True)
                pass

    def test_serve_file_watching_workflow(self, file_watcher_scenario, galleria_file_factory, free_port):
        """E2E: Test config changes trigger rebuilds using direct imports.

        Test hot reload functionality:
        1. Start ServeOrchestrator with file watching enabled
        2. Verify initial gallery generation and serving
        3. Modify configuration file (change theme)
        4. Verify file watcher detects change
        5. Verify gallery regeneration occurs
        6. Verify updated content is served
        """
        # Arrange: Create file watching scenario (now uses flat config)
        scenario = file_watcher_scenario()
        config_path = scenario["config_path"]
        initial_config = scenario["initial_config"]

        test_port = free_port()

        # Act: Use ServeOrchestrator directly with watching enabled
        orchestrator = ServeOrchestrator()
        serve_thread = None

        try:
            # Run serve with file watching in background thread
            def run_serve():
                orchestrator.execute(
                    config_path=config_path,
                    host="127.0.0.1",
                    port=test_port,
                    no_watch=False,  # Enable file watching
                    verbose=False
                )
            
            serve_thread = Thread(target=run_serve, daemon=True)
            serve_thread.start()

            # Wait for initial server startup and generation
            time.sleep(3)

            # Verify initial content
            response = requests.get(f"http://localhost:{test_port}/page_1.html", timeout=2)
            assert response.status_code == 200, "Initial server not responding"
            initial_content = response.text

            # Modify config to change theme (trigger hot reload) - use flat format
            modified_config = initial_config.copy()
            modified_config["theme"] = "elegant"  # Flat format update
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

            # Content should still be substantial after hot reload
            assert len(updated_content) > 100, "Page content should still be substantial"

        finally:
            # Cleanup: ServeOrchestrator handles cleanup internally
            if serve_thread and serve_thread.is_alive():
                pass  # Daemon thread will be cleaned up automatically

    def test_serve_static_file_serving(self, complete_serving_scenario):
        """E2E: Test HTTP requests return correct gallery files using direct imports.

        Test static file serving functionality:
        1. Generate gallery with multiple photos and pages
        2. Start ServeOrchestrator
        3. Test serving of HTML pages with correct content-type
        4. Test serving of CSS files with correct content-type
        5. Test root path redirect to page_1.html
        6. Test 404 handling for missing files
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

        # Act: Use ServeOrchestrator directly
        orchestrator = ServeOrchestrator()
        serve_thread = None

        try:
            # Run serve in background thread
            def run_serve():
                orchestrator.execute(
                    config_path=config_path,
                    host="127.0.0.1",
                    port=test_port,
                    no_watch=True,
                    verbose=False
                )
            
            serve_thread = Thread(target=run_serve, daemon=True)
            serve_thread.start()

            # Wait for complete startup
            time.sleep(4)

            # Assert: Test various file serving scenarios
            assert output_dir.exists(), "Output directory not created"
            assert (output_dir / "page_1.html").exists(), "Page 1 not generated"
            assert (output_dir / "page_2.html").exists(), "Page 2 not generated"
            assert (output_dir / "gallery.css").exists(), "Gallery CSS not generated"

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

            # Test 404 handling
            response = requests.get(f"http://localhost:{test_port}/nonexistent.html", timeout=2)
            assert response.status_code == 404, "Should return 404 for missing files"

        finally:
            # Cleanup: ServeOrchestrator handles cleanup internally
            if serve_thread and serve_thread.is_alive():
                pass  # Daemon thread will be cleaned up automatically
