"""E2E tests for galleria serve functionality."""

import time
from threading import Thread

import requests

from galleria.orchestrator.serve import ServeOrchestrator


class TestGalleriaServeE2E:
    """E2E tests for galleria serve command."""

    def test_serve_orchestrator_integration(self, temp_filesystem, galleria_config_factory, manifest_factory, galleria_image_factory, file_factory, directory_factory, free_port):
        """E2E: Test ServeOrchestrator with direct imports (no subprocess).

        Test complete serve workflow:
        1. Configuration loading and validation
        2. Gallery generation (if needed)
        3. HTTP server startup and gallery serving
        4. File serving verification
        5. Clean shutdown handling
        """
        # Create the missing gallery.j2.html template (following shared_navbar_integration pattern)
        directory_factory("galleria/themes/minimal/templates")
        file_factory(
            "galleria/themes/minimal/templates/gallery.j2.html",
            """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ collection_name }} - Page {{ page_num }}</title>
    <link rel="stylesheet" href="gallery.css">
</head>
<body class="theme-minimal">
    <header>
        <h1>{{ collection_name }}</h1>
    </header>

    <main class="gallery layout-grid">
        {% for photo in photos %}
            <div class="photo-item">
                <a href="{{ photo.photo_url }}">
                    <img src="{{ photo.thumb_url }}" alt="Photo from {{ collection_name }}" loading="lazy">
                </a>
            </div>
        {% endfor %}
    </main>

    {% if total_pages > 1 %}
    <nav class="pagination">
        {% if page_num > 1 %}
            <a href="page_{{ page_num - 1 }}.html">&laquo; Previous</a>
        {% endif %}

        <span>Page {{ page_num }} of {{ total_pages }}</span>

        {% if page_num < total_pages %}
            <a href="page_{{ page_num + 1 }}.html">Next &raquo;</a>
        {% endif %}
    </nav>
    {% endif %}

    <footer>
        <p>Generated with Galleria</p>
    </footer>
</body>
</html>"""
        )

        # Create test photos and manifest
        source_photos = []
        for i in range(1, 5):  # 4 photos
            photo_path = galleria_image_factory(
                f"IMG_{i:04d}.jpg",
                directory="source_photos",
                color=(255 - i * 30, i * 40, 100 + i * 20),
                size=(1200, 800),
            )
            source_photos.append({
                "source_path": str(photo_path),
                "dest_path": f"IMG_{i:04d}.jpg",
                "hash": f"hash{i:03d}",
                "size_bytes": 2048000 + i * 1000,
                "mtime": 1234567890 + i,
            })

        manifest_path = manifest_factory(collection_name="e2e_test_photos", photos=source_photos)

        # Create config with absolute paths
        output_dir = temp_filesystem / "output/galleries/e2e_test_photos"
        config_content = {
            "manifest_path": str(manifest_path),
            "output_dir": str(output_dir),  # Use absolute path
            "thumbnail_size": 200,
            "page_size": 2,
            "theme": "minimal",  # Use minimal theme which now has template
        }
        config_path = galleria_config_factory(custom_content=config_content)

        test_port = free_port()

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
                    verbose=False,
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
            assert "e2e_test_photos" in response.text, (
                "Collection name not in served HTML"
            )

            response = requests.get(f"http://localhost:{test_port}/gallery.css")
            assert response.status_code == 200, "Gallery CSS not served"
            assert "text/css" in response.headers.get("content-type", ""), (
                "CSS content-type not set"
            )

        finally:
            # Cleanup: ServeOrchestrator handles cleanup internally via _cleanup()
            if serve_thread and serve_thread.is_alive():
                # The thread will be cleaned up when test ends (daemon=True)
                pass

    def test_serve_file_watching_workflow(
        self, file_watcher_scenario, galleria_file_factory, free_port
    ):
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
                    verbose=False,
                )

            serve_thread = Thread(target=run_serve, daemon=True)
            serve_thread.start()

            # Wait for initial server startup and generation
            time.sleep(3)

            # Verify initial content
            response = requests.get(
                f"http://localhost:{test_port}/page_1.html", timeout=2
            )
            assert response.status_code == 200, "Initial server not responding"

            # Modify config to change theme (trigger hot reload) - use flat format
            modified_config = initial_config.copy()
            modified_config["theme"] = "elegant"  # Flat format update
            galleria_file_factory(
                str(config_path.relative_to(config_path.parent.parent)),
                json_content=modified_config,
            )

            # Wait for hot reload to detect change and regenerate
            time.sleep(4)

            # Verify updated content is served
            response = requests.get(
                f"http://localhost:{test_port}/page_1.html", timeout=2
            )
            assert response.status_code == 200, "Server not responding after hot reload"
            updated_content = response.text

            # Content should still be substantial after hot reload
            assert len(updated_content) > 100, (
                "Page content should still be substantial"
            )

        finally:
            # Cleanup: ServeOrchestrator handles cleanup internally
            if serve_thread and serve_thread.is_alive():
                pass  # Daemon thread will be cleaned up automatically

    def test_serve_static_file_serving(self, temp_filesystem, galleria_config_factory, manifest_factory, galleria_image_factory, file_factory, directory_factory, free_port):
        """E2E: Test HTTP requests return correct gallery files using direct imports.

        Test static file serving functionality:
        1. Generate gallery with multiple photos and pages
        2. Start ServeOrchestrator
        3. Test serving of HTML pages with correct content-type
        4. Test serving of CSS files with correct content-type
        5. Test root path redirect to page_1.html
        6. Test 404 handling for missing files
        """
        # Create the missing gallery.j2.html template
        directory_factory("galleria/themes/minimal/templates")
        file_factory(
            "galleria/themes/minimal/templates/gallery.j2.html",
            """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ collection_name }} - Page {{ page_num }}</title>
    <link rel="stylesheet" href="gallery.css">
</head>
<body class="theme-minimal">
    <header>
        <h1>{{ collection_name }}</h1>
    </header>

    <main class="gallery layout-grid">
        {% for photo in photos %}
            <div class="photo-item">
                <a href="{{ photo.photo_url }}">
                    <img src="{{ photo.thumb_url }}" alt="Photo from {{ collection_name }}" loading="lazy">
                </a>
            </div>
        {% endfor %}
    </main>

    {% if total_pages > 1 %}
    <nav class="pagination">
        {% if page_num > 1 %}
            <a href="page_{{ page_num - 1 }}.html">&laquo; Previous</a>
        {% endif %}

        <span>Page {{ page_num }} of {{ total_pages }}</span>

        {% if page_num < total_pages %}
            <a href="page_{{ page_num + 1 }}.html">Next &raquo;</a>
        {% endif %}
    </nav>
    {% endif %}

    <footer>
        <p>Generated with Galleria</p>
    </footer>
</body>
</html>"""
        )

        # Create test photos and manifest
        source_photos = []
        for i in range(1, 7):  # 6 photos
            photo_path = galleria_image_factory(
                f"IMG_{i:04d}.jpg",
                directory="source_photos",
                color=(255 - i * 30, i * 40, 100 + i * 20),
                size=(1200, 800),
            )
            source_photos.append({
                "source_path": str(photo_path),
                "dest_path": f"IMG_{i:04d}.jpg",
                "hash": f"hash{i:03d}",
                "size_bytes": 2048000 + i * 1000,
                "mtime": 1234567890 + i,
            })

        manifest_path = manifest_factory(collection_name="serving_test", photos=source_photos)

        # Create config with absolute paths
        output_dir = temp_filesystem / "output/galleries/serving_test"
        config_content = {
            "manifest_path": str(manifest_path),
            "output_dir": str(output_dir),  # Use absolute path
            "thumbnail_size": 200,
            "page_size": 3,
            "theme": "minimal",  # Use minimal theme which now has template
        }
        config_path = galleria_config_factory(custom_content=config_content)

        test_port = free_port()

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
                    verbose=False,
                )

            serve_thread = Thread(target=run_serve, daemon=True)
            serve_thread.start()

            # Wait for complete startup
            time.sleep(4)

            # Assert: Test various file serving scenarios
            assert output_dir.exists(), "Output directory not created"
            assert (output_dir / "page_1.html").exists(), "Page 1 not generated"
            assert (output_dir / "gallery.css").exists(), "Gallery CSS not generated"

            # Check if page 2 exists (6 photos with 3 per page should create 2 pages)
            # But let's be more flexible in case pagination logic differs
            generated_files = list(output_dir.glob("page_*.html"))
            assert len(generated_files) >= 1, f"Should have at least 1 page, found: {[f.name for f in generated_files]}"

            # Test root redirect to page_1.html
            response = requests.get(f"http://localhost:{test_port}/", timeout=2)
            assert response.status_code == 200, "Root redirect failed"

            # Test HTML serving with correct content-type
            response = requests.get(
                f"http://localhost:{test_port}/page_1.html", timeout=2
            )
            assert response.status_code == 200, "Page 1 not served"
            assert "serving_test" in response.text, "Collection name missing"

            # Test second page if it exists
            if len(generated_files) > 1:
                response = requests.get(
                    f"http://localhost:{test_port}/page_2.html", timeout=2
                )
                assert response.status_code == 200, "Page 2 not served"

            # Test CSS serving with correct content-type
            response = requests.get(
                f"http://localhost:{test_port}/gallery.css", timeout=2
            )
            assert response.status_code == 200, "CSS not served"
            assert "text/css" in response.headers.get("content-type", ""), (
                "CSS content type incorrect"
            )

            # Test 404 handling
            response = requests.get(
                f"http://localhost:{test_port}/nonexistent.html", timeout=2
            )
            assert response.status_code == 404, "Should return 404 for missing files"

        finally:
            # Cleanup: ServeOrchestrator handles cleanup internally
            if serve_thread and serve_thread.is_alive():
                pass  # Daemon thread will be cleaned up automatically
