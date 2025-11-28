"""Unit tests for galleria file watcher."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from galleria.util.watcher import FileWatcher


class TestFileWatcher:
    """Unit tests for FileWatcher class."""

    def test_file_watcher_initialization(self):
        """Test FileWatcher can be initialized with paths and callback."""
        watched_paths = {Path("/test/config.json"), Path("/test/manifest.json")}
        callback = MagicMock()

        watcher = FileWatcher(watched_paths, callback)

        assert watcher.watched_paths == watched_paths
        assert watcher.callback == callback
        assert not watcher.is_running()

    def test_file_watcher_start_initializes_watchdog_observer(self):
        """Test start() initializes and starts watchdog observer."""
        watched_paths = {Path("/test/config.json")}
        callback = MagicMock()
        watcher = FileWatcher(watched_paths, callback)

        with patch('galleria.util.watcher.Observer') as mock_observer_class:
            mock_observer = MagicMock()
            mock_observer_class.return_value = mock_observer

            watcher.start()

            # Should create observer and start it
            mock_observer_class.assert_called_once()
            mock_observer.start.assert_called_once()
            assert watcher.is_running()

    def test_file_watcher_stop_gracefully_shuts_down_observer(self):
        """Test stop() gracefully shuts down the watchdog observer."""
        watched_paths = {Path("/test/config.json")}
        callback = MagicMock()
        watcher = FileWatcher(watched_paths, callback)

        with patch('galleria.util.watcher.Observer') as mock_observer_class:
            mock_observer = MagicMock()
            mock_observer_class.return_value = mock_observer

            watcher.start()
            watcher.stop()

            # Should stop observer and join
            mock_observer.stop.assert_called_once()
            mock_observer.join.assert_called_once()
            assert not watcher.is_running()

    def test_file_watcher_calls_callback_when_file_changes(self):
        """Test watcher calls callback when a watched file changes."""
        watched_paths = {Path("/test/config.json")}
        callback = MagicMock()
        watcher = FileWatcher(watched_paths, callback)

        with patch('galleria.util.watcher.Observer') as mock_observer_class:
            with patch('galleria.util.watcher.FileSystemEventHandler') as mock_handler_class:
                mock_observer = MagicMock()
                mock_handler = MagicMock()
                mock_observer_class.return_value = mock_observer
                mock_handler_class.return_value = mock_handler

                watcher.start()

                # Simulate file change event
                from watchdog.events import FileModifiedEvent
                mock_event = FileModifiedEvent("/test/config.json")

                # Get the event handler that was registered
                observer_schedule_calls = mock_observer.schedule.call_args_list
                assert len(observer_schedule_calls) > 0
                event_handler = observer_schedule_calls[0][0][0]

                # Trigger the on_modified method
                event_handler.on_modified(mock_event)

                # Should call callback with changed path
                callback.assert_called_with(Path("/test/config.json"))

    def test_file_watcher_watches_multiple_paths(self):
        """Test watcher can monitor multiple file paths."""
        watched_paths = {
            Path("/test/config.json"),
            Path("/test/manifest.json"),
            Path("/test/template.html")
        }
        callback = MagicMock()
        watcher = FileWatcher(watched_paths, callback)

        with patch('galleria.util.watcher.Observer') as mock_observer_class:
            mock_observer = MagicMock()
            mock_observer_class.return_value = mock_observer

            watcher.start()

            # Should schedule watching for each unique directory
            schedule_calls = mock_observer.schedule.call_args_list

            # All paths are in /test directory, so should have one schedule call
            assert len(schedule_calls) >= 1

            # Verify event handler was created
            event_handler = schedule_calls[0][0][0]
            assert event_handler is not None

    def test_file_watcher_add_path_adds_new_path_to_watch(self):
        """Test add_path() adds new paths to the watched set."""
        watched_paths = {Path("/test/config.json")}
        callback = MagicMock()
        watcher = FileWatcher(watched_paths, callback)

        new_path = Path("/test/new_file.json")
        watcher.add_path(new_path)

        assert new_path in watcher.watched_paths
        assert len(watcher.watched_paths) == 2

    def test_file_watcher_remove_path_removes_path_from_watch(self):
        """Test remove_path() removes paths from the watched set."""
        watched_paths = {Path("/test/config.json"), Path("/test/manifest.json")}
        callback = MagicMock()
        watcher = FileWatcher(watched_paths, callback)

        remove_path = Path("/test/config.json")
        watcher.remove_path(remove_path)

        assert remove_path not in watcher.watched_paths
        assert len(watcher.watched_paths) == 1
        assert Path("/test/manifest.json") in watcher.watched_paths

    def test_file_watcher_handles_nonexistent_paths_gracefully(self):
        """Test watcher handles nonexistent file paths without error."""
        watched_paths = {Path("/nonexistent/config.json")}
        callback = MagicMock()
        watcher = FileWatcher(watched_paths, callback)

        with patch('galleria.util.watcher.Observer') as mock_observer_class:
            mock_observer = MagicMock()
            mock_observer_class.return_value = mock_observer

            # Should not raise exception
            watcher.start()
            watcher.stop()

    def test_file_watcher_ignores_events_for_unwatched_files(self):
        """Test watcher ignores file events for paths not in watched set."""
        watched_paths = {Path("/test/config.json")}
        callback = MagicMock()
        watcher = FileWatcher(watched_paths, callback)

        with patch('galleria.util.watcher.Observer') as mock_observer_class:
            mock_observer = MagicMock()
            mock_observer_class.return_value = mock_observer

            watcher.start()

            # Get the event handler
            event_handler = mock_observer.schedule.call_args_list[0][0][0]

            # Simulate change to unwatched file
            from watchdog.events import FileModifiedEvent
            unwatched_event = FileModifiedEvent("/test/unwatched.json")
            event_handler.on_modified(unwatched_event)

            # Callback should not be called for unwatched files
            callback.assert_not_called()

    def test_file_watcher_handles_callback_exceptions_gracefully(self):
        """Test watcher continues operating when callback raises exceptions."""
        watched_paths = {Path("/test/config.json")}
        callback = MagicMock(side_effect=Exception("Callback error"))
        watcher = FileWatcher(watched_paths, callback)

        with patch('galleria.util.watcher.Observer') as mock_observer_class:
            mock_observer = MagicMock()
            mock_observer_class.return_value = mock_observer

            watcher.start()

            # Get the event handler
            event_handler = mock_observer.schedule.call_args_list[0][0][0]

            # Simulate file change - should not crash watcher
            from watchdog.events import FileModifiedEvent
            mock_event = FileModifiedEvent("/test/config.json")

            # Should not raise exception even though callback does
            event_handler.on_modified(mock_event)

            # Watcher should still be running
            assert watcher.is_running()
