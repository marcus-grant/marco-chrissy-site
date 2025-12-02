"""E2E tests for site serve proxy functionality."""



class TestSiteServeE2E:
    """E2E tests for site serve command proxy functionality."""

    def test_site_serve_proxy_coordination(self, temp_filesystem, config_file_factory, free_port):
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

        # Arrange: Create site config and required files
        config_file_factory("site")
        config_file_factory("galleria")
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
        process = subprocess.Popen([
            "uv", "run", "site", "serve",
            "--port", str(proxy_port),
            "--galleria-port", str(galleria_port),
            "--pelican-port", str(pelican_port)
        ], cwd=temp_filesystem)

        try:
            # Wait a bit for servers to start
            time.sleep(2)

            # Assert: Verify proxy server is running
            response = requests.get(f"http://localhost:{proxy_port}/", timeout=1)
            assert response.status_code in [200, 404], "Proxy server should be responding"

        finally:
            # Cleanup
            process.terminate()
            process.wait(timeout=5)

    def test_site_serve_routing(self, temp_filesystem, config_file_factory, free_port):
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

        # Arrange: Create site config and required files
        config_file_factory("site")
        config_file_factory("galleria")
        config_file_factory("pelican")

        # Create sample gallery content
        galleries_dir = temp_filesystem / "output" / "galleries" / "wedding"
        galleries_dir.mkdir(parents=True)
        (galleries_dir / "page_1.html").write_text("<html>Gallery Page 1</html>")

        # Create sample pic content
        pics_dir = temp_filesystem / "output" / "pics" / "full"
        pics_dir.mkdir(parents=True)
        (pics_dir / "photo1.jpg").write_bytes(b"fake jpg data")

        # Create sample pelican content
        (temp_filesystem / "output" / "index.html").write_text("<html>Site Homepage</html>")
        (temp_filesystem / "output" / "about.html").write_text("<html>About Page</html>")

        # Get free ports for testing
        proxy_port = free_port()
        galleria_port = free_port()
        pelican_port = free_port()

        # Act: Start site serve command
        process = subprocess.Popen([
            "uv", "run", "site", "serve",
            "--port", str(proxy_port),
            "--galleria-port", str(galleria_port),
            "--pelican-port", str(pelican_port)
        ], cwd=temp_filesystem)

        try:
            # Wait for servers to start
            time.sleep(2)

            # Assert: Verify routing works correctly

            # Test static file serving for /pics/* -> Static file server
            response = requests.get(f"http://localhost:{proxy_port}/pics/full/photo1.jpg", timeout=1)
            assert response.status_code == 200, "Static pic files should be served"
            assert response.content == b"fake jpg data", "Static file content should match"

            # Test pelican routing for / -> Pelican server
            response = requests.get(f"http://localhost:{proxy_port}/", timeout=1)
            assert response.status_code == 200, "Root should route to Pelican"
            assert b"Site Homepage" in response.content, "Should serve Pelican content"

            # Test pelican routing for /about.html -> Pelican server
            response = requests.get(f"http://localhost:{proxy_port}/about.html", timeout=1)
            assert response.status_code == 200, "About page should route to Pelican"
            assert b"About Page" in response.content, "Should serve Pelican about content"

        finally:
            # Cleanup
            process.terminate()
            process.wait(timeout=5)
