"""HTTP proxy server classes for routing requests during serve."""

import http.client
import http.server
import mimetypes
import subprocess
from pathlib import Path
from typing import Literal


class SiteServeProxy:
    """Proxy server that routes requests to Galleria, Pelican, or static files."""

    def __init__(self, galleria_port: int, pelican_port: int, static_pics_dir: str):
        """Initialize SiteServeProxy.

        Args:
            galleria_port: Port for Galleria server
            pelican_port: Port for Pelican server
            static_pics_dir: Directory for static pic files
        """
        self.galleria_port = galleria_port
        self.pelican_port = pelican_port
        self.static_pics_dir = static_pics_dir
        self.galleria_process = None
        self.pelican_process = None

    def get_target_for_path(
        self, path: str
    ) -> tuple[Literal["galleria", "pelican", "static"], int | str]:
        """Determine target server/directory for given request path.

        Args:
            path: HTTP request path

        Returns:
            Tuple of (target_type, target_location) where:
            - target_type is "galleria", "pelican", or "static"
            - target_location is port number (int) or directory path (str)
        """
        if path.startswith("/galleries/"):
            return ("galleria", self.galleria_port)
        elif path.startswith("/pics/"):
            return ("static", self.static_pics_dir)
        else:
            return ("pelican", self.pelican_port)

    def start_galleria_server(self, config_path: str, no_generate: bool = False) -> None:
        """Start Galleria server subprocess.

        Args:
            config_path: Path to galleria config file
            no_generate: If True, pass --no-generate flag to galleria serve
        """
        cmd = [
            "uv",
            "run",
            "python",
            "-m",
            "galleria",
            "serve",
            "--config",
            config_path,
            "--port",
            str(self.galleria_port),
        ]
        if no_generate:
            cmd.append("--no-generate")
        self.galleria_process = subprocess.Popen(cmd)

    def start_pelican_server(self, output_dir: str) -> None:
        """Start Pelican server subprocess.

        Args:
            output_dir: Directory containing generated site content
        """
        cmd = [
            "pelican",
            "--listen",
            "--port",
            str(self.pelican_port),
            "--bind",
            "127.0.0.1",
            output_dir,
        ]
        self.pelican_process = subprocess.Popen(cmd)

    def cleanup(self) -> None:
        """Terminate running server subprocesses."""
        if self.galleria_process:
            self.galleria_process.terminate()
            try:
                self.galleria_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.galleria_process.kill()

        if self.pelican_process:
            self.pelican_process.terminate()
            try:
                self.pelican_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.pelican_process.kill()


class ProxyHTTPHandler(http.server.BaseHTTPRequestHandler):
    """HTTP handler that routes requests to appropriate servers."""

    def do_GET(self) -> None:
        """Handle GET requests by routing to appropriate target."""
        target_type, target_location = self.proxy.get_target_for_path(self.path)

        if target_type == "galleria":
            # Strip /galleries/collection/ prefix for Galleria server
            if self.path.startswith("/galleries/"):
                # Remove /galleries/collection/ keeping just the filename part
                path_parts = self.path.split("/", 3)  # ['', 'galleries', 'collection', 'filename']
                galleria_path = "/" + path_parts[3] if len(path_parts) > 3 else "/"
            else:
                galleria_path = self.path
            self.forward_to_server("127.0.0.1", target_location, galleria_path)
        elif target_type == "static":
            self.serve_static_file(target_location, self.path)
        elif target_type == "pelican":
            self.forward_to_server("127.0.0.1", target_location, self.path)

    def forward_to_server(self, host: str, port: int, path: str) -> None:
        """Forward HTTP request to target server."""
        try:
            conn = http.client.HTTPConnection(host, port)
            conn.request("GET", path)
            response = conn.getresponse()

            # Send response back to client
            self.send_response(response.status, response.reason)
            for header_name, header_value in response.getheaders():
                self.send_header(header_name, header_value)
            self.end_headers()

            # Forward response body
            self.wfile.write(response.read())
            conn.close()

        except OSError:
            self.send_error(502, "Bad Gateway - Target server unreachable")

    def serve_static_file(self, static_dir: str, path: str) -> None:
        """Serve static file from filesystem."""
        # Remove /pics/ prefix and construct file path
        if path.startswith("/pics/"):
            relative_path = path[6:]  # Remove "/pics/" prefix
        else:
            relative_path = path
        file_path = Path(static_dir) / relative_path

        if not file_path.exists():
            self.send_error(404, "File not found")
            return

        # Determine content type
        content_type, _ = mimetypes.guess_type(str(file_path))
        if content_type is None:
            content_type = "application/octet-stream"

        # Send file
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(file_path.read_bytes())
