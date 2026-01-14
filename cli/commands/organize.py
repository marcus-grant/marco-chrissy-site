"""Organize command implementation."""

import click

from build.benchmark import TimingContext
from organizer.normpic import NormPicOrganizer

from .validate import validate


@click.command()
@click.option("--benchmark", is_flag=True, help="Output timing metrics for benchmarking")
def organize(benchmark: bool):
    """Orchestrate NormPic photo organization."""
    click.echo("Running photo organization...")

    timer = TimingContext() if benchmark else None
    if timer:
        timer.__enter__()

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
        if timer:
            timer.__exit__(None, None, None)
            click.echo(f"Benchmark: organize duration {timer.duration_s:.3f} seconds")
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
        ctx.exit(1)

    click.echo("Organization completed successfully!")

    if timer:
        timer.__exit__(None, None, None)
        click.echo(f"Benchmark: organize duration {timer.duration_s:.3f} seconds")
