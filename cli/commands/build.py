"""Build command implementation."""

import os

import click

from build.exceptions import BuildError
from build.orchestrator import BuildOrchestrator

from .organize import organize


@click.command()
def build():
    """Build the complete site with galleries and pages."""
    click.echo("Building site...")

    # Run organize first (cascading pattern)
    click.echo("Running organization...")
    ctx = click.get_current_context()
    result = ctx.invoke(organize)

    if result and hasattr(result, "exit_code") and result.exit_code != 0:
        click.echo("✗ Organize failed - stopping build")
        ctx.exit(1)

    # Execute complete build using orchestrator
    click.echo("Generating galleries and site pages...")
    try:
        orchestrator = BuildOrchestrator()
        orchestrator.execute()
        click.echo("✓ Build completed successfully!")

    except BuildError as e:
        click.echo(f"✗ Build failed: {e}")
        ctx.exit(1)


def _is_already_built(output_dir="output"):
    """Check if site is already built and up to date."""
    # Simple check for key output files existence
    output_paths = [f"{output_dir}/galleries", f"{output_dir}/index.html"]

    return all(os.path.exists(path) for path in output_paths)
