"""File watcher for detecting configuration and manifest changes."""

from collections.abc import Callable
from pathlib import Path


class FileWatcher:
    """Watches files for changes and triggers callbacks for hot reload functionality."""

    def __init__(self, watched_paths: set[Path], callback: Callable[[Path], None]):
        """Initialize the file watcher.

        Args:
            watched_paths: Set of file paths to monitor for changes
            callback: Function to call when a file changes (receives changed path)
        """
        self.watched_paths = watched_paths
        self.callback = callback
        self._running = False
        # TODO: Initialize watchdog observer

    def start(self) -> None:
        """Start watching files for changes.

        Raises:
            WatcherError: If watcher fails to start
        """
        # TODO: Implement file watching using watchdog library
        # - Monitor galleria config file
        # - Monitor manifest file
        # - Monitor template directories
        # - Monitor plugin directories
        # - Call callback when changes detected
        raise NotImplementedError("FileWatcher.start not yet implemented")

    def stop(self) -> None:
        """Stop watching files."""
        # TODO: Implement graceful watcher shutdown
        self._running = False
        raise NotImplementedError("FileWatcher.stop not yet implemented")

    def is_running(self) -> bool:
        """Check if watcher is currently running."""
        return self._running

    def add_path(self, path: Path) -> None:
        """Add a new path to watch.

        Args:
            path: File or directory path to monitor
        """
        # TODO: Dynamically add new paths to watch
        self.watched_paths.add(path)
        raise NotImplementedError("FileWatcher.add_path not yet implemented")

    def remove_path(self, path: Path) -> None:
        """Remove a path from watching.

        Args:
            path: Path to stop monitoring
        """
        # TODO: Dynamically remove paths from watching
        self.watched_paths.discard(path)
        raise NotImplementedError("FileWatcher.remove_path not yet implemented")
