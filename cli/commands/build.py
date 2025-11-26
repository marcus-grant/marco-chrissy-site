"""Build command implementation."""

import os

import click

import galleria
import pelican

from .organize import organize


@click.command()
def build():
    """Build the complete site with galleries and pages."""
    click.echo("Building site...")

    # Run organize first (cascading pattern)
    click.echo("Running organization...")
    ctx = click.get_current_context()
    result = ctx.invoke(organize)

    if result and hasattr(result, 'exit_code') and result.exit_code != 0:
        click.echo("✗ Organize failed - stopping build")
        ctx.exit(1)

    # Check if already built (idempotent behavior)
    if _is_already_built():
        click.echo("✓ Site is already built and up to date, skipping...")
        click.echo("Build completed successfully!")
        return

    # Generate galleries using Galleria
    click.echo("Generating galleries with Galleria...")
    try:
        galleria_result = galleria.generate()
        if not galleria_result.success:
            click.echo("✗ Galleria generation failed:")
            for error in getattr(galleria_result, 'errors', ['Unknown error']):
                click.echo(f"  - {error}")
            ctx.exit(1)
        click.echo("✓ Galleria generation completed successfully!")
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


def _is_already_built():
    """Check if site is already built and up to date."""
    # Simple check for key output files existence
    output_paths = [
        "output/galleries",
        "output/index.html"
    ]

    return all(os.path.exists(path) for path in output_paths)
