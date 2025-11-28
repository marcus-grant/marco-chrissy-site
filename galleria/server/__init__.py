"""Static file server for galleria development."""

import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any


class GalleriaRequestHandler(SimpleHTTPRequestHandler):
    """Custom request handler with CORS headers and root redirect."""

    def end_headers(self) -> None:
        """Add CORS headers before ending headers."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self) -> None:
        """Handle GET requests with root path redirect to page_1.html."""
        if self.path == "/" and Path("page_1.html").exists():
            self.send_response(302)
            self.send_header('Location', '/page_1.html')
            self.end_headers()
            return

        super().do_GET()

    def log_request(self, code: int = '-', size: int | str = '-') -> None:
        """Log requests with custom format for development server."""
        self.log_message(f"Galleria server: {code} {self.path}")


class GalleriaHTTPServer:
    """HTTP server for serving static gallery files during development."""

    def __init__(self, output_directory: Path, host: str = "127.0.0.1", port: int = 8000):
        """Initialize the HTTP server.

        Args:
            output_directory: Directory containing generated gallery files
            host: Host address to bind server
            port: Port number for server

        Raises:
            ValueError: If output_directory doesn't exist or isn't a directory
        """
        if not output_directory.exists():
            raise ValueError(f"Output directory {output_directory} does not exist")
        if not output_directory.is_dir():
            raise ValueError(f"Path {output_directory} is not a directory")

        self.output_directory = output_directory
        self.host = host
        self.port = port
        self._server: HTTPServer | None = None

    def start(self, verbose: bool = False) -> None:
        """Start the HTTP server.

        Args:
            verbose: Enable verbose logging

        Raises:
            ServerError: If server fails to start
        """
        # Change to output directory so SimpleHTTPRequestHandler serves from there
        os.chdir(str(self.output_directory))

        # Create and start the HTTP server
        self._server = HTTPServer((self.host, self.port), GalleriaRequestHandler)
        self._server.serve_forever()

    def stop(self) -> None:
        """Stop the HTTP server gracefully."""
        if self._server is not None:
            self._server.shutdown()

    def __enter__(self) -> "GalleriaHTTPServer":
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.stop()
