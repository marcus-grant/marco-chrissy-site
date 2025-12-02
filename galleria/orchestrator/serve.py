"""ServeOrchestrator for coordinating the gallery development server."""

from pathlib import Path

from build.config_manager import ConfigManager
from build.galleria_builder import GalleriaBuilder
from galleria.server import GalleriaHTTPServer
from galleria.util.watcher import FileWatcher


class ServeOrchestrator:
    """Orchestrates the galleria development server with file watching and hot reload."""

    def __init__(self):
        """Initialize ServeOrchestrator."""
        self.config_manager = ConfigManager()
        self.galleria_builder = GalleriaBuilder()
        self._file_watcher = None
        self._http_server = None

    def execute(
        self,
        config_path: Path,
        host: str = "127.0.0.1",
        port: int = 8000,
        no_generate: bool = False,
        no_watch: bool = False,
        verbose: bool = False,
    ) -> bool:
        """Execute the complete serve process.

        Args:
            config_path: Path to galleria configuration file
            host: Host address to bind server
            port: Port number for development server
            no_generate: Skip gallery generation phase
            no_watch: Disable file watching and hot reload
            verbose: Enable verbose output

        Returns:
            True if successful (never returns False, raises on error)

        Raises:
            ServeError: If any step of the serve process fails
        """
        try:
            # 1. Load and validate configuration using injected ConfigManager
            raw_config = self.config_manager.load_galleria_config(config_path)

            # Extract needed paths from config data
            output_dir = Path(raw_config["output_dir"])
            manifest_path = Path(raw_config["manifest_path"])

            # 2. Generate gallery (unless no_generate)
            if not no_generate:
                # Transform config for GalleriaBuilder
                builder_config = {
                    "manifest_path": raw_config["manifest_path"],
                    "output_dir": str(output_dir),
                    **{
                        k: v
                        for k, v in raw_config.items()
                        if k not in ["manifest_path", "output_dir"]
                    },
                }
                self.galleria_builder.build(builder_config, config_path.parent)

            # output_dir and manifest_path already extracted from config above

            # 3. Setup file watcher (unless no_watch)
            if not no_watch:
                self._setup_file_watcher(config_path, manifest_path, raw_config)

            # 4. Start HTTP server
            self._http_server = GalleriaHTTPServer(output_dir, host, port)
            self._http_server.start(verbose=verbose)

            return True

        except KeyboardInterrupt:
            # 5. Handle shutdown gracefully
            self._cleanup()
            raise
        except Exception:
            self._cleanup()
            raise

    def _setup_file_watcher(
        self, config_path: Path, manifest_path: Path, raw_config: dict
    ) -> None:
        """Setup file watcher for hot reload functionality.

        Args:
            config_path: Path to galleria configuration file
            manifest_path: Path to photo manifest file
            raw_config: Raw configuration dict
        """
        # Determine paths to watch
        watched_paths = {config_path, manifest_path}

        # Create rebuild callback that regenerates gallery
        def rebuild_callback(changed_path: Path) -> None:
            """Callback to regenerate gallery when files change."""
            try:
                # Reload config in case it changed using ConfigManager
                updated_raw_config = self.config_manager.load_galleria_config(
                    config_path
                )

                # Extract updated output directory
                updated_output_dir = Path(updated_raw_config["output_dir"])

                # Transform config for GalleriaBuilder
                updated_builder_config = {
                    "manifest_path": updated_raw_config["manifest_path"],
                    "output_dir": str(updated_output_dir),
                    **{
                        k: v
                        for k, v in updated_raw_config.items()
                        if k not in ["manifest_path", "output_dir"]
                    },
                }
                self.galleria_builder.build(updated_builder_config, config_path.parent)
            except Exception:
                # Gracefully handle rebuild errors to keep server running
                pass

        # Start file watcher
        self._file_watcher = FileWatcher(watched_paths, rebuild_callback)
        self._file_watcher.start()

    def _cleanup(self) -> None:
        """Clean up file watcher and HTTP server."""
        if self._file_watcher:
            self._file_watcher.stop()

        if self._http_server:
            self._http_server.stop()
