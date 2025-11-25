"""Organize command implementation."""

import click
from organizer.normpic import NormPicOrganizer


@click.command()
def organize():
    """Orchestrate NormPic photo organization."""
    click.echo("Running photo organization...")
    
    # Initialize organizer with config
    organizer = NormPicOrganizer()
    
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