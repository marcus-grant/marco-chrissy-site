"""Organize command implementation."""

import click
from organizer.normpic import NormPicOrganizer


@click.command()
def organize():
    """Orchestrate NormPic photo organization."""
    click.echo("Running photo organization...")
    
    # Initialize organizer
    organizer = NormPicOrganizer()
    
    # Organize photos using NormPic
    click.echo("Orchestrating NormPic tool...")
    result = organizer.organize_photos()
    
    if result.success:
        click.echo("✓ NormPic organization completed successfully!")
    else:
        click.echo("✗ NormPic organization failed:")
        for error in result.errors:
            click.echo(f"  - {error}")
        return
    
    click.echo("Organization completed successfully!")