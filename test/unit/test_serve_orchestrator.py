"""Unit tests for ServeOrchestrator class."""

import signal
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

        # Mock threading to prevent actual background thread
        with patch('serve.orchestrator.threading.Thread') as mock_thread_class:
            mock_thread = Mock()
            mock_thread_class.return_value = mock_thread

            # Mock time.sleep to immediately trigger KeyboardInterrupt
            with patch('serve.orchestrator.time.sleep', side_effect=KeyboardInterrupt()):
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

    @patch('serve.orchestrator.signal.signal')
    def test_setup_signal_handlers_registers_sigint_and_sigterm(self, mock_signal):
        """Test signal handlers are registered for SIGINT and SIGTERM."""
        # Arrange
        orchestrator = ServeOrchestrator()

        # Act
        orchestrator._setup_signal_handlers()

        # Assert: Should register handlers for both signals
        assert mock_signal.call_count == 2
        mock_signal.assert_any_call(signal.SIGINT, mock_signal.call_args_list[0][0][1])
        mock_signal.assert_any_call(signal.SIGTERM, mock_signal.call_args_list[1][0][1])

    def test_signal_handler_sets_stop_event(self):
        """Test signal handler sets stop event instead of calling cleanup directly."""
        # Arrange
        orchestrator = ServeOrchestrator()
        orchestrator._setup_signal_handlers()

        # Get the signal handler function that was registered
        with patch('serve.orchestrator.signal.signal') as mock_signal:
            orchestrator._setup_signal_handlers()
            signal_handler = mock_signal.call_args_list[0][0][1]

        # Act: Simulate signal reception
        signal_handler(signal.SIGINT, None)

        # Assert: Should set stop event, not call cleanup directly
        assert orchestrator._stop_event.is_set()

    def test_cleanup_terminates_proxy_and_server(self):
        """Test cleanup method terminates proxy and server."""
        # Arrange
        orchestrator = ServeOrchestrator()

        # Create mock proxy and server
        mock_proxy = Mock()
        mock_server = Mock()
        orchestrator.proxy = mock_proxy
        orchestrator.server = mock_server

        # Act
        orchestrator.cleanup()

        # Assert: Should cleanup proxy and server
        mock_proxy.cleanup.assert_called_once()

    def test_cleanup_handles_none_proxy_and_server(self):
        """Test cleanup method handles None proxy and server gracefully."""
        # Arrange
        orchestrator = ServeOrchestrator()
        orchestrator.proxy = None
        orchestrator.server = None

        # Act & Assert: Should not raise any exceptions
        orchestrator.cleanup()

    @patch('serve.orchestrator.http.server.HTTPServer')
    @patch('serve.orchestrator.SiteServeProxy')
    @patch('serve.orchestrator.BuildOrchestrator')
    def test_start_stores_proxy_and_server_references(self, mock_build_orchestrator_class, mock_proxy_class, mock_server_class):
        """Test start method stores references to proxy and server for cleanup."""
        # Arrange
        mock_build_orchestrator = Mock()
        mock_build_orchestrator_class.return_value = mock_build_orchestrator

        mock_proxy = Mock()
        mock_proxy_class.return_value = mock_proxy

        mock_server = Mock()
        mock_server_class.return_value = mock_server

        # Mock threading and time.sleep to prevent hanging
        with patch('serve.orchestrator.threading.Thread') as mock_thread_class:
            mock_thread = Mock()
            mock_thread_class.return_value = mock_thread

            with patch('serve.orchestrator.time.sleep', side_effect=KeyboardInterrupt()):
                orchestrator = ServeOrchestrator()

                # Act
                orchestrator.start(
                    host="127.0.0.1",
                    port=8000,
                    galleria_port=8001,
                    pelican_port=8002
                )

        # Assert: Should store references for cleanup
        assert orchestrator.proxy == mock_proxy
        assert orchestrator.server == mock_server

    @patch('serve.orchestrator.http.server.HTTPServer')
    @patch('serve.orchestrator.SiteServeProxy')
    @patch('serve.orchestrator.BuildOrchestrator')
    def test_start_calls_cleanup_on_keyboard_interrupt(self, mock_build_orchestrator_class, mock_proxy_class, mock_server_class):
        """Test start method calls cleanup when KeyboardInterrupt occurs."""
        # Arrange
        mock_build_orchestrator = Mock()
        mock_build_orchestrator_class.return_value = mock_build_orchestrator

        mock_proxy = Mock()
        mock_proxy_class.return_value = mock_proxy

        mock_server = Mock()
        mock_server_class.return_value = mock_server

        # Mock threading to prevent actual background thread
        with patch('serve.orchestrator.threading.Thread') as mock_thread_class:
            mock_thread = Mock()
            mock_thread_class.return_value = mock_thread

            # Mock time.sleep to trigger KeyboardInterrupt after setup
            with patch('serve.orchestrator.time.sleep', side_effect=KeyboardInterrupt()):
                orchestrator = ServeOrchestrator()

                # Mock cleanup to track calls
                with patch.object(orchestrator, 'cleanup') as mock_cleanup:
                    # Act
                    orchestrator.start(
                        host="127.0.0.1",
                        port=8000,
                        galleria_port=8001,
                        pelican_port=8002
                    )

                    # Assert: Should call cleanup
                    mock_cleanup.assert_called_once()

    def test_signal_handler_does_not_call_cleanup_directly(self):
        """Test signal handler does not call cleanup directly, only sets stop event."""
        orchestrator = ServeOrchestrator()
        mock_proxy = Mock()
        mock_server = Mock()
        orchestrator.proxy = mock_proxy
        orchestrator.server = mock_server

        cleanup_called = False

        def track_cleanup():
            nonlocal cleanup_called
            cleanup_called = True
            mock_proxy.cleanup()
            mock_server.shutdown()
            mock_server.server_close()

        orchestrator.cleanup = track_cleanup

        # Get actual signal handler
        with patch('serve.orchestrator.signal.signal') as mock_signal:
            orchestrator._setup_signal_handlers()
            signal_handler = mock_signal.call_args_list[0][0][1]

        # Act: Call signal handler
        signal_handler(signal.SIGINT, None)

        # Assert: Should NOT call cleanup directly, only set stop event
        assert not cleanup_called
        assert orchestrator._stop_event.is_set()
        mock_proxy.cleanup.assert_not_called()

    @patch('serve.orchestrator.threading.Thread')
    @patch('serve.orchestrator.time.sleep')
    @patch('serve.orchestrator.http.server.HTTPServer')
    @patch('serve.orchestrator.SiteServeProxy')
    @patch('serve.orchestrator.BuildOrchestrator')
    def test_start_runs_server_in_separate_thread_for_signal_handling(self, mock_build_orchestrator_class, mock_proxy_class, mock_server_class, mock_sleep, mock_thread_class):
        """Test start method runs server in separate thread to avoid signal handler deadlock."""
        # Arrange
        mock_build_orchestrator = Mock()
        mock_build_orchestrator_class.return_value = mock_build_orchestrator

        mock_proxy = Mock()
        mock_proxy_class.return_value = mock_proxy

        mock_server = Mock()
        mock_server_class.return_value = mock_server

        mock_thread = Mock()
        mock_thread_class.return_value = mock_thread

        # Make sleep raise KeyboardInterrupt after first call to simulate signal
        mock_sleep.side_effect = [None, KeyboardInterrupt()]

        orchestrator = ServeOrchestrator()

        # Act
        orchestrator.start(
            host="127.0.0.1",
            port=8000,
            galleria_port=8001,
            pelican_port=8002
        )

        # Assert: Should create thread for server with _run_http_server target
        mock_thread_class.assert_called_once()
        thread_call_args = mock_thread_class.call_args
        assert thread_call_args[1]['target'] == orchestrator._run_http_server
        assert thread_call_args[1]['daemon']

        mock_thread.start.assert_called_once()
        mock_server.shutdown.assert_called_once()
        mock_proxy.cleanup.assert_called_once()

    @patch('serve.orchestrator.http.server.HTTPServer')
    @patch('serve.orchestrator.SiteServeProxy')
    @patch('serve.orchestrator.BuildOrchestrator')
    def test_start_calls_cleanup_on_general_exception(self, mock_build_orchestrator_class, mock_proxy_class, mock_server_class):
        """Test start method calls cleanup when general exception occurs."""
        # Arrange
        mock_build_orchestrator = Mock()
        mock_build_orchestrator_class.return_value = mock_build_orchestrator

        mock_proxy = Mock()
        mock_proxy_class.return_value = mock_proxy

        mock_server = Mock()
        mock_server_class.return_value = mock_server

        # Mock threading to prevent actual background thread
        with patch('serve.orchestrator.threading.Thread') as mock_thread_class:
            mock_thread = Mock()
            mock_thread_class.return_value = mock_thread

            # Mock time.sleep to raise RuntimeError after setup
            with patch('serve.orchestrator.time.sleep', side_effect=RuntimeError("Test error")):
                orchestrator = ServeOrchestrator()

                # Mock cleanup to track calls
                with patch.object(orchestrator, 'cleanup') as mock_cleanup:
                    # Act: Exception should be raised but cleanup should still be called in finally
                    try:
                        orchestrator.start(
                            host="127.0.0.1",
                            port=8000,
                            galleria_port=8001,
                            pelican_port=8002
                        )
                    except RuntimeError:
                        pass  # Expected

                    # Assert: Should call cleanup even when exception occurs
                    mock_cleanup.assert_called_once()
