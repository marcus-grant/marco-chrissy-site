"""Unit tests for ServeOrchestrator class."""

from unittest.mock import Mock, patch

from serve.orchestrator import ServeOrchestrator


class TestServeOrchestrator:
    """Unit tests for ServeOrchestrator."""

    def test_init_creates_build_orchestrator(self):
        """Test ServeOrchestrator initializes with BuildOrchestrator."""
        orchestrator = ServeOrchestrator()
        assert hasattr(orchestrator, 'build_orchestrator')
        assert orchestrator.build_orchestrator is not None

    @patch('serve.orchestrator.http.server.HTTPServer')
    @patch('serve.orchestrator.SiteServeProxy')
    @patch('serve.orchestrator.BuildOrchestrator')
    def test_start_calls_build_with_localhost_url_override(self, mock_build_orchestrator_class, mock_proxy_class, mock_server_class):
        """Test start method calls build with localhost URL override."""
        # Arrange
        mock_build_orchestrator = Mock()
        mock_build_orchestrator_class.return_value = mock_build_orchestrator

        # Mock proxy to prevent subprocess calls
        mock_proxy = Mock()
        mock_proxy_class.return_value = mock_proxy

        # Mock HTTP server to prevent actual server startup
        mock_server = Mock()
        mock_server_class.return_value = mock_server
        mock_server.serve_forever.side_effect = KeyboardInterrupt()  # Immediately exit

        orchestrator = ServeOrchestrator()

        # Act
        orchestrator.start(
            host="127.0.0.1",
            port=8000,
            galleria_port=8001,
            pelican_port=8002
        )

        # Assert: Should have called execute with URL override
        mock_build_orchestrator.execute.assert_called_once_with(
            override_site_url="http://127.0.0.1:8000"
        )
