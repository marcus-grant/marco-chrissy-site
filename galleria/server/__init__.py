"""Static file server for galleria development."""

from pathlib import Path


class GalleriaHTTPServer:
    """HTTP server for serving static gallery files during development."""

    def __init__(self, output_directory: Path, host: str = "127.0.0.1", port: int = 8000):
        """Initialize the HTTP server.

        Args:
            output_directory: Directory containing generated gallery files
            host: Host address to bind server
            port: Port number for server
        """
        self.output_directory = output_directory
        self.host = host
        self.port = port
        # TODO: Initialize HTTP server components

    def start(self, verbose: bool = False) -> None:
        """Start the HTTP server.

        Args:
            verbose: Enable verbose logging

        Raises:
            ServerError: If server fails to start
        """
        # TODO: Implement HTTP server startup using SimpleHTTPRequestHandler
        # - Serve files from output_directory
        # - Handle root requests (/ -> /page_1.html)
        # - Add CORS headers for development
        # - Custom request logging based on verbose flag
        raise NotImplementedError("GalleriaHTTPServer.start not yet implemented")

    def stop(self) -> None:
        """Stop the HTTP server gracefully."""
        # TODO: Implement graceful server shutdown
        raise NotImplementedError("GalleriaHTTPServer.stop not yet implemented")
