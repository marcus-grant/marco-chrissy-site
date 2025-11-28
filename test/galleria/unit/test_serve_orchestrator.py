"""Unit tests for ServeOrchestrator."""

from pathlib import Path
from unittest.mock import call, patch

import pytest

from galleria.orchestrator.serve import ServeOrchestrator


class TestServeOrchestrator:
    """Unit tests for ServeOrchestrator coordination logic."""

    def test_serve_orchestrator_can_be_created(self):
        """ServeOrchestrator can be instantiated."""
        orchestrator = ServeOrchestrator()
        assert orchestrator is not None

    @patch('galleria.orchestrator.serve.ConfigManager')
    @patch('galleria.orchestrator.serve.GalleriaBuilder')
    @patch('galleria.orchestrator.serve.GalleriaHTTPServer')
    @patch('galleria.orchestrator.serve.FileWatcher')
    def test_execute_loads_configuration_and_validates(self, mock_watcher, mock_server, mock_builder, mock_config):
        """execute() loads and validates configuration file."""
        # Arrange
        config_path = Path("/test/config/galleria.json")
        mock_config_manager = mock_config.return_value
        mock_galleria_config = {"output": {"directory": "/test/output"}}
        mock_config_manager.load_galleria_config.return_value = mock_galleria_config

        orchestrator = ServeOrchestrator()

        # Act
        result = orchestrator.execute(config_path)

        # Assert
        assert result is True
        mock_config.assert_called_once()
        mock_config_manager.load_galleria_config.assert_called_once_with(config_path)

    @patch('galleria.orchestrator.serve.ConfigManager')
    @patch('galleria.orchestrator.serve.GalleriaBuilder')
    @patch('galleria.orchestrator.serve.GalleriaHTTPServer')
    @patch('galleria.orchestrator.serve.FileWatcher')
    def test_execute_generates_gallery_by_default(self, mock_watcher, mock_server, mock_builder, mock_config):
        """execute() generates gallery by default (no_generate=False)."""
        # Arrange
        config_path = Path("/test/config/galleria.json")
        mock_config_manager = mock_config.return_value
        mock_galleria_config = {"output": {"directory": "/test/output"}}
        mock_config_manager.load_galleria_config.return_value = mock_galleria_config
        mock_galleria_builder = mock_builder.return_value

        orchestrator = ServeOrchestrator()

        # Act
        orchestrator.execute(config_path, no_generate=False)

        # Assert
        mock_galleria_builder.build.assert_called_once_with(mock_galleria_config)

    @patch('galleria.orchestrator.serve.ConfigManager')
    @patch('galleria.orchestrator.serve.GalleriaBuilder')
    @patch('galleria.orchestrator.serve.GalleriaHTTPServer')
    @patch('galleria.orchestrator.serve.FileWatcher')
    def test_execute_skips_generation_when_no_generate_true(self, mock_watcher, mock_server, mock_builder, mock_config):
        """execute() skips gallery generation when no_generate=True."""
        # Arrange
        config_path = Path("/test/config/galleria.json")
        mock_config_manager = mock_config.return_value
        mock_galleria_config = {"output": {"directory": "/test/output"}}
        mock_config_manager.load_galleria_config.return_value = mock_galleria_config
        mock_galleria_builder = mock_builder.return_value

        orchestrator = ServeOrchestrator()

        # Act
        orchestrator.execute(config_path, no_generate=True)

        # Assert
        mock_galleria_builder.build.assert_not_called()

    @patch('galleria.orchestrator.serve.ConfigManager')
    @patch('galleria.orchestrator.serve.GalleriaBuilder')
    @patch('galleria.orchestrator.serve.GalleriaHTTPServer')
    @patch('galleria.orchestrator.serve.FileWatcher')
    def test_execute_starts_http_server_with_output_directory(self, mock_watcher, mock_server, mock_builder, mock_config):
        """execute() starts HTTP server pointing to gallery output directory."""
        # Arrange
        config_path = Path("/test/config/galleria.json")
        output_dir = Path("/test/output")
        mock_config_manager = mock_config.return_value
        mock_galleria_config = {"output": {"directory": str(output_dir)}}
        mock_config_manager.load_galleria_config.return_value = mock_galleria_config
        mock_http_server = mock_server.return_value

        orchestrator = ServeOrchestrator()

        # Act
        orchestrator.execute(config_path, host="localhost", port=8080)

        # Assert
        mock_server.assert_called_once_with(output_dir, "localhost", 8080)
        mock_http_server.start.assert_called_once_with(verbose=False)

    @patch('galleria.orchestrator.serve.ConfigManager')
    @patch('galleria.orchestrator.serve.GalleriaBuilder')
    @patch('galleria.orchestrator.serve.GalleriaHTTPServer')
    @patch('galleria.orchestrator.serve.FileWatcher')
    def test_execute_passes_verbose_flag_to_server(self, mock_watcher, mock_server, mock_builder, mock_config):
        """execute() passes verbose flag to HTTP server."""
        # Arrange
        config_path = Path("/test/config/galleria.json")
        mock_config_manager = mock_config.return_value
        mock_galleria_config = {"output": {"directory": "/test/output"}}
        mock_config_manager.load_galleria_config.return_value = mock_galleria_config
        mock_http_server = mock_server.return_value

        orchestrator = ServeOrchestrator()

        # Act
        orchestrator.execute(config_path, verbose=True)

        # Assert
        mock_http_server.start.assert_called_once_with(verbose=True)

    @patch('galleria.orchestrator.serve.ConfigManager')
    @patch('galleria.orchestrator.serve.GalleriaBuilder')
    @patch('galleria.orchestrator.serve.GalleriaHTTPServer')
    @patch('galleria.orchestrator.serve.FileWatcher')
    def test_execute_sets_up_file_watcher_by_default(self, mock_watcher, mock_server, mock_builder, mock_config):
        """execute() sets up file watcher by default (no_watch=False)."""
        # Arrange
        config_path = Path("/test/config/galleria.json")
        manifest_path = Path("/test/input/manifest.json")
        mock_config_manager = mock_config.return_value
        mock_galleria_config = {
            "input": {"manifest_path": str(manifest_path)},
            "output": {"directory": "/test/output"}
        }
        mock_config_manager.load_galleria_config.return_value = mock_galleria_config
        mock_file_watcher = mock_watcher.return_value

        # Mock rebuild callback
        def mock_rebuild_callback():
            pass

        orchestrator = ServeOrchestrator()

        # Act
        orchestrator.execute(config_path, no_watch=False)

        # Assert
        # File watcher should be created with config and manifest paths
        expected_watched_paths = {config_path, manifest_path}
        mock_watcher.assert_called_once()
        call_args = mock_watcher.call_args
        assert call_args[0][0] == expected_watched_paths  # watched_paths
        assert callable(call_args[0][1])  # callback function
        mock_file_watcher.start.assert_called_once()

    @patch('galleria.orchestrator.serve.ConfigManager')
    @patch('galleria.orchestrator.serve.GalleriaBuilder')
    @patch('galleria.orchestrator.serve.GalleriaHTTPServer')
    @patch('galleria.orchestrator.serve.FileWatcher')
    def test_execute_skips_file_watching_when_no_watch_true(self, mock_watcher, mock_server, mock_builder, mock_config):
        """execute() skips file watcher setup when no_watch=True."""
        # Arrange
        config_path = Path("/test/config/galleria.json")
        mock_config_manager = mock_config.return_value
        mock_galleria_config = {"output": {"directory": "/test/output"}}
        mock_config_manager.load_galleria_config.return_value = mock_galleria_config

        orchestrator = ServeOrchestrator()

        # Act
        orchestrator.execute(config_path, no_watch=True)

        # Assert
        mock_watcher.assert_not_called()

    @patch('galleria.orchestrator.serve.ConfigManager')
    @patch('galleria.orchestrator.serve.GalleriaBuilder')
    @patch('galleria.orchestrator.serve.GalleriaHTTPServer')
    @patch('galleria.orchestrator.serve.FileWatcher')
    def test_execute_rebuild_callback_regenerates_gallery_on_file_change(self, mock_watcher, mock_server, mock_builder, mock_config):
        """execute() file watcher callback regenerates gallery when files change."""
        # Arrange
        config_path = Path("/test/config/galleria.json")
        manifest_path = Path("/test/input/manifest.json")
        mock_config_manager = mock_config.return_value
        mock_galleria_config = {
            "input": {"manifest_path": str(manifest_path)},
            "output": {"directory": "/test/output"}
        }
        mock_config_manager.load_galleria_config.return_value = mock_galleria_config
        mock_galleria_builder = mock_builder.return_value

        orchestrator = ServeOrchestrator()
        orchestrator.execute(config_path, no_watch=False)

        # Get the callback function that was passed to FileWatcher
        callback = mock_watcher.call_args[0][1]

        # Act: Simulate file change by calling the callback
        callback(config_path)

        # Assert: Gallery should be regenerated
        # build() should be called twice: once for initial generation, once for rebuild
        assert mock_galleria_builder.build.call_count == 2
        # Both calls should use the same config
        expected_calls = [call(mock_galleria_config), call(mock_galleria_config)]
        mock_galleria_builder.build.assert_has_calls(expected_calls)

    @patch('galleria.orchestrator.serve.ConfigManager')
    @patch('galleria.orchestrator.serve.GalleriaBuilder')
    @patch('galleria.orchestrator.serve.GalleriaHTTPServer')
    def test_execute_handles_configuration_errors_gracefully(self, mock_server, mock_builder, mock_config):
        """execute() raises ServeError when configuration loading fails."""
        # Arrange
        config_path = Path("/test/config/galleria.json")
        mock_config_manager = mock_config.return_value
        mock_config_manager.load_galleria_config.side_effect = Exception("Config not found")

        orchestrator = ServeOrchestrator()

        # Act & Assert
        with pytest.raises(Exception, match="Config not found"):
            orchestrator.execute(config_path)

    @patch('galleria.orchestrator.serve.ConfigManager')
    @patch('galleria.orchestrator.serve.GalleriaBuilder')
    @patch('galleria.orchestrator.serve.GalleriaHTTPServer')
    @patch('galleria.orchestrator.serve.FileWatcher')
    def test_execute_extracts_output_directory_from_config(self, mock_watcher, mock_server, mock_builder, mock_config):
        """execute() extracts output directory from galleria config for server."""
        # Arrange
        config_path = Path("/test/config/galleria.json")
        expected_output_dir = Path("/custom/output/path")
        mock_config_manager = mock_config.return_value
        mock_galleria_config = {"output": {"directory": str(expected_output_dir)}}
        mock_config_manager.load_galleria_config.return_value = mock_galleria_config

        orchestrator = ServeOrchestrator()

        # Act
        orchestrator.execute(config_path)

        # Assert
        mock_server.assert_called_once_with(expected_output_dir, "127.0.0.1", 8000)

    @patch('galleria.orchestrator.serve.ConfigManager')
    @patch('galleria.orchestrator.serve.GalleriaBuilder')
    @patch('galleria.orchestrator.serve.GalleriaHTTPServer')
    @patch('galleria.orchestrator.serve.FileWatcher')
    def test_execute_extracts_manifest_path_from_config_for_watching(self, mock_watcher, mock_server, mock_builder, mock_config):
        """execute() extracts manifest path from config to add to file watcher."""
        # Arrange
        config_path = Path("/test/config/galleria.json")
        expected_manifest_path = Path("/custom/input/photos.json")
        mock_config_manager = mock_config.return_value
        mock_galleria_config = {
            "input": {"manifest_path": str(expected_manifest_path)},
            "output": {"directory": "/test/output"}
        }
        mock_config_manager.load_galleria_config.return_value = mock_galleria_config

        orchestrator = ServeOrchestrator()

        # Act
        orchestrator.execute(config_path, no_watch=False)

        # Assert
        expected_watched_paths = {config_path, expected_manifest_path}
        call_args = mock_watcher.call_args
        assert call_args[0][0] == expected_watched_paths

    @patch('galleria.orchestrator.serve.ConfigManager')
    @patch('galleria.orchestrator.serve.GalleriaBuilder')
    @patch('galleria.orchestrator.serve.GalleriaHTTPServer')
    @patch('galleria.orchestrator.serve.FileWatcher')
    def test_execute_graceful_shutdown_stops_watcher_and_server(self, mock_watcher, mock_server, mock_builder, mock_config):
        """execute() stops file watcher and HTTP server on shutdown."""
        # Arrange
        config_path = Path("/test/config/galleria.json")
        mock_config_manager = mock_config.return_value
        mock_galleria_config = {"output": {"directory": "/test/output"}}
        mock_config_manager.load_galleria_config.return_value = mock_galleria_config
        mock_file_watcher = mock_watcher.return_value
        mock_http_server = mock_server.return_value

        # Mock server.start() to raise KeyboardInterrupt (simulating Ctrl+C)
        mock_http_server.start.side_effect = KeyboardInterrupt()

        orchestrator = ServeOrchestrator()

        # Act
        try:
            orchestrator.execute(config_path, no_watch=False)
        except KeyboardInterrupt:
            pass  # Expected

        # Assert
        mock_file_watcher.stop.assert_called_once()
        mock_http_server.stop.assert_called_once()
