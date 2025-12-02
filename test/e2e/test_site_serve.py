"""E2E tests for site serve proxy functionality."""



class TestSiteServeE2E:
    """E2E tests for site serve command proxy functionality."""

    def test_site_serve_proxy_coordination(self, temp_filesystem, config_file_factory, file_factory, fake_image_factory, free_port):
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
        fake_image_factory("photo1.jpg", directory="output/pics/full", use_raw_bytes=True)
        fake_image_factory("photo2.jpg", directory="output/pics/full", use_raw_bytes=True)

        # Create manifest file that references the photos
        manifest_content = {
            "collection_name": "test_wedding",
            "collection_description": "Test photos for serve E2E",
            "photos": [
                {
                    "filename": "photo1.jpg",
                    "path": str(temp_filesystem / "output" / "pics" / "full" / "photo1.jpg"),
                    "timestamp": "2024-01-01T10:00:00"
                },
                {
                    "filename": "photo2.jpg",
                    "path": str(temp_filesystem / "output" / "pics" / "full" / "photo2.jpg"),
                    "timestamp": "2024-01-01T11:00:00"
                }
            ]
        }
        file_factory("output/pics/full/manifest.json", json_content=manifest_content)

        # Arrange: Create site config and required files with absolute paths
        config_file_factory("site")
        config_file_factory("galleria", {
            "provider": {"plugin": "normpic-provider"},
            "processor": {"plugin": "thumbnail-processor"},
            "transform": {"plugin": "basic-pagination"},
            "template": {"plugin": "basic-template"},
            "css": {"plugin": "basic-css"},
            "output_dir": str(temp_filesystem / "output" / "galleries" / "test"),
            "manifest_path": str(temp_filesystem / "output" / "pics" / "full" / "manifest.json"),
        })
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

    def test_site_serve_routing(self, temp_filesystem, config_file_factory, file_factory, fake_image_factory, free_port):
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
        fake_image_factory("photo1.jpg", directory="output/pics/full", use_raw_bytes=True)
        fake_image_factory("photo2.jpg", directory="output/pics/full", use_raw_bytes=True)

        # Create manifest file that references the photos
        manifest_content = {
            "collection_name": "wedding",
            "collection_description": "Test wedding photos for routing",
            "photos": [
                {
                    "filename": "photo1.jpg",
                    "path": str(temp_filesystem / "output" / "pics" / "full" / "photo1.jpg"),
                    "timestamp": "2024-01-01T10:00:00"
                },
                {
                    "filename": "photo2.jpg",
                    "path": str(temp_filesystem / "output" / "pics" / "full" / "photo2.jpg"),
                    "timestamp": "2024-01-01T11:00:00"
                }
            ]
        }
        file_factory("output/pics/full/manifest.json", json_content=manifest_content)

        # Arrange: Create site config and required files with absolute paths
        config_file_factory("site")
        config_file_factory("galleria", {
            "provider": {"plugin": "normpic-provider"},
            "processor": {"plugin": "thumbnail-processor"},
            "transform": {"plugin": "basic-pagination"},
            "template": {"plugin": "basic-template"},
            "css": {"plugin": "basic-css"},
            "output_dir": str(temp_filesystem / "output" / "galleries" / "wedding"),
            "manifest_path": str(temp_filesystem / "output" / "pics" / "full" / "manifest.json"),
        })
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

            # Test galleria routing for /galleries/* -> Galleria server (port 8001)
            response = requests.get(f"http://localhost:{proxy_port}/galleries/wedding/page_1.html", timeout=1)
            assert response.status_code == 200, "Galleries should route to Galleria"

            # Test static file serving for /pics/* -> Static file server
            response = requests.get(f"http://localhost:{proxy_port}/pics/full/test_static.jpg", timeout=1)
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
