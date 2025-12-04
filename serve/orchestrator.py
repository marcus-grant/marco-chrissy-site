"""Serve orchestrator for coordinating build and proxy operations."""

import http.server

from build.orchestrator import BuildOrchestrator
from serve.proxy import ProxyHTTPHandler, SiteServeProxy


class ServeOrchestrator:
    """Orchestrates site serving by coordinating build and proxy operations."""

    def __init__(self) -> None:
        """Initialize ServeOrchestrator."""
        self.build_orchestrator = BuildOrchestrator()

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
        # Build site with localhost URL override for development
        localhost_url = f"http://{host}:{port}"

        try:
            # Override site URL for development
            self.build_orchestrator.execute(override_site_url=localhost_url)
        except Exception:
            # Continue with serve using existing output if build fails
            pass

        # Create proxy instance
        proxy = SiteServeProxy(
            galleria_port=galleria_port,
            pelican_port=pelican_port,
            static_pics_dir="output/pics"
        )

        # Start backend servers
        proxy.start_galleria_server("config/galleria.json", no_generate=no_generate)
        proxy.start_pelican_server("output")

        # Link proxy to handler class
        ProxyHTTPHandler.proxy = proxy

        # Create and start HTTP server
        server = http.server.HTTPServer((host, port), ProxyHTTPHandler)

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            # Shutting down server
            proxy.cleanup()
            server.shutdown()
