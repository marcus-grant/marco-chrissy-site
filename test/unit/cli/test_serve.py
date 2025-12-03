"""Unit tests for serve command URL override functionality."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from cli.commands.serve import serve


class TestServeCommandURLOverride:
    """Test serve command URL override functionality."""

    def test_serve_calls_build_with_localhost_url_override(self, temp_filesystem):
        """Test serve command calls build with localhost URL override."""
        from click.testing import CliRunner
        
        # Mock all dependencies to focus on the build call behavior
        with patch('cli.commands.serve.BuildOrchestrator') as mock_orchestrator_class:
            with patch('cli.commands.serve.SiteServeProxy') as mock_proxy_class:
                with patch('cli.commands.serve.http.server.HTTPServer') as mock_server_class:
                    # Mock the orchestrator - this is what we're testing
                    mock_orchestrator = Mock()
                    mock_orchestrator_class.return_value = mock_orchestrator
                    mock_orchestrator.execute.return_value = True
                    
                    # Mock the proxy instance
                    mock_proxy = Mock()
                    mock_proxy_class.return_value = mock_proxy
                    
                    # Mock the HTTP server to exit immediately
                    mock_server = Mock()
                    mock_server_class.return_value = mock_server
                    mock_server.serve_forever.side_effect = KeyboardInterrupt()
                    
                    # Act: Call serve command via CliRunner
                    runner = CliRunner()
                    result = runner.invoke(serve, [
                        '--host', '127.0.0.1',
                        '--port', '8000',
                        '--galleria-port', '8001', 
                        '--pelican-port', '8002'
                    ])
                    
                    # Assert: Command should complete (with KeyboardInterrupt handled)
                    assert result.exit_code == 0
                    
                    # Assert: Should have called execute with URL override
                    mock_orchestrator.execute.assert_called_once_with(
                        override_site_url="http://127.0.0.1:8000"
                    )