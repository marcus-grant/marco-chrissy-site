"""Site serve command with proxy routing functionality."""

import subprocess
from typing import Literal

import click


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

    def get_target_for_path(self, path: str) -> tuple[Literal["galleria", "pelican", "static"], int | str]:
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

    def start_galleria_server(self, config_path: str) -> None:
        """Start Galleria server subprocess.

        Args:
            config_path: Path to galleria config file
        """
        cmd = [
            "uv", "run", "python", "-m", "galleria",
            "serve", config_path,
            "--port", str(self.galleria_port)
        ]
        self.galleria_process = subprocess.Popen(cmd)

    def start_pelican_server(self, output_dir: str) -> None:
        """Start Pelican server subprocess.

        Args:
            output_dir: Directory containing generated site content
        """
        cmd = [
            "pelican", "--listen",
            "--port", str(self.pelican_port),
            "--bind", "127.0.0.1",
            output_dir
        ]
        self.pelican_process = subprocess.Popen(cmd)

    def cleanup(self) -> None:
        """Terminate running server subprocesses."""
        if self.galleria_process:
            self.galleria_process.terminate()
        if self.pelican_process:
            self.pelican_process.terminate()


@click.command()
@click.option("--host", default="127.0.0.1", help="Host to bind proxy server")
@click.option("--port", default=8000, help="Port for proxy server")
@click.option("--galleria-port", default=8001, help="Port for Galleria server")
@click.option("--pelican-port", default=8002, help="Port for Pelican server")
def serve(host: str, port: int, galleria_port: int, pelican_port: int) -> None:
    """Start site serve proxy that coordinates Galleria and Pelican servers.

    Routes requests:
    - /galleries/* → Galleria server
    - /pics/* → Static file server
    - Everything else → Pelican server
    """
    # This is a placeholder - full implementation will be added in next iteration
    click.echo(f"Starting site serve proxy on {host}:{port}")
    click.echo(f"Galleria server will run on port {galleria_port}")
    click.echo(f"Pelican server will run on port {pelican_port}")
