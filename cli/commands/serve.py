"""Site serve command with proxy routing functionality."""


import click

from defaults import get_output_dir
from serve.orchestrator import ServeOrchestrator

from .build import build


@click.command()
@click.option("--host", default="127.0.0.1", help="Host to bind proxy server")
@click.option("--port", default=8000, help="Port for proxy server")
@click.option("--galleria-port", default=8001, help="Port for Galleria server")
@click.option("--pelican-port", default=8002, help="Port for Pelican server")
@click.option("--no-generate", is_flag=True, help="Skip gallery generation, serve existing galleries only")
def serve(host: str, port: int, galleria_port: int, pelican_port: int, no_generate: bool) -> None:
    """Start site serve proxy that coordinates Galleria and Pelican servers.

    Routes requests:
    - /galleries/* → Galleria server
    - /pics/* → Static file server
    - Everything else → Pelican server
    """
    click.echo(f"Starting site serve proxy at http://{host}:{port}")
    click.echo(f"Galleria server will run on port {galleria_port}")
    click.echo(f"Pelican server will run on port {pelican_port}")

    # Check if output directory exists, auto-call build if missing
    if not get_output_dir().exists():
        click.echo("Output directory missing - running build pipeline...")
        ctx = click.get_current_context()
        result = ctx.invoke(build)

        if result and hasattr(result, "exit_code") and result.exit_code != 0:
            click.echo("✗ Build failed - cannot start serve", err=True)
            ctx.exit(1)

        # Verify build created output directory
        if not get_output_dir().exists():
            click.echo("✗ Build completed but output directory still missing", err=True)
            ctx.exit(1)

        click.echo("✓ Build completed - starting serve")

    orchestrator = ServeOrchestrator()
    try:
        orchestrator.start(
            host=host,
            port=port,
            galleria_port=galleria_port,
            pelican_port=pelican_port,
            no_generate=no_generate,
        )
    except KeyboardInterrupt:
        click.echo("\nShutting down server...")
    except Exception as e:
        click.echo(f"Error starting serve: {e}", err=True)
