"""Unit tests for site serve proxy logic."""

from unittest.mock import Mock, patch

# TODO: Will be restored after refactor - classes moved to serve/proxy.py
# from cli.commands.serve import ProxyHTTPHandler, SiteServeProxy, serve



class TestSiteServeCommand:
    """Unit tests for site serve CLI command."""

    @patch('cli.commands.serve.ServeOrchestrator')
    def test_serve_command_prints_complete_url(self, mock_orchestrator_class):
        """Test serve command prints complete HTTP URL for proxy server."""
        from click.testing import CliRunner

        from cli.commands.serve import serve

        # Arrange: Mock orchestrator to prevent actual server startup
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.start.side_effect = KeyboardInterrupt()  # Exit immediately

        # Act: Call serve command via CliRunner
        runner = CliRunner()
        result = runner.invoke(serve, ['--host', '127.0.0.1', '--port', '8000'])

        # Assert: Command should complete gracefully
        assert result.exit_code == 0
        assert "Starting site serve proxy at http://127.0.0.1:8000" in result.output

        # Original test - will work after refactor:
        # @patch('cli.commands.serve.http.server.HTTPServer')
        # @patch('cli.commands.serve.SiteServeProxy')
        # @patch('cli.commands.serve.click.echo')
        # def test_serve_command_prints_complete_url(self, mock_echo, mock_proxy_class, mock_http_server):
        #     from click.testing import CliRunner
        #     # Arrange: Mock proxy and server to prevent hanging
        #     mock_proxy = Mock()
        #     mock_proxy_class.return_value = mock_proxy
        #     mock_server_instance = Mock()
        #     mock_http_server.return_value = mock_server_instance
        #     runner = CliRunner()
        #     result = runner.invoke(serve, ['--host', '127.0.0.1', '--port', '8000'])
        #     assert result.exit_code == 0
        #     mock_echo.assert_any_call("Starting site serve proxy at http://127.0.0.1:8000")

    @patch('cli.commands.serve.ServeOrchestrator')
    def test_serve_function_starts_orchestrator(self, mock_orchestrator_class):
        """Test serve function creates and starts ServeOrchestrator."""
        from click.testing import CliRunner

        from cli.commands.serve import serve

        # Arrange: Mock orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.start.side_effect = KeyboardInterrupt()

        # Act
        runner = CliRunner()
        result = runner.invoke(serve, ['--host', '127.0.0.1', '--port', '8000'])

        # Assert: Should have called orchestrator.start
        mock_orchestrator.start.assert_called_once_with(
            host="127.0.0.1",
            port=8000,
            galleria_port=8001,
            pelican_port=8002,
            no_generate=False
        )
        assert result.exit_code == 0

    @patch('cli.commands.serve.ServeOrchestrator')
    def test_serve_function_with_no_generate_flag(self, mock_orchestrator_class):
        """Test serve function passes --no-generate flag to orchestrator."""
        from click.testing import CliRunner

        from cli.commands.serve import serve

        # Arrange: Mock orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.start.side_effect = KeyboardInterrupt()

        # Act
        runner = CliRunner()
        result = runner.invoke(serve, ['--no-generate'])

        # Assert: Should pass no_generate=True
        mock_orchestrator.start.assert_called_once_with(
            host="127.0.0.1",
            port=8000,
            galleria_port=8001,
            pelican_port=8002,
            no_generate=True
        )
        assert result.exit_code == 0


# Legacy test classes removed - functionality migrated to:
# - test_serve_orchestrator.py (server lifecycle and coordination)
# - test_serve_proxy.py (proxy routing and subprocess management)
