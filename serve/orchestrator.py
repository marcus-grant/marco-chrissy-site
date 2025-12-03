"""Serve orchestrator for coordinating build and proxy operations."""

from build.orchestrator import BuildOrchestrator


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
