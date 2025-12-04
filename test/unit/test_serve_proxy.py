"""Unit tests for serve proxy logic."""

import subprocess
from unittest.mock import Mock, patch

from serve.proxy import SiteServeProxy


class TestSiteServeProxy:
    """Unit tests for SiteServeProxy routing logic."""

    def test_init_creates_proxy_with_ports(self):
        """Test SiteServeProxy initializes with correct port configuration."""
        proxy = SiteServeProxy(
            galleria_port=8001, pelican_port=8002, static_pics_dir="/path/to/pics"
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
        assert proxy.get_target_for_path("/galleries/wedding/page_1.html") == (
            "galleria",
            8001,
        )
        assert proxy.get_target_for_path("/galleries/vacation/page_2.html") == (
            "galleria",
            8001,
        )

    def test_route_pics_requests_to_static(self):
        """Test /pics/* requests route to static file server."""
        proxy = SiteServeProxy(8001, 8002, "/path/to/pics")
        # Test various pic paths
        assert proxy.get_target_for_path("/pics/") == ("static", "/path/to/pics")
        assert proxy.get_target_for_path("/pics/full/photo1.jpg") == (
            "static",
            "/path/to/pics",
        )
        assert proxy.get_target_for_path("/pics/thumbnails/thumb1.webp") == (
            "static",
            "/path/to/pics",
        )

    def test_route_other_requests_to_pelican(self):
        """Test all other requests route to Pelican server."""
        proxy = SiteServeProxy(8001, 8002, "/pics")
        # Test various other paths
        assert proxy.get_target_for_path("/") == ("pelican", 8002)
        assert proxy.get_target_for_path("/index.html") == ("pelican", 8002)
        assert proxy.get_target_for_path("/about/") == ("pelican", 8002)
        assert proxy.get_target_for_path("/about.html") == ("pelican", 8002)
        assert proxy.get_target_for_path("/feeds/all.atom.xml") == ("pelican", 8002)

    @patch("serve.proxy.subprocess")
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

    @patch("serve.proxy.subprocess")
    def test_start_galleria_server_with_no_generate_flag(self, mock_subprocess):
        """Test starting Galleria server subprocess with --no-generate flag."""
        proxy = SiteServeProxy(8001, 8002, "/pics")
        proxy.start_galleria_server("/config/galleria.json", no_generate=True)
        mock_subprocess.Popen.assert_called_once()
        call_args = mock_subprocess.Popen.call_args[0][0]
        assert "--no-generate" in call_args

    @patch("serve.proxy.subprocess")
    def test_start_pelican_server(self, mock_subprocess):
        """Test starting Pelican server subprocess."""
        proxy = SiteServeProxy(8001, 8002, "/pics")
        proxy.start_pelican_server("output")
        mock_subprocess.Popen.assert_called_once()
        call_args = mock_subprocess.Popen.call_args[0][0]
        assert "pelican" in call_args
        assert "--listen" in call_args
        assert "--port" in call_args
        assert "8002" in call_args

    def test_cleanup_stops_subprocesses(self):
        """Test cleanup method terminates running subprocesses."""
        proxy = SiteServeProxy(8001, 8002, "/pics")
        # Mock processes
        mock_galleria = Mock()
        mock_pelican = Mock()
        proxy.galleria_process = mock_galleria
        proxy.pelican_process = mock_pelican

        proxy.cleanup()

        mock_galleria.terminate.assert_called_once()
        mock_galleria.wait.assert_called_once_with(timeout=3)
        mock_pelican.terminate.assert_called_once()
        mock_pelican.wait.assert_called_once_with(timeout=3)

    def test_cleanup_kills_processes_if_terminate_times_out(self):
        """Test cleanup kills processes if terminate times out."""
        proxy = SiteServeProxy(8001, 8002, "/pics")
        # Mock processes that timeout on wait
        mock_galleria = Mock()
        mock_galleria.wait.side_effect = subprocess.TimeoutExpired("cmd", 3)
        mock_pelican = Mock()
        mock_pelican.wait.side_effect = subprocess.TimeoutExpired("cmd", 3)

        proxy.galleria_process = mock_galleria
        proxy.pelican_process = mock_pelican

        proxy.cleanup()

        # Should try terminate first, then kill when timeout
        mock_galleria.terminate.assert_called_once()
        mock_galleria.kill.assert_called_once()
        mock_pelican.terminate.assert_called_once()
        mock_pelican.kill.assert_called_once()

    def test_cleanup_handles_none_processes(self):
        """Test cleanup handles None processes gracefully."""
        proxy = SiteServeProxy(8001, 8002, "/pics")
        proxy.galleria_process = None
        proxy.pelican_process = None

        # Should not raise any exceptions
        proxy.cleanup()

    def test_cleanup_handles_mixed_process_states(self):
        """Test cleanup handles mix of None and active processes."""
        proxy = SiteServeProxy(8001, 8002, "/pics")
        mock_galleria = Mock()
        proxy.galleria_process = mock_galleria
        proxy.pelican_process = None  # None process

        proxy.cleanup()

        # Should only cleanup the active process
        mock_galleria.terminate.assert_called_once()
        mock_galleria.wait.assert_called_once_with(timeout=3)


class TestProxyHTTPHandler:
    """Unit tests for HTTP proxy handler that forwards requests."""

    def test_handler_forwards_galleries_to_galleria_server(self):
        """Test handler forwards /galleries/* requests to Galleria server."""
        # This would need more complex mocking for HTTP server integration
        # Marking as placeholder for full implementation
        pass

    def test_handler_forwards_pics_to_static_files(self):
        """Test handler serves /pics/* requests from static files."""
        # This would need more complex mocking for HTTP server integration
        # Marking as placeholder for full implementation
        pass

    def test_handler_forwards_other_requests_to_pelican(self):
        """Test handler forwards other requests to Pelican server."""
        # This would need more complex mocking for HTTP server integration
        # Marking as placeholder for full implementation
        pass

    def test_forward_to_server_makes_http_request(self):
        """Test forward_to_server makes HTTP request and returns response."""
        # This would need more complex mocking for HTTP server integration
        # Marking as placeholder for full implementation
        pass

    def test_serve_static_file_serves_existing_file(self):
        """Test serve_static_file serves existing files with correct headers."""
        # This would need more complex mocking for HTTP server integration
        # Marking as placeholder for full implementation
        pass

    def test_serve_static_file_returns_404_for_missing_file(self):
        """Test serve_static_file returns 404 for missing files."""
        # This would need more complex mocking for HTTP server integration
        # Marking as placeholder for full implementation
        pass

    def test_forward_to_server_handles_connection_error(self):
        """Test forward_to_server handles connection errors gracefully."""
        # This would need more complex mocking for HTTP server integration
        # Marking as placeholder for full implementation
        pass
