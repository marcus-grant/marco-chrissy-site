"""Serve orchestrator for coordinating build and proxy operations."""

import http.server
import signal
import threading
import time

from build.orchestrator import BuildOrchestrator
from serve.proxy import ProxyHTTPHandler, SiteServeProxy


class ServeOrchestrator:
    """Orchestrates site serving by coordinating build and proxy operations."""

    def __init__(self) -> None:
        """Initialize ServeOrchestrator."""
        self.build_orchestrator = BuildOrchestrator()
        self.proxy: SiteServeProxy | None = None
        self.server: http.server.HTTPServer | None = None

        # Coordination between signal handler and server thread
        self._stop_event = threading.Event()
        self._server_thread: threading.Thread | None = None

    # ------------------------------------------------------------------
    # Signal handling / server loop helpers
    # ------------------------------------------------------------------

    def _signal_handler(self, signum, frame) -> None:  # type: ignore[override]
        """Handle shutdown signals by triggering a graceful stop."""
        print(f"\nReceived signal {signum}, shutting down server...")
        self._stop_event.set()

    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for clean shutdown."""
        # These will run in the main thread; they should *not* call shutdown()
        # directly, just signal the orchestrator to stop.
        signal.signal(signal.SIGINT, self._signal_handler)  # Ctrl+C
        signal.signal(signal.SIGTERM, self._signal_handler)  # Termination request

    def _run_http_server(self) -> None:
        """Run the HTTP server loop in a background thread."""
        if not self.server:
            return

        try:
            # This blocks until shutdown() is called from another thread.
            self.server.serve_forever()
        except BaseException as exc:  # pragma: no cover (defensive)
            # Any unexpected error from the server loop should cause the main
            # loop to exit as well.
            print(f"HTTP server error: {exc!r}")
            self._stop_event.set()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def cleanup(self) -> None:
        """Clean up server resources."""
        if self.proxy:
            try:
                self.proxy.cleanup()
            except Exception as exc:  # pragma: no cover
                print(f"Error during proxy cleanup: {exc!r}")

        if self.server:
            try:
                # Must be called from a different thread than serve_forever().
                self.server.shutdown()
                self.server.server_close()
            except Exception as exc:  # pragma: no cover
                print(f"Error during server shutdown: {exc!r}")

    def start(
        self,
        host: str,
        port: int,
        galleria_port: int,
        pelican_port: int,
        no_generate: bool = False,
    ) -> None:
        """Start the site serve process with proxy coordination.

        Args:
            host: Host to bind proxy server
            port: Port for proxy server
            galleria_port: Port for Galleria server
            pelican_port: Port for Pelican server
            no_generate: If True, skip gallery generation
        """
        # Set up signal handlers for clean shutdown
        self._setup_signal_handlers()

        # Build site with localhost URL override for development
        localhost_url = f"http://{host}:{port}"

        try:
            # Override site URL for development
            self.build_orchestrator.execute(override_site_url=localhost_url)
        except Exception:
            # Continue with serve using existing output if build fails
            pass

        # Create proxy instance and store reference
        self.proxy = SiteServeProxy(
            galleria_port=galleria_port,
            pelican_port=pelican_port,
            static_pics_dir="output/pics",
        )

        # Start backend servers
        self.proxy.start_galleria_server(
            "config/galleria.json",
            no_generate=no_generate,
        )
        self.proxy.start_pelican_server("output")

        # Link proxy to handler class
        ProxyHTTPHandler.proxy = self.proxy

        # Create HTTP server
        self.server = http.server.HTTPServer((host, port), ProxyHTTPHandler)

        # Run HTTP server in a background thread
        self._server_thread = threading.Thread(
            target=self._run_http_server,
            name="serve-orchestrator-http-server",
            daemon=True,
        )
        self._server_thread.start()

        print(f"Server starting on {host}:{port}")

        # Main thread: wait for stop event or Ctrl+C
        try:
            while not self._stop_event.is_set():
                time.sleep(0.2)
        except KeyboardInterrupt:
            # Handles Ctrl+C in local dev even if signals behave differently
            print("\nKeyboard interrupt received, shutting down server...")
            self._stop_event.set()
        finally:
            # Graceful shutdown
            self.cleanup()

            # Ensure server thread has exited
            if self._server_thread is not None:
                self._server_thread.join(timeout=5)
