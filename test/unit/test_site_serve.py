"""Unit tests for site serve proxy logic."""

from unittest.mock import Mock, patch

from cli.commands.serve import SiteServeProxy


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
