"""Unit tests for site serve proxy logic."""

from unittest.mock import Mock, patch

from cli.commands.serve import ProxyHTTPHandler, SiteServeProxy, serve


class TestSiteServeProxy:
    """Unit tests for SiteServeProxy routing logic."""

    def test_init_creates_proxy_with_ports(self):
        """Test SiteServeProxy initializes with correct port configuration."""
        proxy = SiteServeProxy(
            galleria_port=8001,
            pelican_port=8002,
            static_pics_dir="/path/to/pics"
        )

        assert proxy.galleria_port == 8001
        assert proxy.pelican_port == 8002
        assert proxy.static_pics_dir == "/path/to/pics"

    def test_route_galleries_requests_to_galleria(self):
        """Test /galleries/* requests route to Galleria server."""
        proxy = SiteServeProxy(8001, 8002, "/pics")

        # Test various gallery paths
        assert proxy.get_target_for_path("/galleries/") == ("galleria", 8001)
        assert proxy.get_target_for_path("/galleries/wedding/") == ("galleria", 8001)
        assert proxy.get_target_for_path("/galleries/wedding/page_1.html") == ("galleria", 8001)
        assert proxy.get_target_for_path("/galleries/vacation/page_2.html") == ("galleria", 8001)

    def test_route_pics_requests_to_static(self):
        """Test /pics/* requests route to static file server."""
        proxy = SiteServeProxy(8001, 8002, "/path/to/pics")

        # Test various pic paths
        assert proxy.get_target_for_path("/pics/") == ("static", "/path/to/pics")
        assert proxy.get_target_for_path("/pics/full/photo1.jpg") == ("static", "/path/to/pics")
        assert proxy.get_target_for_path("/pics/thumbnails/thumb1.webp") == ("static", "/path/to/pics")

    def test_route_other_requests_to_pelican(self):
        """Test all other requests route to Pelican server."""
        proxy = SiteServeProxy(8001, 8002, "/pics")

        # Test various other paths
        assert proxy.get_target_for_path("/") == ("pelican", 8002)
        assert proxy.get_target_for_path("/index.html") == ("pelican", 8002)
        assert proxy.get_target_for_path("/about/") == ("pelican", 8002)
        assert proxy.get_target_for_path("/about.html") == ("pelican", 8002)
        assert proxy.get_target_for_path("/feeds/all.atom.xml") == ("pelican", 8002)

    @patch('cli.commands.serve.subprocess')
    def test_start_galleria_server(self, mock_subprocess):
        """Test starting Galleria server subprocess."""
        proxy = SiteServeProxy(8001, 8002, "/pics")

        proxy.start_galleria_server("/config/galleria.json")

        mock_subprocess.Popen.assert_called_once()
        call_args = mock_subprocess.Popen.call_args[0][0]
        assert "uv" in call_args
        assert "galleria" in call_args
        assert "serve" in call_args
        assert "--port" in call_args
        assert "8001" in call_args

    @patch('cli.commands.serve.subprocess')
    def test_start_pelican_server(self, mock_subprocess):
        """Test starting Pelican server subprocess."""
        proxy = SiteServeProxy(8001, 8002, "/pics")

        proxy.start_pelican_server("/output/dir")

        mock_subprocess.Popen.assert_called_once()
        call_args = mock_subprocess.Popen.call_args[0][0]
        assert "pelican" in call_args
        assert "--listen" in call_args
        assert "--port" in call_args
        assert "8002" in call_args

    def test_cleanup_stops_subprocesses(self):
        """Test cleanup method terminates running subprocesses."""
        proxy = SiteServeProxy(8001, 8002, "/pics")

        # Mock running processes
        proxy.galleria_process = Mock()
        proxy.pelican_process = Mock()

        proxy.cleanup()

        proxy.galleria_process.terminate.assert_called_once()
        proxy.pelican_process.terminate.assert_called_once()


class TestSiteServeCommand:
    """Unit tests for site serve CLI command."""

    @patch('cli.commands.serve.http.server.HTTPServer')
    @patch('cli.commands.serve.SiteServeProxy')
    @patch('cli.commands.serve.click.echo')
    def test_serve_command_prints_complete_url(self, mock_echo, mock_proxy_class, mock_http_server):
        """Test serve command prints complete HTTP URL for proxy server."""
        from click.testing import CliRunner

        # Arrange: Mock proxy and server to prevent hanging
        mock_proxy = Mock()
        mock_proxy_class.return_value = mock_proxy
        mock_server_instance = Mock()
        mock_http_server.return_value = mock_server_instance

        runner = CliRunner()
        result = runner.invoke(serve, ['--host', '127.0.0.1', '--port', '8000'])

        assert result.exit_code == 0
        mock_echo.assert_any_call("Starting site serve proxy at http://127.0.0.1:8000")

    @patch('cli.commands.serve.http.server.HTTPServer')
    @patch('cli.commands.serve.SiteServeProxy')
    def test_serve_function_starts_http_server(self, mock_proxy_class, mock_http_server):
        """Test serve function creates and starts HTTP server with proxy handler."""
        from click.testing import CliRunner

        # Arrange: Mock proxy instance and server
        mock_proxy = Mock()
        mock_proxy_class.return_value = mock_proxy
        mock_server_instance = Mock()
        mock_http_server.return_value = mock_server_instance

        # Act: Call serve command via Click runner
        runner = CliRunner()
        result = runner.invoke(serve, [
            '--host', '127.0.0.1',
            '--port', '8000',
            '--galleria-port', '8001',
            '--pelican-port', '8002'
        ])

        # Assert: Command completed successfully
        assert result.exit_code == 0

        # Assert: Proxy created with correct ports
        mock_proxy_class.assert_called_once_with(
            galleria_port=8001,
            pelican_port=8002,
            static_pics_dir="output/pics"
        )

        # Assert: Backend servers started
        mock_proxy.start_galleria_server.assert_called_once_with("config/galleria.json")
        mock_proxy.start_pelican_server.assert_called_once_with("output")

        # Assert: HTTP server created with correct parameters
        mock_http_server.assert_called_once_with(("127.0.0.1", 8000), ProxyHTTPHandler)

        # Assert: Handler linked to proxy
        server_args = mock_http_server.call_args[0]
        handler_class = server_args[1]
        assert hasattr(handler_class, 'proxy')
        assert handler_class.proxy == mock_proxy

        # Assert: Server starts listening
        mock_server_instance.serve_forever.assert_called_once()


class TestProxyHTTPHandler:
    """Unit tests for HTTP proxy handler that forwards requests."""

    def test_handler_forwards_galleries_to_galleria_server(self):
        """Test handler forwards /galleries/* requests to Galleria server."""
        from unittest.mock import Mock

        from cli.commands.serve import ProxyHTTPHandler

        # Arrange: Create handler without calling constructor
        handler = ProxyHTTPHandler.__new__(ProxyHTTPHandler)
        handler.path = "/galleries/wedding/page_1.html"
        handler.proxy = SiteServeProxy(8001, 8002, "/pics")

        # Mock the forward_to_server method
        handler.forward_to_server = Mock()

        # Act: Handle GET request
        handler.do_GET()

        # Assert: Request forwarded to Galleria server
        handler.forward_to_server.assert_called_once_with("127.0.0.1", 8001, "/galleries/wedding/page_1.html")

    def test_handler_forwards_pics_to_static_files(self):
        """Test handler serves /pics/* requests from static files."""
        from unittest.mock import Mock

        from cli.commands.serve import ProxyHTTPHandler

        # Arrange: Create handler without calling constructor
        handler = ProxyHTTPHandler.__new__(ProxyHTTPHandler)
        handler.path = "/pics/full/photo1.jpg"
        handler.proxy = SiteServeProxy(8001, 8002, "/path/to/pics")

        # Mock the serve_static_file method
        handler.serve_static_file = Mock()

        # Act: Handle GET request
        handler.do_GET()

        # Assert: File served from static directory
        handler.serve_static_file.assert_called_once_with("/path/to/pics", "/pics/full/photo1.jpg")

    def test_handler_forwards_other_requests_to_pelican(self):
        """Test handler forwards other requests to Pelican server."""
        from unittest.mock import Mock

        from cli.commands.serve import ProxyHTTPHandler

        # Arrange: Create handler without calling constructor
        handler = ProxyHTTPHandler.__new__(ProxyHTTPHandler)
        handler.path = "/about.html"
        handler.proxy = SiteServeProxy(8001, 8002, "/pics")

        # Mock the forward_to_server method
        handler.forward_to_server = Mock()

        # Act: Handle GET request
        handler.do_GET()

        # Assert: Request forwarded to Pelican server
        handler.forward_to_server.assert_called_once_with("127.0.0.1", 8002, "/about.html")

    @patch('cli.commands.serve.http.client.HTTPConnection')
    def test_forward_to_server_makes_http_request(self, mock_http_connection):
        """Test forward_to_server makes HTTP request and returns response."""
        from unittest.mock import Mock

        from cli.commands.serve import ProxyHTTPHandler

        # Arrange: Mock successful HTTP response
        mock_conn = Mock()
        mock_response = Mock()
        mock_response.status = 200
        mock_response.reason = "OK"
        mock_response.read.return_value = b"<html>Gallery Page</html>"
        mock_response.getheaders.return_value = [("Content-Type", "text/html")]

        mock_conn.getresponse.return_value = mock_response
        mock_http_connection.return_value = mock_conn

        handler = ProxyHTTPHandler.__new__(ProxyHTTPHandler)
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()

        # Act: Forward request to server
        handler.forward_to_server("127.0.0.1", 8001, "/galleries/wedding/page_1.html")

        # Assert: HTTP connection made and response sent
        mock_http_connection.assert_called_once_with("127.0.0.1", 8001)
        mock_conn.request.assert_called_once_with("GET", "/galleries/wedding/page_1.html")
        handler.send_response.assert_called_once_with(200, "OK")
        handler.wfile.write.assert_called_once_with(b"<html>Gallery Page</html>")

    @patch('cli.commands.serve.mimetypes.guess_type')
    @patch('cli.commands.serve.Path')
    def test_serve_static_file_serves_existing_file(self, mock_path_class, mock_guess_type):
        """Test serve_static_file serves existing files with correct headers."""
        from unittest.mock import Mock

        from cli.commands.serve import ProxyHTTPHandler

        # Arrange: Mock existing file
        mock_file_path = Mock()
        mock_file_path.exists.return_value = True
        mock_file_path.read_bytes.return_value = b"fake jpg data"

        # Mock Path constructor and __truediv__ method
        mock_path_instance = Mock()
        mock_path_instance.__truediv__ = Mock(return_value=mock_file_path)
        mock_path_class.return_value = mock_path_instance

        # Mock mimetypes
        mock_guess_type.return_value = ("image/jpeg", None)

        handler = ProxyHTTPHandler.__new__(ProxyHTTPHandler)
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()

        # Act: Serve static file
        handler.serve_static_file("/path/to/pics", "/pics/full/photo1.jpg")

        # Assert: File served with correct headers
        handler.send_response.assert_called_once_with(200)
        handler.send_header.assert_any_call("Content-Type", "image/jpeg")
        handler.wfile.write.assert_called_once_with(b"fake jpg data")

    @patch('cli.commands.serve.Path')
    def test_serve_static_file_returns_404_for_missing_file(self, mock_path_class):
        """Test serve_static_file returns 404 for missing files."""
        from unittest.mock import Mock

        from cli.commands.serve import ProxyHTTPHandler

        # Arrange: Mock missing file
        mock_file_path = Mock()
        mock_file_path.exists.return_value = False

        # Mock Path constructor and __truediv__ method
        mock_path_instance = Mock()
        mock_path_instance.__truediv__ = Mock(return_value=mock_file_path)
        mock_path_class.return_value = mock_path_instance

        handler = ProxyHTTPHandler.__new__(ProxyHTTPHandler)
        handler.send_error = Mock()

        # Act: Try to serve missing file
        handler.serve_static_file("/path/to/pics", "/pics/full/missing.jpg")

        # Assert: 404 error sent
        handler.send_error.assert_called_once_with(404, "File not found")

    @patch('cli.commands.serve.http.client.HTTPConnection')
    def test_forward_to_server_handles_connection_error(self, mock_http_connection):
        """Test forward_to_server handles connection errors gracefully."""
        from unittest.mock import Mock

        from cli.commands.serve import ProxyHTTPHandler

        # Arrange: Mock connection error
        mock_http_connection.side_effect = OSError("Connection refused")

        handler = ProxyHTTPHandler.__new__(ProxyHTTPHandler)
        handler.send_error = Mock()

        # Act: Try to forward to unreachable server
        handler.forward_to_server("127.0.0.1", 8001, "/galleries/wedding/page_1.html")

        # Assert: 502 error sent
        handler.send_error.assert_called_once_with(502, "Bad Gateway - Target server unreachable")
