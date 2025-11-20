"""Galleria CLI entry point."""

import click
from pathlib import Path
from .config import GalleriaConfig


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
        raise click.ClickException(f"Configuration error: {e}")
    
    if verbose:
        click.echo(f"Manifest path: {galleria_config.input_manifest_path}")
        click.echo(f"Output directory: {galleria_config.output_directory}")
        click.echo(f"Pipeline stages configured: {len(galleria_config.pipeline.__dict__)} stages")
        click.echo("Configuration loaded and validated successfully")
        click.echo("Plugin orchestration not yet implemented (pending Commit 8d)")
    
    click.echo("galleria generate: Configuration system working correctly")


if __name__ == "__main__":
    cli()