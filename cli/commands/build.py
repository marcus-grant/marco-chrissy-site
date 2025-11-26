"""Build command implementation."""

import os
import subprocess
import sys
from pathlib import Path

import click

import pelican

from serializer.json import JsonConfigLoader
from .organize import organize


@click.command()
def build():
    """Build the complete site with galleries and pages."""
    click.echo("Building site...")

    # Load site configuration
    try:
        config_loader = JsonConfigLoader()
        site_config = config_loader.load_config(Path("config/site.json"))
        galleria_config = config_loader.load_config(Path("config/galleria.json"))
    except Exception as e:
        click.echo(f"✗ Failed to load configuration: {e}")
        ctx = click.get_current_context()
        ctx.exit(1)

    # Run organize first (cascading pattern)
    click.echo("Running organization...")
    ctx = click.get_current_context()
    result = ctx.invoke(organize)

    if result and hasattr(result, 'exit_code') and result.exit_code != 0:
        click.echo("✗ Organize failed - stopping build")
        ctx.exit(1)

    # Check if already built (idempotent behavior)
    output_dir = site_config.get("output_dir", "output")
    if _is_already_built(output_dir):
        click.echo("✓ Site is already built and up to date, skipping...")
        click.echo("Build completed successfully!")
        return

    # Generate galleries using Galleria
    click.echo("Generating galleries with Galleria...")
    try:
        # Create galleria config file in temp location
        import tempfile
        import json
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(galleria_config, f, indent=2)
            temp_config_path = f.name
        
        try:
            # Call galleria CLI with the config
            cmd = [sys.executable, "-m", "galleria", "generate", "--config", temp_config_path]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            click.echo("✓ Galleria generation completed successfully!")
        finally:
            # Clean up temp file
            os.unlink(temp_config_path)
            
    except subprocess.CalledProcessError as e:
        click.echo(f"✗ Galleria generation failed: {e.stderr or e.stdout}")
        ctx.exit(1)
    except Exception as e:
        click.echo(f"✗ Galleria generation failed: {e}")
        ctx.exit(1)

    # Generate site pages using Pelican
    click.echo("Generating site pages with Pelican...")
    try:
        pelican_instance = pelican.Pelican()
        pelican_instance.run()
        click.echo("✓ Pelican generation completed successfully!")
    except Exception as e:
        click.echo(f"✗ Pelican generation failed: {e}")
        ctx.exit(1)

    click.echo("Build completed successfully!")


def _is_already_built(output_dir="output"):
    """Check if site is already built and up to date."""
    # Simple check for key output files existence
    output_paths = [
        f"{output_dir}/galleries",
        f"{output_dir}/index.html"
    ]

    return all(os.path.exists(path) for path in output_paths)
