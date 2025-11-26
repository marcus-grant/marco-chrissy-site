"""Organize command implementation."""

import click

from organizer.normpic import NormPicOrganizer

from .validate import validate


@click.command()
def organize():
    """Orchestrate NormPic photo organization."""
    click.echo("Running photo organization...")

    # Run validation first (cascading pattern)
    click.echo("Running validation checks...")
    ctx = click.get_current_context()
    ctx.invoke(validate)

    # Initialize organizer with config
    organizer = NormPicOrganizer()

    # Check if already organized (idempotent behavior)
    if organizer.is_already_organized():
        click.echo("✓ Photos are already organized, skipping...")
        click.echo("Organization completed successfully!")
        return

    # Organize photos using NormPic
    click.echo("Orchestrating NormPic tool...")
    result = organizer.organize_photos()

    if result.success:
        click.echo("✓ NormPic organization completed successfully!")
        if result.pics_processed:
            click.echo(f"  Processed {result.pics_processed} photos")
        if result.manifest_path:
            click.echo(f"  Generated manifest: {result.manifest_path}")
    else:
        click.echo("✗ NormPic organization failed:")
        for error in result.errors:
            click.echo(f"  - {error}")
        return

    click.echo("Organization completed successfully!")
