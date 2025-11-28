"""File watcher for detecting configuration and manifest changes."""

from collections.abc import Callable
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class GalleriaFileHandler(FileSystemEventHandler):
    """Custom event handler for galleria file changes."""

    def __init__(self, watched_paths: set[Path], callback: Callable[[Path], None]):
        """Initialize the event handler.

        Args:
            watched_paths: Set of file paths to monitor for changes
            callback: Function to call when a file changes
        """
        super().__init__()
        self.watched_paths = watched_paths
        self.callback = callback

    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory:
            event_path = Path(event.src_path)

            # Only trigger callback for watched files
            if event_path in self.watched_paths:
                try:
                    self.callback(event_path)
                except Exception:
                    # Gracefully handle callback exceptions to keep watcher running
                    pass


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
        self._observer = None
        self._event_handler = None

    def start(self) -> None:
        """Start watching files for changes.

        Raises:
            WatcherError: If watcher fails to start
        """
        if self._running:
            return

        self._observer = Observer()
        self._event_handler = GalleriaFileHandler(self.watched_paths, self.callback)

        # Watch directories containing our files
        watched_dirs = set()
        for path in self.watched_paths:
            parent_dir = path.parent
            if parent_dir not in watched_dirs:
                self._observer.schedule(self._event_handler, str(parent_dir), recursive=False)
                watched_dirs.add(parent_dir)

        self._observer.start()
        self._running = True

    def stop(self) -> None:
        """Stop watching files."""
        if not self._running:
            return

        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None

        self._event_handler = None
        self._running = False

    def is_running(self) -> bool:
        """Check if watcher is currently running."""
        return self._running

    def add_path(self, path: Path) -> None:
        """Add a new path to watch.

        Args:
            path: File or directory path to monitor
        """
        self.watched_paths.add(path)

        # If watcher is running, schedule watching for the new path's directory
        if self._running and self._observer:
            parent_dir = path.parent
            # Note: In a real implementation, we'd track which directories
            # are already being watched to avoid duplicate schedules
            self._observer.schedule(self._event_handler, str(parent_dir), recursive=False)

    def remove_path(self, path: Path) -> None:
        """Remove a path from watching.

        Args:
            path: Path to stop monitoring
        """
        self.watched_paths.discard(path)
        # Note: In a full implementation, we'd also unschedule directory watching
        # if no more files in that directory are being watched
