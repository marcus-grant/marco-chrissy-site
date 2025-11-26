"""Galleria CLI entry point."""

import threading
import time
from pathlib import Path

import click

from .config import GalleriaConfig
from .manager.pipeline import PipelineManager
from .plugins.base import PluginContext
from .plugins.css import BasicCSSPlugin
from .plugins.pagination import BasicPaginationPlugin
from .plugins.processors.thumbnail import ThumbnailProcessorPlugin
from .plugins.providers.normpic import NormPicProviderPlugin
from .plugins.template import BasicTemplatePlugin


@click.group()
@click.version_option(version="0.1.0", prog_name="galleria")
def cli():
    """Galleria static gallery generator."""
    pass


@cli.command()
@click.option(
    "--config", "-c",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to galleria configuration file"
)
@click.option(
    "--output", "-o",
    type=click.Path(path_type=Path),
    help="Output directory for generated gallery (overrides config)"
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Enable verbose output"
)
def generate(config: Path, output: Path | None, verbose: bool):
    """Generate static gallery from configuration file.

    This command processes a photo collection through the galleria plugin
    pipeline to generate a static HTML gallery with thumbnails.
    """
    if verbose:
        click.echo(f"Loading configuration from: {config}")
        if output:
            click.echo(f"Output directory override: {output}")

    # Load and validate configuration
    try:
        galleria_config = GalleriaConfig.from_file(config, output)
        galleria_config.validate_paths()
    except click.ClickException:
        raise  # Re-raise click exceptions as-is
    except Exception as e:
        raise click.ClickException(f"Configuration error: {e}") from e

    if verbose:
        click.echo(f"Manifest path: {galleria_config.input_manifest_path}")
        click.echo(f"Output directory: {galleria_config.output_directory}")
        click.echo("Configuration loaded and validated successfully")

    # Create output directory
    galleria_config.output_directory.mkdir(parents=True, exist_ok=True)

    # Initialize pipeline manager and register plugins
    if verbose:
        click.echo("Initializing plugin pipeline...")

    pipeline = PipelineManager()
    pipeline.registry.register(NormPicProviderPlugin(), "provider")
    pipeline.registry.register(ThumbnailProcessorPlugin(), "processor")
    pipeline.registry.register(BasicPaginationPlugin(), "transform")
    pipeline.registry.register(BasicTemplatePlugin(), "template")
    pipeline.registry.register(BasicCSSPlugin(), "css")

    # Define pipeline stages
    stages = [
        ("provider", "normpic-provider"),
        ("processor", "thumbnail-processor"),
        ("transform", "basic-pagination"),
        ("template", "basic-template"),
        ("css", "basic-css")
    ]

    # Create initial context
    initial_context = PluginContext(
        input_data={"manifest_path": str(galleria_config.input_manifest_path)},
        config=galleria_config.to_pipeline_config(),
        output_dir=galleria_config.output_directory
    )

    # Execute pipeline with progress reporting
    if verbose:
        click.echo("Executing plugin pipeline:")

    try:
        for i, (stage, plugin_name) in enumerate(stages, 1):
            if verbose:
                click.echo(f"  [{i}/{len(stages)}] Running {stage} ({plugin_name})...")

        # Execute complete pipeline
        final_result = pipeline.execute_stages(stages, initial_context)

        if not final_result.success:
            error_msg = "Pipeline execution failed:\n" + "\n".join(final_result.errors)
            raise click.ClickException(error_msg)

        if verbose:
            click.echo("Pipeline execution completed successfully")

        # Write generated files to disk
        final_output = final_result.output_data
        collection_name = final_output.get("collection_name", "gallery")

        # Write HTML files
        if "html_files" in final_output:
            for html_file in final_output["html_files"]:
                html_path = galleria_config.output_directory / html_file["filename"]
                html_path.write_text(html_file["content"], encoding="utf-8")
                if verbose:
                    click.echo(f"  Wrote: {html_path}")

            page_count = len(final_output["html_files"])
            click.echo(f"Generated {page_count} HTML pages for '{collection_name}'")

        # Write CSS files
        if "css_files" in final_output:
            for css_file in final_output["css_files"]:
                css_path = galleria_config.output_directory / css_file["filename"]
                css_path.write_text(css_file["content"], encoding="utf-8")
                if verbose:
                    click.echo(f"  Wrote: {css_path}")

            css_count = len(final_output["css_files"])
            click.echo(f"Generated {css_count} CSS files")

        if "thumbnail_count" in final_output:
            thumb_count = final_output["thumbnail_count"]
            click.echo(f"Processed {thumb_count} thumbnails")

        click.echo(f"Gallery generated successfully in: {galleria_config.output_directory}")

    except Exception as e:
        if isinstance(e, click.ClickException):
            raise
        raise click.ClickException(f"Pipeline execution error: {e}") from e


@cli.command()
@click.option(
    "--config", "-c",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to galleria configuration file"
)
@click.option(
    "--port", "-p",
    type=int,
    default=8000,
    help="Port number for development server (default: 8000)"
)
@click.option(
    "--host", "-h",
    type=str,
    default="127.0.0.1",
    help="Host address to bind server (default: 127.0.0.1)"
)
@click.option(
    "--no-generate",
    is_flag=True,
    help="Skip gallery generation phase (serve existing files only)"
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Enable verbose output"
)
@click.option(
    "--no-watch",
    is_flag=True,
    help="Disable file watching and hot reload functionality"
)
def serve(config: Path, port: int, host: str, no_generate: bool, verbose: bool, no_watch: bool):
    """Start development server for static gallery.

    This command generates the gallery (unless --no-generate is specified)
    and serves it on a local development server with hot reload capability.
    """
    import http.server
    import socketserver

    if verbose:
        click.echo("Starting galleria development server...")
        click.echo(f"Config: {config}")
        click.echo(f"Server: http://{host}:{port}")
        if no_generate:
            click.echo("Skipping gallery generation (--no-generate)")

    # Validate port range
    if not (1024 <= port <= 65535):
        raise click.ClickException(f"Port must be between 1024 and 65535, got: {port}")

    # Load configuration to determine output directory
    try:
        from .config import GalleriaConfig
        galleria_config = GalleriaConfig.from_file(config)
        galleria_config.validate_paths()
        output_directory = galleria_config.output_directory

        if verbose:
            click.echo(f"Output directory: {output_directory}")

    except Exception as e:
        raise click.ClickException(f"Configuration error: {e}") from e

    # Generation phase (unless --no-generate)
    if not no_generate:
        if verbose:
            click.echo("Generating gallery before serving...")

        try:
            # Use subprocess to call generate command for better isolation
            import subprocess
            import sys

            generate_cmd = [
                sys.executable, "-m", "galleria", "generate",
                "--config", str(config)
            ]
            if verbose:
                generate_cmd.append("--verbose")

            result = subprocess.run(generate_cmd,
                                  capture_output=True,
                                  text=True,
                                  cwd=Path.cwd())

            if result.returncode != 0:
                error_msg = f"Generation failed: {result.stderr or result.stdout}"
                raise click.ClickException(error_msg)

            if verbose:
                click.echo("Gallery generation completed")
                if result.stdout:
                    click.echo(result.stdout)

        except subprocess.SubprocessError as e:
            raise click.ClickException(f"Generation subprocess failed: {e}") from e
        except Exception as e:
            if isinstance(e, click.ClickException):
                raise
            raise click.ClickException(f"Generation failed: {e}") from e

    # Ensure output directory exists
    if not output_directory.exists():
        raise click.ClickException(f"Output directory does not exist: {output_directory}")

    # Setup file watching for hot reload (unless disabled)
    watch_files = set()
    file_watcher_thread = None

    if not no_watch:
        # Files to watch for changes
        watch_files.add(config)
        if galleria_config.input_manifest_path.exists():
            watch_files.add(galleria_config.input_manifest_path)

        if verbose and watch_files:
            click.echo(f"Watching files for changes: {[str(f) for f in watch_files]}")

        # Start file watcher thread
        def file_watcher():
            """Watch files for changes and trigger regeneration."""
            file_mtimes = {}

            # Initialize modification times
            for file_path in watch_files:
                try:
                    if file_path.exists():
                        file_mtimes[file_path] = file_path.stat().st_mtime
                except OSError:
                    if verbose:
                        click.echo(f"Warning: Could not get mtime for {file_path}")

            while True:
                try:
                    time.sleep(1)  # Check every second

                    # Check for file changes
                    for file_path in watch_files:
                        try:
                            if file_path.exists():
                                current_mtime = file_path.stat().st_mtime
                                if file_path not in file_mtimes or current_mtime > file_mtimes[file_path]:
                                    if verbose:
                                        click.echo(f"File changed: {file_path}")
                                        click.echo("Regenerating gallery...")

                                    # Trigger regeneration
                                    regenerate_gallery(config, verbose)
                                    file_mtimes[file_path] = current_mtime

                                    if verbose:
                                        click.echo("Gallery regeneration completed")
                        except OSError:
                            # File might have been deleted or inaccessible
                            if file_path in file_mtimes:
                                del file_mtimes[file_path]

                except Exception as e:
                    if verbose:
                        click.echo(f"File watcher error: {e}")

        def regenerate_gallery(config_path, verbose_mode):
            """Regenerate gallery when files change."""
            try:
                import subprocess
                import sys

                generate_cmd = [
                    sys.executable, "-m", "galleria", "generate",
                    "--config", str(config_path)
                ]
                if verbose_mode:
                    generate_cmd.append("--verbose")

                result = subprocess.run(generate_cmd,
                                      capture_output=True,
                                      text=True,
                                      cwd=Path.cwd())

                if result.returncode != 0 and verbose_mode:
                    click.echo(f"Regeneration failed: {result.stderr}")

            except Exception as e:
                if verbose_mode:
                    click.echo(f"Regeneration error: {e}")

        if watch_files:
            file_watcher_thread = threading.Thread(target=file_watcher, daemon=True)
            file_watcher_thread.start()

            if verbose:
                click.echo("File watcher started (hot reload enabled)")

    # Setup HTTP server
    class GalleriaHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        """Custom request handler with gallery-specific behavior."""

        def __init__(self, *args, **kwargs):
            # Change to output directory for serving files
            super().__init__(*args, directory=str(output_directory), **kwargs)

        def end_headers(self):
            # Add CORS headers for local development
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')
            super().end_headers()

        def log_message(self, format, *args):
            # Only log in verbose mode
            if verbose:
                super().log_message(format, *args)

        def do_GET(self):
            # Serve index.html for root requests
            if self.path == '/':
                self.path = '/page_1.html'
            super().do_GET()

    # Start server with improved error handling
    try:
        # Allow port reuse to avoid "Address already in use" errors
        socketserver.TCPServer.allow_reuse_address = True

        with socketserver.TCPServer((host, port), GalleriaHTTPRequestHandler) as httpd:
            actual_host, actual_port = httpd.server_address

            if verbose:
                click.echo(f"Server started at http://{actual_host}:{actual_port}")
                click.echo("Press Ctrl+C to stop the server")
            else:
                click.echo(f"Serving gallery at http://{actual_host}:{actual_port}")

            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                if verbose:
                    click.echo("\nShutting down server...")
                httpd.shutdown()

    except OSError as e:
        if e.errno == 98:  # Address already in use
            raise click.ClickException(f"Port {port} is already in use. Try a different port with --port")
        elif e.errno == 13:  # Permission denied
            raise click.ClickException(f"Permission denied for port {port}. Try a port > 1024 or run with sudo")
        else:
            raise click.ClickException(f"Failed to start server on {host}:{port}: {e}") from e


def main():
    """Entry point for the galleria CLI."""
    cli()


if __name__ == "__main__":
    main()

