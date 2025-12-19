"""Unit tests for site serve proxy logic."""

from unittest.mock import Mock, patch

# TODO: Will be restored after refactor - classes moved to serve/proxy.py
# from cli.commands.serve import ProxyHTTPHandler, SiteServeProxy, serve



class TestSiteServeCommand:
    """Unit tests for site serve CLI command."""

    @patch('cli.commands.serve.get_output_dir')
    @patch('cli.commands.serve.ServeOrchestrator')
    def test_serve_command_prints_complete_url(self, mock_orchestrator_class, mock_get_output_dir):
        """Test serve command prints complete HTTP URL for proxy server."""
        from click.testing import CliRunner

        from cli.commands.serve import serve

        # Arrange: Mock get_output_dir to return an existing directory (to skip build)
        mock_output_dir = Mock()
        mock_output_dir.exists.return_value = True  # Directory exists, skip build
        mock_get_output_dir.return_value = mock_output_dir

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

    @patch('cli.commands.serve.build')
    @patch('cli.commands.serve.get_output_dir')
    @patch('cli.commands.serve.ServeOrchestrator')
    def test_serve_fails_when_build_cannot_create_output_dir(self, mock_orchestrator_class, mock_get_output_dir, mock_build):
        """Test serve command fails when build completes but output directory still missing."""
        from click.testing import CliRunner

        from cli.commands.serve import serve

        # Arrange: Mock output directory never exists, even after build
        mock_output_dir = Mock()
        mock_output_dir.exists.return_value = False  # Directory never exists
        mock_get_output_dir.return_value = mock_output_dir

        # Mock build to succeed but directory still doesn't exist
        mock_build.return_value = None

        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator

        # Act: Run serve command
        runner = CliRunner()
        result = runner.invoke(serve)

        # Assert: Should fail when build doesn't create output directory
        assert result.exit_code == 1
        assert "build completed but output directory still missing" in result.output.lower()
        # Orchestrator should not have been called
        mock_orchestrator.start.assert_not_called()

    @patch('cli.commands.serve.build')
    @patch('cli.commands.serve.get_output_dir')
    @patch('cli.commands.serve.ServeOrchestrator')
    def test_serve_auto_calls_build_when_output_missing(self, mock_orchestrator_class, mock_get_output_dir, mock_build):
        """Test serve command automatically calls build when output directory missing."""
        from unittest.mock import Mock

        from click.testing import CliRunner

        from cli.commands.serve import serve

        # Arrange: Mock that output directory doesn't exist initially but build creates it
        mock_output_dir = Mock()
        call_count = 0
        def exists_side_effect():
            nonlocal call_count
            call_count += 1
            # First call: output doesn't exist, second call: output exists after build
            return call_count > 1

        mock_output_dir.exists.side_effect = exists_side_effect
        mock_get_output_dir.return_value = mock_output_dir

        # Mock build to succeed
        mock_build.return_value = None

        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.start.side_effect = KeyboardInterrupt()  # Exit immediately

        # Act: Run serve command
        runner = CliRunner()
        result = runner.invoke(serve)

        # Assert: Should succeed after auto-calling build
        assert result.exit_code == 0
        assert "running build" in result.output.lower()
        # Orchestrator should have been called after successful build
        mock_orchestrator.start.assert_called_once()

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

    @patch('cli.commands.serve.get_output_dir')
    @patch('cli.commands.serve.ServeOrchestrator')
    def test_serve_function_starts_orchestrator(self, mock_orchestrator_class, mock_get_output_dir):
        """Test serve function creates and starts ServeOrchestrator."""
        from click.testing import CliRunner

        from cli.commands.serve import serve

        # Arrange: Mock get_output_dir to return an existing directory (to skip build)
        mock_output_dir = Mock()
        mock_output_dir.exists.return_value = True  # Directory exists, skip build
        mock_get_output_dir.return_value = mock_output_dir

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

    @patch('cli.commands.serve.get_output_dir')
    @patch('cli.commands.serve.ServeOrchestrator')
    def test_serve_function_with_no_generate_flag(self, mock_orchestrator_class, mock_get_output_dir):
        """Test serve function passes --no-generate flag to orchestrator."""
        from click.testing import CliRunner

        from cli.commands.serve import serve

        # Arrange: Mock get_output_dir to return an existing directory (to skip build)
        mock_output_dir = Mock()
        mock_output_dir.exists.return_value = True  # Directory exists, skip build
        mock_get_output_dir.return_value = mock_output_dir

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
