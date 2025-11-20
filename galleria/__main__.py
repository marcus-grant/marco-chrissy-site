"""Galleria CLI entry point."""

import click
import json
from pathlib import Path


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
    # Placeholder implementation for Commit 8b
    # Real plugin orchestration will be implemented in Commit 8d
    
    if verbose:
        click.echo(f"Loading configuration from: {config}")
        if output:
            click.echo(f"Output directory override: {output}")
    
    # Basic validation
    if not config.exists():
        raise click.FileError(str(config), hint="Configuration file not found")
    
    # JSON validation  
    try:
        with open(config) as f:
            config_data = json.load(f)
    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid JSON in configuration file: {e}")
    
    if verbose:
        click.echo("Configuration loaded successfully")
        click.echo("Plugin orchestration not yet implemented (pending Commit 8d)")
    
    click.echo("galleria generate: CLI argument parsing working correctly")


if __name__ == "__main__":
    cli()