"""Unit tests for galleria static file server."""

from pathlib import Path
from unittest import mock
from unittest.mock import Mock, patch

import pytest

from galleria.server import GalleriaHTTPServer


class TestGalleriaHTTPServer:
    """Test the static file server for galleria development."""

    def test_server_initialization(self, temp_filesystem):
        """Test server can be initialized with output directory."""
        output_dir = temp_filesystem / "gallery_output"
        output_dir.mkdir()

        server = GalleriaHTTPServer(output_dir, host="127.0.0.1", port=8000)

        assert server.output_directory == output_dir
        assert server.host == "127.0.0.1"
        assert server.port == 8000

    def test_server_initialization_with_nonexistent_directory(self):
        """Test server raises error for nonexistent output directory."""
        nonexistent_dir = Path("/nonexistent/path")

        with pytest.raises(ValueError, match="Output directory .* does not exist"):
            GalleriaHTTPServer(nonexistent_dir)

    def test_server_initialization_with_file_not_directory(self, temp_filesystem):
        """Test server raises error when path is file not directory."""
        file_path = temp_filesystem / "not_a_directory.txt"
        file_path.write_text("content")

        with pytest.raises(ValueError, match="Path .* is not a directory"):
            GalleriaHTTPServer(file_path)

    def test_server_default_parameters(self, temp_filesystem):
        """Test server uses reasonable defaults."""
        output_dir = temp_filesystem / "output"
        output_dir.mkdir()

        server = GalleriaHTTPServer(output_dir)

        assert server.host == "127.0.0.1"
        assert server.port == 8000

    @patch('galleria.server.HTTPServer')
    def test_start_creates_http_server(self, mock_http_server, temp_filesystem):
        """Test start method creates and configures HTTP server."""
        output_dir = temp_filesystem / "output"
        output_dir.mkdir()

        mock_server_instance = Mock()
        mock_http_server.return_value = mock_server_instance

        server = GalleriaHTTPServer(output_dir, host="0.0.0.0", port=9000)
        server.start()

        # Should create HTTPServer with correct address
        mock_http_server.assert_called_once()
        call_args = mock_http_server.call_args
        assert call_args[0][0] == ("0.0.0.0", 9000)

        # Should call serve_forever on the created server
        mock_server_instance.serve_forever.assert_called_once()

    @patch('galleria.server.HTTPServer')
    def test_start_changes_working_directory(self, mock_http_server, temp_filesystem):
        """Test start method changes to output directory for serving."""
        output_dir = temp_filesystem / "output"
        output_dir.mkdir()

        with patch('galleria.server.os.chdir') as mock_chdir:
            server = GalleriaHTTPServer(output_dir)
            server.start()

            # Should change to output directory
            mock_chdir.assert_called_with(str(output_dir))

    def test_stop_terminates_server(self, temp_filesystem):
        """Test stop method terminates the running server."""
        output_dir = temp_filesystem / "output"
        output_dir.mkdir()

        server = GalleriaHTTPServer(output_dir)
        mock_http_server = Mock()
        server._server = mock_http_server

        server.stop()

        mock_http_server.shutdown.assert_called_once()

    def test_stop_without_running_server(self, temp_filesystem):
        """Test stop method handles case where no server is running."""
        output_dir = temp_filesystem / "output"
        output_dir.mkdir()

        server = GalleriaHTTPServer(output_dir)

        # Should not raise error when no server is running
        server.stop()

    def test_context_manager_protocol(self, temp_filesystem):
        """Test server can be used as context manager."""
        output_dir = temp_filesystem / "output"
        output_dir.mkdir()

        with patch('galleria.server.HTTPServer') as mock_http_server:
            mock_server_instance = Mock()
            mock_http_server.return_value = mock_server_instance

            server = GalleriaHTTPServer(output_dir)

            with server:
                # Should start server in context
                mock_http_server.assert_called_once()

            # Should stop server when exiting context
            mock_server_instance.shutdown.assert_called_once()

    @patch('galleria.server.HTTPServer')
    def test_custom_request_handler_setup(self, mock_http_server, temp_filesystem):
        """Test server creates custom request handler with CORS headers."""
        output_dir = temp_filesystem / "output"
        output_dir.mkdir()

        server = GalleriaHTTPServer(output_dir)
        server.start()

        # Should create HTTPServer with custom handler class
        mock_http_server.assert_called_once()
        call_args = mock_http_server.call_args
        handler_class = call_args[0][1]

        # Handler should be our custom class
        assert hasattr(handler_class, 'end_headers')


class TestGalleriaRequestHandler:
    """Test the custom HTTP request handler."""

    @patch('galleria.server.SimpleHTTPRequestHandler.__init__')
    def test_cors_headers_added(self, mock_init):
        """Test CORS headers are added to responses."""
        from galleria.server import GalleriaRequestHandler

        # Mock initialization to avoid filesystem operations
        mock_init.return_value = None

        # Create handler instance
        handler = GalleriaRequestHandler(Mock(), Mock(), Mock())
        handler.send_header = Mock()

        # Mock parent end_headers method
        with patch('galleria.server.SimpleHTTPRequestHandler.end_headers') as mock_parent_end:
            handler.end_headers()

            # Should add CORS headers before calling parent
            expected_calls = [
                mock.call('Access-Control-Allow-Origin', '*'),
                mock.call('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
                mock.call('Access-Control-Allow-Headers', 'Content-Type')
            ]
            handler.send_header.assert_has_calls(expected_calls)
            mock_parent_end.assert_called_once()

    @patch('galleria.server.SimpleHTTPRequestHandler.__init__')
    def test_root_path_redirect(self, mock_init):
        """Test root path redirects to page_1.html if it exists."""
        from galleria.server import GalleriaRequestHandler

        # Mock initialization
        mock_init.return_value = None

        handler = GalleriaRequestHandler(Mock(), Mock(), Mock())
        handler.path = "/"
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()

        # Mock file existence check
        with patch('galleria.server.Path.exists', return_value=True):
            handler.do_GET()

        # Should redirect to page_1.html
        handler.send_response.assert_called_with(302)
        handler.send_header.assert_called_with('Location', '/page_1.html')
        handler.end_headers.assert_called_once()

    @patch('galleria.server.SimpleHTTPRequestHandler.__init__')
    def test_root_path_no_redirect_when_page_missing(self, mock_init):
        """Test root path serves normally when page_1.html doesn't exist."""
        from galleria.server import GalleriaRequestHandler

        mock_init.return_value = None

        handler = GalleriaRequestHandler(Mock(), Mock(), Mock())
        handler.path = "/"

        # Mock parent do_GET method
        with patch('galleria.server.SimpleHTTPRequestHandler.do_GET') as mock_parent_get:
            # Mock file doesn't exist
            with patch('galleria.server.Path.exists', return_value=False):
                handler.do_GET()

            # Should call parent do_GET (normal serving)
            mock_parent_get.assert_called_once()

    @patch('galleria.server.SimpleHTTPRequestHandler.__init__')
    def test_non_root_path_normal_serving(self, mock_init):
        """Test non-root paths are served normally."""
        from galleria.server import GalleriaRequestHandler

        mock_init.return_value = None

        handler = GalleriaRequestHandler(Mock(), Mock(), Mock())
        handler.path = "/page_2.html"

        # Mock parent do_GET method
        with patch('galleria.server.SimpleHTTPRequestHandler.do_GET') as mock_parent_get:
            handler.do_GET()

            # Should call parent do_GET (normal serving)
            mock_parent_get.assert_called_once()

    @patch('galleria.server.SimpleHTTPRequestHandler.__init__')
    def test_custom_logging_format(self, mock_init):
        """Test custom log message format for development server."""
        from galleria.server import GalleriaRequestHandler

        mock_init.return_value = None

        handler = GalleriaRequestHandler(Mock(), Mock(), Mock())
        handler.path = "/test.html"

        # Mock log_message to capture the format
        with patch.object(handler, 'log_message') as mock_log:
            handler.log_request(200, 1024)

            # Should log with custom format
            mock_log.assert_called_once()
            format_str = mock_log.call_args[0][0]
            assert "Galleria server: 200 /test.html" == format_str
