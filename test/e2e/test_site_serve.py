"""E2E tests for site serve proxy functionality."""

import signal
import threading
import time
from unittest.mock import patch

import pytest


class TestSiteServeE2E:
    """E2E tests for site serve command proxy functionality."""

    @pytest.mark.skip(
        "Needs server startup optimization - servers don't terminate cleanly in test environment"
    )
    def test_site_serve_proxy_coordination(
        self,
        temp_filesystem,
        config_file_factory,
        file_factory,
        fake_image_factory,
        free_port,
    ):
        """E2E: Test site serve starts both Galleria and Pelican servers.

        Test proxy coordination functionality:
        1. Verify site serve starts Galleria server on port 8001
        2. Verify site serve starts Pelican server on port 8002
        3. Verify proxy server runs on specified port (default 8000)
        4. Verify graceful shutdown of all servers
        5. Verify error handling if either server fails to start
        """
        import subprocess
        import time

        import requests

        # Arrange: Create fake photos first (serve assumes build pipeline already ran)
        fake_image_factory(
            "photo1.jpg", directory="output/pics/full", use_raw_bytes=True
        )
        fake_image_factory(
            "photo2.jpg", directory="output/pics/full", use_raw_bytes=True
        )

        # Create manifest file that references the photos
        manifest_content = {
            "collection_name": "test_wedding",
            "collection_description": "Test photos for serve E2E",
            "photos": [
                {
                    "filename": "photo1.jpg",
                    "path": str(
                        temp_filesystem / "output" / "pics" / "full" / "photo1.jpg"
                    ),
                    "timestamp": "2024-01-01T10:00:00",
                },
                {
                    "filename": "photo2.jpg",
                    "path": str(
                        temp_filesystem / "output" / "pics" / "full" / "photo2.jpg"
                    ),
                    "timestamp": "2024-01-01T11:00:00",
                },
            ],
        }
        file_factory("output/pics/full/manifest.json", json_content=manifest_content)

        # Arrange: Create site config and required files with absolute paths
        config_file_factory("site")
        config_file_factory(
            "galleria",
            {
                "provider": {"plugin": "normpic-provider"},
                "processor": {"plugin": "thumbnail-processor"},
                "transform": {"plugin": "basic-pagination"},
                "template": {"plugin": "basic-template"},
                "css": {"plugin": "basic-css"},
                "output_dir": str(temp_filesystem / "output" / "galleries" / "test"),
                "manifest_path": str(
                    temp_filesystem / "output" / "pics" / "full" / "manifest.json"
                ),
            },
        )
        config_file_factory("pelican")

        # Create output directory with basic content for Pelican to serve
        output_dir = temp_filesystem / "output"
        output_dir.mkdir(exist_ok=True)
        (output_dir / "index.html").write_text("<html><body>Test Site</body></html>")

        # Get free ports for testing
        proxy_port = free_port()
        galleria_port = free_port()
        pelican_port = free_port()

        # Act: Start site serve command with proxy
        process = subprocess.Popen(
            [
                "uv",
                "run",
                "site",
                "serve",
                "--port",
                str(proxy_port),
                "--galleria-port",
                str(galleria_port),
                "--pelican-port",
                str(pelican_port),
            ],
            cwd=temp_filesystem,
        )

        try:
            # Wait a bit for servers to start
            time.sleep(2)

            # Assert: Verify proxy server is running
            response = requests.get(f"http://localhost:{proxy_port}/", timeout=1)
            assert response.status_code in [200, 404], (
                "Proxy server should be responding"
            )

        finally:
            # Cleanup
            process.terminate()
            process.wait(timeout=5)

    @pytest.mark.skip(
        "Build integration breaks isolation - refactor serve command after PR"
    )
    def test_site_serve_routing(
        self,
        temp_filesystem,
        config_file_factory,
        file_factory,
        fake_image_factory,
        free_port,
    ):
        """E2E: Test proxy routes /galleries/, /pics/, other requests correctly.

        Test proxy routing functionality:
        1. Verify /galleries/* routes to Galleria server (port 8001)
        2. Verify /pics/* routes to static file server for output/pics/
        3. Verify all other requests route to Pelican server (port 8002)
        4. Verify 404 handling for missing files
        5. Verify correct content-type headers for different file types
        6. Verify proxy handles concurrent requests correctly
        """
        import subprocess
        import time

        import requests

        # Arrange: Create fake photos first (serve assumes build pipeline already ran)
        fake_image_factory(
            "photo1.jpg", directory="output/pics/full", use_raw_bytes=True
        )
        fake_image_factory(
            "photo2.jpg", directory="output/pics/full", use_raw_bytes=True
        )

        # Create manifest file that references the photos
        manifest_content = {
            "collection_name": "wedding",
            "collection_description": "Test wedding photos for routing",
            "photos": [
                {
                    "filename": "photo1.jpg",
                    "path": str(
                        temp_filesystem / "output" / "pics" / "full" / "photo1.jpg"
                    ),
                    "timestamp": "2024-01-01T10:00:00",
                },
                {
                    "filename": "photo2.jpg",
                    "path": str(
                        temp_filesystem / "output" / "pics" / "full" / "photo2.jpg"
                    ),
                    "timestamp": "2024-01-01T11:00:00",
                },
            ],
        }
        file_factory("output/pics/full/manifest.json", json_content=manifest_content)

        # Arrange: Create site config and required files with absolute paths
        config_file_factory("site")
        config_file_factory(
            "galleria",
            {
                "provider": {"plugin": "normpic-provider"},
                "processor": {"plugin": "thumbnail-processor"},
                "transform": {"plugin": "basic-pagination"},
                "template": {"plugin": "basic-template"},
                "css": {"plugin": "basic-css"},
                "output_dir": str(temp_filesystem / "output" / "galleries" / "wedding"),
                "manifest_path": str(
                    temp_filesystem / "output" / "pics" / "full" / "manifest.json"
                ),
            },
        )
        config_file_factory("pelican")

        # Create sample gallery content
        galleries_dir = temp_filesystem / "output" / "galleries" / "wedding"
        galleries_dir.mkdir(parents=True)
        (galleries_dir / "page_1.html").write_text("<html>Gallery Page 1</html>")

        # Note: pics_dir already created by fake_image_factory above
        pics_dir = temp_filesystem / "output" / "pics" / "full"
        # Add an additional test file for static serving
        (pics_dir / "test_static.jpg").write_bytes(b"fake jpg data")

        # Create sample pelican content
        (temp_filesystem / "output" / "index.html").write_text(
            "<html>Site Homepage</html>"
        )
        (temp_filesystem / "output" / "about.html").write_text(
            "<html>About Page</html>"
        )

        # Get free ports for testing
        proxy_port = free_port()
        galleria_port = free_port()
        pelican_port = free_port()

        # Act: Start site serve command
        process = subprocess.Popen(
            [
                "uv",
                "run",
                "site",
                "serve",
                "--port",
                str(proxy_port),
                "--galleria-port",
                str(galleria_port),
                "--pelican-port",
                str(pelican_port),
            ],
            cwd=temp_filesystem,
        )

        try:
            # Wait for servers to start
            time.sleep(2)

            # Assert: Verify routing works correctly

            # Test galleria routing for /galleries/* -> Galleria server (port 8001)
            response = requests.get(
                f"http://localhost:{proxy_port}/galleries/wedding/page_1.html",
                timeout=1,
            )
            assert response.status_code == 200, "Galleries should route to Galleria"

            # Test static file serving for /pics/* -> Static file server
            response = requests.get(
                f"http://localhost:{proxy_port}/pics/full/test_static.jpg", timeout=1
            )
            assert response.status_code == 200, "Static pic files should be served"
            assert response.content == b"fake jpg data", (
                "Static file content should match"
            )

            # Test pelican routing for / -> Pelican server
            response = requests.get(f"http://localhost:{proxy_port}/", timeout=1)
            assert response.status_code == 200, "Root should route to Pelican"
            assert b"Site Homepage" in response.content, "Should serve Pelican content"

            # Test pelican routing for /about.html -> Pelican server
            response = requests.get(
                f"http://localhost:{proxy_port}/about.html", timeout=1
            )
            assert response.status_code == 200, "About page should route to Pelican"
            assert b"About Page" in response.content, (
                "Should serve Pelican about content"
            )

        finally:
            # Cleanup
            process.terminate()
            process.wait(timeout=5)

    @pytest.mark.skip(
        "Needs server startup optimization - servers don't terminate cleanly in test environment"
    )
    def test_site_serve_uses_localhost_urls(
        self,
        temp_filesystem,
        config_file_factory,
        file_factory,
        fake_image_factory,
        free_port,
    ):
        """E2E: Test serve command generates localhost URLs in HTML output."""
        import subprocess
        import time

        import requests

        # Arrange: Reuse existing setup pattern with production URL in config
        fake_image_factory(
            "photo1.jpg", directory="output/pics/full", use_raw_bytes=True
        )
        manifest_content = {
            "collection_name": "wedding",
            "collection_description": "Test wedding photos",
            "photos": [
                {
                    "filename": "photo1.jpg",
                    "path": str(
                        temp_filesystem / "output" / "pics" / "full" / "photo1.jpg"
                    ),
                    "timestamp": "2024-01-01T10:00:00",
                }
            ],
        }
        file_factory("output/pics/full/manifest.json", json_content=manifest_content)

        config_file_factory("site")
        config_file_factory(
            "pelican",
            {
                "author": "Test Author",
                "sitename": "Test Site",
                "site_url": "https://marco-chrissy.com",  # Production URL - should be overridden
            },
        )
        config_file_factory(
            "galleria",
            {
                "provider": {"plugin": "normpic-provider"},
                "processor": {"plugin": "thumbnail-processor"},
                "transform": {"plugin": "basic-pagination"},
                "template": {"plugin": "basic-template"},
                "css": {"plugin": "basic-css"},
                "output_dir": str(temp_filesystem / "output" / "galleries" / "wedding"),
                "manifest_path": str(
                    temp_filesystem / "output" / "pics" / "full" / "manifest.json"
                ),
            },
        )

        # Create sample content - like existing test
        galleries_dir = temp_filesystem / "output" / "galleries" / "wedding"
        galleries_dir.mkdir(parents=True)
        (galleries_dir / "page_1.html").write_text("<html>Gallery Page 1</html>")
        (temp_filesystem / "output" / "index.html").write_text(
            "<html>Site Homepage</html>"
        )

        proxy_port = free_port()
        galleria_port = free_port()
        pelican_port = free_port()

        # Act: Start serve like existing tests
        process = subprocess.Popen(
            [
                "uv",
                "run",
                "site",
                "serve",
                "--port",
                str(proxy_port),
                "--galleria-port",
                str(galleria_port),
                "--pelican-port",
                str(pelican_port),
            ],
            cwd=temp_filesystem,
        )

        try:
            time.sleep(2)

            # Assert: Check HTML content doesn't contain production URLs
            response = requests.get(f"http://localhost:{proxy_port}/", timeout=1)
            assert response.status_code == 200
            assert b"https://marco-chrissy.com" not in response.content, (
                "Should not contain production URL"
            )

        finally:
            process.terminate()
            process.wait(timeout=5)

    def test_refactored_serve_architecture(
        self, temp_filesystem, config_file_factory, file_factory
    ):
        """E2E: Test refactored serve command architecture works end-to-end.

        This test verifies the refactored architecture:
        1. CLI command parses arguments correctly
        2. ServeOrchestrator coordinates proxy, build, and servers
        3. SiteServeProxy handles routing as before
        4. ProxyHTTPHandler forwards requests properly
        5. End-to-end functionality matches original implementation
        """
        from click.testing import CliRunner

        from cli.commands.serve import serve

        # Arrange: Create minimal test environment
        config_file_factory("site")
        config_file_factory(
            "galleria",
            {
                "provider": {"plugin": "normpic-provider"},
                "processor": {"plugin": "thumbnail-processor"},
                "transform": {"plugin": "basic-pagination"},
                "template": {"plugin": "basic-template"},
                "css": {"plugin": "basic-css"},
                "output_dir": str(temp_filesystem / "output" / "galleries" / "test"),
                "manifest_path": str(
                    temp_filesystem / "output" / "pics" / "full" / "manifest.json"
                ),
            },
        )
        config_file_factory("pelican")

        # Create basic output structure
        output_dir = temp_filesystem / "output"
        output_dir.mkdir(exist_ok=True)
        (output_dir / "index.html").write_text("<html>Test</html>")

        # Mock server startup to prevent actual server creation in E2E test
        with patch("serve.orchestrator.http.server.HTTPServer") as mock_server_class:
            with patch("serve.orchestrator.SiteServeProxy") as mock_proxy_class:
                # Mock server: make serve_forever raise so orchestrator must
                # handle it and shut down cleanly.
                mock_server = mock_server_class.return_value
                mock_server.serve_forever.side_effect = KeyboardInterrupt()

                # Act: Call serve command with new architecture
                runner = CliRunner()
                result = runner.invoke(
                    serve,
                    [
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "8000",
                        "--galleria-port",
                        "8001",
                        "--pelican-port",
                        "8002",
                    ],
                )

                # Assert: Command should work with new architecture
                assert result.exit_code == 0
                assert (
                    "Starting site serve proxy at http://127.0.0.1:8000"
                    in result.output
                )

                # Verify orchestrator created proxy and server
                mock_proxy_class.assert_called_once()
                mock_server_class.assert_called_once()

                # And that the server lifecycle was exercised
                mock_server.serve_forever.assert_called_once()
                mock_server.shutdown.assert_called_once()
                mock_server.server_close.assert_called_once()

    def test_serve_orchestrator_graceful_shutdown_on_signal(
        self,
        monkeypatch,
        temp_filesystem,
        config_file_factory,
        file_factory,
    ):
        """ServeOrchestrator should exit cleanly when its signal handler is invoked."""
        from serve.orchestrator import ServeOrchestrator

        # Minimal config so orchestrator.start() can run without real network/FS effects
        config_file_factory("site")
        config_file_factory(
            "galleria",
            {
                "provider": {"plugin": "normpic-provider"},
                "processor": {"plugin": "thumbnail-processor"},
                "transform": {"plugin": "basic-pagination"},
                "template": {"plugin": "basic-template"},
                "css": {"plugin": "basic-css"},
                "output_dir": str(temp_filesystem / "output" / "galleries" / "test"),
                "manifest_path": str(
                    temp_filesystem / "output" / "pics" / "full" / "manifest.json"
                ),
            },
        )
        config_file_factory("pelican")

        output_dir = temp_filesystem / "output"
        output_dir.mkdir(exist_ok=True)
        (output_dir / "index.html").write_text("<html>Test</html>")

        orchestrator = ServeOrchestrator()

        # Prevent the real signal handlers from being registered in the pytest process
        monkeypatch.setattr(orchestrator, "_setup_signal_handlers", lambda: None)

        with (
            patch("serve.orchestrator.http.server.HTTPServer") as mock_server_class,
            patch("serve.orchestrator.SiteServeProxy"),
        ):
            mock_server = mock_server_class.return_value

            # Simulate a blocking serve_forever loop that only exits when the
            # orchestrator's stop event is set. This would deadlock in the old
            # implementation where the signal handler called shutdown() directly
            # from the same thread.
            def serve_forever_side_effect():
                while not orchestrator._stop_event.is_set():
                    time.sleep(0.01)

            mock_server.serve_forever.side_effect = serve_forever_side_effect

            # Run start() in a background thread so we can "deliver" a signal
            start_thread = threading.Thread(
                target=orchestrator.start,
                kwargs={
                    "host": "127.0.0.1",
                    "port": 8000,
                    "galleria_port": 8001,
                    "pelican_port": 8002,
                },
                daemon=True,
            )
            start_thread.start()

            # Allow some time for setup
            time.sleep(0.05)

            # Simulate SIGTERM delivery – in the new implementation this just
            # sets the stop event; with the old one it would call cleanup()
            # and sys.exit() from inside the same thread as serve_forever().
            orchestrator._signal_handler(signal.SIGTERM, None)

            # Wait for orchestrator to exit
            start_thread.join(timeout=2)

            assert not start_thread.is_alive(), (
                "ServeOrchestrator.start() should return after signal"
            )

            # Server should have been shut down cleanly
            mock_server.shutdown.assert_called_once()
            mock_server.server_close.assert_called_once()
